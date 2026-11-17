"""G03: somente fixture literal; não ler nenhum dado externo ou reservado."""
from __future__ import annotations

import csv
import io
import json
import sys
from copy import deepcopy

import pytest

from backend.politica_ausencias_bloco36 import (
    ESTADO, POLITICA_ESTRITA, POLITICA_CONTABILIZAR, POLITICA_APROVADA,
    _csv, _sha, cenario_ficticio, preparar_anotacoes_sinteticas,
    executar_ensaio_sintetico, comparar_opcoes, verificar_contrato, executar_final, main,
)


def _ficha_alterada(ficha, campo, valor, linha=0):
    registros = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    registros[linha][campo] = valor
    return _csv(registros)


def test_sem_aprovacao_e_com_real_bloqueado():
    v = verificar_contrato()
    assert POLITICA_APROVADA is None
    assert v["estado"] == ESTADO
    assert v["dados_reservados_lidos"] is False
    assert v["autorizacao_execucao_final"] is False
    assert v["programa_real_autorizado"] is False


def test_fixture_completa_possui_27_respostas():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    p, a, faltas = preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_ESTRITA)
    assert len(p) == len(a) == 27
    assert faltas == 0
    assert sum(x["equivalencia"] == "sim" for x in a) == 21


def test_uma_falta_artificial_preservada_e_nao_imputada():
    fonte, ficha = cenario_ficticio(inserir_pendencia=True)
    p, a, faltas = preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_CONTABILIZAR)
    assert len(p) == len(a) == 27
    assert faltas == 1
    assert a[0]["equivalencia"] == a[0]["rotulo"] == ""
    assert a[0]["observacoes"] == ""


def test_politica_estrita_bloqueia_anotacao_pendente():
    fonte, ficha = cenario_ficticio(inserir_pendencia=True)
    with pytest.raises(ValueError, match="Ficha incompleta"):
        preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_ESTRITA)


def test_falha_antes_de_classificar_com_resposta_ausente():
    fonte, ficha = cenario_ficticio(inserir_pendencia=True)
    chamados = []
    def executor(*args):
        chamados.append(True)
    with pytest.raises(ValueError, match="Ficha incompleta"):
        executar_ensaio_sintetico(fonte, ficha, politica=POLITICA_ESTRITA, executor=executor)
    assert chamados == []


def test_politica_nao_aprovada_ou_desconhecida_rejeitada():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    for politica in ("", "aprovado", None, "executar_final", "aceitar_tudo"):
        with pytest.raises(ValueError, match="Política"):
            preparar_anotacoes_sinteticas(fonte, ficha, politica=politica)


@pytest.mark.parametrize("campo,valor", [
    ("id_par", "AV001"), ("frase_feminina", "Conteudo alterado"),
    ("frase_masculina", "Conteudo alterado"), ("rotulo", "mista"),
    ("equivalencia", "talvez"),
])
def test_entrada_invalida_bloqueada_independente_da_politica(campo, valor):
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    invalida = _ficha_alterada(ficha, campo, valor)
    for pol in (POLITICA_ESTRITA, POLITICA_CONTABILIZAR):
        with pytest.raises(ValueError):
            preparar_anotacoes_sinteticas(fonte, invalida, politica=pol)


def test_sim_sem_rotulo_invalido_em_ambas_politicas():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    ficha = _ficha_alterada(ficha, "rotulo", "")
    with pytest.raises(ValueError, match="rótulo"):
        preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_CONTABILIZAR)


def test_nao_sem_justificativa_invalido_em_ambas_politicas():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    ficha = _ficha_alterada(ficha, "observacoes", "", 3)
    with pytest.raises(ValueError, match="justificativa"):
        preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_CONTABILIZAR)


def test_nao_equivalente_nao_pode_ter_rotulo():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    ficha = _ficha_alterada(ficha, "rotulo", "positiva", 3)
    with pytest.raises(ValueError, match="não pode"):
        preparar_anotacoes_sinteticas(fonte, ficha, politica=POLITICA_CONTABILIZAR)


