"""Testes sintéticos de regressão: não são resultados de validação científica."""
from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
import re

import pytest

from backend.comparacao_baselines_v01_v02 import (
    _checar_relacao, comparar_desenvolvimento, salvar_relatorios,
)
from backend.baseline_experimental import STATUS_PONTUADO
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_audit import EntradaLexical
from backend.pares_piloto import CAMPOS, validar_pares


@dataclass
class FakeToken:
    text: str
    idx: int
    pos_: str


class FakeNLP:
    def __init__(self):
        self.textos_processados = []

    def __call__(self, texto):
        self.textos_processados.append(texto)
        regras = {"pedido": "NOUN", "dedicada": "ADJ", "dedicado": "ADJ"}
        return [FakeToken(m.group(0), m.start(), regras.get(m.group(0).casefold(), "NOUN"))
                for m in re.finditer(r"\w+", texto)]


def lex(termo, polaridade=1, categoria="adj"):
    return EntradaLexical(
        origem="oplexicon", arquivo="fixture.txt", linha=1, termo=termo,
        lema=None, categoria=categoria, polaridades=(("GLOBAL", polaridade),),
        alvo=None, flexao=None, anotacao="TESTE", revisao=None, atributos_originais=(),
    )


def par(id, familia, feminina, masculina, rotulo, *, particao="desenvolvimento", aprovado=True):
    dados = {k: "" for k in CAMPOS}
    dados.update({
        "id_par": id, "familia": familia, "particao": particao,
        "frase_feminina": feminina, "frase_masculina": masculina,
        "_linha_csv": int(id[-2:]) + 1,
    })
    if aprovado:
        dados.update({"rotulo_revisor1": rotulo, "rotulo_revisor2": rotulo,
                      "equivalencia_revisor1": "sim", "equivalencia_revisor2": "sim",
                      "id_revisor1": "R01", "id_revisor2": "R02"})
    return dados


def fixture():
    linhas = [
        par("P001", "atendimento", "A atendente registrou o pedido.", "O atendente registrou o pedido.", "neutra"),
        par("P002", "estudo", "A aluna é dedicada.", "O aluno é dedicado.", "positiva"),
        par("P003", "rotina", "A aluna estudou.", "O aluno estudou.", "neutra"),
        par("P004", "reserva", "A cientista registrou o pedido.", "O cientista registrou o pedido.", "neutra", particao="avaliacao"),
    ]
    auditoria = validar_pares(linhas, sha256="sha-teste")
    assert not auditoria["erros"], auditoria["erros"]
    indice = IndiceLexical([lex("pedido"), lex("dedicada"), lex("dedicado")], lexico="oplexicon")
    nlp = FakeNLP()
    return linhas, auditoria, indice, nlp


def test_contagens_e_transicoes_nao_confundem_abstencao_com_acerto():
    linhas, auditoria, indice, nlp = fixture()
    resumo, detalhes = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    assert resumo["pares_desenvolvimento_aprovados"] == 3
    assert len(detalhes) == 6
    assert resumo["pares_avaliacao_classificados"] == 0
    v01 = resumo["metricas"]["v01"]
    v02 = resumo["metricas"]["v02"]
    assert (v01["frases_pontuadas"], v01["previsoes_corretas"], v01["previsoes_incorretas"]) == (4, 2, 2)
    assert (v02["frases_pontuadas"], v02["previsoes_corretas"], v02["previsoes_incorretas"]) == (2, 2, 0)
    assert v01["acuracia_seletiva"] == 0.5
    assert v02["acuracia_seletiva"] == 1.0  # apenas neste cenário artificial
    assert resumo["previsoes_incorretas_v01_retiradas_por_abstencao"] == 2
    assert resumo["previsoes_corretas_v01_perdidas_por_abstencao"] == 0
    assert resumo["transicoes_v01_para_v02"] == {
        "abstencao_preservada": 2,
        "pontuacao_para_abstencao": 2,
        "pontuacao_preservada": 2,
    }


def test_reserva_nunca_enviada_ao_modelo_gramatical():
    linhas, auditoria, indice, nlp = fixture()
    _, detalhes = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    assert all(x["id_par"] != "P004" for x in detalhes)
    assert not any("cientista" in texto for texto in nlp.textos_processados)


