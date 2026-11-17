"""Bloco 37 — testes exclusivamente sobre fixtures inventadas nesta versão.

Não abrir corpus, léxicos ou qualquer arquivo da partição reservada.
"""
from __future__ import annotations

from copy import deepcopy
import csv
import io
import json
import sys

import pytest

from backend import executor_avaliacao_bloco37 as b


class IndiceFicticio:
    lexico = "sentilex"


class EtiquetadorFicticio:
    pass


def _preparar(politica=b.POLITICA_ESTRITA):
    origem, ficha = b._fixture()
    pares = b.validar_origem_em_memoria(origem)
    anotacoes, faltas = b.validar_ficha_em_memoria(ficha, pares, politica=politica)
    return origem, ficha, pares, anotacoes, faltas


def _fake(chamadas=None, *, abster=False, erro=False):
    if chamadas is None:
        chamadas = []
    def fake(versao):
        def classificar(texto, indice, **kwargs):
            chamadas.append((versao, texto, kwargs))
            if erro and len(chamadas) == 9:
                raise RuntimeError("falha fictícia do baseline")
            if abster:
                return {"status": "SEM_COBERTURA", "pontuacao_exploratoria": None,
                        "classe_exploratoria": None}
            pont = -1 if "grosseria" in texto else 1
            return {"status": b.PONTUADO, "pontuacao_exploratoria": pont,
                    "classe_exploratoria": "negativa" if pont < 0 else "positiva"}
        return classificar
    return {name: fake(name) for name in b.METODOS}


def _reescrever(rows, cols):
    return b._escrever_csv(rows, cols)


def _alterar_origem(campo, valor, linha=0):
    origem, _ = b._fixture()
    dados = b._ler_csv(origem, b.COLUNAS_ORIGEM)
    dados[linha][campo] = valor
    return _reescrever(dados, b.COLUNAS_ORIGEM)


def _alterar_ficha(campo, valor, linha=0):
    _, ficha = b._fixture()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    rows[linha][campo] = valor
    return _reescrever(rows, b.COLUNAS_FICHA)


def test_contrato_explicitamente_nao_autorizado():
    c = b.verificar_contrato()
    assert c["estado"] == "NAO_CONGELADO_NAO_AUTORIZADO"
    assert c["executor_real_habilitado"] is False
    assert c["politica_aprovada"] is None
    assert c["autorizacao_execucao_final"] is False
    assert c["dados_reservados_lidos"] is False


def test_27_pares_9_familias_14_colunas_sem_uniformidade_obrigatoria():
    orig, ficha, pares, anot, _ = _preparar()
    assert len(pares) == len(anot) == 27
    assert len({p["familia"] for p in pares}) == 9
    assert tuple(b._ler_csv(orig, b.COLUNAS_ORIGEM)[0]) == b.COLUNAS_ORIGEM
    assert len(b._ler_csv(ficha, b.COLUNAS_FICHA)) == 27
    assert all(p["particao"] == "sintetica" for p in pares)


def test_nao_requer_tres_pares_por_familia():
    origem, _, _, _, _ = _preparar()
    rows = b._ler_csv(origem, b.COLUNAS_ORIGEM)
    rows[0]["familia"] = rows[3]["familia"]
    assert len(b.validar_origem_em_memoria(_reescrever(rows, b.COLUNAS_ORIGEM))) == 27


def test_ficha_cega_so_seis_colunas_e_sem_metadados():
    _, _, pares, _, _ = _preparar()
    saida = b.gerar_ficha_cega_em_memoria(pares)
    assert tuple(b._ler_csv(saida, b.COLUNAS_FICHA)[0]) == b.COLUNAS_FICHA
    for segredo in ("DADO_ANTIGO", "R_FICTICIO_ANTIGO", "N1", "METADADO_FICTICIO", "familia", "particao"):
        assert segredo not in saida
    assert all(not x["equivalencia"] and not x["rotulo"] for x in b._ler_csv(saida, b.COLUNAS_FICHA))


@pytest.mark.parametrize("campo,valor", [
    ("id_par", "SIM37_002"), ("id_par", "sem espaço"),
    ("familia", ""), ("familia", "FAMILIA_NOVA"),
    ("particao", "desenvolvimento"),
    ("frase_feminina", ""), ("frase_feminina", "a" * 5001),
    ("frase_masculina", ""),
])
def test_origem_recusa_erros(campo, valor):
    with pytest.raises(ValueError):
        b.validar_origem_em_memoria(_alterar_origem(campo, valor))


