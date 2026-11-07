"""Testes de isolamento e rastreabilidade; NÃO avaliam desempenho científico."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from backend.controles_sintaticos_v03 import (
    ARQUIVO_CONTROLES, CABECALHO, CENARIOS, METODO, SHA256_CONTROLES,
    _numeros, analisar_controles, ler_controles, salvar,
)
from backend.frase_diagnostico import IndiceLexical
from backend.tests.test_baseline_contextual_v03 import FakeNLP, lexema


def fixture_controles():
    return [
        {"id_controle": "C900", "cenario": "modo_potencial", "texto": "A atendente tratou com gentileza."},
        {"id_controle": "C901", "cenario": "avaliacao_sem_com", "texto": "O atendente respondeu."},
    ]


def index():
    return IndiceLexical([lexema("gentileza", 1)], lexico="sentilex")


def fixture_file(tmp_path, rows, header=CABECALHO):
    path = tmp_path / "controles.csv"
    with path.open("w", encoding="utf-8", newline="") as fd:
        wr = csv.writer(fd, delimiter=";", lineterminator="\n")
        wr.writerow(header)
        wr.writerows(rows)
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_arq_original_fingerprint_e_tamanho():
    path = Path(__file__).resolve().parents[2] / ARQUIVO_CONTROLES
    cont, sha = ler_controles(path)
    assert sha == SHA256_CONTROLES
    assert len(cont) == 36
    assert {c["cenario"] for c in cont} == CENARIOS
    assert len({c["texto"] for c in cont}) == 36


def test_fingerprint_nao_permite_arquivos_arbitrarios(tmp_path):
    path, _ = fixture_file(tmp_path, [["C001", "modo_potencial", "Um texto de controle adicional."]])
    with pytest.raises(ValueError, match="SHA-256"):
        ler_controles(path)


def test_reserva_com_colunas_de_piloto_rejeitada(tmp_path):
    path, sha = fixture_file(tmp_path, [["P001", "avaliacao", "texto", "frase"]],
                             header=("id_par", "particao", "frase_feminina", "frase_masculina"))
    with pytest.raises(ValueError, match="Schema"):
        ler_controles(path, sha256_esperado=sha)


def test_id_invalido_rejeitado(tmp_path):
    path, sha = fixture_file(tmp_path, [["P003", "modo_potencial", "Uma frase com sentido completo."]])
    with pytest.raises(ValueError, match="ID inválido"):
        ler_controles(path, sha256_esperado=sha)


def test_id_duplicado_rejeitado(tmp_path):
    path, sha = fixture_file(tmp_path, [["C001", "modo_potencial", "Uma frase com sentido completo."],
                                        ["C001", "modo_potencial", "Outra frase com sentido completo."]])
    with pytest.raises(ValueError, match="repetido"):
        ler_controles(path, sha256_esperado=sha)


def test_cenario_desconhecido_rejeitado(tmp_path):
    path, sha = fixture_file(tmp_path, [["C001", "avaliacao", "Uma frase com sentido completo."]])
    with pytest.raises(ValueError, match="cenário"):
        ler_controles(path, sha256_esperado=sha)


def test_texto_duplicado_rejeitado(tmp_path):
    path, sha = fixture_file(tmp_path, [["C001", "modo_potencial", "Uma frase com sentido completo."],
                                        ["C002", "modo_potencial", "Uma frase com sentido completo."]])
    with pytest.raises(ValueError, match="duplicada"):
        ler_controles(path, sha256_esperado=sha)


def test_truncado_ou_coluna_extra_rejeitado(tmp_path):
    path, sha = fixture_file(tmp_path, [["C001", "modo_potencial"]])
    with pytest.raises(ValueError, match="campos"):
        ler_controles(path, sha256_esperado=sha)
    path, sha = fixture_file(tmp_path, [["C001", "modo_potencial", "Frase adequada para o controle.", "extra"]])
    with pytest.raises(ValueError, match="campos"):
        ler_controles(path, sha256_esperado=sha)


def test_controles_v01_v03_sem_rotulo_humano():
    resumo, linhas = analisar_controles(fixture_controles(), index(), nlp=FakeNLP(),
                                       alvo="N0", hipotese_modo=True)
    assert resumo["metodo"] == METODO
    assert resumo["n_controles"] == 2
    assert resumo["n_pares_avaliacao_processados"] == 0
    assert resumo["acuracia"] is None and resumo["f1_macro"] is None
    assert resumo["metricas"]["v01"]["acuracia"] is None
    assert resumo["metricas"]["v03"]["f1_macro"] is None
    assert linhas[0]["status_v01"] == "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
    assert linhas[0]["status_v03"] == "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
    assert linhas[1]["status_v03"] == "SEM_COBERTURA"
    assert all("rotulo_referencia" not in l for l in linhas)
    assert all("particao" not in l for l in linhas)


def test_alvo_ou_hipotese_ausentes_rejeitados():
    for alvo, hipotese in [(None, True), ("N0", False), ("N2", True)]:
        with pytest.raises(ValueError):
            analisar_controles(fixture_controles(), index(), nlp=FakeNLP(),
                              alvo=alvo, hipotese_modo=hipotese)


def test_nao_permite_indices_oplexicon():
    with pytest.raises(ValueError, match="SentiLex"):
        analisar_controles(fixture_controles(), IndiceLexical([], lexico="oplexicon"),
                          nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_rejeita_particao_mesmo_na_funcao_interna():
    dados = fixture_controles()
    dados[0]["particao"] = "avaliacao"
    with pytest.raises(ValueError, match="Somente controles"):
        analisar_controles(dados, index(), nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_rejeita_rotulos_injetados():
    dados = fixture_controles()
    dados[0]["rotulo_revisor1"] = "positiva"
    with pytest.raises(ValueError, match="Somente controles"):
        analisar_controles(dados, index(), nlp=FakeNLP(), alvo="N0", hipotese_modo=True)


def test_preserva_v01_apos_v03():
    from backend.baseline_experimental import classificar_exploratoriamente
    i = index()
    frase = fixture_controles()[0]["texto"]
    antes = classificar_exploratoriamente(frase, i, alvo="N0")
    analisar_controles(fixture_controles(), i, nlp=FakeNLP(), alvo="N0", hipotese_modo=True)
    depois = classificar_exploratoriamente(frase, i, alvo="N0")
    assert antes == depois


def test_saidas_json_e_csv(tmp_path):
    resumo, linhas = analisar_controles(fixture_controles(), index(), nlp=FakeNLP(),
                                       alvo="N0", hipotese_modo=True)
    j, c = tmp_path / "result.json", tmp_path / "result.csv"
    salvar(resumo, linhas, j, c)
    d = json.loads(j.read_text(encoding="utf-8"))
    assert d["evidencia_de_vies"] is None
    assert d["acuracia"] is None
    with c.open(encoding="utf-8-sig", newline="") as fd:
        rows = list(csv.DictReader(fd, delimiter=";"))
    assert len(rows) == 2
    assert rows[0]["id_controle"] == "C900"
    assert "rotulo_referencia" not in rows[0]


def test_nao_sobrescreve(tmp_path):
    resumo, linhas = analisar_controles(fixture_controles(), index(), nlp=FakeNLP(),
                                       alvo="N0", hipotese_modo=True)
    j, c = tmp_path / "result.json", tmp_path / "result.csv"
    salvar(resumo, linhas, j, c)
    with pytest.raises(FileExistsError, match="existe"):
        salvar(resumo, linhas, j, c)


def test_mesmo_caminho_rejeitado(tmp_path):
    with pytest.raises(ValueError, match="distintas"):
        salvar({}, [{"foo": 1}], tmp_path/"mesmo", tmp_path/"mesmo")


def test_estatisticas_sem_previsoes():
    x = _numeros([{"status_v03": "SEM_COBERTURA"}], "v03")
    assert x == {"n_frases": 1, "pontuadas": 0, "sem_pontuacao": 1,
                 "taxa_pontuadas": 0.0, "status": {"SEM_COBERTURA": 1},
                 "acuracia": None, "f1_macro": None}


def test_resultados_nao_leem_piloto(monkeypatch):
    """Nenhum módulo de leitura do piloto é necessário para controles."""
    import backend.controles_sintaticos_v03 as mod
    def nao_leia(*args, **kwargs):
        raise AssertionError("Não deve abrir o piloto")
    # O diagnóstico recebe frases diretamente e não referencia caminhos privados.
    assert "pares_piloto" not in mod.analisar_controles.__code__.co_names
    assert "revisao_humana" not in mod.analisar_controles.__code__.co_names
    resumo, _ = mod.analisar_controles(fixture_controles(), index(), nlp=FakeNLP(),
                                      alvo="N0", hipotese_modo=True)
    assert resumo["n_pares_avaliacao_processados"] == 0
