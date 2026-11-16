"""Contratos da camada explicativa. Não carrega dados de avaliação ou léxicos.

Os testes de API e baseline continuam nos módulos preexistentes.
"""
from pathlib import Path
import re
import pytest

ROOT = Path(__file__).resolve().parents[2]
JS = (ROOT / 'frontend/app.js').read_text(encoding='utf-8')
CSS = (ROOT / 'frontend/styles.css').read_text(encoding='utf-8')


@pytest.mark.parametrize('codigo', [
    'categoria_gramatical_incompativel',
    'sintagma_com_ligado_a_nome',
    'sem_adjunto_com_unico_ligado_a_verbo',
    'hipotese_modo_nao_ativada',
    'ambiguidade_categoria',
    'ambiguidade_lema',
    'negacao_sem_escopo',
    'modificador_sem_escopo',
])
def test_codigos_traduzidos_sem_apagar_origem_tecnica(codigo):
    assert codigo in JS
    assert 'function explicarMotivo(codigo)' in JS
    assert 'motivos:data.motivos' in JS


def test_c005_c006_explicacao_distingue_ligacao_e_pontuacao():
    assert "status === 'ABSTENCAO_ANEXACAO_AMBIGUA'" in JS
    assert 'Nenhuma pontuação foi atribuída' in JS
    assert 'anexacao_nominal_ambigua' in JS


def test_cobertura_nao_e_acuracia():
    assert 'Cobertura lexical não é acurácia' in JS
    assert 'tokens_cobertos' in JS
    assert 'tokens_totais' in JS
    assert 'correspondência descartada também pode constar na cobertura' in JS


def test_estado_neutro_nao_confundido_com_zero_lexical():
    assert 'pontuacao_exploratoria === 0' in JS
    assert 'não prova que a frase é neutra' in JS


def test_comparacao_nao_infere_vies():
    assert 'A diferença exibida, quando calculável, é apenas descritiva' in JS
    assert 'não mede viés de gênero' in JS
    assert 'Não calculável' in JS


def test_interface_explica_abstencao_nos_dois_modos():
    assert 'banner(data.status, data.motivos) + interpretacao(data)' in JS
    assert '${interpretacao(data, true)}' in JS
    assert '${coberturaNota(data, true)}' in JS


def test_termos_fonte_e_modelos_continuam_no_detalhe_tecnico():
    for token in ['manifesto_fontes', 'etiquetador', 'checagens_contextuais', 'filtragem_neutros_pos']:
        assert token in JS
    assert 'function technical(data)' in JS


def test_pistas_gramaticais_nao_sao_apresentadas_como_certeza():
    assert 'Ligação a substantivo — incerta' in JS
    assert 'As categorias e ligações são estimativas' in JS
    assert 'não confirmação do significado' in JS


def test_valores_dinamicos_sao_escapados_na_interpretacao():
    assert '${esc(explicacaoResultado(data))}' in JS
    assert '${esc(x.expressao)}' in JS
    assert '${esc(nomePapel(x.papel_hipotetico))}' in JS
    assert '${esc(x.motivo ? explicarMotivo(x.motivo)' in JS


def test_nao_exibe_percentual_como_precisao():
    assert 'Cobertura lexical superficial' in JS
    assert "metric('Precisão'" not in JS
    assert "metric('Acurácia'" not in JS


def test_seletores_de_estilo_responsivo():
    for selector in ['.interpretation-panel', '.interpretation-panel.compact', '.coverage-note', '@media(max-width:520px)']:
        assert selector in CSS


def test_js_nao_consulta_arquivos_privados():
    assert 'data/piloto/restrito' not in JS
    assert 'pares_avaliacao' not in JS
    assert re.search(r"const API = \{ info: '/api/ui/info', analisar: '/api/ui/analisar', comparar: '/api/ui/comparar' \}", JS)