def test_origem_recusa_par_identico():
    origem, _, _, _, _ = _preparar()
    rows = b._ler_csv(origem, b.COLUNAS_ORIGEM)
    rows[0]["frase_masculina"] = rows[0]["frase_feminina"]
    with pytest.raises(ValueError, match="idênticos"):
        b.validar_origem_em_memoria(_reescrever(rows, b.COLUNAS_ORIGEM))


def test_origem_recusa_par_textualmente_duplicado():
    origem, _, _, _, _ = _preparar()
    rows = b._ler_csv(origem, b.COLUNAS_ORIGEM)
    rows[1]["frase_feminina"] = rows[0]["frase_feminina"]
    rows[1]["frase_masculina"] = rows[0]["frase_masculina"]
    with pytest.raises(ValueError, match="duplicado"):
        b.validar_origem_em_memoria(_reescrever(rows, b.COLUNAS_ORIGEM))


def test_origem_recusa_mistura_particoes():
    origem, _, _, _, _ = _preparar()
    rows = b._ler_csv(origem, b.COLUNAS_ORIGEM)
    rows[0]["particao"] = "avaliacao"
    with pytest.raises(ValueError, match="misturar"):
        b.validar_origem_em_memoria(_reescrever(rows, b.COLUNAS_ORIGEM))


@pytest.mark.parametrize("entrada", ["", "faltando", "a"*1_000_001, "\x00", None])
def test_csv_recusa_string_invalida(entrada):
    with pytest.raises(ValueError):
        b._ler_csv(entrada, b.COLUNAS_ORIGEM)


def test_csv_14_colunas_estritas():
    orig, _, _, _, _ = _preparar()
    with pytest.raises(ValueError, match="Cabeçalho"):
        b.validar_origem_em_memoria(orig.replace("id_par;familia", "codigo;familia", 1))
    with pytest.raises(ValueError, match="Cabeçalho"):
        b.validar_origem_em_memoria(orig.replace(";", ","))


def test_csv_extras_e_faltas():
    orig, _, _, _, _ = _preparar()
    with pytest.raises(ValueError, match="coluna"):
        b.validar_origem_em_memoria(orig.replace("\n", ";extra\n", 2))
    rows = b._ler_csv(orig, b.COLUNAS_ORIGEM)
    with pytest.raises(ValueError, match="27"):
        b.validar_origem_em_memoria(_reescrever(rows[:-1], b.COLUNAS_ORIGEM))
    with pytest.raises(ValueError, match="27"):
        b.validar_origem_em_memoria(_reescrever(rows+[rows[-1]], b.COLUNAS_ORIGEM))


def test_bom_utf8_pode_ser_lido_em_memoria():
    orig, _, _, _, _ = _preparar()
    assert len(b.validar_origem_em_memoria("\ufeff" + orig)) == 27


@pytest.mark.parametrize("campo,valor", [
    ("id_par", "ID_FORA"),
    ("frase_feminina", "Frase substituída"),
    ("frase_masculina", "Frase substituída"),
    ("equivalencia", "talvez"),
    ("rotulo", "indefinida"),
])
def test_ficha_bloqueia_modificacao(campo, valor):
    _, _, pares, _, _ = _preparar()
    with pytest.raises(ValueError):
        b.validar_ficha_em_memoria(_alterar_ficha(campo, valor), pares, politica=b.POLITICA_CONTABILIZAR)


def test_ficha_bloqueia_sim_sem_rotulo():
    _, _, pares, _, _ = _preparar()
    with pytest.raises(ValueError, match="sem rótulo"):
        b.validar_ficha_em_memoria(_alterar_ficha("rotulo", ""), pares, politica=b.POLITICA_CONTABILIZAR)


def test_ficha_bloqueia_nao_sem_justificativa():
    _, _, pares, _, _ = _preparar()
    with pytest.raises(ValueError, match="justificativa"):
        b.validar_ficha_em_memoria(_alterar_ficha("observacoes", "", 3), pares, politica=b.POLITICA_CONTABILIZAR)


def test_ficha_bloqueia_nao_com_rotulo():
    _, _, pares, _, _ = _preparar()
    with pytest.raises(ValueError, match="rótulo"):
        b.validar_ficha_em_memoria(_alterar_ficha("rotulo", "positiva", 3), pares, politica=b.POLITICA_CONTABILIZAR)


