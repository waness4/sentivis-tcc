"""Comparação descritiva pós-coleta, dados inteiramente sintéticos."""
import pytest
from scripts.comparar_r01_bloco27 import comparar, medir


def dados():
    anot = [
        {"id_controle": "C001", "polaridade": "positivo"},
        {"id_controle": "C002", "polaridade": "negativo"},
        {"id_controle": "C003", "polaridade": "neutro"},
    ]
    v1 = {
        "C001": {"status_v01": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA", "classe_v01": "positiva", "status_v03": "ABSTENCAO", "classe_v03": ""},
        "C002": {"status_v01": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA", "classe_v01": "positiva", "status_v03": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA", "classe_v03": "negativa"},
        "C003": {"status_v01": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA", "classe_v01": "neutra", "status_v03": "ABSTENCAO", "classe_v03": ""},
    }
    v4 = {k: {"status_v03": x["status_v03"], "classe_v03": x["classe_v03"],
              "status_v04": x["status_v03"], "classe_v04": x["classe_v03"]} for k, x in v1.items()}
    return anot, v1, v4


def test_contagem_coincidencia_descritiva_e_abstencao():
    anot, v1, v4 = dados()
    rel = comparar(anot, v1, v4)
    x = rel["analise_total"]["v01"]
    assert x["marcacoes_positivas_negativas_elegiveis"] == 2
    assert x["modelo_pontuou_no_recorte"] == 3
    assert x["modelo_pontuou_nas_marcacoes_bivalentes"] == 2
    assert x["coincidencias_nas_pontuadas_bivalentes"] == 1
    assert x["fracao_descritiva_coincidencia_condicional"] == .5
    assert rel["acuracia"] is None


def test_recorte_neutro_excluido_sem_fingir_gabarito():
    anot, v1, v4 = dados()
    x = comparar(anot, v1, v4)["analise_total"]["v03"]
    assert x["modelo_pontuou_nas_marcacoes_bivalentes"] == 1
    assert x["modelo_absteve_nas_marcacoes_bivalentes"] == 1
    assert x["marcacoes_nao_bivalentes_sem_conversao"] == 1


def test_sensibilidade_sem_C001():
    anot, v1, v4 = dados()
    x = comparar(anot, v1, v4)["sensibilidade_sem_C001"]["v01"]
    assert x["frases_no_recorte"] == 2
    assert x["marcacoes_positivas_negativas_elegiveis"] == 1


def test_relatorios_contraditorios_rejeitados():
    anot, v1, v4 = dados()
    v4["C002"]["classe_v03"] = "positiva"
    with pytest.raises(ValueError, match="discordam"):
        comparar(anot, v1, v4)
