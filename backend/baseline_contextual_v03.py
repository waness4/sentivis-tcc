"""SentiVis V03 — hipótese contextual conservadora para SentiLex-PT02.

Esta etapa é EXPLORATÓRIA, não identifica semanticamente N0/N1 nem valida
referentes. Não modifica V01/V02 e não processa automaticamente o piloto.

Apenas em modo de HIPÓTESE explicitamente autorizado, seleciona UM sintagma
`com + substantivo` cujo substantivo recebe relação `obl` diretamente com um
verbo. A análise não distingue com segurança modo, instrumento ou companhia;
o operador deve interpretar o resultado como hipótese para investigação.

Qualquer anexação ambígua `nmod` com `com`, conflito lexical, PoS incerta,
negação/modificador bloqueado ou alvos ausentes leva à abstenção.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.baseline_experimental import (
    STATUS_PONTUADO,
    classificar_exploratoriamente,
)
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.frase_diagnostico import IndiceLexical, normalizar
from backend.lexicon_consulta import ROOT, carregar_para_consulta

PROTOCOLO_V03 = "baseline_contextual_sentilex_v0.3_hipotese_nao_validada"
STATUS_ABSTENCAO_SINTATICA = "ABSTENCAO_PAPEL_SINTATICO"
STATUS_ABSTENCAO_ANEXACAO = "ABSTENCAO_ANEXACAO_AMBIGUA"
STATUS_ABSTENCAO_POS = "ABSTENCAO_CATEGORIA_GRAMATICAL"
STATUS_ABSTENCAO_HIPOTESE = "ABSTENCAO_HIPOTESE_NAO_AUTORIZADA"

# Mapeamento conservador de categorias morfossintáticas do SentiLex.
CATEGORIAS_SENTILEX = {
    "n": "NOUN", "nom": "NOUN", "noun": "NOUN",
    "adj": "ADJ", "a": "ADJ", "adjetivo": "ADJ",
    "v": "VERB", "verb": "VERB", "verbo": "VERB",
    "adv": "ADV", "adverbio": "ADV",
}


def _token_correspondente(ocorrencia: dict, doc: Any) -> Any | None:
    """Aceita somente UMA palavra e offsets idênticos aos do diagnóstico."""
    inicio, fim = ocorrencia["inicio"], ocorrencia["fim"]
    sobrepostos = [t for t in doc if t.idx < fim and t.idx + len(t.text) > inicio]
    if len(sobrepostos) != 1:
        return None
    tok = sobrepostos[0]
    if tok.idx != inicio or tok.idx + len(tok.text) != fim:
        return None
    return tok


def _possui_com(tok: Any) -> bool:
    # spaCy representa tipicamente a preposição 'com' como filho `case`.
    return any(normalizar(c.text) == "com" and c.dep_ == "case" for c in tok.children)


def _analisar_ocorrencia(ocorrencia: dict, doc: Any) -> dict[str, Any]:
    """Anota sintaxe/PoS, sem atribuir significado ou referente."""
    t = _token_correspondente(ocorrencia, doc)
    categorias = sorted({str(x.get("categoria", "")).casefold().strip()
                         for x in ocorrencia.get("candidatos", [])})
    esperadas = sorted({CATEGORIAS_SENTILEX[c] for c in categorias
                        if c in CATEGORIAS_SENTILEX})
    saida = {
        "expressao": ocorrencia["expressao"],
        "inicio": ocorrencia["inicio"], "fim": ocorrencia["fim"],
        "polaridade_lexical": ocorrencia.get("polaridade_lexical_consultada"),
        "fonte": ocorrencia.get("fonte"),
        "categorias_lexico": categorias, "pos_esperadas": esperadas,
        "token": None, "pos": None, "dependencia": None, "cabeca": None,
        "preposicao_com": False, "papel_hipotetico": "indeterminado",
        "pos_compativel": False, "motivo": None,
    }
    if t is None:
        saida["motivo"] = "alinhamento_ou_expressao_composta_sem_suporte"
        return saida
    saida.update({
        "token": t.text, "pos": t.pos_, "dependencia": t.dep_,
        "cabeca": t.head.text if t.head is not None else None,
        "preposicao_com": _possui_com(t),
    })
    if not categorias or any(x not in CATEGORIAS_SENTILEX for x in categorias):
        saida["motivo"] = "categoria_lexical_nao_mapeada"
    elif len(esperadas) != 1:
        saida["motivo"] = "categorias_lexicais_multiplas"
    elif not t.pos_:
        saida["motivo"] = "pos_nao_determinada"
    elif t.pos_ != esperadas[0]:
        saida["motivo"] = "categoria_gramatical_incompativel"
    else:
        saida["pos_compativel"] = True
        # `obl` adjunto do verbo é pista sintática, NÃO prova de modo.
        if t.pos_ == "NOUN" and saida["preposicao_com"]:
            if t.dep_ == "obl" and t.head.pos_ == "VERB":
                saida["papel_hipotetico"] = "adjunto_com_ligado_ao_verbo"
            elif t.dep_ == "nmod":
                saida["papel_hipotetico"] = "anexacao_nominal_ambigua"
            else:
                saida["papel_hipotetico"] = "com_sem_vinculo_verbal_suportado"
        elif t.dep_ in ("obj", "iobj"):
            saida["papel_hipotetico"] = "argumento_objeto_nao_somado"
        else:
            saida["papel_hipotetico"] = "outra_ocorrencia_nao_somada"
    return saida


def _abster(resultado: dict, status: str, motivos: list[str]) -> dict:
    resultado["status"] = status
    resultado["motivos"] = sorted(set(motivos))
    resultado["pontuacao_exploratoria"] = None
    resultado["classe_exploratoria"] = None
    resultado["origem_soma_zero"] = None
    resultado["termos_pontuados"] = []
    return resultado


def classificar_v03(
    texto: str,
    indice: IndiceLexical,
    *,
    alvo: str | None = None,
    nlp: Any | None = None,
    hipotese_modo: bool = False,
    incluir_diagnostico: bool = False,
) -> dict[str, Any]:
    """V03 experimental para SentiLex; nunca infere N0/N1 automaticamente.

    `hipotese_modo=True` é consentimento explícito para computar uma *hipótese*
    do predicado preposicional. Sem isso, mesmo evidência sintática compatível
    não gera polaridade. Não usa rótulos de referência nem dados do piloto.
    """
    if indice.lexico != "sentilex":
        raise ValueError("V03 é restrito ao SentiLex; OpLexicon V01/V02 permanecem inalterados.")
    if alvo not in (None, "N0", "N1"):
        raise ValueError("Alvo deve ser N0, N1 ou omitido.")
    base = classificar_exploratoriamente(texto, indice, alvo=alvo, incluir_diagnostico=True)
    diagnostico = base.pop("diagnostico_lexical")
    base.update({
        "metodo": PROTOCOLO_V03,
        "baseline_referencia": "baseline_aditivo_exploratorio_v0.1",
        "alvo_resolvido_automaticamente": False,
        "papel_semantico_validado": False,
        "hipotese_modo_ativada": bool(hipotese_modo),
        "checagens_contextuais": [],
        "politica_contextual": "pista_estrutural_com_NOUN_obl_VERB_sem_resolucao_semantica",
        "evidencia_de_vies": None,
    })
    base["avisos"] = list(base["avisos"]) + [
        "V03: preposicao e dependencias sao pistas; nao distinguem modo, instrumento ou companhia.",
        "N0/N1 informado manualmente, sem validacao do referente na frase.",
        "Nao usar resultados do desenvolvimento como validacao de generalizacao ou vies.",
    ]

    if base["status"] == STATUS_PONTUADO:
        etiquetador = nlp if nlp is not None else carregar_etiquetador()
        doc = etiquetador(texto)
        checagens = [_analisar_ocorrencia(o, doc) for o in diagnostico["ocorrencias"]]
        base["checagens_contextuais"] = checagens
        motivos_pos = [x["motivo"] for x in checagens if not x["pos_compativel"]]
        ambiguas = [x for x in checagens if x["papel_hipotetico"] == "anexacao_nominal_ambigua"]
        candidatas = [x for x in checagens if x["papel_hipotetico"] == "adjunto_com_ligado_ao_verbo"]
        if motivos_pos:
            _abster(base, STATUS_ABSTENCAO_POS, motivos_pos)
        elif ambiguas:
            _abster(base, STATUS_ABSTENCAO_ANEXACAO, ["sintagma_com_ligado_a_nome"])
        elif len(candidatas) != 1:
            _abster(base, STATUS_ABSTENCAO_SINTATICA, [
                "sem_adjunto_com_unico_ligado_a_verbo" if not candidatas
                else "multiplos_adjuntos_com_avaliativos"
            ])
        elif not hipotese_modo:
            _abster(base, STATUS_ABSTENCAO_HIPOTESE, ["hipotese_modo_nao_ativada"])
        else:
            candidato = candidatas[0]
            pol = candidato["polaridade_lexical"]
            if type(pol) is not int or pol not in (-1, 0, 1):
                raise ValueError("Inconsistência: polaridade válida ausente na candidata.")
            base["pontuacao_exploratoria"] = pol
            base["classe_exploratoria"] = "positiva" if pol > 0 else "negativa" if pol < 0 else "neutra"
            base["origem_soma_zero"] = "polaridade_lexical_zero" if pol == 0 else None
            base["termos_pontuados"] = [{
                "expressao": candidato["expressao"], "polaridade": pol,
                "inicio": candidato["inicio"], "fim": candidato["fim"],
                "fonte": candidato["fonte"],
                "papel": "hipotese_de_adjunto_com_sem_validacao_semantica",
            }]
            base["motivos"] = []
            base["status"] = STATUS_PONTUADO
            base["avisos"].append("Pontuacao de UMA expressao selecionada por hipotese; demais ocorrencias nao somadas.")
    if incluir_diagnostico:
        base["diagnostico_lexical"] = diagnostico
    return base


def comparar_v03(
    feminina: str,
    masculina: str,
    indice: IndiceLexical,
    *, alvo: str | None = None, nlp: Any | None = None,
    hipotese_modo: bool = False, incluir_diagnostico: bool = False,
) -> dict[str, Any]:
    """Comparação descritiva sem verificar equivalência humana ou estimar viés."""
    # Sem alvo, não carrega modelo. Com alvo, o classificador carrega se necessário.
    if nlp is None and alvo is not None:
        nlp = carregar_etiquetador()
    f = classificar_v03(feminina, indice, alvo=alvo, nlp=nlp,
                       hipotese_modo=hipotese_modo, incluir_diagnostico=incluir_diagnostico)
    m = classificar_v03(masculina, indice, alvo=alvo, nlp=nlp,
                       hipotese_modo=hipotese_modo, incluir_diagnostico=incluir_diagnostico)
    ambas = f["status"] == m["status"] == STATUS_PONTUADO
    return {
        "metodo": PROTOCOLO_V03, "status": "COMPARACAO_EXPLORATORIA_NAO_VIES",
        "lexico": "sentilex", "feminina": f, "masculina": m,
        "ambas_pontuaveis": ambas,
        "delta_feminino_masculino_exploratorio": (
            f["pontuacao_exploratoria"] - m["pontuacao_exploratoria"] if ambas else None),
        "classes_diferentes_exploratorias": (
            f["classe_exploratoria"] != m["classe_exploratoria"] if ambas else None),
        "equivalencia_semantica_validada": False,
        "alvo_resolvido_automaticamente": False,
        "evidencia_de_vies": None,
        "aviso": "Somente hipotese experimental; delta zero nao prova ausencia de vies.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="SentiLex V03: hipotese sintatica experimental, sem validacao cientifica")
    p.add_argument("--texto", help="Frase isolada")
    p.add_argument("--feminina", help="Frase feminina para comparacao")
    p.add_argument("--masculina", help="Frase masculina para comparacao")
    p.add_argument("--alvo", choices=("N0", "N1"), help="Hipotese MANUAL; nunca inferida automaticamente")
    p.add_argument("--hipotese-modo", action="store_true", help="Ativar selecao exploratoria de sintagma com+NOUN")
    p.add_argument("--raiz", type=Path, default=ROOT)
    p.add_argument("--saida", type=Path)
    p.add_argument("--detalhado", action="store_true")
    args = p.parse_args()
    unitario = args.texto is not None and args.feminina is None and args.masculina is None
    par = args.texto is None and args.feminina is not None and args.masculina is not None
    if not (unitario or par):
        p.error("Informe --texto OU --feminina e --masculina.")
    if args.hipotese_modo and args.alvo is None:
        p.error("--hipotese-modo exige --alvo N0 ou N1 explicitamente.")
    try:
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "sentilex")
        indice = IndiceLexical(entradas, lexico="sentilex")
        nlp = carregar_etiquetador() if args.alvo is not None else None
        if unitario:
            dados = classificar_v03(args.texto, indice, alvo=args.alvo, nlp=nlp,
                                   hipotese_modo=args.hipotese_modo, incluir_diagnostico=args.detalhado)
        else:
            dados = comparar_v03(args.feminina, args.masculina, indice, alvo=args.alvo,
                                 nlp=nlp, hipotese_modo=args.hipotese_modo,
                                 incluir_diagnostico=args.detalhado)
        dados["manifesto_fontes"] = fontes
        dados["etiquetador"] = ({"modelo": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada")}
                               if nlp is not None else None)
        resultado = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            if args.saida.exists():
                raise FileExistsError("Arquivo de saída já existe; escolha novo nome para preservar histórico.")
            with args.saida.open("x", encoding="utf-8") as arq:
                arq.write(resultado)
            print(f"Resultado salvo em: {args.saida}")
        else:
            print(resultado, end="")
        print("AVISO: V03 é HIPÓTESE sintática, sem validação de alvo, sem inferência de viés.")
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError, UnicodeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