def test_ficha_preserva_observacao_sem_inferir_rotulo():
    _, _, pares, _, _ = _preparar()
    origem, ficha = b._fixture()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    rows[0]["equivalencia"] = rows[0]["rotulo"] = ""
    rows[0]["observacoes"] = "Em dúvida"
    a, faltantes = b.validar_ficha_em_memoria(_reescrever(rows, b.COLUNAS_FICHA), pares,
                                                politica=b.POLITICA_CONTABILIZAR)
    assert faltantes == 1 and a[0]["observacoes"] == "Em dúvida" and a[0]["rotulo"] == ""


def test_ficha_bloqueia_id_duplicado():
    _, ficha, pares, _, _ = _preparar()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    rows[-1]["id_par"] = rows[0]["id_par"]
    with pytest.raises(ValueError, match="repetido"):
        b.validar_ficha_em_memoria(_reescrever(rows, b.COLUNAS_FICHA), pares, politica=b.POLITICA_CONTABILIZAR)


def test_ficha_política_estrita_vs_permissiva():
    _, ficha, pares, _, _ = _preparar()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    rows[0]["equivalencia"] = rows[0]["rotulo"] = ""
    alterada = _reescrever(rows, b.COLUNAS_FICHA)
    with pytest.raises(ValueError, match="incompleta"):
        b.validar_ficha_em_memoria(alterada, pares, politica=b.POLITICA_ESTRITA)
    _, faltas = b.validar_ficha_em_memoria(alterada, pares, politica=b.POLITICA_CONTABILIZAR)
    assert faltas == 1


def test_politica_invalida_impede_anotacao():
    _, ficha, pares, _, _ = _preparar()
    for opcao in ("", "escolhida", "outra", None):
        with pytest.raises(ValueError, match="Política"):
            b.validar_ficha_em_memoria(ficha, pares, politica=opcao)


def test_ficha_cega_recusa_formula_sem_alterar_frase():
    _, _, pares, _, _ = _preparar()
    p = deepcopy(pares)
    p[0]["frase_feminina"] = "  =HYPERLINK(\"http://teste\")"
    with pytest.raises(ValueError, match="fórmula"):
        b.gerar_ficha_cega_em_memoria(p)


def test_ficha_cega_recusa_colunas_adicionais():
    _, _, pares, _, _ = _preparar()
    p = deepcopy(pares)
    p[0]["rotulo_revisor1"] = "falso"
    with pytest.raises(ValueError):
        b.gerar_ficha_cega_em_memoria(p)


def test_ensaiar_somente_fixture_literal():
    indice, nlp = IndiceFicticio(), EtiquetadorFicticio()
    with pytest.raises(PermissionError):
        b.ensaiar_sintetico(conteudo_fonte="qualquer dado", indice=indice, nlp=nlp,
                           classificadores=_fake())
    with pytest.raises(PermissionError):
        b.ensaiar_sintetico(conteudo_ficha="id_par;dados externos", indice=indice, nlp=nlp,
                           classificadores=_fake())


def test_162_chamadas_tres_baselines_parametros_fixos():
    chamadas = []
    result = b.ensaiar_sintetico(indice=IndiceFicticio(), nlp=EtiquetadorFicticio(),
                                 classificadores=_fake(chamadas))
    assert len(chamadas) == 162
    assert {c[0] for c in chamadas} == set(b.METODOS)
    for versao, texto, kw in chamadas:
        assert kw["alvo"] == "N0" and kw["incluir_diagnostico"] is False
        if versao == "v01":
            assert "nlp" not in kw and "hipotese_modo" not in kw
        else:
            assert kw["hipotese_modo"] is True and isinstance(kw["nlp"], EtiquetadorFicticio)
    assert result["resumo_sintetico"]["P_total"] == 27
    assert result["resumo_sintetico"]["F_total"] == 54
    assert result["resumo_sintetico"]["P_equivalentes_R01"] == 21
    assert result["dados_reservados_lidos"] is False
    assert result["protocolo_congelado"] is False


def test_delta_em_par_e_nao_duas_amostras_independentes():
    def fake_v01(t, i, **kw):
        return {"status": b.PONTUADO,
                "pontuacao_exploratoria": 2 if t.startswith("A atendente") else 1,
                "classe_exploratoria": "positiva"}
    _, _, pares, ficha, _ = _preparar()
    classif = {metodo: fake_v01 for metodo in b.METODOS}
    r = b.executar_nucleo_em_memoria(pares, ficha, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=classif)
    for dados in r["resumo"]["metodos"].values():
        assert dados["P_delta_calculavel"] == 21
        assert dados["P_delta_nao_nulo"] == 21
        assert all(p["delta"] == 1 for p in dados["deltas_por_par_para_analise_privada"])
        assert len(dados["deltas_por_par_para_analise_privada"]) == 21


