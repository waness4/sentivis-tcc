"""Bloco 22: UI V04, validações HTTP, dados sintéticos e nenhum dado reservado."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend import ui_server
from backend.tests.test_ui_server import client  # noqa: F401: fixture sintética existente


class FakeNLP:
    meta = {"version": "fixture"}


def payload_single(**extra):
    return {"texto": "A pesquisadora apresentou os dados com segurança.",
            "lexico": "sentilex", "alvo": "N0", "metodo": "contextual_v04",
            "hipotese_modo": True, **extra}


def payload_compare():
    return {"feminina": "A pesquisadora explicou com segurança.",
            "masculina": "O pesquisador explicou com segurança.",
            "lexico": "sentilex", "alvo": "N0", "metodo": "contextual_v04",
            "hipotese_modo": True}


def test_info_lista_metodos_sem_dados_privados(client):
    data = client.get('/api/ui/info').json()
    assert data['metodos'] == ['aditivo_v01', 'contextual_v04']
    assert not data['validacao_cientifica']
    assert 'pares_finais' not in str(data)


@pytest.mark.parametrize('campo,valor', [
    ('alvo', None), ('hipotese_modo', False), ('lexico', 'oplexicon'),
])
def test_rejeita_contextual_sem_condicoes(client, campo, valor):
    p = payload_single()
    p[campo] = valor
    resp = client.post('/api/ui/analisar', json=p)
    assert resp.status_code == 422


def test_rejeita_metodo_inexistente(client):
    p = payload_single()
    p['metodo'] = 'v05'
    assert client.post('/api/ui/analisar', json=p).status_code == 422


def test_rejeita_hipotese_na_v01(client):
    p = payload_single()
    p['metodo'] = 'aditivo_v01'
    assert client.post('/api/ui/analisar', json=p).status_code == 422


def test_analisar_v04_chama_baseline_sem_alterar_dados(client, monkeypatch):
    entradas = []

    def fake(txt, indice, **kwargs):
        entradas.append(kwargs)
        return {"metodo": "baseline_contextual_sentilex_v0.4_filtro_neutro_pos_hipotese_nao_validada",
                "status": "ABSTENCAO_ANEXACAO_AMBIGUA",
                "motivos": ["sintagma_com_ligado_a_nome"],
                "pontuacao_exploratoria": None,
                "filtragem_neutros_pos": {"aplicada": True, "descartados": [{"expressao": "dados"}]}}

    monkeypatch.setattr(ui_server, '_obter_etiquetador', lambda: FakeNLP())
    monkeypatch.setattr(ui_server, 'classificar_v04', fake)
    resp = client.post('/api/ui/analisar', json=payload_single())
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ABSTENCAO_ANEXACAO_AMBIGUA'
    assert data['pontuacao_exploratoria'] is None
    assert data['validacao_cientifica'] is False
    assert data['etiquetador'] == {"modelo": "pt_core_news_sm", "versao": "fixture"}
    assert data['metodo_solicitado'] == 'contextual_v04'
    assert data['manifesto_fontes']['sentilex']['sha256'] == 'fixture-nao-cientifica'
    assert entradas == [{"alvo": "N0", "nlp": entradas[0]['nlp'],
                         "hipotese_modo": True, "incluir_diagnostico": False}]


def test_comparar_v04_preserva_delta_nulo(client, monkeypatch):
    def fake(f, m, indice, **kwargs):
        return {"metodo": "baseline_contextual_sentilex_v0.4_filtro_neutro_pos_hipotese_nao_validada",
                "feminina": {"status": "ABSTENCAO_ANEXACAO_AMBIGUA", "pontuacao_exploratoria": None},
                "masculina": {"status": "ABSTENCAO_ANEXACAO_AMBIGUA", "pontuacao_exploratoria": None},
                "ambas_pontuaveis": False,
                "delta_feminino_masculino_exploratorio": None,
                "evidencia_de_vies": None}

    monkeypatch.setattr(ui_server, '_obter_etiquetador', lambda: FakeNLP())
    monkeypatch.setattr(ui_server, 'comparar_v04', fake)
    resp = client.post('/api/ui/comparar', json=payload_compare())
    assert resp.status_code == 200
    data = resp.json()
    assert not data['ambas_pontuaveis']
    assert data['delta_feminino_masculino_exploratorio'] is None
    assert data['evidencia_de_vies'] is None
    assert not data['validacao_cientifica']


@pytest.mark.parametrize('campo,valor', [
    ('alvo', None), ('hipotese_modo', False), ('lexico', 'oplexicon')
])
def test_comparar_v04_rejeita_entrada_nao_autorizada(client, campo, valor):
    p = payload_compare()
    p[campo] = valor
    assert client.post('/api/ui/comparar', json=p).status_code == 422


def test_modelo_indisponivel_retorna_503_sem_dados_privados(client, monkeypatch):
    def indisponivel():
        raise HTTPException(status_code=503, detail='Modelo linguístico indisponível')
    monkeypatch.setattr(ui_server, '_obter_etiquetador', indisponivel)
    r = client.post('/api/ui/analisar', json=payload_single())
    assert r.status_code == 503
    assert 'Modelo' in r.json()['detail']


def test_html_tem_seletor_de_versao_e_hipotese(client):
    html = client.get('/').text
    for token in ['id="metodo"', 'value="contextual_v04"',
                  'id="hipotese-modo"', 'id="alvo"', 'id="method-tag"']:
        assert token in html


def test_javascript_renderiza_abstencoes_e_proveniencia(client):
    js = client.get('/static/app.js').text
    for token in ['function contextual(data)', 'ABSTENCAO_ANEXACAO_AMBIGUA',
                  'filtragem_neutros_pos', 'checagens_contextuais',
                  'function getOptions()', 'hipotese_modo']:
        assert token in js
    assert 'data/piloto/restrito' not in js


def test_interface_nao_envia_avaliacao_final_para_browser(client):
    paths = ['/api/ui/info', '/']
    for path in paths:
        resp = client.get(path)
        assert resp.status_code == 200
        assert 'pares_desenvolvimento_revisados_v02.csv' not in resp.text
        assert 'ficha_controles_R01_v01.csv' not in resp.text


def test_analisar_v04_com_algoritmo_real_e_etiquetador_sintetico(client, monkeypatch):
    from backend.tests.test_baseline_contextual_v04 import NLPV04
    from backend.tests.test_baseline_contextual_v03 import idx, lexema

    indice = idx(lexema('dados', 0, 'Adj'), lexema('segurança', 1, 'N'))
    monkeypatch.setattr(ui_server, '_obter_indice', lambda _: (indice, {'fixture': True}))
    monkeypatch.setattr(ui_server, '_obter_etiquetador',
                        lambda: NLPV04(anexacao={'segurança': ('nmod', 'dados')}))
    resp = client.post('/api/ui/analisar', json=payload_single())
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ABSTENCAO_ANEXACAO_AMBIGUA'
    assert data['pontuacao_exploratoria'] is None
    assert data['filtragem_neutros_pos']['aplicada'] is True
    assert [x['expressao'] for x in data['filtragem_neutros_pos']['descartados']] == ['dados']
    assert data['validacao_cientifica'] is False
