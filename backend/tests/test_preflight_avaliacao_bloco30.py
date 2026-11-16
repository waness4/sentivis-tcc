"""Bloco 30: somente pares SINT e caminhos públicos artificiais em tmp_path."""
from __future__ import annotations

from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import sys

import pytest

from backend.avaliacao_final_preparacao_bloco29 import _ficticios
from backend.preflight_avaliacao_bloco30 import (
    ARQUIVOS_PUBLICOS, COLUNAS_FICHA, hash_bytes, ficha_sintetica_csv,
    main, manifesto_publico, registrar_ensaio_unico, validar_conteudo_ficha_csv,
)


def fixture_publica(tmp_path: Path) -> Path:
    for relativo in ARQUIVOS_PUBLICOS:
        p = tmp_path / relativo
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("arquivo público sintético: " + relativo, encoding="utf-8")
    return tmp_path


def resumo_falso() -> dict:
    return {
        "fase": "SIMULACAO_SINTETICA_SEM_ACESSO_AVALIACAO_FINAL",
        "P_total": 4, "F_total": 8, "metodos": {}, "evidencia_de_vies": None,
    }


def test_ficha_sem_previsoes_seis_colunas_e_quatro_ids():
    pares, _ = _ficticios()
    csv_s = ficha_sintetica_csv(pares)
    leitor = csv.DictReader(io.StringIO(csv_s), delimiter=";")
    assert tuple(leitor.fieldnames) == COLUNAS_FICHA
    linhas = list(leitor)
    assert len(linhas) == 4
    assert all(l["equivalencia"] == l["rotulo"] == "" for l in linhas)
    assert all(set(l) == set(COLUNAS_FICHA) for l in linhas)


def test_anotacoes_sinteticas_preenchidas_validadas():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True)
    assert len(validar_conteudo_ficha_csv(texto, pares)) == 4


def test_template_vazio_e_aceito_como_resposta_pendente():
    pares, _ = _ficticios()
    assert len(validar_conteudo_ficha_csv(ficha_sintetica_csv(pares), pares)) == 4


def test_cabecalho_e_separador_incorretos_falham():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True)
    with pytest.raises(ValueError, match="Cabeçalho"):
        validar_conteudo_ficha_csv(texto.replace(";", ","), pares)
    with pytest.raises(ValueError, match="Cabeçalho"):
        validar_conteudo_ficha_csv(texto.replace("observacoes", "previsao"), pares)


def test_colunas_em_ordem_errada_falham():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True)
    with pytest.raises(ValueError, match="Cabeçalho"):
        validar_conteudo_ficha_csv(texto.replace("id_par;frase_feminina", "frase_feminina;id_par", 1), pares)


def test_duplicacao_e_ausencia_de_id_falham():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True)
    linha_ultima = texto.splitlines()[-1]
    with pytest.raises(ValueError, match="duplicado"):
        validar_conteudo_ficha_csv(texto + linha_ultima + "\n", pares)
    with pytest.raises(ValueError, match="incompleta"):
        validar_conteudo_ficha_csv("\n".join(texto.splitlines()[:-1]) + "\n", pares)


def test_texto_de_ficha_alterado_falha():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True).replace("tratou com gentileza", "falou com gentileza", 1)
    with pytest.raises(ValueError, match="Frase"):
        validar_conteudo_ficha_csv(texto, pares)


def test_inclusao_de_coluna_previsao_falha():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True).replace(";observacoes", ";previsao;observacoes", 1)
    with pytest.raises(ValueError, match="Cabeçalho"):
        validar_conteudo_ficha_csv(texto, pares)


def test_anotacao_nao_equivalente_sem_justificativa_falha():
    pares, _ = _ficticios()
    texto = ficha_sintetica_csv(pares, preenchida=True).replace("Textos semanticamente diferentes (fictício).", "")
    with pytest.raises(ValueError, match="justificativa"):
        validar_conteudo_ficha_csv(texto, pares)


def test_indice_real_ou_dados_externos_rejeitados():
    pares, _ = _ficticios()
    real = deepcopy(pares)
    real[0]["id_par"] = "AV001"
    with pytest.raises(ValueError, match="fictícios"):
        ficha_sintetica_csv(real)
    real = deepcopy(pares)
    real[0]["frase_feminina"] = "Uma frase modificada."
    with pytest.raises(ValueError, match="textos sintéticos"):
        ficha_sintetica_csv(real)


def test_sha256_deterministico_e_bom():
    assert hash_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_manifesto_ler_somente_publicos_e_marcar_nao_congelado(tmp_path):
    root = fixture_publica(tmp_path)
    privado = root / "data/piloto/restrito/avaliacao_final/secreto.csv"
    privado.parent.mkdir(parents=True)
    privado.write_text("NÃO PODE LER", encoding="utf-8")
    m = manifesto_publico(root)
    assert m["estado"] == "NAO_CONGELADO_NAO_AUTORIZADO"
    assert m["autorizacao_execucao_final"] is False
    assert m["dados_reservados_lidos"] is False
    assert m["hash_particao_reservada"] is None
    assert len(m["hashes_sha256_arquivos_publicos"]) == len(ARQUIVOS_PUBLICOS)
    assert "restrito" not in json.dumps(m).lower()
    assert privado.exists()


def test_manifesto_publico_ausente_falha_fechada(tmp_path):
    root = fixture_publica(tmp_path)
    (root / ARQUIVOS_PUBLICOS[0]).unlink()
    with pytest.raises(FileNotFoundError):
        manifesto_publico(root)


def test_marcador_de_execucao_unica_e_reexecucao_bloqueada(tmp_path):
    root = fixture_publica(tmp_path)
    saida = registrar_ensaio_unico(root, resumo=resumo_falso())
    assert saida["avaliacao_final_executada"] is False
    base = root / "data/piloto/restrito/bloco30_ensaio"
    marcador = base / "marcador_tentativa_bloco30.json"
    relatorio = base / "relatorio_ensaio_bloco30.json"
    assert marcador.exists() and relatorio.exists()
    antes = relatorio.read_bytes()
    with pytest.raises(FileExistsError):
        registrar_ensaio_unico(root, resumo=resumo_falso())
    assert relatorio.read_bytes() == antes
    assert json.loads(relatorio.read_text(encoding="utf-8"))["resumo_simulacao"]["P_total"] == 4


def test_marcador_existente_sem_relatorio_continua_bloqueado(tmp_path):
    root = fixture_publica(tmp_path)
    base = root / "data/piloto/restrito/bloco30_ensaio"
    base.mkdir(parents=True)
    (base / "marcador_tentativa_bloco30.json").write_text("TENTATIVA EXISTENTE", encoding="utf-8")
    with pytest.raises(FileExistsError):
        registrar_ensaio_unico(root, resumo=resumo_falso())
    assert not (base / "relatorio_ensaio_bloco30.json").exists()


def test_relatorio_incorreto_nao_cria_marcador(tmp_path):
    root = fixture_publica(tmp_path)
    dados = resumo_falso()
    dados["P_total"] = 27
    with pytest.raises(ValueError, match="sintético"):
        registrar_ensaio_unico(root, resumo=dados)
    assert not (root / "data/piloto/restrito/bloco30_ensaio/marcador_tentativa_bloco30.json").exists()


def test_cli_rejeita_caminhos_e_modo_avaliacao(monkeypatch):
    for args in (["verificar-ambiente", "--entrada", "data/piloto/restrito/avaliacao.csv"],
                 ["avaliar-final"]):
        monkeypatch.setattr(sys, "argv", ["preflight_avaliacao_bloco30", *args])
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 2
