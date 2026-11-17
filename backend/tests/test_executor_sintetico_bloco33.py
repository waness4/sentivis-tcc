"""Bloco 33: TODAS as entradas são artificiais; nunca ler partição reservada."""
from __future__ import annotations

from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import sys

import pytest

from backend.executor_sintetico_bloco33 import (
    DESTINO, ESTADO, N_FAMILIAS, N_PARES, _pasta_segura,
    ensaiar_unica_vez, executar_em_memoria, ficha_cega_csv, fixture_27,
    main, validar_ficha_ficticia, validar_lote_ficticio, verificar_contrato,
)


def _modelo():
    from backend.executor_sintetico_bloco33 import _modelo_ficticio
    return _modelo_ficticio()


def _resposta(nota=1):
    if nota is None:
        return {"status": "SEM_COBERTURA", "pontuacao_exploratoria": None,
                "classe_exploratoria": None}
    return {"status": "PONTUACAO_EXPLORATORIA_NAO_VALIDADA",
            "pontuacao_exploratoria": nota,
            "classe_exploratoria": "positiva" if nota > 0 else "negativa" if nota < 0 else "neutra"}


def _falsos(chamadas):
    def f(metodo):
        def executar(texto, indice, **kwargs):
            chamadas.append((metodo, texto, dict(kwargs)))
            return _resposta(None if "ficha" in texto else 1)
        return executar
    return {"v01": f("v01"), "v03": f("v03"), "v04": f("v04")}


def test_corpus_e_familias_somente_sinteticos():
    pares, ficha = fixture_27()
    validar_lote_ficticio(pares)
    assert len(pares) == len(ficha) == N_PARES == 27
    assert len({p["familia"] for p in pares}) == N_FAMILIAS == 9
    assert all(sum(x["familia"] == p["familia"] for x in pares) == 3 for p in pares)
    assert all(p["id_par"].startswith("SINT") and p["particao"] == "sintetica" for p in pares)


def test_ficha_cega_nao_expoe_referencias_e_nem_previsoes():
    pares, ficha = fixture_27()
    buf = ficha_cega_csv(pares)
    csvrows = list(csv.DictReader(io.StringIO(buf), delimiter=";"))
    assert len(csvrows) == 27
    assert list(csvrows[0]) == ["id_par", "frase_feminina", "frase_masculina", "equivalencia", "rotulo", "observacoes"]
    assert all(r["rotulo"] == r["equivalencia"] == r["observacoes"] == "" for r in csvrows)
    assert all("familia" not in r and "previsao" not in r for r in csvrows)
    assert len(validar_ficha_ficticia(pares, ficha)) == 27


@pytest.mark.parametrize("modificacao", [
    lambda p: p.__setitem__(0, {**p[0], "frase_feminina": "Frase não autorizada"}),
    lambda p: p.__setitem__(0, {**p[0], "id_par": "AV001"}),
    lambda p: p.__setitem__(0, {**p[0], "familia": "FAMILIA_REAL"}),
    lambda p: p.__setitem__(0, {**p[0], "particao": "avaliacao"}),
    lambda p: p.append(deepcopy(p[-1])),
    lambda p: p[0].update({"coluna_extra": "vazar"}),
])
def test_lote_externo_ou_modificado_bloqueado(modificacao):
    p, _ = fixture_27()
    modificacao(p)
    with pytest.raises(ValueError):
        validar_lote_ficticio(p)


def test_anotacao_invalida_impede_qualquer_classificacao():
    p, ficha = fixture_27()
    ficha[0]["frase_masculina"] += " alterada"
    chamadas = []
    idx, nlp = _modelo()
    with pytest.raises(ValueError, match="Frase"):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp, classificadores=_falsos(chamadas))
    assert not chamadas


def test_ficha_duplicada_impede_pontuar():
    p, ficha = fixture_27()
    ficha[-1]["id_par"] = ficha[0]["id_par"]
    chamadas = []
    idx, nlp = _modelo()
    with pytest.raises(ValueError):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp, classificadores=_falsos(chamadas))
    assert not chamadas


def test_tres_metodos_54_frases_parametros_fixos():
    p, ficha = fixture_27()
    idx, nlp = _modelo()
    chamadas = []
    r = executar_em_memoria(p, ficha, indice=idx, nlp=nlp, classificadores=_falsos(chamadas))
    assert len(chamadas) == 3 * 54
    assert {c[0] for c in chamadas} == {"v01", "v03", "v04"}
    assert all(c[2]["alvo"] == "N0" and c[2]["incluir_diagnostico"] is False for c in chamadas)
    assert all(c[2]["hipotese_modo"] is True and c[2]["nlp"] is nlp for c in chamadas if c[0] != "v01")
    assert all("hipotese_modo" not in c[2] for c in chamadas if c[0] == "v01")
    assert r["resumo"]["F_total"] == 54
    assert r["avaliacao_final_executada"] is False


def test_integracao_real_dos_baselines_com_lexico_artificial():
    p, ficha = fixture_27()
    r = executar_em_memoria(p, ficha)
    agg = r["resumo"]
    assert agg["P_total"] == 27
    assert agg["P_equivalentes_R01"] == 21
    assert agg["P_nao_elegiveis"] == 6
    assert agg["P_elegiveis_com_rotulo_neutro_separado"] == 7
    assert agg["F_elegiveis"] == 42
    for metodo in ("v01", "v03", "v04"):
        m = agg["metodos"][metodo]
        assert m["F_pontuadas_global"] + m["F_abstidas_global"] == 54
        assert m["P_delta_calculavel"] + m["P_delta_nao_calculavel"] == 21
    assert agg["acuracia_validada"] is None
    assert agg["evidencia_de_vies"] is None
    assert r["protocolo_congelado"] is False
    assert r["fase"] == "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL"