def test_ausencia_de_previsoes_retorna_acuracia_indefinida():
    linhas, auditoria, indice, nlp = fixture()
    resumo, _ = comparar_desenvolvimento(linhas, auditoria, IndiceLexical([lex("inexistente")], lexico="oplexicon"), nlp=nlp)
    for versao in ("v01", "v02"):
        assert resumo["metricas"][versao]["acuracia_seletiva"] is None
        assert resumo["metricas"][versao]["frases_pontuadas"] == 0


def test_p006_falso_positivo_v01_para_abstencao_v02():
    linhas, auditoria, indice, nlp = fixture()
    _, detalhes = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    p006 = [x for x in detalhes if x["id_par"] == "P001"]
    assert len(p006) == 2
    assert all(x["classe_v01"] == "positiva" and x["acerto_v01"] is False for x in p006)
    assert all(x["status_v02"] == "ABSTENCAO_CATEGORIA_GRAMATICAL" for x in p006)
    assert all(x["acerto_v02"] is None for x in p006)


def test_família_ou_rotulo_de_avaliacao_nao_entra_no_resumo():
    linhas, auditoria, indice, nlp = fixture()
    resumo, _ = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    assert "cientista" not in json.dumps(resumo)
    assert "\"familia\": \"reserva\"" not in json.dumps(resumo)


def test_exige_indice_oplexicon():
    linhas, auditoria, indice, nlp = fixture()
    indice.lexico = "sentilex"
    with pytest.raises(ValueError, match="OpLexicon"):
        comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)


def test_falha_fechada_em_auditoria_invalida():
    linhas, auditoria, indice, nlp = fixture()
    auditoria["erros"] = ["duplicado"]
    with pytest.raises(ValueError, match="validado"):
        comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)


def test_sem_revisores_aprovados_falha():
    linhas = [par("P001", "f", "A aluna estudou.", "O aluno estudou.", "neutra", aprovado=False)]
    auditoria = validar_pares(linhas, sha256="x")
    with pytest.raises(ValueError, match="aprovados"):
        comparar_desenvolvimento(linhas, auditoria, IndiceLexical([lex("pedido")], lexico="oplexicon"), nlp=FakeNLP())


def test_inconsistencia_v02_nao_pode_mudar_classe_sem_abster():
    with pytest.raises(ValueError, match="modificou pontuação"):
        _checar_relacao(
            {"status": STATUS_PONTUADO, "pontuacao_exploratoria": 1, "classe_exploratoria": "positiva"},
            {"status": STATUS_PONTUADO, "pontuacao_exploratoria": -1, "classe_exploratoria": "negativa"},
        )


def test_relatorios_csv_json_e_sem_sobrescrita(tmp_path):
    linhas, auditoria, indice, nlp = fixture()
    resumo, dados = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    j = tmp_path / "privado" / "resumo.json"
    c = tmp_path / "privado" / "linhas.csv"
    salvar_relatorios(j, c, resumo, dados)
    assert json.loads(j.read_text(encoding="utf-8"))["pares_avaliacao_classificados"] == 0
    with c.open(encoding="utf-8-sig", newline="") as f:
        assert len(list(csv.DictReader(f, delimiter=";"))) == 6
    with pytest.raises(FileExistsError):
        salvar_relatorios(j, c, resumo, dados)


def test_saida_csv_sem_texto_das_frases(tmp_path):
    linhas, auditoria, indice, nlp = fixture()
    resumo, dados = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    j, c = tmp_path / "a.json", tmp_path / "b.csv"
    salvar_relatorios(j, c, resumo, dados)
    assert "A atendente registrou o pedido." not in c.read_text(encoding="utf-8-sig")
    assert "A atendente registrou o pedido." not in j.read_text(encoding="utf-8")


def test_pares_ambos_pontuados_diminuem_com_filtragem():
    linhas, auditoria, indice, nlp = fixture()
    resumo, _ = comparar_desenvolvimento(linhas, auditoria, indice, nlp=nlp)
    assert resumo["metricas"]["v01"]["pares_ambos_pontuados"] == 2
    assert resumo["metricas"]["v02"]["pares_ambos_pontuados"] == 1
