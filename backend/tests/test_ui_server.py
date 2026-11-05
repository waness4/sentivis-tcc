"""Testes da interface HTTP, independentes de léxicos reais e partições reservadas."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_audit import EntradaLexical
from backend import ui_server

ORIGINAL_OBTER_INDICE = ui_server._obter_indice


@pytest.fixture
def client(monkeypatch):
    def registro(termo, polaridade, *, lexico="oplexicon", linha=1):
        sentilex = lexico == "sentilex"
        return EntradaLexical(
            origem="sentilex_flex" if sentilex else "oplexicon",
            arquivo="fixture.txt", linha=linha, termo=termo,
            lema=termo if sentilex else None,
            categoria="Adj" if sentilex else "adj",
            polaridades=(("N0" if sentilex else "GLOBAL", polaridade),),
            alvo="HUM:N0" if sentilex else None,
            flexao="fs" if sentilex else None, anotacao="MAN", revisao=None,
            atributos_originais=(), atributos_sem_chave=(),
        )
    def dados(lexico):
        if lexico == "oplexicon":
            items = [registro("dedicada", 1), registro("dedicado", 1), registro("fácil", 1, linha=10), registro("fácil", 0, linha=11)]
        else:
            items = [registro("alegre", 1, lexico="sentilex")]
        return IndiceLexical(items, lexico=lexico), {lexico: {"sha256": "fixture-nao-cientifica"}}
    monkeypatch.setattr(ui_server, "_obter_indice", dados)
    return TestClient(ui_server.app)


def test_pagina_inicial(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Sentimentos" in resp.text
    assert "não pode" in resp.text


def test_assets_css_e_js(client):
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")
    assert css.status_code == js.status_code == 200
    assert "--teal" in css.text
    assert "fetchJson" in js.text


def test_info_nao_contem_dados_reservados(client):
    dados = client.get("/api/ui/info").json()
    assert dados["validacao_cientifica"] is False
    assert "lexicos_arquivos_presentes" in dados
    assert "avaliacao" not in dados


def test_analisar_polaridade_exploratoria(client):
    r = client.post("/api/ui/analisar", json={"texto": "A aluna é dedicada.", "lexico": "oplexicon"})
    assert r.status_code == 200
    assert r.json()["pontuacao_exploratoria"] == 1
    assert r.json()["validacao_cientifica"] is False
    assert r.json()["manifesto_fontes"]["oplexicon"]["sha256"] == "fixture-nao-cientifica"


def test_analisar_abstencao_lexical(client):
    r = client.post("/api/ui/analisar", json={"texto": "A prova foi fácil.", "lexico": "oplexicon"})
    assert r.status_code == 200
    assert r.json()["status"] == "ABSTENCAO_LEXICAL"
    assert r.json()["pontuacao_exploratoria"] is None


def test_analisar_negacao_abstencao(client):
    r = client.post("/api/ui/analisar", json={"texto": "A aluna não é dedicada.", "lexico": "oplexicon"})
    assert r.status_code == 200
    assert r.json()["status"] == "ABSTENCAO_CONTEXTO"
    assert r.json()["pontuacao_exploratoria"] is None


def test_comparar_par_com_delta_zero_nao_e_vies(client):
    r = client.post("/api/ui/comparar", json={"lexico": "oplexicon", "feminina": "A aluna é dedicada.", "masculina": "O aluno é dedicado."})
    assert r.status_code == 200
    assert r.json()["delta_feminino_masculino_exploratorio"] == 0
    assert r.json()["evidencia_de_vies"] is None
    assert r.json()["equivalencia_semantica_validada"] is False


def test_sentilex_sem_alvo_abstem(client):
    r = client.post("/api/ui/analisar", json={"lexico": "sentilex", "texto": "A aluna é alegre."})
    assert r.status_code == 200
    assert r.json()["status"] == "ABSTENCAO_ALVO"


def test_sentilex_alvo_manual_explicito(client):
    r = client.post("/api/ui/analisar", json={"lexico": "sentilex", "texto": "A aluna é alegre.", "alvo": "N0"})
    assert r.status_code == 200
    assert r.json()["alvo_informado_manualmente"] == "N0"
    assert r.json()["pontuacao_exploratoria"] == 1


def test_oplexicon_bloqueia_alvo_indevido(client):
    r = client.post("/api/ui/analisar", json={"lexico": "oplexicon", "texto": "dedicada", "alvo": "N1"})
    assert r.status_code == 422


@pytest.mark.parametrize("texto", ["", "   ", "\t"])
def test_texto_vazio_bloqueado(client, texto):
    r = client.post("/api/ui/analisar", json={"lexico": "oplexicon", "texto": texto})
    assert r.status_code == 422


def test_limite_5000(client):
    r = client.post("/api/ui/analisar", json={"lexico": "oplexicon", "texto": "a" * 5001})
    assert r.status_code == 422


def test_modo_comparacao_exige_duas_frases(client):
    r = client.post("/api/ui/comparar", json={"lexico": "oplexicon", "feminina": "A aluna é dedicada.", "masculina": " "})
    assert r.status_code == 422


def test_falha_lexico_retorna_503(client, monkeypatch):
    def erro(_):
        raise FileNotFoundError("Léxico ausente")
    ui_server._carregar_indice.cache_clear()
    monkeypatch.setattr(ui_server, "_carregar_indice", erro)
    monkeypatch.setattr(ui_server, "_obter_indice", ORIGINAL_OBTER_INDICE)
    r = client.post("/api/ui/analisar", json={"lexico": "oplexicon", "texto": "dedicada"})
    assert r.status_code == 503
    assert "integridade" in r.json()["detail"]
