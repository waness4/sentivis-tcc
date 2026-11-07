"""Testes do comparador V03 × V04: exclusivamente engenharia, não validade científica."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from backend.baseline_contextual_v03 import classificar_v03
from backend.baseline_contextual_v04 import classificar_v04
from backend.comparacao_controles_v03_v04 import (
    _transicao, comparar_controles, salvar, METODO,
)
from backend.controles_sintaticos_v03 import ARQUIVO_CONTROLES, ler_controles
from backend.tests.test_baseline_contextual_v03 import idx, lexema
from backend.tests.test_baseline_contextual_v04 import NLPV04


def exemplos():
    return [
        {"id_controle": "C005", "cenario": "modo_potencial",
         "texto": "A pesquisadora apresentou os dados com segurança."},
        {"id_controle": "C006", "cenario": "modo_potencial",
         "texto": "O pesquisador apresentou os dados com arrogância."},
    ]


def indice():
    return idx(lexema("dados", 0, "Adj"), lexema("segurança", 1, "N"),
               lexema("arrogância", -1, "N"))


def nlp():
    return NLPV04(anexacao={"segurança": ("nmod", "dados"),
                              "arrogância": ("nmod", "dados")})


def resultado():
    return comparar_controles(exemplos(), indice(), nlp=nlp(),
                              alvo="N0", hipotese_modo=True)


def test_c005_c006_ambiguidade_diagnosticada_apos_filtragem():
    resumo, linhas = resultado()
    assert len(linhas) == 2
    assert all(l["status_v03"] == "ABSTENCAO_CATEGORIA_GRAMATICAL" for l in linhas)
    assert all(l["status_v04"] == "ABSTENCAO_ANEXACAO_AMBIGUA" for l in linhas)
    assert all(l["filtro_neutro_aplicado"] is True for l in linhas)
    assert all(l["neutros_descartados"] == ["dados"] for l in linhas)
    assert all(l["motivos_v04"] == ["sintagma_com_ligado_a_nome"] for l in linhas)
    assert resumo["frases_com_status_alterado"] == 2
    assert resumo["metricas"]["v03"]["pontuadas"] == 0
    assert resumo["metricas"]["v04"]["pontuadas"] == 0


def test_relatorio_nao_produz_metricas_de_validacao():
    r, _ = resultado()
    assert r["metodo"] == METODO
    assert r["n_pares_avaliacao_processados"] == 0
    assert r["evidencia_de_vies"] is None
    assert r["acuracia"] is None and r["f1_macro"] is None
    assert all(r["metricas"][v]["acuracia"] is None for v in ("v03", "v04"))


def test_sem_esquema_de_piloto_rejeita_particao_e_rotulos():
    exemplo = {**exemplos()[0], "particao": "avaliacao", "rotulo_referencia": "positiva"}
    with pytest.raises(ValueError, match="Somente controles"):
        comparar_controles([exemplo], indice(), nlp=nlp(), alvo="N0", hipotese_modo=True)


def test_id_do_piloto_rejeitado():
    exemplo = {**exemplos()[0], "id_controle": "P001"}
    with pytest.raises(ValueError, match="ID de controle"):
        comparar_controles([exemplo], indice(), nlp=nlp(), alvo="N0", hipotese_modo=True)


def test_duplicado_rejeitado():
    with pytest.raises(ValueError, match="duplicado"):
        comparar_controles(exemplos() * 2, indice(), nlp=nlp(), alvo="N0", hipotese_modo=True)


def test_indice_oplexicon_rejeitado():
    from backend.frase_diagnostico import IndiceLexical
    i = IndiceLexical([lexema("segurança", 1)], lexico="oplexicon")
    with pytest.raises(ValueError, match="SentiLex"):
        comparar_controles(exemplos(), i, nlp=nlp(), alvo="N0", hipotese_modo=True)


def test_alvo_e_hipotese_obrigatorios():
    with pytest.raises(ValueError, match="Alvo"):
        comparar_controles(exemplos(), indice(), nlp=nlp(), alvo="", hipotese_modo=True)
    with pytest.raises(ValueError, match="hipótese"):
        comparar_controles(exemplos(), indice(), nlp=nlp(), alvo="N0", hipotese_modo=False)
    with pytest.raises(ValueError, match="Etiquetador"):
        comparar_controles(exemplos(), indice(), nlp=None, alvo="N0", hipotese_modo=True)


def test_salvar_json_csv_e_campos(tmp_path):
    resumo, linhas = resultado()
    j = tmp_path / "comparacao.json"
    c = tmp_path / "comparacao.csv"
    salvar(resumo, linhas, j, c)
    assert json.loads(j.read_text(encoding="utf-8"))["n_controles"] == 2
    with c.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert len(rows) == 2
    assert rows[0]["neutros_descartados"] == "dados"
    assert rows[0]["motivos_v03"] == "categoria_gramatical_incompativel"
    assert rows[0]["motivos_v04"] == "sintagma_com_ligado_a_nome"
    assert "rotulo_referencia" not in rows[0]
    assert "particao" not in rows[0]


def test_nao_sobrescreve_resultados(tmp_path):
    resumo, linhas = resultado()
    j = tmp_path / "a.json"
    c = tmp_path / "b.csv"
    salvar(resumo, linhas, j, c)
    with pytest.raises(FileExistsError):
        salvar(resumo, linhas, j, c)
    assert json.loads(j.read_text(encoding="utf-8"))["n_controles"] == 2


def test_mesmo_arquivo_rejeitado(tmp_path):
    resumo, linhas = resultado()
    with pytest.raises(ValueError, match="distintos"):
        salvar(resumo, linhas, tmp_path / "iguais", tmp_path / "iguais")


def test_sem_linhas_rejeitado(tmp_path):
    with pytest.raises(ValueError, match="Nenhum resultado"):
        salvar({}, [], tmp_path / "a", tmp_path / "b")


def test_reprodutibilidade_sem_mutar_baselines():
    e = exemplos()[0]["texto"]
    i, tag = indice(), nlp()
    v03 = classificar_v03(e, i, alvo="N0", nlp=tag, hipotese_modo=True)
    v04 = classificar_v04(e, i, alvo="N0", nlp=tag, hipotese_modo=True)
    _, _ = comparar_controles(exemplos(), i, nlp=tag, alvo="N0", hipotese_modo=True)
    assert classificar_v03(e, i, alvo="N0", nlp=tag, hipotese_modo=True) == v03
    assert classificar_v04(e, i, alvo="N0", nlp=tag, hipotese_modo=True) == v04


def test_categorias_de_transicao():
    base = {"status": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA", "classe_exploratoria": "positiva", "pontuacao_exploratoria": 1}
    outro = {"status": "ABSTENCAO_LEXICAL", "classe_exploratoria": None, "pontuacao_exploratoria": None}
    assert _transicao(base, outro) == "pontuada_para_abstencao"
    assert _transicao(outro, base) == "abstencao_para_pontuada"
    assert _transicao(outro, outro) == "abstencoes_com_mesmo_status"
    assert _transicao(base, base) == "pontuadas_ambas_iguais"
    assert _transicao(base, {**base, "pontuacao_exploratoria": 2}) == "pontuadas_ambas_diferentes"
    assert _transicao(outro, {**outro, "status": "SEM_COBERTURA"}) == "abstencoes_com_status_diferente"


def test_arquivo_fixado_36_frases_sha():
    arquivo = Path(__file__).resolve().parents[2] / ARQUIVO_CONTROLES
    controles, sha = ler_controles(arquivo)
    assert len(controles) == 36
    assert sha == "a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc"


def test_entrada_vazia_rejeitada():
    with pytest.raises(ValueError, match="Nenhum controle"):
        comparar_controles([], indice(), nlp=nlp(), alvo="N0", hipotese_modo=True)
