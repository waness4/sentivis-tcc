"""Integração Blocos 7/12: JSON real do CLI do piloto + métricas.

Usa apenas dados sintéticos; nenhuma avaliação humana real é acessada.
"""
import json
import pytest

from backend.metricas_exploratorias import calcular
from backend.pares_piloto import ler_csv, validar_pares
from backend.tests.test_metricas_exploratorias import _dataset, _piloto


def _relatorio_integrado(tmp_path):
    dataset = _dataset(tmp_path)
    piloto_direto = _piloto(tmp_path, dataset)
    dados = json.loads(piloto_direto.read_text(encoding="utf-8"))
    linhas, sha = ler_csv(dataset)
    auditoria = validar_pares(linhas, sha256=sha)
    relatorio = tmp_path / "relatorio_integrado.json"
    relatorio.write_text(json.dumps({"auditoria": auditoria, "piloto": dados}, ensure_ascii=False), encoding="utf-8")
    return dataset, relatorio


def test_metrica_aceita_saida_real_do_cli_pares_piloto(tmp_path):
    dataset, relatorio = _relatorio_integrado(tmp_path)
    resumo, linhas = calcular(dataset, relatorio)
    assert resumo["pares_desenvolvimento_aprovados"] == 2
    assert resumo["pares_avaliacao_processados"] == 0
    assert len(linhas) == 4


def test_metrica_bloqueia_auditoria_invalida_no_envelope(tmp_path):
    dataset, relatorio = _relatorio_integrado(tmp_path)
    documento = json.loads(relatorio.read_text(encoding="utf-8"))
    documento["auditoria"]["erros"] = ["erro sintético"]
    documento["auditoria"]["status"] = "INVALIDO"
    relatorio.write_text(json.dumps(documento), encoding="utf-8")
    with pytest.raises(ValueError, match="Auditoria"):
        calcular(dataset, relatorio)


def test_metrica_bloqueia_hash_incompativel_da_auditoria(tmp_path):
    dataset, relatorio = _relatorio_integrado(tmp_path)
    documento = json.loads(relatorio.read_text(encoding="utf-8"))
    documento["auditoria"]["sha256_dataset"] = "hash-incorreto"
    relatorio.write_text(json.dumps(documento), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        calcular(dataset, relatorio)


def test_metrica_bloqueia_envelope_sem_piloto(tmp_path):
    dataset, relatorio = _relatorio_integrado(tmp_path)
    documento = json.loads(relatorio.read_text(encoding="utf-8"))
    documento.pop("piloto")
    relatorio.write_text(json.dumps(documento), encoding="utf-8")
    with pytest.raises(ValueError, match="integrado"):
        calcular(dataset, relatorio)
