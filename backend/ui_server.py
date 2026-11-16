"""Interface web do SentiVis — endpoints exclusivamente exploratórios.

Inicia a API original (backend.main.app) sem substituir os endpoints anteriores.
Nunca acessa os dados reservados de avaliação nem fichas dos revisores.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.main import app
from backend.baseline_experimental import (
    classificar_exploratoriamente,
    comparar_exploratoriamente,
)
from backend.baseline_contextual_v04 import classificar_v04, comparar_v04
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

FRONTEND = ROOT / "frontend"
LEXICOS = ("oplexicon", "sentilex")


class AnalisarEntrada(BaseModel):
    texto: str = Field(min_length=1, max_length=5000)
    lexico: Literal["oplexicon", "sentilex"]
    alvo: Literal["N0", "N1"] | None = None
    metodo: Literal["aditivo_v01", "contextual_v04"] = "aditivo_v01"
    hipotese_modo: bool = False


class CompararEntrada(BaseModel):
    feminina: str = Field(min_length=1, max_length=5000)
    masculina: str = Field(min_length=1, max_length=5000)
    lexico: Literal["oplexicon", "sentilex"]
    alvo: Literal["N0", "N1"] | None = None
    metodo: Literal["aditivo_v01", "contextual_v04"] = "aditivo_v01"
    hipotese_modo: bool = False


def _validar_entrada(
    lexico: str, alvo: str | None, *textos: str,
    metodo: str = "aditivo_v01", hipotese_modo: bool = False,
) -> None:
    if any(not txt.strip() for txt in textos):
        raise HTTPException(status_code=422, detail="A frase não pode estar em branco.")
    if lexico == "oplexicon" and alvo is not None:
        raise HTTPException(status_code=422, detail="OpLexicon não aceita N0/N1.")
    if metodo == "contextual_v04":
        if lexico != "sentilex":
            raise HTTPException(status_code=422, detail="V04 funciona somente com SentiLex.")
        if alvo is None:
            raise HTTPException(status_code=422, detail="V04 exige N0 ou N1 informado manualmente.")
        if not hipotese_modo:
            raise HTTPException(status_code=422, detail="V04 exige ativação explícita da hipótese de modo.")
    elif hipotese_modo:
        raise HTTPException(status_code=422, detail="Hipótese de modo só é permitida na V04.")


@lru_cache(maxsize=2)
def _carregar_indice(lexico: str) -> tuple[IndiceLexical, dict]:
    """Verificação de SHA-256 no carregamento; reinicie após mudar os arquivos."""
    entradas, manifesto = carregar_para_consulta(ROOT, lexico)
    return IndiceLexical(entradas, lexico=lexico), manifesto


@lru_cache(maxsize=1)
def _obter_etiquetador():
    """O modelo sintático é carregado somente quando a V04 é solicitada."""
    try:
        return carregar_etiquetador()
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Modelo linguístico pt_core_news_sm indisponível. Verifique a instalação.",
        ) from exc


def _obter_indice(lexico: str) -> tuple[IndiceLexical, dict]:
    try:
        return _carregar_indice(lexico)
    except (FileNotFoundError, ValueError, UnicodeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Léxico não disponível ou falha na verificação de integridade: {exc}",
        ) from exc


@app.get("/api/ui/info", tags=["Interface experimental"])
def info_interface():
    base = ROOT / "data" / "lexicos"
    orig = base / "originais"
    nomes = {"oplexicon": ("lexico_v3.0.txt",),
             "sentilex": ("SentiLex-flex-PT02.txt", "SentiLex-lem-PT02.txt")}
    arquivos_presentes = {
        nome: bool((base / "relatorio_curadoria.json").is_file()
                   and orig.is_dir()
                   and all(any(orig.rglob(arquivo)) for arquivo in lista))
        for nome, lista in nomes.items()
    }
    return {
        "app": "SentiVis", "fase": "interface_exploratoria_v0.1",
        "lexicos_arquivos_presentes": arquivos_presentes,
        "validacao_cientifica": False,
        "metodos": ["aditivo_v01", "contextual_v04"],
        "nota": "Presença dos arquivos não substitui a validação de integridade no momento da consulta.",
    }


@app.post("/api/ui/analisar", tags=["Interface experimental"])
def analisar_interface(pedido: AnalisarEntrada):
    _validar_entrada(
        pedido.lexico, pedido.alvo, pedido.texto,
        metodo=pedido.metodo, hipotese_modo=pedido.hipotese_modo,
    )
    indice, fontes = _obter_indice(pedido.lexico)
    if pedido.metodo == "contextual_v04":
        nlp = _obter_etiquetador()
        resposta = classificar_v04(
            pedido.texto, indice, alvo=pedido.alvo, nlp=nlp,
            hipotese_modo=pedido.hipotese_modo, incluir_diagnostico=False,
        )
        resposta["etiquetador"] = {
            "modelo": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada")
        }
    else:
        resposta = classificar_exploratoriamente(pedido.texto, indice, alvo=pedido.alvo)
    resposta["manifesto_fontes"] = fontes
    resposta["validacao_cientifica"] = False
    resposta["metodo_solicitado"] = pedido.metodo
    return resposta


@app.post("/api/ui/comparar", tags=["Interface experimental"])
def comparar_interface(pedido: CompararEntrada):
    _validar_entrada(
        pedido.lexico, pedido.alvo, pedido.feminina, pedido.masculina,
        metodo=pedido.metodo, hipotese_modo=pedido.hipotese_modo,
    )
    indice, fontes = _obter_indice(pedido.lexico)
    if pedido.metodo == "contextual_v04":
        nlp = _obter_etiquetador()
        resposta = comparar_v04(
            pedido.feminina, pedido.masculina, indice,
            alvo=pedido.alvo, nlp=nlp,
            hipotese_modo=pedido.hipotese_modo, incluir_diagnostico=False,
        )
        resposta["etiquetador"] = {
            "modelo": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada")
        }
    else:
        resposta = comparar_exploratoriamente(
            pedido.feminina, pedido.masculina, indice, alvo=pedido.alvo
        )
    resposta["manifesto_fontes"] = fontes
    resposta["validacao_cientifica"] = False
    resposta["metodo_solicitado"] = pedido.metodo
    return resposta


@app.get("/", include_in_schema=False)
def pagina_interface():
    caminho = FRONTEND / "index.html"
    if not caminho.is_file():
        raise HTTPException(status_code=503, detail="Instale a pasta frontend do Bloco 10.")
    return FileResponse(caminho)


if FRONTEND.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="sentivis-static")
