"""Testes de contrato estático do Bloco 11; não substituem testes visuais.

Não exigem léxicos originais nem os pares reservados para avaliação.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"


def test_pagina_preserva_estrutura_da_interface():
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    for element in ('id="form-analisar"', 'id="form-comparar"', 'id="results"', 'id="lexico"'):
        assert element in page


def test_comparacao_destacada_sem_alegacao_cientifica():
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert 'id="hero-compare"' in page
    assert 'Comparar referências de gênero' in page
    assert "não determina viés" in page


def test_compatibilidade_com_rotas_existentes():
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    for route in ('/api/ui/info', '/api/ui/analisar', '/api/ui/comparar'):
        assert route in js


def test_cartoes_nomeiam_metricas_como_exploratorias():
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    assert "metric('Pontuação (exploratória)'" in js
    assert "metric('Classe (exploratória)'" in js


def test_diferenca_zero_nao_interpretada_como_ausencia_de_vies():
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    assert 'não demonstra ausência de viés' in js
    assert 'sem inferência causal ou estatística de viés' in js


def test_abstencao_em_par_impede_delta_numerico():
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    assert 'data.ambas_pontuaveis === true' in js
    assert 'Não calculável' in js
    assert 'Abstenção — sem pontuação' in js


def test_ignora_resultado_de_consulta_obsoleta():
    js = (FRONTEND / "app.js").read_text(encoding="utf-8")
    assert 'const seq = ++state.requestSeq;' in js
    assert js.count('seq !== state.requestSeq || mode !== state.mode') == 2


def test_sem_dependencias_web_externas():
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert '<script src="/static/app.js" defer>' in page
    assert 'href="/static/styles.css"' in page
    assert 'https://cdn' not in page


def test_estilos_comportamento_responsivo():
    css = (FRONTEND / "styles.css").read_text(encoding="utf-8")
    assert '.compare-results{grid-template-columns:1fr}' in css
    assert '.delta-panel{flex-direction:column' in css


def test_favicon_svg_local():
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    favicon = FRONTEND / "favicon.svg"
    assert 'href="/static/favicon.svg"' in page
    assert favicon.exists()
    assert '<svg ' in favicon.read_text(encoding="utf-8")
