"""Baseline exploratorio V02: filtro POS sobre os candidatos OpLexicon V01.

NUNCA decide sentidos, polaridade neutra, viés de gênero, nem alvos N0/N1.
Mantem o baseline V01 inalterado e falha fechado sem correspondencia POS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.baseline_experimental import STATUS_PONTUADO, classificar_exploratoriamente
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

PROTOCOLO_V02 = "baseline_aditivo_filtro_pos_v0.2_experimental"
STATUS_ABSTENCAO_POS = "ABSTENCAO_CATEGORIA_GRAMATICAL"
# Mapeamentos explicitamente suportados; desconhecidos levam a abstencao.
CATEGORIAS_OPLEXICON = {
    "adj": "ADJ", "adjetivo": "ADJ",
    "adv": "ADV", "adverbio": "ADV",
    "n": "NOUN", "nom": "NOUN", "noun": "NOUN", "subst": "NOUN", "sub": "NOUN", "s": "NOUN",
    "v": "VERB", "verb": "VERB", "verbo": "VERB",
}


def carregar_etiquetador():
    """Carrega modelo treinado; sem ele, e proibido simular etiquetas gramaticais."""
    try:
        import spacy  # dependencia opcional somente do baseline V02
    except ImportError as exc:
        raise RuntimeError(
            "spaCy nao instalado. Execute: python -m pip install 'spacy>=3.8.7,<3.9'"
        ) from exc
    try:
        nlp = spacy.load("pt_core_news_sm")
    except OSError as exc:
        raise RuntimeError(
            "Modelo pt_core_news_sm indisponivel. Execute: python -m spacy download pt_core_news_sm"
        ) from exc
    # Bloqueia blank('pt') e pipelines sem morfologizador funcional.
    if not nlp.has_pipe("morphologizer") and not nlp.has_pipe("tagger"):
        raise RuntimeError("Modelo carregado nao possui etiquetador gramatical treinado.")
    return nlp


def _avaliar_pos(ocorrencia: dict[str, Any], doc: Any) -> dict[str, Any]:
    inicio, fim = ocorrencia["inicio"], ocorrencia["fim"]
    tokens = [t for t in doc if t.idx < fim and t.idx + len(t.text) > inicio]
    categorias_raw = sorted({str(c.get("categoria", "")).strip().casefold()
                            for c in ocorrencia.get("candidatos", [])})
    pos_esperadas = sorted({CATEGORIAS_OPLEXICON[c] for c in categorias_raw
                           if c in CATEGORIAS_OPLEXICON})
    registro = {
        "expressao": ocorrencia["expressao"], "inicio": inicio, "fim": fim,
        "categorias_lexico": categorias_raw, "pos_esperadas": pos_esperadas,
        "tokens_spacy": [{"texto": t.text, "inicio": t.idx, "fim": t.idx + len(t.text),
                          "pos": t.pos_} for t in tokens],
        "compativel": False, "motivo": None,
    }
    # Apenas uma palavra com offsets identicos permite comparacao direta.
    if len(tokens) != 1 or tokens[0].idx != inicio or tokens[0].idx + len(tokens[0].text) != fim:
        registro["motivo"] = "alinhamento_ou_expressao_composta_sem_suporte"
    elif not categorias_raw or any(cat not in CATEGORIAS_OPLEXICON for cat in categorias_raw):
        registro["motivo"] = "categoria_lexical_nao_mapeada"
    elif len(pos_esperadas) != 1:
        registro["motivo"] = "categorias_lexicais_multiplas"
    elif not tokens[0].pos_:
        registro["motivo"] = "pos_nao_determinada"
    elif tokens[0].pos_ not in pos_esperadas:
        registro["motivo"] = "categoria_gramatical_incompativel"
    else:
        registro["compativel"] = True
    return registro


def classificar_v02(texto: str, indice: IndiceLexical, *, nlp: Any | None = None,
                     incluir_diagnostico: bool = False) -> dict[str, Any]:
    """Executa V01 e filtra pontuacoes por PoS, sem sobrescrever V01.

    `nlp` permite injetar um etiquetador em testes; na CLI carrega spaCy.
    """
    if indice.lexico != "oplexicon":
        raise ValueError("Filtro PoS V02 cobre somente OpLexicon; SentiLex/N0/N1 pendente.")

    resposta = classificar_exploratoriamente(texto, indice, incluir_diagnostico=True)
    diagnostico = resposta.pop("diagnostico_lexical")
    resposta["metodo"] = PROTOCOLO_V02
    resposta["baseline_referencia"] = "baseline_aditivo_exploratorio_v0.1"
    resposta["checagens_gramaticais"] = []
    resposta["validacao_gramatical"] = "nao_realizada_sem_pontuacao_v01"
    resposta["avisos"] = [
        "V01: filtro PoS nao aplicado. V02: somente compatibilidade gramatical estimada, sem desambiguacao semantica."
        if aviso == "Não há desambiguação sintática, semântica, de referente ou da categoria gramatical."
        else aviso for aviso in resposta["avisos"]
    ]
    resposta["avisos"].append(
        "PoS predita por modelo estatistico: sujeito a erro; compatibilidade nao valida sentido ou classe."
    )
    if resposta["status"] == STATUS_PONTUADO:
        etiquetador = nlp if nlp is not None else carregar_etiquetador()
        doc = etiquetador(texto)
        checagens = [_avaliar_pos(o, doc) for o in diagnostico["ocorrencias"]]
        resposta["checagens_gramaticais"] = checagens
        resposta["validacao_gramatical"] = (
            "compativel_pos_predita" if all(x["compativel"] for x in checagens)
            else "incompatibilidade_ou_indeterminacao"
        )
        if not all(x["compativel"] for x in checagens):
            resposta["status"] = STATUS_ABSTENCAO_POS
            resposta["motivos"] = sorted({x["motivo"] for x in checagens if x["motivo"]})
            resposta["pontuacao_exploratoria"] = None
            resposta["classe_exploratoria"] = None
            resposta["origem_soma_zero"] = None
            resposta["termos_pontuados"] = []
    if incluir_diagnostico:
        resposta["diagnostico_lexical"] = diagnostico
    resposta["evidencia_de_vies"] = None
    return resposta


def comparar_v02(feminina: str, masculina: str, indice: IndiceLexical, *,
                  nlp: Any | None = None, incluir_diagnostico: bool = False) -> dict[str, Any]:
    # Carrega uma vez o modelo se pelo menos uma das frases precisar; nao infere genero.
    if nlp is None:
        nlp = carregar_etiquetador()
    f = classificar_v02(feminina, indice, nlp=nlp, incluir_diagnostico=incluir_diagnostico)
    m = classificar_v02(masculina, indice, nlp=nlp, incluir_diagnostico=incluir_diagnostico)
    ambas = f["status"] == m["status"] == STATUS_PONTUADO
    return {
        "metodo": PROTOCOLO_V02, "status": "COMPARACAO_EXPLORATORIA_NAO_VIES",
        "lexico": indice.lexico, "feminina": f, "masculina": m,
        "ambas_pontuaveis": ambas,
        "delta_feminino_masculino_exploratorio": (
            f["pontuacao_exploratoria"] - m["pontuacao_exploratoria"] if ambas else None
        ),
        "classes_diferentes_exploratorias": (
            f["classe_exploratoria"] != m["classe_exploratoria"] if ambas else None
        ),
        "equivalencia_semantica_validada": False,
        "evidencia_de_vies": None,
        "aviso": "Sem inferencia ou validacao de vies; delta zero nao exclui vies.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Filtro PoS sobre OpLexicon V01; exploratorio")
    p.add_argument("--lexico", choices=("oplexicon",), default="oplexicon")
    p.add_argument("--texto")
    p.add_argument("--feminina")
    p.add_argument("--masculina")
    p.add_argument("--raiz", type=Path, default=ROOT)
    p.add_argument("--saida", type=Path)
    p.add_argument("--detalhado", action="store_true")
    args = p.parse_args()
    unitario = args.texto is not None and args.feminina is None and args.masculina is None
    par = args.texto is None and args.feminina is not None and args.masculina is not None
    if not (unitario or par):
        p.error("Informe --texto OU --feminina e --masculina.")
    try:
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "oplexicon")
        indice = IndiceLexical(entradas, lexico="oplexicon")
        nlp = carregar_etiquetador()
        if unitario:
            dados = classificar_v02(args.texto, indice, nlp=nlp, incluir_diagnostico=args.detalhado)
        else:
            dados = comparar_v02(args.feminina, args.masculina, indice,
                                 nlp=nlp, incluir_diagnostico=args.detalhado)
        dados["fontes_verificadas"] = fontes
        dados["etiquetador"] = {"modelo": "pt_core_news_sm",
                               "versao": nlp.meta.get("version", "nao_informada")}
        conteudo = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            args.saida.write_text(conteudo, encoding="utf-8")
            print(f"Resultado salvo em: {args.saida}")
        else:
            print(conteudo, end="")
        print("AVISO: baseline V02 experimental; nao comprova vies ou validacao cientifica.")
    except (ValueError, FileNotFoundError, RuntimeError, UnicodeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
