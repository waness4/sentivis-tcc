"""Bloco 34. Todos os textos e anotacões vêm da fixture INVENTADA do Bloco 33.

Nenhum teste lê arquivos de avaliação, relatórios privados ou léxicos reais.
"""
from __future__ import annotations

from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import sys

import pytest

from backend.executor_final_bloqueado_bloco34 import (
    CAMPOS_FONTE_14, COLUNAS_FICHA, PASTA_RELATORIO, _fixture_14,
    _ficha_ficticia_preenchida, _ler_14_em_memoria, ensaio_em_memoria,
    ensaiar_uma_vez, executar_final, gerar_ficha_cega_ficticia,
    main, validar_ficha_finalizada_ficticia, validar_origem_ficticia,
    verificar_contrato,
)
from backend.executor_sintetico_bloco33 import fixture_27


def dados():
    origem = _fixture_14()
    pares = validar_origem_ficticia(origem)
    ficha = _ficha_ficticia_preenchida(pares)
    return origem, pares, ficha


def _reescrever_orig(linhas):
    buff = io.StringIO(newline="")
    w = csv.DictWriter(buff, fieldnames=CAMPOS_FONTE_14, delimiter=";", lineterminator="\n")
    w.writeheader()
    w.writerows(linhas)
    return buff.getvalue()


def _reescrever_ficha(linhas):
    buff = io.StringIO(newline="")
    w = csv.DictWriter(buff, fieldnames=COLUNAS_FICHA, delimiter=";", lineterminator="\n")
    w.writeheader()
    w.writerows(linhas)
    return buff.getvalue()


def test_fixture_fonte_14_colunas_e_27_pares():
    origem, pares, _ = dados()
    linhas = _ler_14_em_memoria(origem)
    assert len(linhas) == len(pares) == 27
    assert len({p["familia"] for p in pares}) == 9
    assert tuple(linhas[0]) == CAMPOS_FONTE_14
    assert all(p["particao"] == "sintetica" for p in pares)


def test_ficha_cega_tem_6_colunas_sem_metadados():
    origem, _, _ = dados()
    texto = gerar_ficha_cega_ficticia(origem)
    linhas = list(csv.DictReader(io.StringIO(texto), delimiter=";"))
    assert len(linhas) == 27
    assert tuple(linhas[0]) == COLUNAS_FICHA
    assert all(not l["equivalencia"] and not l["rotulo"] and not l["observacoes"] for l in linhas)
    for segredo in ("REV_FICTICIO", "OBSERVACAO_INTERNA", "N1", "familia", "rotulo_revisor1"):
        assert segredo not in texto


def test_ficha_ficticia_preenchida_aceita_tres_rotulos_e_rejeita_pendencias():
    origem, _, ficha = dados()
    anotacoes = validar_ficha_finalizada_ficticia(origem, ficha)
    assert len(anotacoes) == 27
    assert {x["rotulo"] for x in anotacoes} == {"positiva", "negativa", "neutra", ""}
    assert all(x["equivalencia"] in {"sim", "nao"} for x in anotacoes)


@pytest.mark.parametrize("campo,valor", [
    ("id_par", "AVALIACAO001"),
    ("frase_feminina", "Texto externo proibido"),
    ("frase_masculina", "Frase alterada"),
    ("familia", "FAMILIA_RESERVADA"),
    ("particao", "avaliacao"),
    ("rotulo_revisor1", "positiva"),
    ("id_revisor1", "ID_REVISOR_REAL"),
    ("alvo_sentilex_feminina", "N0"),
    ("observacoes", "Substituição"),
])
def test_modificacoes_na_origem_rejeitadas(campo, valor):
    origem, _, _ = dados()
    linhas = _ler_14_em_memoria(origem)
    linhas[0][campo] = valor
    with pytest.raises(ValueError):
        validar_origem_ficticia(_reescrever_orig(linhas))


def test_faltando_linha_fonte_bloqueia():
    linhas = _ler_14_em_memoria(_fixture_14())
    with pytest.raises(ValueError, match="27"):
        validar_origem_ficticia(_reescrever_orig(linhas[:-1]))


def test_linha_adicional_fonte_bloqueia():
    linhas = _ler_14_em_memoria(_fixture_14())
    with pytest.raises(ValueError, match="27"):
        validar_origem_ficticia(_reescrever_orig(linhas + [linhas[0]]))


def test_cabecalho_menor_ou_diferente_bloqueia():
    origem = _fixture_14()
    with pytest.raises(ValueError, match="14 colunas"):
        _ler_14_em_memoria(origem.replace("id_par;familia", "codigo;familia", 1))
    with pytest.raises(ValueError, match="14 colunas"):
        _ler_14_em_memoria(origem.replace(";", ","))
    with pytest.raises(ValueError, match="14 colunas"):
        _ler_14_em_memoria(origem.replace(";observacoes\n", "\n", 1))


def test_cabecalho_extra_rejeitado():
    origem = _fixture_14().replace(";observacoes\n", ";observacoes;previsao\n", 1)
    with pytest.raises(ValueError, match="14 colunas"):
        _ler_14_em_memoria(origem)


def test_linha_csv_com_campo_extra_rejeitada():
    origem = _fixture_14().replace("\n", ";extra\n", 2)
    with pytest.raises((ValueError, csv.Error)):
        _ler_14_em_memoria(origem)


def test_cabecalho_bom_aceito():
    origem, _, _ = dados()
    assert len(validar_origem_ficticia("\ufeff" + origem)) == 27


def test_fonte_excessiva_rejeitada():
    with pytest.raises(ValueError, match="limite"):
        _ler_14_em_memoria("a" * 1_000_001)


