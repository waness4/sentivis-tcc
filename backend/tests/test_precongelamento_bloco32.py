"""Bloco 32: testes exclusivamente artificiais, sem leitura da partição reservada."""
from __future__ import annotations

from copy import deepcopy
import json
import sys

import pytest

import backend.precongelamento_bloco32 as modulo


def exemplo():
    return {
        "estado": "NAO_CONGELADO_NAO_AUTORIZADO",
        "autorizacao_execucao_final": False,
        "dados_reservados_lidos": False,
        "hash_particao_reservada": None,
        "integridade_lexicos": "CONFERIDA_COM_RELATORIOS_LOCAIS",
        "git_commit_observado": "a" * 40,
        "ambiente": {"python": "3.13.0", "spacy": "3.8.18", "pt_core_news_sm": "3.8.0"},
        "configuracao_proposta_nao_aprovada": deepcopy(modulo.CONFIGURACAO_PREVISTA),
        "hashes_lexicos_originais": {
            x: {"sha256": "b" * 64, "tamanho_bytes": 100,
                ("confere_com_auditoria_e_md5_publicado" if x == "sentilex_zip" else "confere_com_curadoria_e_auditoria"): True}
            for x in ("oplexicon", "sentilex_lem", "sentilex_flex", "sentilex_zip")
        },
        "hashes_codigo_protocolos": {p: "c" * 64 for p in modulo.HASHES_NECESSARIOS},
    }


def test_verificacao_conservadora_com_dados_ficticios():
    resultado = modulo.validar_inventario(exemplo())
    assert resultado["estado"] == "NAO_CONGELADO_NAO_AUTORIZADO"
    assert resultado["integridade_lexicos"] == "CONFERIDA_COM_RELATORIOS_LOCAIS"
    assert resultado["protocolo_congelado"] is False
    assert resultado["autorizacao_execucao_final"] is False
    assert resultado["dados_reservados_lidos"] is False
    assert resultado["hash_particao_reservada"] is None
    assert resultado["acuracia_validada"] is None
    assert resultado["evidencia_de_vies"] is None
    assert "frase_feminina" not in json.dumps(resultado)


@pytest.mark.parametrize("chave,valor", [
    ("estado", "CONGELADO"),
    ("autorizacao_execucao_final", True),
    ("dados_reservados_lidos", True),
    ("hash_particao_reservada", "a" * 64),
])
def test_inventario_nao_bloqueado_rejeitado(chave, valor):
    inv = exemplo()
    inv[chave] = valor
    with pytest.raises(ValueError, match="bloqueada"):
        modulo.validar_inventario(inv)


def test_modificacao_configuracao_rejeitada():
    inv = exemplo()
    inv["configuracao_proposta_nao_aprovada"]["alvo_manual"] = "N1"
    with pytest.raises(ValueError, match="Configuração"):
        modulo.validar_inventario(inv)


def test_modelo_ausente_rejeitado():
    inv = exemplo()
    inv["ambiente"]["pt_core_news_sm"] = None
    with pytest.raises(ValueError, match="Versões"):
        modulo.validar_inventario(inv)


def test_lexico_sem_hash_rejeitado():
    inv = exemplo()
    inv["hashes_lexicos_originais"]["sentilex_flex"]["sha256"] = "xyz"
    with pytest.raises(ValueError, match="Hash lexical"):
        modulo.validar_inventario(inv)


def test_lexico_sem_conferencia_rejeitado():
    inv = exemplo()
    inv["hashes_lexicos_originais"]["sentilex_zip"]["confere_com_auditoria_e_md5_publicado"] = False
    with pytest.raises(ValueError, match="não verificado"):
        modulo.validar_inventario(inv)


def test_codigo_sem_hash_rejeitado():
    inv = exemplo()
    del inv["hashes_codigo_protocolos"][modulo.HASHES_NECESSARIOS[0]]
    with pytest.raises(ValueError, match="incompletos"):
        modulo.validar_inventario(inv)


def test_verificar_delega_apenas_ao_manifesto_publico(monkeypatch, tmp_path):
    caminho_privado = tmp_path / "data/piloto/avaliacao_final/nao_abrir.csv"
    caminho_privado.parent.mkdir(parents=True)
    caminho_privado.write_text("CONTEUDO_SIGILOSO", encoding="utf-8")
    recebido = []
    monkeypatch.setattr(modulo, "preparar_manifesto", lambda raiz: recebido.append(raiz) or exemplo())
    resultado = modulo.verificar(tmp_path)
    assert recebido == [tmp_path]
    assert resultado["dados_reservados_lidos"] is False
    assert "CONTEUDO_SIGILOSO" not in json.dumps(resultado)
    assert caminho_privado.exists()


def test_cli_rejeita_entrada_e_modo_de_execucao(monkeypatch):
    for args in (("verificar", "--entrada", "avaliacao.csv"), ("executar-final",)):
        monkeypatch.setattr(sys, "argv", ["precongelamento_bloco32", *args])
        with pytest.raises(SystemExit) as erro:
            modulo.main()
        assert erro.value.code == 2


def test_cli_verificar_ficticio(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["precongelamento_bloco32", "verificar"])
    monkeypatch.setattr(modulo, "verificar", lambda: modulo.validar_inventario(exemplo()))
    modulo.main()
    saida = capsys.readouterr().out
    assert "NAO_CONGELADO_NAO_AUTORIZADO" in saida
    assert "NÃO congelado" in saida
