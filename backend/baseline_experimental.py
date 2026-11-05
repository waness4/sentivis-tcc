"""Baseline aditivo *exploratório* e rastreável para o SentiVis.

Não é classificador validado de sentimentos e não estima viés social.
Abstém-se em casos de ambiguidade lexical, alvo ausente ou pistas explícitas
que exigiriam interpretação de contexto ainda não implementada.

Por construção, o resultado decorre exclusivamente de correspondência
ortográfica de lexemas: não resolve PoS, sentido, referentes, ironia ou elipse.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.frase_diagnostico import (
    IndiceLexical, diagnosticar_frase, normalizar, tokenizar,
)
from backend.lexicon_consulta import ROOT, carregar_para_consulta

PROTOCOLO_ID = "baseline_aditivo_exploratorio_v0.1"
# O detector reconhece apenas os marcadores explicitamente enumerados.
# A falta de detecção NÃO significa ausência desses fenômenos no texto.
NEGADORES = frozenset({"não", "nem", "nunca", "jamais", "ninguém", "nenhum", "nenhuma", "nada"})
MODIFICADORES = frozenset({"muito", "muita", "muitos", "muitas", "pouco", "pouca", "poucos", "poucas", "bastante", "bastantes", "extremamente", "demais", "quase"})
STATUS_PONTUADO = "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
AVISOS = [
    "Somatório lexical aditivo provisório; NÃO é modelo validado de análise de sentimentos.",
    "Não há desambiguação sintática, semântica, de referente ou da categoria gramatical.",
    "Negações e alguns modificadores explícitos são bloqueados; ironia, comparações e outros fenômenos não são detectados.",
    "Ausência de uma palavra no léxico não equivale a polaridade neutra.",
    "Não é possível inferir viés de gênero com resultados deste módulo.",
]


def _classe(pontuacao: int) -> str:
    return "positiva" if pontuacao > 0 else "negativa" if pontuacao < 0 else "neutra"


def classificar_exploratoriamente(texto: str, indice: IndiceLexical, *, alvo: str | None = None,
                                  incluir_diagnostico: bool = False) -> dict:
    """Executa baseline conservador; abstenções retornam pontuação e classe nulas.

    Alvo N0/N1 informado pelo operador é hipótese de leitura, NÃO algo
    inferido da frase. Saídas com alvo manual têm marcador específico.
    """
    diagnostico = diagnosticar_frase(texto, indice, alvo=alvo)
    ocorrencias = diagnostico["ocorrencias"]
    marcadores = sorted({normalizar(t.texto) for t in tokenizar(texto)})
    negadores = sorted(NEGADORES.intersection(marcadores))
    modificadores = sorted(MODIFICADORES.intersection(marcadores))
    avisos = list(AVISOS)
    if indice.lexico == "sentilex" and alvo is not None:
        avisos.append(f"Alvo {alvo} selecionado manualmente: papel na frase não foi validado.")

    # A prioridade dos bloqueios é deliberada e pré-definida.
    if not ocorrencias:
        status, motivos = "SEM_COBERTURA", ["nenhuma_correspondencia_lexical"]
    elif indice.lexico == "sentilex" and alvo is None:
        status, motivos = "ABSTENCAO_ALVO", ["alvo_n0_n1_nao_definido"]
    elif any(o["status"] != "candidata_lexical_consistente" for o in ocorrencias):
        status = "ABSTENCAO_LEXICAL"
        motivos = sorted({motivo for o in ocorrencias for motivo in o.get("motivos", [])} or
                         {o["status"] for o in ocorrencias if o["status"] != "candidata_lexical_consistente"})
    elif negadores or modificadores:
        status, motivos = "ABSTENCAO_CONTEXTO", (
            (["negacao_sem_escopo"] if negadores else []) +
            (["modificador_sem_escopo"] if modificadores else [])
        )
    else:
        status, motivos = STATUS_PONTUADO, []

    pontuacao = None
    classe = None
    origem_zero = None
    termos_pontuados = []
    if status == STATUS_PONTUADO:
        for ocorrencia in ocorrencias:
            p = ocorrencia["polaridade_lexical_consultada"]
            # Falha fechada. Evita substituir ausências ou valores inválidos por zero.
            if type(p) is not int or p not in (-1, 0, 1):
                raise ValueError("Inconsistência interna: candidato não possui polaridade válida.")
            termos_pontuados.append({
                "expressao": ocorrencia["expressao"],
                "polaridade": p,
                "inicio": ocorrencia["inicio"],
                "fim": ocorrencia["fim"],
                "fonte": ocorrencia["fonte"],
            })
        pontuacao = sum(t["polaridade"] for t in termos_pontuados)
        classe = _classe(pontuacao)
        if pontuacao == 0:
            origem_zero = "apenas_neutros" if all(t["polaridade"] == 0 for t in termos_pontuados) else "cancelamento_de_polaridades"

    resposta = {
        "metodo": PROTOCOLO_ID,
        "status": status,
        "motivos": motivos,
        "lexico": indice.lexico,
        "alvo_informado_manualmente": alvo,
        "texto": texto,
        "pontuacao_exploratoria": pontuacao,
        "classe_exploratoria": classe,
        "origem_soma_zero": origem_zero,
        "termos_pontuados": termos_pontuados,
        "tokens_cobertos": diagnostico["resumo"]["tokens_com_correspondencia"],
        "tokens_totais": diagnostico["resumo"]["tokens_ortograficos"],
        "cobertura_superficial": diagnostico["resumo"]["cobertura_superficial"],
        "termos_sem_correspondencia": [a["termo"] for a in diagnostico["ausentes"]],
        "ocorrencias_com_pendencia": diagnostico["resumo"]["ocorrencias_com_pendencia"],
        "marcadores_de_negacao": negadores,
        "marcadores_de_modificacao": modificadores,
        "avisos": avisos,
    }
    if incluir_diagnostico:
        resposta["diagnostico_lexical"] = diagnostico
    return resposta


def comparar_exploratoriamente(feminina: str, masculina: str, indice: IndiceLexical,
                                *, alvo: str | None = None,
                                incluir_diagnostico: bool = False) -> dict:
    """Diferença descritiva sem inferir igualdade semântica, gênero ou viés."""
    f = classificar_exploratoriamente(feminina, indice, alvo=alvo,
                                     incluir_diagnostico=incluir_diagnostico)
    m = classificar_exploratoriamente(masculina, indice, alvo=alvo,
                                     incluir_diagnostico=incluir_diagnostico)
    ambas = f["status"] == m["status"] == STATUS_PONTUADO
    return {
        "metodo": PROTOCOLO_ID,
        "status": "COMPARACAO_EXPLORATORIA_NAO_VIES",
        "lexico": indice.lexico,
        "feminina": f,
        "masculina": m,
        "ambas_pontuaveis": ambas,
        "delta_feminino_masculino_exploratorio": (
            f["pontuacao_exploratoria"] - m["pontuacao_exploratoria"] if ambas else None
        ),
        "classes_diferentes_exploratorias": (
            f["classe_exploratoria"] != m["classe_exploratoria"] if ambas else None
        ),
        "equivalencia_semantica_validada": False,
        "evidencia_de_vies": None,
        "aviso": "O delta numérico, inclusive zero, NÃO confirma nem descarta viés de gênero.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline aditivo exploratório, NÃO validado cientificamente")
    parser.add_argument("--lexico", choices=("oplexicon", "sentilex"), required=True)
    parser.add_argument("--texto", help="Frase isolada")
    parser.add_argument("--feminina", help="Primeira frase do par")
    parser.add_argument("--masculina", help="Segunda frase do par")
    parser.add_argument("--alvo", choices=("N0", "N1"), help="Hipótese manual de alvo para o SentiLex")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--saida", type=Path, help="Salvar JSON completo UTF-8")
    parser.add_argument("--detalhado", action="store_true", help="Incluir diagnóstico com candidatos e proveniência")
    args = parser.parse_args()
    so_texto = args.texto is not None and args.feminina is None and args.masculina is None
    so_par = args.texto is None and args.feminina is not None and args.masculina is not None
    if not (so_texto or so_par):
        parser.error("Informe --texto OU --feminina e --masculina.")
    if args.lexico == "oplexicon" and args.alvo is not None:
        parser.error("O OpLexicon não possui alvos N0/N1; omita --alvo.")

    try:
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), args.lexico)
        indice = IndiceLexical(entradas, lexico=args.lexico)
        if so_texto:
            dados = classificar_exploratoriamente(args.texto, indice, alvo=args.alvo,
                                                 incluir_diagnostico=args.detalhado)
        else:
            dados = comparar_exploratoriamente(args.feminina, args.masculina, indice,
                                               alvo=args.alvo, incluir_diagnostico=args.detalhado)
        dados["manifesto_fontes"] = fontes
        dados["indexacao"] = {
            "entradas_indexadas": indice.entradas_indexadas,
            "entradas_nao_indexadas_por_formato": indice.entradas_ignoradas_formato,
        }
        saida = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            args.saida.write_text(saida, encoding="utf-8")
            print(f"Resultado salvo em: {args.saida}")
        else:
            print(saida, end="")
        print("AVISO: pontuação aditiva EXPLORATÓRIA, sem validação; NÃO comprova viés.")
    except (ValueError, FileNotFoundError, UnicodeError) as exc:
        parser.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
