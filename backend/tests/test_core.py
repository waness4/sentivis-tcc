from backend.core import analisar, comparar, ler_lexico, normalizar
import pytest


def test_normalizacao_preserva_acentos():
    assert normalizar(" ÓTIMA ") == "ótima"


def test_ausencia_nao_e_neutralidade():
    saida = analisar("A médica entregou o documento.", {"ótimo": 1})
    assert saida["classe"] == "sem_cobertura"
    assert saida["pontuacao"] is None


def test_neutralidade_requer_cobertura():
    saida = analisar("documento", {"documento": 0})
    assert saida["classe"] == "neutra"
    assert len(saida["encontrados"]) == 1


def test_comparacao_diferencas_em_fixture_artificial():
    fixture_sintetica = {"ótimo": 1, "ótima": -1}
    saida = comparar("ótima", "ótimo", fixture_sintetica)
    assert saida["delta_feminino_masculino"] == -2
    assert saida["classificacao_divergente"] is True


def test_aviso_negacao():
    saida = analisar("não bom", {"bom": 1})
    assert saida["avisos"]
    assert saida["classe"] == "positiva"  # comprova limitação atual do protótipo


def test_csv_rejeita_polaridades_conflitantes(tmp_path):
    caminho = tmp_path / "fixture.csv"
    caminho.write_text("termo;polaridade\nbom;1\nbom;-1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="conflitantes"):
        ler_lexico(caminho)
