"""Testes sintéticos; nenhum resultado de avaliação final é classificado."""
from __future__ import annotations

from copy import deepcopy

import pytest

from backend.comparacao_sentilex_v01_v03 import (
    _estatisticas, comparar_desenvolvimento_sentilex, salvar,
)
from backend.frase_diagnostico import IndiceLexical
from backend.pares_piloto import validar_pares
from backend.tests.test_baseline_contextual_v03 import FakeNLP, lexema


def par(id_par, familia, parte, fem, masc, *, rotulo="positiva", aprovado=True):
    return {
        "id_par": id_par, "familia": familia, "particao": parte,
        "frase_feminina": fem, "frase_masculina": masc,
        "rotulo_revisor1": rotulo if aprovado else "",
        "rotulo_revisor2": rotulo if aprovado else "",
        "equivalencia_revisor1": "sim" if aprovado else "",
        "equivalencia_revisor2": "sim" if aprovado else "",
        "id_revisor1": "R01" if aprovado else "",
        "id_revisor2": "R02" if aprovado else "",
        "alvo_sentilex_feminina": "", "alvo_sentilex_masculina": "",
        "observacoes": "", "_linha_csv": 2 if parte == "desenvolvimento" else 3,
    }


def conjunto():
    return [
        par("DEV", "atendimento", "desenvolvimento",
            "A atendente tratou com gentileza.", "O atendente tratou com gentileza."),
        par("RESERVADO", "tecnologia", "avaliacao",
            "Texto secreto reservado feminino.", "Texto secreto reservado masculino.",
            aprovado=False),
    ]


def preparar(pares=None):
    dados = pares if pares is not None else conjunto()
    relatorio = validar_pares(dados, sha256="fixture-sha")
    assert not relatorio["erros"]
    indice = IndiceLexical([lexema("gentileza", 1)], lexico="sentilex")
    return dados, relatorio, indice


def test_reservado_nao_e_classificado(monkeypatch):
    import backend.comparacao_sentilex_v01_v03 as modulo
    dados, relatorio, indice = preparar()
    orig_v01, orig_v03 = modulo.classificar_exploratoriamente, modulo.classificar_v03
    vistos = []

    def vigiar_v01(texto, *args, **kw):
        vistos.append(texto)
        return orig_v01(texto, *args, **kw)

    def vigiar_v03(texto, *args, **kw):
        vistos.append(texto)
        return orig_v03(texto, *args, **kw)

    monkeypatch.setattr(modulo, "classificar_exploratoriamente", vigiar_v01)
    monkeypatch.setattr(modulo, "classificar_v03", vigiar_v03)
    resumo, linhas = comparar_desenvolvimento_sentilex(
        dados, relatorio, indice, nlp=FakeNLP(), alvo="N0", hipotese_modo=True,
    )
    assert len(vistos) == 4
    assert not any("secreto" in v for v in vistos)
    assert resumo["pares_avaliacao_classificados"] == 0
    assert resumo["pares_aprovados_desenvolvimento"] == 1
    assert len(linhas) == 2
    assert all(l["id_par"] == "DEV" for l in linhas)


def test_v01_v03_dois_acertos_exploratorios():
    dados, relatorio, indice = preparar()
    r, linhas = comparar_desenvolvimento_sentilex(
        dados, relatorio, indice, nlp=FakeNLP(), alvo="N0", hipotese_modo=True)
    assert r["estatisticas"]["v01"]["previsoes_corretas"] == 2
    assert r["estatisticas"]["v03"]["previsoes_corretas"] == 2
    assert r["pares_com_ambas_pontuadas"] == {"v01": 1, "v03": 1}
    assert all(l["transicao"] == "pontuadas_ambas" for l in linhas)


def test_sem_alvo_manual_bloqueado():
    dados, relatorio, indice = preparar()
    with pytest.raises(ValueError, match="alvo manual"):
        comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                          nlp=FakeNLP(), alvo="", hipotese_modo=True)


def test_sem_hipotese_explicita_bloqueado():
    dados, relatorio, indice = preparar()
    with pytest.raises(ValueError, match="hipótese sintática"):
        comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                          nlp=FakeNLP(), alvo="N0", hipotese_modo=False)


def test_dataset_invalido_bloqueado():
    dados, relatorio, indice = preparar()
    relatorio["erros"] = ["vazamento"]
    with pytest.raises(ValueError, match="não validado"):
        comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                          nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_desenvolvimento_nao_revisado_bloqueado():
    dados, _, indice = preparar()
    dados[0] = par("DEV", "atendimento", "desenvolvimento",
                   "A atendente tratou com gentileza.", "O atendente tratou com gentileza.",
                   aprovado=False)
    relatorio = validar_pares(dados, sha256="fixture")
    with pytest.raises(ValueError, match="Nenhum par"):
        comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                          nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_idx_oplexicon_rejeitado():
    dados, relatorio, _ = preparar()
    indice = IndiceLexical([], lexico="oplexicon")
    with pytest.raises(ValueError, match="SentiLex"):
        comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                          nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_acuracia_indefinida_sem_pontuacoes():
    linhas = [{"status_v03": "SEM_COBERTURA", "acerto_v03": None}]
    metrica = _estatisticas(linhas, "v03")
    assert metrica["acuracia_seletiva"] is None
    assert metrica["frases_sem_pontuacao"] == 1


def test_relatorios_nao_sobrescrevem(tmp_path):
    dados, relatorio, indice = preparar()
    r, l = comparar_desenvolvimento_sentilex(dados, relatorio, indice,
                                              nlp=FakeNLP(), alvo="N0", hipotese_modo=True)
    j, c = tmp_path / "comparacao.json", tmp_path / "comparacao.csv"
    salvar(r, l, j, c)
    assert '"pares_avaliacao_classificados": 0' in j.read_text(encoding="utf-8")
    assert "pontuada" in c.read_text(encoding="utf-8-sig")
    with pytest.raises(FileExistsError):
        salvar(r, l, j, c)


def test_relatorios_saida_igual_rejeitados(tmp_path):
    with pytest.raises(ValueError, match="distintos"):
        salvar({}, [], tmp_path / "a.json", tmp_path / "a.json")
