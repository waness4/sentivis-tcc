"""Bloco 20: comparação descritiva V03 × V04 em 36 controles fixados.

Não usa rótulos humanos, não acessa pares do piloto/avaliação e não mede
acurácia, F1 ou viés. N0/N1 é hipótese manual explicitamente informada.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from backend.baseline_contextual_v03 import PROTOCOLO_V03, classificar_v03
from backend.baseline_contextual_v04 import PROTOCOLO_V04, classificar_v04
from backend.baseline_experimental import STATUS_PONTUADO
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.controles_sintaticos_v03 import (
    ARQUIVO_CONTROLES, CABECALHO, CENARIOS, SHA256_CONTROLES, ler_controles,
)
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

METODO = "comparacao_diagnostica_controles_sentilex_v03_v04_v01"
COLUNAS = (
    "id_controle", "cenario", "texto", "alvo_manual",
    "status_v03", "classe_v03", "pontuacao_v03", "motivos_v03", "termos_v03",
    "status_v04", "classe_v04", "pontuacao_v04", "motivos_v04", "termos_v04",
    "filtro_neutro_aplicado", "neutros_descartados", "transicao", "status_alterado",
)


def _estatisticas(linhas: list[dict], versao: str) -> dict[str, Any]:
    total = len(linhas)
    pontuadas = sum(l[f"status_{versao}"] == STATUS_PONTUADO for l in linhas)
    return {
        "frases": total,
        "pontuadas": pontuadas,
        "sem_pontuacao": total - pontuadas,
        "taxa_pontuadas": round(pontuadas / total, 6) if total else None,
        "status": dict(sorted(Counter(l[f"status_{versao}"] for l in linhas).items())),
        "motivos": dict(sorted(Counter(m for l in linhas for m in l[f"motivos_{versao}"]).items())),
        "acuracia": None,
        "f1_macro": None,
    }


def _transicao(v03: dict, v04: dict) -> str:
    p3 = v03["status"] == STATUS_PONTUADO
    p4 = v04["status"] == STATUS_PONTUADO
    if p3 and p4:
        return "pontuadas_ambas_iguais" if (
            v03["classe_exploratoria"], v03["pontuacao_exploratoria"]
        ) == (
            v04["classe_exploratoria"], v04["pontuacao_exploratoria"]
        ) else "pontuadas_ambas_diferentes"
    if p3:
        return "pontuada_para_abstencao"
    if p4:
        return "abstencao_para_pontuada"
    return "abstencoes_com_status_diferente" if v03["status"] != v04["status"] else "abstencoes_com_mesmo_status"


def comparar_controles(
    controles: list[dict[str, str]], indice: IndiceLexical, *,
    nlp: Any, alvo: str, hipotese_modo: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Exige schema exclusivo de controles sem rótulos/partições.

    Em CLI, SHA-256 fixado é validado por `ler_controles` antes desta função.
    """
    if indice.lexico != "sentilex":
        raise ValueError("Comparação exclusiva para SentiLex.")
    if alvo not in ("N0", "N1"):
        raise ValueError("Alvo N0 ou N1 deve ser informado manualmente.")
    if hipotese_modo is not True:
        raise ValueError("Ative explicitamente a hipótese sintática.")
    if nlp is None or not callable(nlp):
        raise ValueError("Etiquetador não disponível.")
    if not controles:
        raise ValueError("Nenhum controle fornecido.")
    ids = set()
    for c in controles:
        if set(c) != set(CABECALHO) or c["cenario"] not in CENARIOS:
            raise ValueError("Somente controles sem rótulos ou partições são permitidos.")
        ident = c["id_controle"]
        if not isinstance(ident, str) or len(ident) != 4 or ident[0] != "C" or not ident[1:].isdigit():
            raise ValueError("ID de controle inválido.")
        if ident in ids or not isinstance(c["texto"], str) or not c["texto"].strip():
            raise ValueError("Controle duplicado ou frase vazia.")
        ids.add(ident)

    linhas = []
    for controle in controles:
        texto = controle["texto"]
        a = classificar_v03(texto, indice, alvo=alvo, nlp=nlp,
                            hipotese_modo=True, incluir_diagnostico=False)
        b = classificar_v04(texto, indice, alvo=alvo, nlp=nlp,
                            hipotese_modo=True, incluir_diagnostico=False)
        filtro = b["filtragem_neutros_pos"]
        if a.get("evidencia_de_vies") is not None or b.get("evidencia_de_vies") is not None:
            raise ValueError("Classificadores não devem produzir evidência de viés.")
        linhas.append({
            **controle, "alvo_manual": alvo,
            "status_v03": a["status"], "classe_v03": a["classe_exploratoria"],
            "pontuacao_v03": a["pontuacao_exploratoria"], "motivos_v03": list(a["motivos"]),
            "termos_v03": [t["expressao"] for t in a["termos_pontuados"]],
            "status_v04": b["status"], "classe_v04": b["classe_exploratoria"],
            "pontuacao_v04": b["pontuacao_exploratoria"], "motivos_v04": list(b["motivos"]),
            "termos_v04": [t["expressao"] for t in b["termos_pontuados"]],
            "filtro_neutro_aplicado": bool(filtro["aplicada"]),
            "neutros_descartados": [t["expressao"] for t in filtro["descartados"]],
            "transicao": _transicao(a, b), "status_alterado": a["status"] != b["status"],
        })

    por_cenario = defaultdict(list)
    for l in linhas:
        por_cenario[l["cenario"]].append(l)
    resumo = {
        "metodo": METODO,
        "fase": "CONTROLES_DIAGNOSTICOS_SEM_ROTULOS_NAO_VALIDACAO",
        "baseline_v03": PROTOCOLO_V03,
        "baseline_v04": PROTOCOLO_V04,
        "n_controles": len(linhas),
        "n_pares_avaliacao_processados": 0,
        "alvo_manual_nao_validado": alvo,
        "hipotese_sintatica_ativada": True,
        "metricas": {"v03": _estatisticas(linhas, "v03"), "v04": _estatisticas(linhas, "v04")},
        "por_cenario": {
            k: {"v03": _estatisticas(v, "v03"), "v04": _estatisticas(v, "v04")}
            for k, v in sorted(por_cenario.items())
        },
        "transicoes": dict(sorted(Counter(l["transicao"] for l in linhas).items())),
        "filtro_neutro": {
            "frases_com_filtro_aplicado": sum(l["filtro_neutro_aplicado"] for l in linhas),
            "ocorrencias_neutras_descartadas": sum(len(l["neutros_descartados"]) for l in linhas),
        },
        "frases_com_status_alterado": sum(l["status_alterado"] for l in linhas),
        "acuracia": None, "f1_macro": None, "evidencia_de_vies": None,
        "limites": [
            "Controles já inspecionados durante o desenvolvimento da V04: não são teste externo independente.",
            "Sem rótulos humanos independentes: acurácia e F1 não calculáveis.",
            "N0/N1 é seleção manual e não é resolução automática de referente.",
            "Heurística sintática não valida modo, instrumento, companhia ou anexação nominal.",
            "Nenhum par reservado de avaliação final é lido ou classificado.",
        ],
    }
    return resumo, linhas


