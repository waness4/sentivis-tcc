"""Diagnóstico de cobertura lexical de frases — etapa pré-classificatória.

IMPORTANTE: NÃO produz polaridade agregada, classificação de sentimento ou
métrica de viés. Reconhece apenas correspondências literais, sem análise sintática.
Preserva a proveniência e bloqueios definidos em lexicon_consulta.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from backend.lexicon_audit import EntradaLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta, consultar_entradas

# Palavras com acentos e compostos com hífen/apóstrofo; emoticons, hashtags e
# outros símbolos do OpLexicon NÃO são cobertos nesta etapa.
PALAVRA_RE = re.compile(r"[^\W\d_]+(?:[-’'][^\W\d_]+)*", re.UNICODE)
NEGADORES = frozenset({"não", "nem", "nunca", "jamais", "ninguém", "nenhum", "nenhuma", "nada"})
MAX_CARACTERES = 5000


def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFC", texto).casefold()


@dataclass(frozen=True)
class Token:
    texto: str
    inicio: int
    fim: int
    chave: str


def tokenizar(texto: str) -> list[Token]:
    return [Token(m.group(), m.start(), m.end(), normalizar(m.group()))
            for m in PALAVRA_RE.finditer(texto)]


class IndiceLexical:
    """Índice apenas de formas lexicais alfabetizáveis, preservando duplicatas.

    A correspondência é ORTOGRÁFICA, nunca desambiguação semântica ou PoS.
    """

    def __init__(self, entradas: Iterable[EntradaLexical], *, lexico: str):
        if lexico not in ("oplexicon", "sentilex"):
            raise ValueError("Léxico desconhecido")
        self.lexico = lexico
        self.indice: dict[tuple[str, ...], list[EntradaLexical]] = defaultdict(list)
        self.tamanhos: dict[str, set[int]] = defaultdict(set)
        self.entradas_ignoradas_formato = 0
        self.entradas_indexadas = 0
        for entrada in entradas:
            if (lexico == "oplexicon" and entrada.origem != "oplexicon") or (
                lexico == "sentilex" and entrada.origem not in {"sentilex_lem", "sentilex_flex"}
            ):
                continue
            # Emoticons e hashtags exigem tokenizer específico; "xd" poderia
            # parecer uma palavra comum, por isso a categoria também bloqueia.
            if lexico == "oplexicon" and entrada.categoria.strip().casefold() in {"emot", "htag"}:
                self.entradas_ignoradas_formato += 1
                continue
            partes = entrada.termo.split()
            # Exige equivalência à grafia, evitando falsos positivos como
            # 'erro:510', ':P', 'xD', hashtags ou pontuação interna arbitrária.
            if not partes or any(PALAVRA_RE.fullmatch(p) is None for p in partes):
                self.entradas_ignoradas_formato += 1
                continue
            chave = tuple(normalizar(p) for p in partes)
            self.indice[chave].append(entrada)
            self.tamanhos[chave[0]].add(len(chave))
            self.entradas_indexadas += 1

    def _proxima_correspondencia(self, texto: str, tokens: list[Token], i: int):
        possiveis = self.tamanhos.get(tokens[i].chave, ())
        for comprimento in sorted(possiveis, reverse=True):
            fim = i + comprimento
            if fim > len(tokens):
                continue
            # Não é permitido atravessar sinais de pontuação: "bom, humor"
            # NÃO corresponde à expressão lexical "bom humor".
            if any(not texto[tokens[j].fim:tokens[j + 1].inicio].isspace()
                   for j in range(i, fim - 1)):
                continue
            chave = tuple(tok.chave for tok in tokens[i:fim])
            if chave in self.indice:
                return fim, self.indice[chave]
        return None


def diagnosticar_frase(
    texto: str, indice: IndiceLexical, *, alvo: str | None = None
) -> dict:
    """Evidências de cobertura sem computar sentimento nem declarar viés."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Texto não pode estar vazio.")
    if len(texto) > MAX_CARACTERES:
        raise ValueError(f"Texto não pode ultrapassar {MAX_CARACTERES} caracteres.")
    if indice.lexico == "sentilex" and alvo not in (None, "N0", "N1"):
        raise ValueError("Para SentiLex, alvo deve ser N0 ou N1 ou omitido.")
    if indice.lexico == "oplexicon" and alvo is not None:
        raise ValueError("O OpLexicon não possui N0/N1; omita alvo.")

    tokens = tokenizar(texto)
    ocorrencias = []
    ausentes = []
    cobertos = 0
    i = 0
    while i < len(tokens):
        match = indice._proxima_correspondencia(texto, tokens, i)
        if match is None:
            token = tokens[i]
            ausentes.append({"termo": token.texto, "inicio": token.inicio, "fim": token.fim})
            i += 1
            continue
        fim, candidatas = match
        trecho = texto[tokens[i].inicio:tokens[fim - 1].fim]
        consulta = consultar_entradas(candidatas, trecho, lexico=indice.lexico, alvo=alvo)
        ocorrencias.append({
            "expressao": trecho,
            "inicio": tokens[i].inicio,
            "fim": tokens[fim - 1].fim,
            "quantidade_tokens": fim - i,
            "status": consulta["status"],
            "motivos": consulta.get("motivos", []),
            "fonte": consulta["fonte"],
            "polaridade_lexical_consultada": consulta.get("polaridade_consulta"),
            "candidatos": consulta["candidatos"],
        })
        cobertos += fim - i
        i = fim

    negadores = [t.texto for t in tokens if t.chave in NEGADORES]
    contexto = []
    if negadores:
        contexto.append("negacao_detectada_sem_interpretacao_de_escopo")
    if indice.lexico == "sentilex":
        contexto.append("alvo_lexical_nao_determinado_sintaticamente")
        if alvo is not None:
            contexto.append("alvo_informado_manualmente_sem_validacao_contextual")
    total = len(tokens)
    resumo = {
        "tokens_ortograficos": total,
        "tokens_com_correspondencia": cobertos,
        "tokens_sem_correspondencia": len(ausentes),
        "cobertura_superficial": round(cobertos / total, 6) if total else None,
        "ocorrencias_reconhecidas": len(ocorrencias),
        "ocorrencias_com_pendencia": sum(x["status"] != "candidata_lexical_consistente"
                                         for x in ocorrencias),
        "ocorrencias_candidatas_consistentes": sum(
            x["status"] == "candidata_lexical_consistente" for x in ocorrencias),
    }
    return {
        "status": "DIAGNOSTICO_ORTOGRAFICO_NAO_CLASSIFICACAO",
        "lexico": indice.lexico,
        "alvo_fornecido": alvo,
        "texto": texto,
        "resumo": resumo,
        "ocorrencias": ocorrencias,
        "ausentes": ausentes,
        "sinais_contextuais": contexto,
        "restricoes": [
            "Não há classificação ou pontuação agregada de sentimento.",
            "Correspondências ortográficas não garantem sentido, categoria gramatical ou alvo.",
            "Não há escopo de negação, ironia, intensificação ou análise sintática.",
            "Emoticons, hashtags e símbolos não alfabéticos não são reconhecidos nesta etapa.",
            "Cobertura superficial não é métrica de viés nem de acurácia.",
        ],
    }


