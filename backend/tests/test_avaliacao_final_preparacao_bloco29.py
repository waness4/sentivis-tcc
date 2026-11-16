"""Somente fixtures artificiais. Não importa corpus reservado ou arquivos privados."""
from copy import deepcopy
import sys

import pytest

from backend.avaliacao_final_preparacao_bloco29 import (
    PONTUADO, _ficticios, _razao, _validar_saida,
    main, resumir, validar_ficha,
)


def saida(nota=None):
    if nota is None:
        return {"status": "ABSTENCAO_TESTE", "pontuacao_exploratoria": None,
                "classe_exploratoria": None}
    classe = "positiva" if nota > 0 else "negativa" if nota < 0 else "neutra"
    return {"status": PONTUADO, "pontuacao_exploratoria": nota,
            "classe_exploratoria": classe}


def dados():
    pares, ficha = _ficticios()
    valores = {"SINT001": 1, "SINT002": -1, "SINT003": 0, "SINT004": 1}
    pred = {p["id_par"]: {m: {lado: saida(valores[p["id_par"]])
                 for lado in ("feminina", "masculina")}
                 for m in ("v01", "v03", "v04")} for p in pares}
    return pares, ficha, pred


def test_ficha_sintetica_valida_e_preserva_todos_os_ids():
    p, f, _ = dados()
    assert set(validar_ficha(p, f)) == {x["id_par"] for x in p}


def test_estruturas_e_denominadores_globais():
    p, f, resultados = dados()
    resumo = resumir(p, f, resultados)
    assert (resumo["P_total"], resumo["F_total"], resumo["P_equivalentes_R01"]) == (4, 8, 3)
    assert resumo["P_elegiveis_com_rotulo_posneg"] == 2
    assert resumo["P_elegiveis_com_rotulo_neutro_separado"] == 1
    assert resumo["P_nao_elegiveis_por_motivo"] == {"equivalencia_nao": 1}
    for m in resumo["metodos"].values():
        assert (m["F_pontuadas_global"], m["F_pontuadas_elegiveis"]) == (8, 6)
        assert (m["F_posneg_compativeis"], m["F_posneg_pontuadas"], m["F_posneg_coincidentes"]) == (4, 4, 4)
        assert m["P_delta_calculavel"] == 3
        assert m["P_delta_nao_nulo"] == 0
    assert resumo["acuracia_validada"] is None
    assert resumo["concordancia_interavaliadores"] is None
    assert resumo["evidencia_de_vies"] is None


def test_abstencao_nao_vira_delta_zero():
    p, f, r = dados()
    r["SINT001"]["v04"]["masculina"] = saida(None)
    x = resumir(p, f, r)["metodos"]["v04"]
    assert x["F_abstidas_global"] == 1
    assert x["P_delta_calculavel"] == 2
    assert x["P_delta_nao_calculavel"] == 1
    assert x["F_posneg_pontuadas"] == 3


def test_delta_nao_nulo_somente_se_duas_pontuacoes():
    p, f, r = dados()
    r["SINT002"]["v03"]["masculina"] = saida(1)
    x = resumir(p, f, r)["metodos"]["v03"]
    assert x["P_delta_calculavel"] == 3
    assert x["P_delta_nao_nulo"] == 1
    assert x["F_posneg_coincidentes"] == 3


def test_anotacao_neutra_nao_entra_na_coincidencia_primaria():
    p, f, r = dados()
    r["SINT003"]["v01"]["feminina"] = saida(1)
    x = resumir(p, f, r)["metodos"]["v01"]
    assert x["F_posneg_compativeis"] == 4
    assert x["F_posneg_coincidentes"] == 4
    assert x["P_delta_nao_nulo"] == 1


def test_denominadores_zero_ficam_indefinidos():
    p, f, r = dados()
    for x in f:
        x["equivalencia"], x["rotulo"], x["observacoes"] = "nao", "", "Exemplo fictício"
    x = resumir(p, f, r)["metodos"]["v04"]
    for key in ("taxa_pontuacao_elegivel", "coincidencia_nominal_seletiva_anotacao_unica",
                "taxa_pares_delta_calculavel", "fracao_delta_nao_nulo"):
        assert x[key] is None
    assert _razao(0, 0) is None


def test_ficha_sem_par_ou_id_duplicado_falha():
    p, f, _ = dados()
    with pytest.raises(ValueError):
        validar_ficha(p, f[:-1])
    with pytest.raises(ValueError):
        validar_ficha(p, f + [f[0]])


def test_texto_modificado_falha():
    p, f, _ = dados()
    f[0]["frase_feminina"] += " modificado"
    with pytest.raises(ValueError, match="Frase"):
        validar_ficha(p, f)


def test_nao_equivalente_precisa_justificar_e_nao_pode_ter_rotulo():
    p, f, _ = dados()
    f[3]["observacoes"] = ""
    with pytest.raises(ValueError, match="justificativa"):
        validar_ficha(p, f)
    f[3]["observacoes"] = "não equivalente"
    f[3]["rotulo"] = "positiva"
    with pytest.raises(ValueError, match="não pode"):
        validar_ficha(p, f)


def test_abstencao_com_zero_falha_fechada():
    with pytest.raises(ValueError, match="Abstenção"):
        _validar_saida({"status": "ABSTENCAO", "pontuacao_exploratoria": 0,
                       "classe_exploratoria": "neutra"})


def test_classe_nao_coerente_com_sinal_falha_fechada():
    with pytest.raises(ValueError, match="contradiz"):
        _validar_saida({"status": PONTUADO, "pontuacao_exploratoria": 1,
                       "classe_exploratoria": "negativa"})


def test_metodos_incompletos_falham():
    p, f, r = dados()
    del r["SINT001"]["v04"]
    with pytest.raises(ValueError, match="Métodos"):
        resumir(p, f, r)


def test_saida_de_par_incompleta_falha():
    p, f, r = dados()
    del r["SINT001"]["v04"]["masculina"]
    with pytest.raises(ValueError, match="dois lados"):
        resumir(p, f, r)


def test_nenhum_arquivo_de_avaliacao_pode_ser_informado_na_cli(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["avaliacao_final_preparacao_bloco29", "simular",
                                    "--entrada", "data/piloto/restrito/avaliacao_final.csv"])
    with pytest.raises(SystemExit) as erro:
        main()
    assert erro.value.code == 2