def salvar(resumo: dict, linhas: list[dict], destino_json: Path, destino_csv: Path) -> None:
    if destino_json.resolve() == destino_csv.resolve():
        raise ValueError("Arquivos JSON e CSV devem ter caminhos distintos.")
    if destino_json.exists() or destino_csv.exists():
        raise FileExistsError("Relatório já existe. Não sobrescrever resultados anteriores.")
    if not linhas:
        raise ValueError("Nenhum resultado para salvar.")
    texto_json = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(buffer, fieldnames=COLUNAS, delimiter=";", lineterminator="\n")
    escritor.writeheader()
    for l in linhas:
        escritor.writerow({
            **l,
            "motivos_v03": "|".join(l["motivos_v03"]),
            "motivos_v04": "|".join(l["motivos_v04"]),
            "termos_v03": "|".join(l["termos_v03"]),
            "termos_v04": "|".join(l["termos_v04"]),
            "neutros_descartados": "|".join(l["neutros_descartados"]),
        })
    destino_json.parent.mkdir(parents=True, exist_ok=True)
    destino_csv.parent.mkdir(parents=True, exist_ok=True)
    with destino_json.open("x", encoding="utf-8") as f:
        f.write(texto_json)
    with destino_csv.open("x", encoding="utf-8-sig", newline="") as f:
        f.write(buffer.getvalue())


def main() -> None:
    p = argparse.ArgumentParser(description="SentiVis: comparar V03 x V04 em controles sintáticos sem rótulos")
    p.add_argument("--entrada", type=Path, default=ARQUIVO_CONTROLES)
    p.add_argument("--raiz", type=Path, default=ROOT)
    p.add_argument("--alvo", choices=("N0", "N1"), required=True)
    p.add_argument("--hipotese-modo", action="store_true", required=True)
    p.add_argument("--saida-json", type=Path, required=True)
    p.add_argument("--saida-csv", type=Path, required=True)
    args = p.parse_args()
    try:
        controles, sha = ler_controles(args.entrada, sha256_esperado=SHA256_CONTROLES)
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "sentilex")
        indice = IndiceLexical(entradas, lexico="sentilex")
        nlp = carregar_etiquetador()
        resumo, linhas = comparar_controles(controles, indice, nlp=nlp,
                                           alvo=args.alvo, hipotese_modo=True)
        resumo["sha256_controles"] = sha
        resumo["manifesto_lexical"] = fontes
        resumo["etiquetador"] = {
            "modelo": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada"),
        }
        salvar(resumo, linhas, args.saida_json, args.saida_csv)
        print(f"Controles: {len(linhas)} | V03 pontuadas: {resumo['metricas']['v03']['pontuadas']} "
              f"| V04 pontuadas: {resumo['metricas']['v04']['pontuadas']}")
        print(f"Filtro aplicado: {resumo['filtro_neutro']['frases_com_filtro_aplicado']} frases "
              f"| Status alterados: {resumo['frases_com_status_alterado']}")
        print(f"Relatórios: {args.saida_json} | {args.saida_csv}")
        print("AVISO: sem rótulos; sem acurácia, F1, avaliação final ou conclusão sobre viés.")
    except (ValueError, FileNotFoundError, FileExistsError, UnicodeError, OSError, RuntimeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
