"""Testes sintéticos do Bloco 27, sem leitura de fichas privadas."""
import pytest
from scripts.auditar_r01_bloco27 import descrever


def exemplo():
    m = {"C001": "Exemplo positivo.", "C002": "Exemplo negativo."}
    r = [
        dict(id_controle="C001", texto="Exemplo positivo.", polaridade="positivo", referente="livre", papel_com="", observacoes=""),
        dict(id_controle="C002", texto="Exemplo negativo.", polaridade="negativo", referente="livre", papel_com="", observacoes=""),
    ]
    return m, r


def analizar(m, r):
    return descrever(m, r, sha_controles="hash", sha_ficha="ficha", separador="virgula")


def test_nao_calcula_metrica_de_validacao():
    m, r = exemplo()
    x = analizar(m, r)
    assert x["acuracia"] is None and x["kappa_cohen"] is None
    assert x["concordancia_entre_avaliadores"] is None
    assert x["dados_da_avaliacao_final_lidos"] is False


def test_termos_individuais_nao_transformados_em_gabarito():
    m, r = exemplo()
    x = analizar(m, r)
    assert x["polaridade_informada"] == {"negativo": 1, "positivo": 1}
    assert x["polaridade_positiva_negativa_com_normalizacao_morfologica_possivel"] == 2
    assert x["referentes_fora_do_vocabulario_controlado"] == 2


def test_neutro_permanece_ambiguo():
    m, r = exemplo()
    r[0]["polaridade"] = "neutro"
    x = analizar(m, r)
    assert x["neutro_generico_a_revisar"] == 1
    assert x["polaridade_positiva_negativa_com_normalizacao_morfologica_possivel"] == 1


def test_espaco_duplicado_sinalizado_sem_alterar_ficha():
    m, r = exemplo()
    r[0]["texto"] = "Exemplo  positivo."
    x = analizar(m, r)
    assert x["id_texto_espacamento_divergente"] == ["C001"]
    assert r[0]["texto"] == "Exemplo  positivo."


def test_rejeita_mudanca_substantiva_de_texto():
    m, r = exemplo()
    r[0]["texto"] = "Exemplo diferente."
    with pytest.raises(ValueError, match="diferença substantiva"):
        analizar(m, r)


def test_rejeita_duplicidade_ids():
    m, r = exemplo()
    r[1]["id_controle"] = "C001"
    with pytest.raises(ValueError, match="repetidos"):
        analizar(m, r)


def test_nao_inventa_segunda_ficha():
    m, r = exemplo()
    x = analizar(m, r)
    assert x["avaliadores_com_resposta"] == 1
