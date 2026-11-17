"""Bloco 35: sem corpus, sem fichas reais, sem recursos lexicais externos."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

from backend.precongelamento_bloco32 import CONFIGURACAO_PREVISTA
from backend.revisao_congelamento_bloco35 import (
    ARQUIVOS_PUBLICOS, DESTINO, ESTADO, PORTOES, _publico_regular,
    _validar_contrato, _validar_inventario, main, preparar_dossie, registrar_dossie,
)


def _raiz_falsa(tmp_path: Path) -> Path:
    for nome in ARQUIVOS_PUBLICOS:
        p = tmp_path / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("ARQUIVO_PUBLICO_SINTETICO=" + nome + "\n", encoding="utf-8")
    return tmp_path


def _inv_falso():
    retorno = {
        "estado": ESTADO,
        "autorizacao_execucao_final": False, "dados_reservados_lidos": False,
        "hash_particao_reservada": None,
        "integridade_lexicos": "CONFERIDA_COM_RELATORIOS_LOCAIS",
        "git_commit_observado": "a" * 40,
        "configuracao_proposta_nao_aprovada": deepcopy(CONFIGURACAO_PREVISTA),
        "ambiente": {"python": "3.13.0", "spacy": "3.8.18", "pt_core_news_sm": "3.8.0"},
        "hashes_lexicos_originais": {
            nome: {"sha256": "a" * 64, "arquivo": nome + ".txt",
                   "confere_com_auditoria_e_md5_publicado" if nome == "sentilex_zip" else "confere_com_curadoria_e_auditoria": True}
            for nome in ("oplexicon", "sentilex_lem", "sentilex_flex", "sentilex_zip")
        },
        "hashes_codigo_protocolos": {
            x: "b" * 64 for x in (
                "backend/baseline_experimental.py", "backend/baseline_contextual_v03.py",
                "backend/baseline_contextual_v04.py", "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md"
            )
        },
    }
    return retorno


def _contrato_falso():
    return {
        "estado": ESTADO,
        "dados_reservados_lidos": False, "autorizacao_execucao_final": False,
        "executor_real_liberado": False,
        "origem_campos": 14, "ficha_campos": 6,
        "n_pares_sinteticos": 27, "n_familias_sinteticas": 9,
        "ficha_individual_e_validada_antes_da_pontuacao": True,
    }


def _conferir(tmp_path, inv=None, con=None):
    return preparar_dossie(_raiz_falsa(tmp_path), inventario=inv or _inv_falso(),
                           contrato=con or _contrato_falso())


def test_dossie_ficticio_tem_dados_publicos_e_todos_portoes_pendentes(tmp_path):
    d = _conferir(tmp_path)
    assert d["estado"] == ESTADO
    assert d["protocolo_congelado"] is False
    assert d["autorizacao_execucao_final"] is False
    assert d["avaliacao_final_executada"] is False
    assert d["aprovacao_academica_registrada"] is False
    assert d["dados_reservados_lidos"] is False
    assert d["hash_particao_reservada"] is None
    assert d["contrato_final_atual"] == "B34_SOMENTE_SINTETICO_EXECUCAO_REAL_BLOQUEADA"
    assert d["n_pendencias"] == len(PORTOES) == 8
    assert all(p["concluida"] is False for p in d["questoes_pendentes"])
    assert len(d["hashes_sha256_codigo_documentos_publicos"]) == len(ARQUIVOS_PUBLICOS)


def test_portoes_incluem_divergencia_de_ficha_e_aprovacao_humana(tmp_path):
    j = json.dumps(_conferir(tmp_path), ensure_ascii=False)
    assert "não resposta" in j
    assert "aprovação acadêmica" in j
    assert "executor final real" in j
    assert "C001" in j
    assert "symlink" in j


def test_dossie_nao_reproduz_qualquer_frase_ou_dado_reservado(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    privado = raiz / "data/piloto/restrito/avaliacao_final/conteudo.csv"
    privado.parent.mkdir(parents=True)
    privado.write_text("MENSAGEM_SECRETA_QUE_NAO_PODE_SAIR", encoding="utf-8")
    d = preparar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())
    assert "MENSAGEM_SECRETA_QUE_NAO_PODE_SAIR" not in json.dumps(d)
    assert privado.is_file()
    assert "data/piloto/" not in json.dumps(d)


def test_sha_documento_muda_se_arquivo_publico_mudar(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    a = preparar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())
    caminho = raiz / ARQUIVOS_PUBLICOS[0]
    caminho.write_text("NOVO PUBLICO", encoding="utf-8")
    b = preparar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())
    assert a["hashes_sha256_codigo_documentos_publicos"][ARQUIVOS_PUBLICOS[0]] != b["hashes_sha256_codigo_documentos_publicos"][ARQUIVOS_PUBLICOS[0]]


def test_publico_ausente_bloqueia(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    (raiz / ARQUIVOS_PUBLICOS[0]).unlink()
    with pytest.raises(FileNotFoundError):
        preparar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())


@pytest.mark.parametrize("path", ["data/piloto/restrito/a.txt", "data/lexicos/originais/a.txt",
                                  "backend/../../data/piloto/a.csv", "../.env", "/etc/passwd"])
def test_caminho_nao_autorizado_bloqueia(tmp_path, path):
    _raiz_falsa(tmp_path)
    with pytest.raises(ValueError, match="autorizada"):
        _publico_regular(tmp_path, path)


@pytest.mark.parametrize("alteracao", [
    {"autorizacao_execucao_final": True},
    {"dados_reservados_lidos": True},
    {"hash_particao_reservada": "b"*64},
    {"estado": "CONGELADO"},
    {"integridade_lexicos": "NAO_VERIFICADA"},
])
def test_inventario_sem_bloqueio_ou_sem_integridade_falha(alteracao):
    inv = _inv_falso()
    inv.update(alteracao)
    with pytest.raises(ValueError):
        _validar_inventario(inv)


def test_inventario_parametros_incompativeis_falha():
    inv = _inv_falso()
    inv["configuracao_proposta_nao_aprovada"]["alvo_manual"] = "N1"
    with pytest.raises(ValueError, match="Configuração"):
        _validar_inventario(inv)


def test_inventario_lexico_incompleto_falha():
    inv = _inv_falso()
    del inv["hashes_lexicos_originais"]["sentilex_flex"]
    with pytest.raises(ValueError, match="lexical"):
        _validar_inventario(inv)


def test_inventario_hash_invalido_falha():
    inv = _inv_falso()
    inv["hashes_lexicos_originais"]["oplexicon"]["sha256"] = "invalido"
    with pytest.raises(ValueError, match="Original"):
        _validar_inventario(inv)


@pytest.mark.parametrize("alteracao", [
    {"executor_real_liberado": True}, {"autorizacao_execucao_final": True},
    {"origem_campos": 6}, {"ficha_campos": 14},
    {"dados_reservados_lidos": True},
    {"ficha_individual_e_validada_antes_da_pontuacao": False},
])
def test_contrato_invalido_falha(alteracao):
    con = _contrato_falso()
    con.update(alteracao)
    with pytest.raises(ValueError):
        _validar_contrato(con)


def test_registro_preliminar_unico_sem_sobrescrita(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    out = registrar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())
    assert out["sobrescrita_bloqueada"] is True
    assert out["protocolo_congelado"] is False
    arquivo = raiz / DESTINO
    antes = arquivo.read_bytes()
    with pytest.raises(FileExistsError):
        registrar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())
    assert arquivo.read_bytes() == antes
    assert json.loads(antes)["avaliacao_final_executada"] is False


def test_destino_com_arquivo_em_vez_de_pasta_bloqueia(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    (raiz / "data").write_text("arquivos privados proibidos aqui", encoding="utf-8")
    with pytest.raises(ValueError, match="não é pasta"):
        registrar_dossie(raiz, inventario=_inv_falso(), contrato=_contrato_falso())


def test_validacao_acontece_antes_de_criar_arquivo(tmp_path):
    raiz = _raiz_falsa(tmp_path)
    con = _contrato_falso()
    con["executor_real_liberado"] = True
    with pytest.raises(ValueError):
        registrar_dossie(raiz, inventario=_inv_falso(), contrato=con)
    assert not (raiz / DESTINO).exists()


def test_cli_nao_aceita_executar_final(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["bloco35", "executar-final"])
    with pytest.raises(SystemExit) as erro:
        main()
    assert erro.value.code == 2


def test_cli_nao_aceita_entrada_reservada(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["bloco35", "verificar", "--entrada", "data/piloto/restrito/avaliacao.csv"])
    with pytest.raises(SystemExit) as erro:
        main()
    assert erro.value.code == 2