def test_predicoes_privadas_sanitizadas_sem_frases():
    p, ficha = fixture_27()
    saida = executar_em_memoria(p, ficha)
    pr = saida["resultados_por_par_somente_sinteticos"]
    assert len(pr) == 27
    assert all(set(pr[i]) == {"v01", "v03", "v04"} for i in pr)
    assert all(set(v) == {"status", "pontuacao_exploratoria", "classe_exploratoria"}
               for par in pr.values() for metodo in par.values() for v in metodo.values())
    assert "atendente" not in json.dumps(saida, ensure_ascii=False).lower()
    assert "observacoes" not in json.dumps(saida, ensure_ascii=False)


def test_saida_malformada_falha_fechada():
    p, ficha = fixture_27()
    idx, nlp = _modelo()
    funcoes = _falsos([])
    funcoes["v04"] = lambda *a, **k: {"status": "SEM_COBERTURA", "pontuacao_exploratoria": 0,
                                         "classe_exploratoria": "neutra"}
    with pytest.raises(ValueError, match="Abstenção"):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp, classificadores=funcoes)


def test_excecao_de_baseline_nao_converte_em_abstencao():
    p, ficha = fixture_27()
    idx, nlp = _modelo()
    funcoes = _falsos([])
    def erro(*args, **kwargs):
        raise RuntimeError("falha sintética de modelo")
    funcoes["v03"] = erro
    with pytest.raises(RuntimeError, match="falha sintética"):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp, classificadores=funcoes)


def test_baselines_incompletos_bloqueados():
    p, ficha = fixture_27()
    idx, nlp = _modelo()
    with pytest.raises(ValueError, match="baselines"):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp,
                           classificadores={"v01": lambda *a, **k: _resposta(1)})


def test_indice_nao_sentilex_bloqueado():
    p, ficha = fixture_27()
    idx, nlp = _modelo()
    idx.lexico = "oplexicon"
    with pytest.raises(ValueError, match="SentiLex"):
        executar_em_memoria(p, ficha, indice=idx, nlp=nlp)


def test_ensaio_escreve_uma_vez_e_privado(tmp_path):
    saida = ensaiar_unica_vez(tmp_path)
    assert saida["estado"] == "ENSAIO_SINTETICO_CONCLUIDO"
    raiz = tmp_path / DESTINO
    marcador = raiz / "marcador_tentativa_bloco33.json"
    rel = raiz / "relatorio_sintetico_bloco33.json"
    assert marcador.is_file() and rel.is_file()
    anterior = rel.read_bytes()
    with pytest.raises(FileExistsError):
        ensaiar_unica_vez(tmp_path)
    assert rel.read_bytes() == anterior
    dados = json.loads(rel.read_text(encoding="utf-8"))
    assert dados["ensaio"]["resumo"]["F_total"] == 54
    assert dados["reserva"]["avaliacao_final_executada"] is False


def test_falha_parcial_preserva_marcador_sem_relatorio(tmp_path):
    def falha(p, f):
        raise RuntimeError("falha de experimento")
    with pytest.raises(RuntimeError):
        ensaiar_unica_vez(tmp_path, executor=falha)
    raiz = tmp_path / DESTINO
    assert (raiz / "marcador_tentativa_bloco33.json").is_file()
    assert not (raiz / "relatorio_sintetico_bloco33.json").exists()
    with pytest.raises(FileExistsError):
        ensaiar_unica_vez(tmp_path)


def test_marcador_preexistente_bloqueia_nova_pontuacao(tmp_path):
    p = tmp_path / DESTINO
    p.mkdir(parents=True)
    (p / "marcador_tentativa_bloco33.json").write_text("ensaio anterior", encoding="utf-8")
    acionado = []
    with pytest.raises(FileExistsError):
        ensaiar_unica_vez(tmp_path, executor=lambda *args: acionado.append(True))
    assert not acionado


def test_marcador_sem_rela_avalia_final_sempre_bloqueada():
    m = verificar_contrato()
    assert m["estado"] == ESTADO
    assert m["dados_reservados_lidos"] is False
    assert m["programa_real_implementado"] is False
    assert m["autorizacao_execucao_final"] is False


def test_cli_rejeita_entrada_real_e_modo_final(monkeypatch):
    for args in (["avaliar-final"], ["verificar-contrato", "--entrada", "reservado.csv"],
                 ["ensaiar", "--entrada", "reservado.csv"]):
        monkeypatch.setattr(sys, "argv", ["executor_sintetico_bloco33", *args])
        with pytest.raises(SystemExit) as erro:
            main()
        assert erro.value.code == 2


def test_contrato_nao_grava_arquivos_em_tmp_path(tmp_path, monkeypatch):
    import backend.executor_sintetico_bloco33 as exe
    monkeypatch.setattr(exe, "RAIZ", tmp_path)
    result = exe.verificar_contrato()
    assert result["autorizacao_execucao_final"] is False
    assert list(tmp_path.iterdir()) == []