def diagnosticar_par(
    feminina: str, masculina: str, indice: IndiceLexical, *, alvo: str | None = None
) -> dict:
    """Contrasta cobertura de duas frases, SEM verificar equivalência semântica."""
    f = diagnosticar_frase(feminina, indice, alvo=alvo)
    m = diagnosticar_frase(masculina, indice, alvo=alvo)
    return {
        "status": "COMPARACAO_DE_COBERTURA_NAO_VIES",
        "lexico": indice.lexico,
        "frase_feminina": f,
        "frase_masculina": m,
        "equivalencia_semantica_validada": False,
        "diferenca_polaridade": None,
        "diferenca_cobertura_superficial": (
            round(f["resumo"]["cobertura_superficial"] -
                  m["resumo"]["cobertura_superficial"], 6)
            if f["resumo"]["cobertura_superficial"] is not None and
            m["resumo"]["cobertura_superficial"] is not None else None
        ),
        "aviso": "Diferença de cobertura não demonstra viés de gênero.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnóstico de cobertura lexical; sem classificação")
    parser.add_argument("--lexico", choices=["oplexicon", "sentilex"], required=True)
    parser.add_argument("--texto")
    parser.add_argument("--feminina")
    parser.add_argument("--masculina")
    parser.add_argument("--alvo", choices=["N0", "N1"])
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--saida", type=Path, help="Salvar JSON UTF-8 opcionalmente")
    args = parser.parse_args()
    so_texto = args.texto is not None and args.feminina is None and args.masculina is None
    so_par = args.texto is None and args.feminina is not None and args.masculina is not None
    if not (so_texto or so_par):
        parser.error("Informe --texto OU --feminina e --masculina.")
    try:
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), args.lexico)
        indice = IndiceLexical(entradas, lexico=args.lexico)
        if so_texto:
            dados = diagnosticar_frase(args.texto, indice, alvo=args.alvo)
        else:
            dados = diagnosticar_par(args.feminina, args.masculina, indice, alvo=args.alvo)
        dados["manifesto_fontes"] = fontes
        dados["escopo_indexacao"] = {
            "entradas_indexadas": indice.entradas_indexadas,
            "entradas_nao_indexadas_por_formato": indice.entradas_ignoradas_formato,
            "regra": "Somente entradas com palavras alfabéticas e compostos com hífen/apóstrofo; frases separadas por espaços.",
        }
        saida = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            args.saida.write_text(saida, encoding="utf-8")
            print(f"Resultado salvo em: {args.saida}")
        else:
            print(saida, end="")
        print("AVISO: diagnóstico de cobertura apenas. NÃO constitui classificação científica ou demonstração de viés.")
    except (ValueError, FileNotFoundError, UnicodeError) as exc:
        parser.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