def test_duplicacao_de_id_bloqueada():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    registros = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    registros[-1]["id_par"] = registros[0]["id_par"]
    with pytest.raises(ValueError, match="duplicado"):
        preparar_anotacoes_sinteticas(fonte, _csv(registros), politica=POLITICA_CONTABILIZAR)


def test_origem_modificada_bloqueia_sem_computar():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    with pytest.raises(ValueError):
        preparar_anotacoes_sinteticas(fonte.replace("REV_FICTICIO_SEM_VALOR", "PESSOA_REAL"),
                                     ficha, politica=POLITICA_CONTABILIZAR)


def test_fonte_real_ou_path_rejeitada():
    _, ficha = cenario_ficticio(inserir_pendencia=False)
    with pytest.raises((ValueError, TypeError)):
        preparar_anotacoes_sinteticas("data/piloto/restrito/final.csv", ficha,
                                     politica=POLITICA_CONTABILIZAR)


def test_resumo_permissivo_conta_ausencia_no_global():
    fonte, ficha = cenario_ficticio(inserir_pendencia=True)
    d = executar_ensaio_sintetico(fonte, ficha, politica=POLITICA_CONTABILIZAR)
    x = d["resumo_sintetico"]
    assert x["P_total"] == 27 and x["F_total"] == 54
    assert x["P_equivalentes_R01"] == 20
    assert x["P_nao_elegiveis"] == 7
    assert x["P_nao_elegiveis_por_motivo"] == {"equivalencia_nao": 6, "sem_resposta": 1}
    assert x["F_elegiveis"] == 40
    assert d["acuracia_validada"] is None and d["evidencia_de_vies"] is None
    for m in x["metodos"].values():
        assert m["F_pontuadas_global"] + m["F_abstidas_global"] == 54
        assert m["P_delta_calculavel"] + m["P_delta_nao_calculavel"] == 20


def test_completo_mesmas_metricas_de_desenvolvimento():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    d = executar_ensaio_sintetico(fonte, ficha, politica=POLITICA_ESTRITA)
    assert d["resumo_sintetico"]["P_equivalentes_R01"] == 21
    assert d["resumo_sintetico"]["F_elegiveis"] == 42
    assert d["P_sem_resposta"] == 0


def test_simulacao_de_duas_politicas_somente_uma_roda_com_pendencia():
    resultado = comparar_opcoes()
    assert resultado["politica_aprovada"] is None
    assert resultado["cenario_ficha_completa"]["P_equivalentes"] == 21
    assert resultado["cenario_uma_resposta_ausente"]["opcao_bloquear"]["pontuacao_iniciada"] is False
    c = resultado["cenario_uma_resposta_ausente"]["opcao_contabilizar"]
    assert c["P_sem_resposta"] == 1 and c["F_total"] == 54
    assert resultado["autorizacao_execucao_final"] is False


def test_qualquer_execucao_final_sempre_bloqueada():
    with pytest.raises(PermissionError, match="BLOQUEADO"):
        executar_final()
    with pytest.raises(PermissionError):
        executar_final("data/piloto/restrito/avaliacao_final.csv", autorizado=True)


def test_cli_rejeita_arquivos_externos_antes_de_abrir(monkeypatch):
    for args in (["comparar-opcoes", "--entrada", "data/piloto/restrito/final.csv"],
                 ["--entrada", "data/piloto/restrito/final.csv"],
                 ["executar-final", "--autorizado"]):
        monkeypatch.setattr(sys, "argv", ["politica_ausencias_bloco36", *args])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2


def test_cli_bloqueia_executar_final_sem_flags(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["politica_ausencias_bloco36", "executar-final"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "BLOQUEADO" in capsys.readouterr().err


def test_sha256_deterministico():
    assert _sha("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_ficha_vazia_pode_ser_contada_mas_nao_imputada():
    fonte, ficha = cenario_ficticio(inserir_pendencia=False)
    linhas = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    for linha in linhas:
        linha["equivalencia"] = linha["rotulo"] = linha["observacoes"] = ""
    p, a, n = preparar_anotacoes_sinteticas(fonte, _csv(linhas), politica=POLITICA_CONTABILIZAR)
    assert len(p) == len(a) == n == 27
    assert all(x["rotulo"] == "" for x in a)