def test_ficha_vazia_bloqueia_antes_da_pontuacao():
    origem, _, _ = dados()
    chamadas = []
    def executor(*args, **kwargs):
        chamadas.append(1)
        raise RuntimeError("não deveria ser chamado")
    with pytest.raises(ValueError, match="integralmente"):
        ensaio_em_memoria(origem, gerar_ficha_cega_ficticia(origem), executor=executor)
    assert chamadas == []


def test_ficha_duplicada_bloqueia_antes_da_pontuacao():
    origem, _, ficha = dados()
    linhas = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    linhas[1]["id_par"] = linhas[0]["id_par"]
    chamadas = []
    with pytest.raises(ValueError):
        ensaio_em_memoria(origem, _reescrever_ficha(linhas), executor=lambda *_: chamadas.append(1))
    assert not chamadas


def test_ficha_com_frase_alterada_ou_rotulo_invalido_bloqueia():
    origem, _, ficha = dados()
    linhas = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    linhas[0]["frase_feminina"] += " alterada"
    with pytest.raises(ValueError, match="Frase"):
        validar_ficha_finalizada_ficticia(origem, _reescrever_ficha(linhas))
    linhas = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    linhas[0]["rotulo"] = "mista"
    with pytest.raises(ValueError):
        validar_ficha_finalizada_ficticia(origem, _reescrever_ficha(linhas))


def test_inconsistencia_equivalencia_bloqueia():
    origem, _, ficha = dados()
    linhas = list(csv.DictReader(io.StringIO(ficha), delimiter=";"))
    linhas[0]["equivalencia"] = "nao"
    with pytest.raises(ValueError, match="não pode"):
        validar_ficha_finalizada_ficticia(origem, _reescrever_ficha(linhas))


def test_ensaio_real_dos_baselines_somente_fixture():
    origem, _, ficha = dados()
    rel = ensaio_em_memoria(origem, ficha)
    assert rel["fase"] == "CONTRATO_FINAL_ENSAIADO_SOMENTE_FICTICIO"
    assert rel["resumo_sintetico"]["P_total"] == 27
    assert rel["resumo_sintetico"]["F_total"] == 54
    assert set(rel["resumo_sintetico"]["metodos"]) == {"v01", "v03", "v04"}
    assert rel["avaliacao_final_executada"] is False
    assert rel["acuracia_validada"] is None
    assert rel["evidencia_de_vies"] is None
    assert rel["resumo_sintetico"]["P_elegiveis_com_rotulo_neutro_separado"] == 7
    assert 'atendente' not in json.dumps(rel)


def test_mau_retorno_do_executor_rejeitado():
    origem, _, ficha = dados()
    for r in (None, {}, {"fase": "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL",
                           "avaliacao_final_executada": True,
                           "resumo": {"P_total": 27, "F_total": 54}}):
        with pytest.raises(ValueError):
            ensaio_em_memoria(origem, ficha, executor=lambda *_: r)


def test_falha_de_baseline_propaga_sem_relatorio_parcial():
    origem, _, ficha = dados()
    with pytest.raises(RuntimeError, match="falha inventada"):
        ensaio_em_memoria(origem, ficha,
                         executor=lambda *_: (_ for _ in ()).throw(RuntimeError("falha inventada")))


def test_nenhuma_forma_de_habilitar_execucao_real():
    for args, kwargs in (((), {}), (("caminho",), {"autorizacao": True}),
                         ((), {"congelado": True, "forcar": True})):
        with pytest.raises(PermissionError, match="BLOQUEADO"):
            executar_final(*args, **kwargs)
    assert verificar_contrato()["autorizacao_execucao_final"] is False


def test_cli_rejeita_entrada_de_arquivo_e_argumentos_extras(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["executor_final_bloqueado_bloco34",
                                    "ensaiar", "--entrada", "data/piloto/restrito/final.csv"])
    with pytest.raises(SystemExit) as erro:
        main()
    assert erro.value.code == 2


def test_cli_modo_final_retorna_erro_sem_ler_arquivos(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["executor_final_bloqueado_bloco34", "executar-final"])
    with pytest.raises(SystemExit) as erro:
        main()
    assert erro.value.code == 1
    assert "BLOQUEADO" in capsys.readouterr().err


def test_ensaio_persiste_registro_uma_vez(tmp_path):
    resposta = ensaiar_uma_vez(tmp_path)
    assert resposta["avaliacao_final_executada"] is False
    base = tmp_path / PASTA_RELATORIO
    marcador = base / "marcador_tentativa_bloco34.json"
    relatorio = base / "relatorio_contrato_bloco34.json"
    assert marcador.exists() and relatorio.exists()
    doc = json.loads(relatorio.read_text(encoding="utf-8"))
    assert doc["resumo"]["resumo_sintetico"]["P_total"] == 27
    antes = relatorio.read_bytes()
    with pytest.raises(FileExistsError):
        ensaiar_uma_vez(tmp_path)
    assert relatorio.read_bytes() == antes


def test_falha_no_ensaio_preserva_marcador_e_bloqueia_reexecucao(tmp_path):
    def erro(*_):
        raise RuntimeError("Falha simulada após marcador")
    with pytest.raises(RuntimeError):
        ensaiar_uma_vez(tmp_path, executor=erro)
    pasta = tmp_path / PASTA_RELATORIO
    assert (pasta / "marcador_tentativa_bloco34.json").exists()
    assert not (pasta / "relatorio_contrato_bloco34.json").exists()
    with pytest.raises(FileExistsError):
        ensaiar_uma_vez(tmp_path)


def test_verificacao_contrato_estatica_sem_acesso_real():
    c = verificar_contrato()
    assert c["origem_campos"] == 14 and c["ficha_campos"] == 6
    assert c["executor_real_liberado"] is False
    assert c["dados_reservados_lidos"] is False
    assert c["n_familias_sinteticas"] == 9
