"""Motor provisório de engenharia, NÃO VALIDADO para os experimentos do TCC.

Ainda não implementa alvos do SentiLex, negação ou expressões compostas.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def normalizar(termo: str) -> str:
    """Padroniza sem apagar acentos, importantes no português."""
    return unicodedata.normalize("NFC", termo.strip().casefold())


def ler_lexico(caminho: str | Path) -> dict[str, int]:
    """Aceita um CSV de engenharia previamente auditado: termo;polaridade."""
    resultado: dict[str, int] = {}
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        if not {"termo", "polaridade"}.issubset(leitor.fieldnames or []):
            raise ValueError("CSV deve possuir colunas 'termo' e 'polaridade'.")
        for num, linha in enumerate(leitor, start=2):
            termo = normalizar(linha["termo"])
            if not termo:
                raise ValueError(f"Termo vazio na linha {num}.")
            polaridade = int(linha["polaridade"])
            if polaridade not in (-1, 0, 1):
                raise ValueError(f"Polaridade inválida na linha {num}: {polaridade}.")
            if termo in resultado and resultado[termo] != polaridade:
                raise ValueError(f"Polaridades conflitantes para '{termo}' na linha {num}.")
            resultado[termo] = polaridade
    return resultado


def analisar(texto: str, lexico: dict[str, int]) -> dict:
    """Teste básico do pipeline; não interpretar como resultado de pesquisa."""
    tokens = TOKEN_RE.findall(normalizar(texto))
    encontrados = [{"termo": token, "polaridade": lexico[token]}
                   for token in tokens if token in lexico]
    ausentes = [token for token in tokens if token not in lexico]
    avisos = []
    if "não" in tokens or "nem" in tokens or "nunca" in tokens:
        avisos.append("Negação ainda não tratada: protótipo técnico.")
    if not encontrados:
        return {"classe": "sem_cobertura", "pontuacao": None,
                "encontrados": [], "ausentes": ausentes,
                "avisos": avisos + ["Não foi encontrada entrada lexical. Isso não significa neutralidade."]}
    pontuacao = sum(item["polaridade"] for item in encontrados)
    classe = "positiva" if pontuacao > 0 else "negativa" if pontuacao < 0 else "neutra"
    return {"classe": classe, "pontuacao": pontuacao,
            "encontrados": encontrados, "ausentes": ausentes, "avisos": avisos}


def comparar(frase_feminina: str, frase_masculina: str, lexico: dict[str, int]) -> dict:
    feminino = analisar(frase_feminina, lexico)
    masculino = analisar(frase_masculina, lexico)
    valores = (feminino["pontuacao"], masculino["pontuacao"])
    delta = (valores[0] - valores[1]) if None not in valores else None
    return {"feminino": feminino, "masculino": masculino,
            "delta_feminino_masculino": delta,
            "classificacao_divergente": (feminino["classe"] != masculino["classe"])
                if None not in valores else None,
            "status": "PROTOTIPO_NAO_VALIDADO"}
