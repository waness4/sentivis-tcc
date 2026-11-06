"""Comparação SentiLex V01 x V03 APENAS nos pares revisados de desenvolvimento.

Os resultados são hipóteses sintáticas/lexicais, não validação do modelo.
N0/N1 é fornecido manualmente e não é inferido a partir do texto.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.baseline_experimental import STATUS_PONTUADO, classificar_exploratoriamente
from backend.baseline_contextual_v03 import PROTOCOLO_V03, classificar_v03
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta
from backend.pares_piloto import ler_csv, status_revisao, validar_pares

METODO = "comparacao_sentilex_desenvolvimento_v01_v03_hipotese_v0.1"
COLUNAS = (
    "id_par", "familia", "sexo_frase", "rotulo_referencia", "alvo_manual",
    "status_v01", "classe_v01", "pontuacao_v01", "acerto_v01",
    "status_v03", "classe_v03", "pontuacao_v03", "acerto_v03",
    "motivos_v03", "termos_selecionados_v03", "transicao",
)


def _estatisticas(linhas: list[dict], versao: str) -> dict:
    validas = [l for l in linhas if l[f"status_{versao}"] == STATUS_PONTUADO]
    acertos = sum(l[f"acerto_{versao}"] is True for l in validas)
    return {
        "total_frases": len(linhas),
        "frases_pontuadas": len(validas),
        "frases_sem_pontuacao": len(linhas) - len(validas),
        "previsoes_corretas": acertos,
        "previsoes_incorretas": len(validas) - acertos,
        "cobertura_de_pontuacao": round(len(validas)/len(linhas), 6) if linhas else None,
        "acuracia_seletiva": round(acertos/len(validas), 6) if validas else None,
        "status": dict(sorted(Counter(l[f"status_{versao}"] for l in linhas).items())),
    }


def comparar_desenvolvimento_sentilex(
    pares: list[dict[str, str]], auditoria: dict, indice: IndiceLexical,
    *, nlp: Any, alvo: str, hipotese_modo: bool,
) -> tuple[dict, list[dict]]:
    if indice.lexico != "sentilex":
        raise ValueError("Comparação V03 disponível apenas para SentiLex.")
    if alvo not in ("N0", "N1"):
        raise ValueError("A comparação exige um alvo manual N0 ou N1.")
    if not hipotese_modo:
        raise ValueError("Ative explicitamente a hipótese sintática com --hipotese-modo.")
    if auditoria.get("erros") or auditoria.get("status") != "ESTRUTURA_VALIDADA_SEM_INFERENCIA_DE_VIES":
        raise ValueError("Dataset não validado estruturalmente.")
    selecionados = [p for p in pares if p["particao"] == "desenvolvimento" and
                   status_revisao(p) == "APROVADO_DUPLA_REVISAO"]
    if not selecionados:
        raise ValueError("Nenhum par de desenvolvimento aprovado.")
    linhas = []
    pares_completo = {"v01": 0, "v03": 0}
    mudancas = Counter()
    for p in selecionados:
        par_resultados = {"v01": {}, "v03": {}}
        for sexo, campo in (("feminina", "frase_feminina"), ("masculina", "frase_masculina")):
            texto = p[campo]
            v01 = classificar_exploratoriamente(texto, indice, alvo=alvo)
            v03 = classificar_v03(texto, indice, alvo=alvo, nlp=nlp, hipotese_modo=True)
            par_resultados["v01"][sexo], par_resultados["v03"][sexo] = v01, v03
            antes, depois = v01["status"] == STATUS_PONTUADO, v03["status"] == STATUS_PONTUADO
            transicao = ("pontuadas_ambas" if antes and depois else
                         "pontuada_para_abstencao" if antes else
                         "abstencao_para_pontuada" if depois else "abstencoes_ambas")
            mudancas[transicao] += 1
            linhas.append({
                "id_par": p["id_par"], "familia": p["familia"],
                "sexo_frase": sexo, "rotulo_referencia": p["rotulo_revisor1"],
                "alvo_manual": alvo,
                "status_v01": v01["status"], "classe_v01": v01["classe_exploratoria"],
                "pontuacao_v01": v01["pontuacao_exploratoria"],
                "acerto_v01": (v01["classe_exploratoria"] == p["rotulo_revisor1"]) if antes else None,
                "status_v03": v03["status"], "classe_v03": v03["classe_exploratoria"],
                "pontuacao_v03": v03["pontuacao_exploratoria"],
                "acerto_v03": (v03["classe_exploratoria"] == p["rotulo_revisor1"]) if depois else None,
                "motivos_v03": list(v03["motivos"]),
                "termos_selecionados_v03": [x["expressao"] for x in v03["termos_pontuados"]],
                "transicao": transicao,
            })
        for versao in ("v01", "v03"):
            if all(par_resultados[versao][s]["status"] == STATUS_PONTUADO
                   for s in ("feminina", "masculina")):
                pares_completo[versao] += 1
    return {
        "metodo": METODO, "fase": "DESENVOLVIMENTO_EXPLORATORIO_SEM_INFERENCIA",
        "sha256_dataset_revisado": auditoria["sha256_dataset"],
        "pares_aprovados_desenvolvimento": len(selecionados),
        "pares_avaliacao_classificados": 0,
        "alvo_manual_uniforme_nao_validado": alvo,
        "hipotese_modo_sintatica_ativada": True,
        "baseline_v01": "baseline_aditivo_exploratorio_v0.1",
        "baseline_v03": PROTOCOLO_V03,
        "estatisticas": {"v01": _estatisticas(linhas, "v01"),
                         "v03": _estatisticas(linhas, "v03")},
        "pares_com_ambas_pontuadas": pares_completo,
        "transicoes": dict(sorted(mudancas.items())),
        "evidencia_de_vies": None,
        "inferencia_estatistica": None,
        "limitacoes": [
            "Resultados exclusivamente descritivos dos pares de desenvolvimento.",
            "V01 com N0/N1 manual NÃO corresponde ao baseline original sem alvo.",
            "N0/N1 não foram ligados a referentes ou validados na frase.",
            "Heurística 'com + substantivo' pode indicar modo, instrumento ou companhia.",
            "V03 compara somente contextos selecionados; abstencao reduz a cobertura.",
            "As regras foram desenvolvidas observando o conjunto de desenvolvimento; não há generalização provada.",
            "O modelo estatistico spaCy pode errar em PoS e anexação sintática.",
            "A avaliação final permanece isolada, nenhum teste de vies foi executado.",
        ],
    }, linhas


def salvar(resumo: dict, linhas: list[dict], saida_json: Path, saida_csv: Path) -> None:
    if saida_json.resolve() == saida_csv.resolve():
        raise ValueError("JSON e CSV devem possuir nomes distintos.")
    if saida_json.exists() or saida_csv.exists():
        raise FileExistsError("Saída existente; use nomes novos para evitar sobrescrever resultados.")
    texto = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, delimiter=";", fieldnames=COLUNAS)
    writer.writeheader()
    for linha in linhas:
        writer.writerow({**linha,
                         "motivos_v03": "|".join(linha["motivos_v03"]),
                         "termos_selecionados_v03": "|".join(linha["termos_selecionados_v03"])})
    saida_json.parent.mkdir(parents=True, exist_ok=True)
    saida_csv.parent.mkdir(parents=True, exist_ok=True)
    with saida_json.open("x", encoding="utf-8") as arquivo:
        arquivo.write(texto)
    with saida_csv.open("x", encoding="utf-8-sig", newline="") as arquivo:
        arquivo.write(buf.getvalue())


def main() -> None:
    p = argparse.ArgumentParser(description="Comparar SentiLex V01 x V03 apenas no desenvolvimento")
    p.add_argument("--entrada", type=Path, required=True)
    p.add_argument("--saida-json", type=Path, required=True)
    p.add_argument("--saida-csv", type=Path, required=True)
    p.add_argument("--alvo", choices=("N0", "N1"), required=True,
                   help="Hipotese manual GLOBAL do experimento; NAO valida referentes")
    p.add_argument("--hipotese-modo", action="store_true", required=True)
    p.add_argument("--raiz", type=Path, default=ROOT)
    args = p.parse_args()
    try:
        todos, sha = ler_csv(args.entrada)
        auditoria = validar_pares(todos, sha256=sha)
        if auditoria["erros"]:
            raise ValueError("Dataset inválido: " + " | ".join(auditoria["erros"][:3]))
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "sentilex")
        indice = IndiceLexical(entradas, lexico="sentilex")
        nlp = carregar_etiquetador()
        resumo, linhas = comparar_desenvolvimento_sentilex(
            todos, auditoria, indice, nlp=nlp, alvo=args.alvo,
            hipotese_modo=args.hipotese_modo,
        )
        resumo["fontes_lexicais"] = fontes
        resumo["etiquetador"] = {"nome": "pt_core_news_sm", "versao": nlp.meta.get("version")}
        salvar(resumo, linhas, args.saida_json, args.saida_csv)
        a, b = resumo["estatisticas"]["v01"], resumo["estatisticas"]["v03"]
        print(f"Comparação SentiLex; {resumo['pares_aprovados_desenvolvimento']} pares de desenvolvimento.")
        print(f"V01 (alvo manual): {a['frases_pontuadas']} pontuadas; {a['previsoes_corretas']} corretas; {a['frases_sem_pontuacao']} sem pontuação.")
        print(f"V03 (hipótese sintática): {b['frases_pontuadas']} pontuadas; {b['previsoes_corretas']} corretas; {b['frases_sem_pontuacao']} sem pontuação.")
        print("AVISO: nenhum par de avaliação classificado e nenhuma conclusão de viés.")
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError, UnicodeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
