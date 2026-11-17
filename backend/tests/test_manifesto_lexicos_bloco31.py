"""Bloco 31: exclusivamente fixtures de léxicos inventados em tmp_path."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

import backend.manifesto_lexicos_bloco31 as mod


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ambiente(tmp_path: Path, monkeypatch) -> Path:
    """Produz somente objetos inventados: nenhum léxico real ou dado reservado."""
    base = tmp_path / "data/lexicos/originais"
    base.mkdir(parents=True)
    curadoria = {"total_falhas_de_leitura": 0, "fontes": {}}
    auditoria = {"arquivos": {}}
    for chave, nome in mod.ORIGINAIS.items():
        p = base / nome
        dados = ("simulacao-ficticia:" + nome).encode()
        p.write_bytes(dados)
        if chave != "sentilex_zip":
            curadoria["fontes"][chave] = {"sha256": sha(dados)}
            auditoria["arquivos"][chave] = {"sha256": sha(dados)}
        else:
            auditoria["sentilex_zip"] = {"sha256": sha(dados), "md5": hashlib.md5(dados).hexdigest()}
            monkeypatch.setattr(mod, "MD5_SENTILEX_PUBLICADO", hashlib.md5(dados).hexdigest())
    for nome, obj in (("relatorio_curadoria.json", curadoria), ("relatorio_auditoria.json", auditoria)):
        (tmp_path / "data/lexicos" / nome).write_text(json.dumps(obj), encoding="utf-8")
    for relativo in mod.CODIGO_E_PROTOCOLOS:
        p = tmp_path / relativo
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("exemplo publico ficticio " + relativo, encoding="utf-8")
    return tmp_path


def test_integridade_valida_e_sem_avaliacao(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    manifesto = mod.preparar_manifesto(raiz)
    assert manifesto["estado"] == mod.ESTADO
    assert manifesto["autorizacao_execucao_final"] is False
    assert manifesto["dados_reservados_lidos"] is False
    assert manifesto["hash_particao_reservada"] is None
    assert manifesto["integridade_lexicos"] == "CONFERIDA_COM_RELATORIOS_LOCAIS"
    assert len(manifesto["hashes_lexicos_originais"]) == 4
    assert len(manifesto["hashes_codigo_protocolos"]) == len(mod.CODIGO_E_PROTOCOLOS)


def test_status_configuracao_ainda_nao_congelado(tmp_path, monkeypatch):
    m = mod.preparar_manifesto(ambiente(tmp_path, monkeypatch))
    conf = m["configuracao_proposta_nao_aprovada"]
    assert conf["baselines"] == ["V01", "V03", "V04"]
    assert conf["alvo_manual"] == "N0"
    assert conf["hipotese_modo_v03"] and conf["hipotese_modo_v04"]
    assert m["pendencias"]


def test_arquivo_original_alterado_e_bloqueado(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    (raiz / "data/lexicos/originais/lexico_v3.0.txt").write_bytes(b"modificado")
    with pytest.raises(ValueError, match="DIVERGÊNCIA"):
        mod.preparar_manifesto(raiz)


def test_hash_de_auditoria_divergente_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    p = raiz / "data/lexicos/relatorio_auditoria.json"
    obj = json.loads(p.read_text())
    obj["arquivos"]["sentilex_lem"]["sha256"] = "a" * 64
    p.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="DIVERGÊNCIA"):
        mod.preparar_manifesto(raiz)


def test_curadoria_com_falha_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    p = raiz / "data/lexicos/relatorio_curadoria.json"
    obj = json.loads(p.read_text())
    obj["total_falhas_de_leitura"] = 1
    p.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="zero falhas"):
        mod.preparar_manifesto(raiz)


def test_md5_zip_diferente_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    monkeypatch.setattr(mod, "MD5_SENTILEX_PUBLICADO", "0"*32)
    with pytest.raises(ValueError, match="MD5"):
        mod.preparar_manifesto(raiz)


def test_zip_sha_auditoria_diferente_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    p = raiz / "data/lexicos/relatorio_auditoria.json"
    obj = json.loads(p.read_text())
    obj["sentilex_zip"]["sha256"] = "0"*64
    p.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256 do ZIP"):
        mod.preparar_manifesto(raiz)


def test_original_ausente_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    (raiz / "data/lexicos/originais/SentiLex-flex-PT02.txt").unlink()
    with pytest.raises(FileNotFoundError, match="único original"):
        mod.preparar_manifesto(raiz)


def test_original_duplicado_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    pasta = raiz / "data/lexicos/originais/outro"
    pasta.mkdir()
    (pasta / "lexico_v3.0.txt").write_text("copia")
    with pytest.raises(FileNotFoundError, match="encontrados 2"):
        mod.preparar_manifesto(raiz)


def test_arquivo_publico_ausente_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    (raiz / mod.CODIGO_E_PROTOCOLOS[1]).unlink()
    with pytest.raises(FileNotFoundError):
        mod.preparar_manifesto(raiz)


def test_symlink_de_original_bloqueia(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    p = raiz / "data/lexicos/originais/lexico_v3.0.txt"
    alvo = tmp_path / "externo.txt"
    alvo.write_text("conteudo")
    p.unlink()
    try:
        p.symlink_to(alvo)
    except OSError:
        pytest.skip("Sistema não admite symlink")
    with pytest.raises(ValueError, match="fora da pasta|simbólico"):
        mod.preparar_manifesto(raiz)


def test_registro_unico_privado_sem_sobrescrita(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    status = mod.registrar_manifesto(raiz)
    assert status["registro_sem_sobrescrita"]
    caminho = raiz / mod.DESTINO_RELATIVO
    original = caminho.read_bytes()
    with pytest.raises(FileExistsError):
        mod.registrar_manifesto(raiz)
    assert caminho.read_bytes() == original
    assert json.loads(original)["autorizacao_execucao_final"] is False


def test_falha_nos_lexicos_nao_cria_registro(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    (raiz / "data/lexicos/originais/lexico_v3.0.txt").unlink()
    with pytest.raises(FileNotFoundError):
        mod.registrar_manifesto(raiz)
    assert not (raiz / mod.DESTINO_RELATIVO).exists()


def test_diretorio_privado_symlink_recusa_gravacao(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    pasta = raiz / "data/piloto"
    try:
        pasta.symlink_to(tmp_path / "data/lexicos", target_is_directory=True)
    except OSError:
        pytest.skip("Sistema não admite symlink")
    with pytest.raises(ValueError, match="simbólico"):
        mod.registrar_manifesto(raiz)


def test_nao_le_reservados(tmp_path, monkeypatch):
    raiz = ambiente(tmp_path, monkeypatch)
    privado = raiz / "data/piloto/restrito/avaliacao_final/pares_reservados.txt"
    privado.parent.mkdir(parents=True)
    privado.write_text("ESTE_ARQUIVO_NAO_PODE_SER_LIDO", encoding="utf-8")
    manifesto = mod.preparar_manifesto(raiz)
    assert "ESTE_ARQUIVO_NAO_PODE_SER_LIDO" not in json.dumps(manifesto)
    assert "avaliacao_final/" not in json.dumps(manifesto)
    assert privado.read_text() == "ESTE_ARQUIVO_NAO_PODE_SER_LIDO"


def test_cli_rejeita_arquivo_arbitrario_e_execucao_final(monkeypatch):
    for args in (["verificar", "--entrada", "data/piloto/restrito/avaliacao.csv"], ["avaliar-final"]):
        monkeypatch.setattr(sys, "argv", ["manifesto_lexicos_bloco31", *args])
        with pytest.raises(SystemExit) as err:
            mod.main()
        assert err.value.code == 2
