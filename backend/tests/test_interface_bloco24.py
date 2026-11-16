"""Contratos do ajuste de interface do Bloco 24, sem dados de avaliação."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "aplicar_bloco24.py"

spec = importlib.util.spec_from_file_location("sentivis_aplicar_bloco24", SCRIPT)
assert spec is not None and spec.loader is not None
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


@pytest.fixture
def mock_projeto(tmp_path):
    pasta = tmp_path / "frontend"
    pasta.mkdir()
    (pasta / "index.html").write_text(
        '<span class="aside-note">Versão de demonstração · v0.1</span>',
        encoding="utf-8",
    )
    (pasta / "styles.css").write_text(
        '.context-table-wrap{overflow:auto}.compare-card{padding:20px}\n',
        encoding="utf-8",
    )
    return tmp_path


def test_identificacao_nao_confunde_versao_da_interface_com_baseline(mock_projeto):
    patch.aplicar(mock_projeto)
    html = (mock_projeto / "frontend/index.html").read_text(encoding="utf-8")
    assert patch.TEXTO_NOVO in html
    assert patch.TEXTO_ANTIGO not in html
    assert "V01 e V04" in html


def test_tabela_contextual_conserva_primeira_coluna_sem_quebrar(mock_projeto):
    patch.aplicar(mock_projeto)
    css = (mock_projeto / "frontend/styles.css").read_text(encoding="utf-8")
    assert ".context-table td:first-child" in css
    assert "white-space: nowrap" in css
    assert "overflow-wrap: normal" in css
    assert "min-width: 88px" in css


def test_tabela_permite_rolagem_local(mock_projeto):
    patch.aplicar(mock_projeto)
    css = (mock_projeto / "frontend/styles.css").read_text(encoding="utf-8")
    assert "overflow-x: auto" in css
    assert "min-width: 660px" in css
    assert "max-width: 100%" in css


def test_preserva_quebra_legivel_nas_colunas_descritivas(mock_projeto):
    patch.aplicar(mock_projeto)
    css = (mock_projeto / "frontend/styles.css").read_text(encoding="utf-8")
    assert ".context-table td:not(:first-child)" in css
    assert "overflow-wrap: break-word" in css


def test_aplicacao_idempotente(mock_projeto):
    assert len(patch.aplicar(mock_projeto)) == 2
    assert patch.aplicar(mock_projeto) == []
    css = (mock_projeto / "frontend/styles.css").read_text(encoding="utf-8")
    assert css.count(patch.MARCADOR_CSS) == 1


def test_nao_altera_css_se_html_nao_corresponde(mock_projeto):
    html = mock_projeto / "frontend/index.html"
    css = mock_projeto / "frontend/styles.css"
    html.write_text("<html>página não identificada</html>", encoding="utf-8")
    original = css.read_bytes()
    with pytest.raises(ValueError, match="versão esperada"):
        patch.aplicar(mock_projeto)
    assert css.read_bytes() == original


def test_nao_altera_html_se_css_nao_corresponde(mock_projeto):
    html = mock_projeto / "frontend/index.html"
    css = mock_projeto / "frontend/styles.css"
    css.write_text("body{}", encoding="utf-8")
    original = html.read_bytes()
    with pytest.raises(ValueError, match="Bloco 23"):
        patch.aplicar(mock_projeto)
    assert html.read_bytes() == original


def test_apenas_frontend_é_modificado(mock_projeto):
    (mock_projeto / "dados_privados.txt").write_text("não tocar", encoding="utf-8")
    patch.aplicar(mock_projeto)
    assert (mock_projeto / "dados_privados.txt").read_text(encoding="utf-8") == "não tocar"


def test_arquivo_real_possui_a_identificacao_e_tabela():
    pagina = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    assert patch.TEXTO_NOVO in pagina
    assert patch.MARCADOR_CSS in css
