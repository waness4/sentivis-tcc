"""API de prototipação; não relatar saídas como dados científicos."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core import ler_lexico, analisar, comparar

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "oplexicon": ROOT / "data" / "lexicos" / "oplexicon_3.csv",
    "sentilex": ROOT / "data" / "lexicos" / "sentilex_pt02.csv",
}
app = FastAPI(title="Sentivis — API técnica (protótipo)", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


class PedidoAnalise(BaseModel):
    frase: str = Field(min_length=1, max_length=5000)
    lexico: Literal["oplexicon", "sentilex"]


class PedidoComparacao(BaseModel):
    feminina: str = Field(min_length=1, max_length=5000)
    masculina: str = Field(min_length=1, max_length=5000)
    lexico: Literal["oplexicon", "sentilex"]


def carregar(nome: str) -> dict[str, int]:
    caminho = SOURCES[nome]
    if not caminho.exists():
        raise HTTPException(status_code=503, detail=f"Léxico '{nome}' ainda não foi importado e auditado.")
    try:
        return ler_lexico(caminho)
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Erro de validação do léxico: {exc}") from exc


@app.get("/api/health")
def health():
    return {"status": "ok", "fase": "bloco1_prototipo", "lexicos_disponiveis":
            {chave: caminho.is_file() for chave, caminho in SOURCES.items()}}


@app.post("/api/analisar")
def analise(pedido: PedidoAnalise):
    return {"status": "PROTOTIPO_NAO_VALIDADO", **analisar(pedido.frase, carregar(pedido.lexico))}


@app.post("/api/comparar")
def comparacao(pedido: PedidoComparacao):
    return comparar(pedido.feminina, pedido.masculina, carregar(pedido.lexico))
