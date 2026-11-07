"""SentiVis V04: refinamento conservador do diagnóstico contextual SentiLex.

V04 não altera V03, não corrige anexação `nmod` e não resolve referentes N0/N1.
Somente permite descartar uma correspondência *neutra* de PoS incompatível
quando coexistem candidatos lexicalmente consistentes; a decisão final pode
continuar sendo abstenção. NÃO confundir a remoção de candidato com prova de
sentimento da frase.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.baseline_contextual_v03 import (
    STATUS_ABSTENCAO_ANEXACAO,
    STATUS_ABSTENCAO_POS,
    STATUS_ABSTENCAO_SINTATICA,
    STATUS_ABSTENCAO_HIPOTESE,
    _abster,
    classificar_v03,
)
from backend.baseline_experimental import STATUS_PONTUADO
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

PROTOCOLO_V04 = "baseline_contextual_sentilex_v0.4_filtro_neutro_pos_hipotese_nao_validada"


def classificar_v04(
    texto: str,
    indice: IndiceLexical,
    *,
    alvo: str | None = None,
    nlp: Any | None = None,
    hipotese_modo: bool = False,
    incluir_diagnostico: bool = False,
) -> dict[str, Any]:
    """Só reavalia bloqueios exclusivamente por PoS de lexemas neutros.

    Proteções: bases com conflitos lexicais, negação, alvo ausente, categoria
    não mapeada ou PoS desconhecida conservam os bloqueios da V03.
    Sem resolver ligação da expressão ou permitir modo explicitamente, abster.
    """
    resultado = classificar_v03(
        texto, indice, alvo=alvo, nlp=nlp,
        hipotese_modo=hipotese_modo, incluir_diagnostico=True,
    )
    resultado["metodo"] = PROTOCOLO_V04
    resultado["baseline_referencia"] = "baseline_contextual_sentilex_v0.3_hipotese_nao_validada"
    resultado["politica_contextual"] = (
        "V04: filtra apenas lexema neutro com PoS incompatível; "
        "hipotese de adjunto obl_VERB permanece nao validada"
    )
    resultado["filtragem_neutros_pos"] = {
        "politica": "descartar_apenas_polaridade_zero_com_pos_incompativel",
        "aplicada": False,
        "descartados": [],
        "aviso": "PoS estimada e falivel; descartar uma entrada nao valida a interpretacao restante.",
    }
    resultado["avisos"] = list(resultado["avisos"]) + [
        "V04: descarta somente entradas lexicais neutras de PoS comprovadamente incompatível na predição.",
        "Anexações nmod, papéis semânticos e alvo N0/N1 continuam não resolvidos.",
    ]

    # Não transformar erros distintos de PoS em pontuação.
    if resultado["status"] == STATUS_ABSTENCAO_POS:
        checagens = resultado["checagens_contextuais"]
        descartar = [x for x in checagens if x["motivo"] == "categoria_gramatical_incompativel"
                     and type(x["polaridade_lexical"]) is int and x["polaridade_lexical"] == 0]
        bloqueios = [x for x in checagens if x["motivo"] is not None and x not in descartar]
        validos = [x for x in checagens if x["pos_compativel"] and x["motivo"] is None]
        # Exige ao menos uma ocorrência válida; erros não neutros/desconhecidos bloqueiam.
        if descartar and validos and not bloqueios:
            resultado["filtragem_neutros_pos"]["aplicada"] = True
            resultado["filtragem_neutros_pos"]["descartados"] = [
                {"expressao": x["expressao"], "inicio": x["inicio"], "fim": x["fim"],
                 "polaridade_lexical": 0, "categoria_lexico": x["categorias_lexico"],
                 "pos_observada": x["pos"], "motivo": x["motivo"]} for x in descartar
            ]
            ambiguos = [x for x in validos if x["papel_hipotetico"] == "anexacao_nominal_ambigua"]
            candidatos = [x for x in validos if x["papel_hipotetico"] == "adjunto_com_ligado_ao_verbo"]
            if ambiguos:
                _abster(resultado, STATUS_ABSTENCAO_ANEXACAO, ["sintagma_com_ligado_a_nome"])
            elif len(candidatos) != 1:
                _abster(resultado, STATUS_ABSTENCAO_SINTATICA, [
                    "sem_adjunto_com_unico_ligado_a_verbo" if not candidatos
                    else "multiplos_adjuntos_com_avaliativos"
                ])
            elif not hipotese_modo:
                _abster(resultado, STATUS_ABSTENCAO_HIPOTESE, ["hipotese_modo_nao_ativada"])
            else:
                candidato = candidatos[0]
                pol = candidato["polaridade_lexical"]
                if type(pol) is not int or pol not in (-1, 0, 1):
                    raise ValueError("Inconsistência: candidato válido sem polaridade adequada")
                resultado.update({
                    "status": STATUS_PONTUADO, "motivos": [],
                    "pontuacao_exploratoria": pol,
                    "classe_exploratoria": "positiva" if pol > 0 else "negativa" if pol < 0 else "neutra",
                    "origem_soma_zero": "polaridade_lexical_zero" if pol == 0 else None,
                    "termos_pontuados": [{
                        "expressao": candidato["expressao"], "polaridade": pol,
                        "inicio": candidato["inicio"], "fim": candidato["fim"],
                        "fonte": candidato["fonte"],
                        "papel": "hipotese_de_adjunto_com_sem_validacao_semantica",
                    }],
                })
                resultado["avisos"].append(
                    "Uma hipotese de adjunto foi pontuada apos filtrar uma entrada neutra de PoS incompatível.")
    if not incluir_diagnostico:
        resultado.pop("diagnostico_lexical", None)
    return resultado


def comparar_v04(
    feminina: str, masculina: str, indice: IndiceLexical, *,
    alvo: str | None = None, nlp: Any | None = None,
    hipotese_modo: bool = False, incluir_diagnostico: bool = False,
) -> dict[str, Any]:
    if nlp is None and alvo is not None:
        nlp = carregar_etiquetador()
    f = classificar_v04(feminina, indice, alvo=alvo, nlp=nlp,
                       hipotese_modo=hipotese_modo, incluir_diagnostico=incluir_diagnostico)
    m = classificar_v04(masculina, indice, alvo=alvo, nlp=nlp,
                       hipotese_modo=hipotese_modo, incluir_diagnostico=incluir_diagnostico)
    ambos = f["status"] == m["status"] == STATUS_PONTUADO
    return {
        "metodo": PROTOCOLO_V04, "status": "COMPARACAO_EXPLORATORIA_NAO_VIES",
        "lexico": "sentilex", "feminina": f, "masculina": m,
        "ambas_pontuaveis": ambos,
        "delta_feminino_masculino_exploratorio": (
            f["pontuacao_exploratoria"] - m["pontuacao_exploratoria"] if ambos else None),
        "classes_diferentes_exploratorias": (
            f["classe_exploratoria"] != m["classe_exploratoria"] if ambos else None),
        "equivalencia_semantica_validada": False, "alvo_resolvido_automaticamente": False,
        "evidencia_de_vies": None,
        "aviso": "V04 é hipótese; delta numérico não evidencia nem exclui viés.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="SentiVis V04: filtro PoS neutro, hipótese não validada")
    p.add_argument("--texto")
    p.add_argument("--feminina")
    p.add_argument("--masculina")
    p.add_argument("--alvo", choices=("N0", "N1"))
    p.add_argument("--hipotese-modo", action="store_true")
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
        dados = (classificar_v04(args.texto, indice, alvo=args.alvo, nlp=nlp,
                                hipotese_modo=args.hipotese_modo, incluir_diagnostico=args.detalhado)
                 if unitario else
                 comparar_v04(args.feminina, args.masculina, indice, alvo=args.alvo, nlp=nlp,
                              hipotese_modo=args.hipotese_modo, incluir_diagnostico=args.detalhado))
        dados["manifesto_fontes"] = fontes
        dados["etiquetador"] = (
            {"modelo": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada")}
            if nlp is not None else None)
        saida = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
        if args.saida:
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            if args.saida.exists():
                raise FileExistsError("Arquivo de saída já existe; escolha nome novo.")
            with args.saida.open("x", encoding="utf-8") as arq:
                arq.write(saida)
            print(f"Resultado salvo em: {args.saida}")
        else:
            print(saida, end="")
        print("AVISO: V04 é hipótese exploratória; sem validação de alvo, sem inferência sobre viés.")
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError, UnicodeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