def test_abstencoes_nao_viram_delta_zero():
    _, _, pares, ficha, _ = _preparar()
    r = b.executar_nucleo_em_memoria(pares, ficha, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(abster=True))
    for dados in r["resumo"]["metodos"].values():
        assert dados["F_abstidas_global"] == 54
        assert dados["F_pontuadas_global"] == 0
        assert dados["P_delta_calculavel"] == 0
        assert dados["P_delta_nao_calculavel"] == 21
        assert dados["fracao_delta_nao_nulo"] is None
        assert dados["coincidencia_nominal_seletiva_anotacao_unica"] is None
        assert dados["deltas_por_par_para_analise_privada"] == []


def test_baseline_falha_interrompe_sem_resumo_parcial():
    _, _, pares, ficha, _ = _preparar()
    with pytest.raises(RuntimeError, match="falha fictícia"):
        b.executar_nucleo_em_memoria(pares, ficha, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(erro=True))


@pytest.mark.parametrize("saida", [
    {},
    {"status": b.PONTUADO, "pontuacao_exploratoria": 1.0, "classe_exploratoria": "positiva"},
    {"status": b.PONTUADO, "pontuacao_exploratoria": 1, "classe_exploratoria": "negativa"},
    {"status": b.PONTUADO, "pontuacao_exploratoria": True, "classe_exploratoria": "positiva"},
    {"status": "SEM_COBERTURA", "pontuacao_exploratoria": 0, "classe_exploratoria": "neutra"},
    {"status": "SEM_COBERTURA", "pontuacao_exploratoria": None, "classe_exploratoria": "neutra"},
])
def test_saida_baseline_malformada_bloqueada(saida):
    with pytest.raises(ValueError):
        b._saida_reduzida(saida)


def test_neutro_lexical_zero_distinto_do_rótulo_humano():
    assert b._saida_reduzida({"status": b.PONTUADO, "pontuacao_exploratoria": 0,
                              "classe_exploratoria": "neutra"})["pontuacao_exploratoria"] == 0


def test_sanitizacao_da_saida_nao_repassa_diagnostico_textual():
    completo = {"status": b.PONTUADO, "pontuacao_exploratoria": 1,
                "classe_exploratoria": "positiva", "diagnostico": "texto secreto"}
    reduzido = b._saida_reduzida(completo)
    assert set(reduzido) == {"status", "pontuacao_exploratoria", "classe_exploratoria"}
    assert "texto secreto" not in json.dumps(reduzido)


def test_politica_contabilizar_mantem_27_54_e_pendencia_separada():
    _, ficha, pares, _, _ = _preparar()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    rows[0]["equivalencia"] = rows[0]["rotulo"] = ""
    anot, faltas = b.validar_ficha_em_memoria(_reescrever(rows, b.COLUNAS_FICHA), pares,
                                                politica=b.POLITICA_CONTABILIZAR)
    r = b.executar_nucleo_em_memoria(pares, anot, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(),
                                     politica=b.POLITICA_CONTABILIZAR)
    res = r["resumo"]
    assert faltas == 1 and res["P_total"] == 27 and res["F_total"] == 54
    assert res["P_equivalentes_R01"] == 20 and res["P_nao_elegiveis"] == 7
    assert res["P_nao_elegiveis_por_motivo"] == {"equivalencia_nao": 6, "sem_resposta": 1}
    assert res["F_elegiveis"] == 40


def test_ausencia_total_de_elegiveis_produz_taxas_nulas():
    _, ficha, pares, _, _ = _preparar()
    rows = b._ler_csv(ficha, b.COLUNAS_FICHA)
    for row in rows:
        row["equivalencia"] = row["rotulo"] = row["observacoes"] = ""
    anot, falta = b.validar_ficha_em_memoria(_reescrever(rows, b.COLUNAS_FICHA), pares,
                                              politica=b.POLITICA_CONTABILIZAR)
    r = b.executar_nucleo_em_memoria(pares, anot, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(),
                                     politica=b.POLITICA_CONTABILIZAR)
    assert falta == 27
    for m in r["resumo"]["metodos"].values():
        assert m["taxa_pontuacao_elegivel"] is None
        assert m["taxa_pares_delta_calculavel"] is None
        assert m["F_pontuadas_global"] == 54


def test_metodos_errados_recusados():
    _, _, pares, ficha, _ = _preparar()
    for cls in ({"v01": _fake()["v01"]}, {"v01": None, "v03": None, "v04": None}):
        with pytest.raises(ValueError, match="baseline"):
            b.executar_nucleo_em_memoria(pares, ficha, indice=IndiceFicticio(),
                                         nlp=EtiquetadorFicticio(), classificadores=cls)


def test_indice_errado_recusado():
    _, _, pares, ficha, _ = _preparar()
    class LexErrado: lexico="oplexicon"
    with pytest.raises(ValueError, match="SentiLex"):
        b.executar_nucleo_em_memoria(pares, ficha, indice=LexErrado(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake())


def test_cli_real_sempre_bloqueado_e_ignora_flags(monkeypatch, capsys):
    with pytest.raises(PermissionError, match="BLOQUEADO"):
        b.executar_final(autorizado=True, caminho="arquivo.csv")
    monkeypatch.setattr(sys, "argv", ["bloco37", "executar-final"])
    with pytest.raises(SystemExit) as exc:
        b.main()
    assert exc.value.code == 1
    assert "BLOQUEADO" in capsys.readouterr().err
    monkeypatch.setattr(sys, "argv", ["bloco37", "simular", "--entrada", "privado.csv"])
    with pytest.raises(SystemExit) as exc:
        b.main()
    assert exc.value.code == 2


def test_sha256_fixture_deterministico():
    a, z = b._fixture()
    assert b._sha(a) == b._sha(b._fixture()[0])
    assert b._sha(z) == b._sha(b._fixture()[1])
    assert b._sha(a) != b._sha(z)


def test_ensaio_nao_gera_arquivo(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    resultado = b.ensaiar_sintetico(indice=IndiceFicticio(), nlp=EtiquetadorFicticio(),
                                    classificadores=_fake())
    assert resultado["fase"] == "ENSAIO_SOMENTE_FICTICIO_NAO_AVALIACAO_FINAL"
    assert resultado["acuracia_validada"] is None
    assert list(tmp_path.iterdir()) == []


def test_nucleo_defesa_em_profundidade_rejeita_ficha_invalida_antes_de_pontuar():
    _, _, pares, ficha, _ = _preparar()
    alterada = deepcopy(ficha)
    alterada[0]["frase_feminina"] += " adulterada"
    chamadas = []
    with pytest.raises(ValueError, match="diverge"):
        b.executar_nucleo_em_memoria(pares, alterada, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(chamadas))
    assert chamadas == []


def test_nucleo_recusa_falta_estrita_mesmo_sem_validador_externo():
    _, _, pares, ficha, _ = _preparar()
    alterada = deepcopy(ficha)
    alterada[0]["equivalencia"] = alterada[0]["rotulo"] = ""
    chamadas = []
    with pytest.raises(ValueError, match="incompleta"):
        b.executar_nucleo_em_memoria(pares, alterada, indice=IndiceFicticio(),
                                     nlp=EtiquetadorFicticio(), classificadores=_fake(chamadas))
    assert chamadas == []


def test_metricas_coincidem_com_agregador_existente_bloco29():
    """Verificação cruzada; no repositório completo o B29 está disponível."""
    from backend.avaliacao_final_preparacao_bloco29 import resumir
    _, _, pares, ficha, _ = _preparar()
    saida = b.executar_nucleo_em_memoria(pares, ficha, indice=IndiceFicticio(),
                                         nlp=EtiquetadorFicticio(), classificadores=_fake())
    antigo = resumir(pares, ficha, saida["predicoes"])
    novo = saida["resumo"]
    for chave in ("P_total", "F_total", "P_equivalentes_R01", "P_nao_elegiveis",
                  "P_nao_elegiveis_por_motivo", "F_elegiveis"):
        assert novo[chave] == antigo[chave]
    for metodo in b.METODOS:
        for chave, valor in antigo["metodos"][metodo].items():
            assert novo["metodos"][metodo][chave] == valor, (metodo, chave)


def test_integracao_baselines_existentes_com_indice_e_etiquetador_ficticios():
    """Usa módulos reais V01/V03/V04; SOMENTE frases/léxico/etiquetador artificiais."""
    from backend.executor_sintetico_bloco33 import _modelo_ficticio
    indice, nlp = _modelo_ficticio()
    resultado = b.ensaiar_sintetico(indice=indice, nlp=nlp)
    assert resultado["resumo_sintetico"]["P_total"] == 27
    assert resultado["resumo_sintetico"]["F_total"] == 54
    assert set(resultado["resumo_sintetico"]["metodos"]) == {"v01", "v03", "v04"}
    assert resultado["avaliacao_final_executada"] is False
    assert resultado["dados_reservados_lidos"] is False
