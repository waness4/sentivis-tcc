"""Comparação pós-coleta DESCRITIVA: uma marcação humana e baselines em 36 controles.

Os sete rótulos `neutro` não se convertem automaticamente em `neutra` ou
`sem_avaliacao`. A análise de coincidências considera apenas positivo/negativo,
sempre com denominadores explícitos, abstenções e sensibilidade sem C001.
Não acessa a partição de avaliação final nem mede desempenho independente.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from scripts.auditar_r01_bloco27 import descrever, ler_controles, ler_ficha, salvar

STATUS_PONTUADO = "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
ROTULOS_BIVALENTES = {"positivo": "positiva", "negativo": "negativa",
                     "positiva": "positiva", "negativa": "negativa"}


def ler_predicoes(path: Path, expected_ids: set[str], colunas: tuple[str, ...], textos: dict[str, str]):
    reader = csv.DictReader(io.StringIO(path.read_bytes().decode("utf-8-sig"), newline=""), delimiter=";")
    if not reader.fieldnames or any(k not in reader.fieldnames for k in ("id_controle", "texto", *colunas)):
        raise ValueError(f"CSV de resultados sem cabeçalho necessário: {path}")
    rows = list(reader)
    if len(rows) != len(expected_ids) or any(None in x or any(v is None for v in x.values()) for x in rows):
        raise ValueError(f"CSV de resultados incompleto ou malformado: {path}")
    by_id = {x["id_controle"]: x for x in rows}
    if set(by_id) != expected_ids:
        raise ValueError(f"IDs divergentes no relatório de resultados: {path}")
    if any(by_id[i]["texto"] != textos[i] for i in expected_ids):
        raise ValueError(f"Textos divergentes no relatório de resultados: {path}")
    return by_id


def medir(revisor: dict[str, dict], predicoes: dict[str, dict], versao: str, excluir: set[str]):
    ids = sorted(set(revisor) - excluir)
    bivalentes = [i for i in ids if revisor[i]["polaridade"].strip().lower() in ROTULOS_BIVALENTES]
    pontuadas = [i for i in ids if predicoes[i][f"status_{versao}"] == STATUS_PONTUADO]
    elegiveis = [i for i in pontuadas if i in bivalentes]
    concordantes = [i for i in elegiveis if predicoes[i][f"classe_{versao}"] ==
                    ROTULOS_BIVALENTES[revisor[i]["polaridade"].strip().lower()]]
    if any(not predicoes[i][f"classe_{versao}"] for i in pontuadas):
        raise ValueError("Modelo pontuado sem classe prevista.")
    return {
        "frases_no_recorte": len(ids),
        "marcacoes_positivas_negativas_elegiveis": len(bivalentes),
        "marcacoes_nao_bivalentes_sem_conversao": len(ids) - len(bivalentes),
        "modelo_pontuou_no_recorte": len(pontuadas),
        "modelo_absteve_no_recorte": len(ids) - len(pontuadas),
        "modelo_pontuou_nas_marcacoes_bivalentes": len(elegiveis),
        "modelo_absteve_nas_marcacoes_bivalentes": len(bivalentes) - len(elegiveis),
        "coincidencias_nas_pontuadas_bivalentes": len(concordantes),
        "divergencias_nas_pontuadas_bivalentes": len(elegiveis) - len(concordantes),
        "fracao_descritiva_coincidencia_condicional": round(len(concordantes) / len(elegiveis), 6) if elegiveis else None,
        "observacao": "Coincidência pós-coleta com R01; NÃO é acurácia, F1 ou referência consensual.",
    }


def comparar(revisao: list[dict], anterior: dict, atual: dict) -> dict:
    rmap = {r["id_controle"]: r for r in revisao}
    # Verifica alinhamento descritivo entre os relatórios da mesma V03.
    if any(anterior[i]["status_v03"] != atual[i]["status_v03"] or
           anterior[i]["classe_v03"] != atual[i]["classe_v03"] for i in rmap):
        raise ValueError("Relatórios discordam sobre V03: não misturar execuções.")
    return {
        "fase": "COMPARACAO_DESCRITIVA_POS_COLETA_UMA_PESSOA_SEM_INFERENCIA",
        "avaliadores": 1,
        "avaliacao_final_processada": False,
        "concordancia_interavaliadores": None,
        "acuracia": None,
        "f1_macro": None,
        "evidencia_de_vies": None,
        "regras": ["Apenas positivo/negativo entram no recorte bivalente.",
                   "Neutro informado pela pessoa não é convertido automaticamente.",
                   "Abstenções não contam como acertos nem erros.",
                   "C001 é excluído no recorte de sensibilidade por possível exposição prévia."],
        "analise_total": {
            "v01": medir(rmap, anterior, "v01", set()),
            "v03": medir(rmap, anterior, "v03", set()),
            "v04": medir(rmap, atual, "v04", set()),
        },
        "sensibilidade_sem_C001": {
            "v01": medir(rmap, anterior, "v01", {"C001"}),
            "v03": medir(rmap, anterior, "v03", {"C001"}),
            "v04": medir(rmap, atual, "v04", {"C001"}),
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Bloco 27: comparação DESCRITIVA R01 x V01/V03/V04.")
    pasta = Path("data/piloto/restrito")
    p.add_argument("--ficha", type=Path, default=pasta / "ficha_controles_R01_recebida.csv")
    p.add_argument("--controles", type=Path, default=Path("data/controles/controles_sintaticos_v01.csv"))
    p.add_argument("--v01-v03", type=Path, default=pasta / "controles_sintaticos_v03_resultado.csv")
    p.add_argument("--v03-v04", type=Path, default=pasta / "comparacao_controles_v03_v04.csv")
    p.add_argument("--saida", type=Path, default=pasta / "comparacao_descritiva_r01_bloco27.json")
    args = p.parse_args()
    try:
        cmap, hc = ler_controles(args.controles)
        ficha, hf, sep = ler_ficha(args.ficha)
        aud = descrever(cmap, ficha, sha_controles=hc, sha_ficha=hf, separador=sep)
        nomes = set(cmap)
        orig = ler_predicoes(args.v01_v03, nomes,
                            ("status_v01", "classe_v01", "status_v03", "classe_v03"), cmap)
        nova = ler_predicoes(args.v03_v04, nomes,
                            ("status_v03", "classe_v03", "status_v04", "classe_v04"), cmap)
        rel = comparar(ficha, orig, nova)
        rel["sha256_controles"] = hc
        rel["sha256_ficha"] = hf
        rel["integridade_ficha"] = {"ids": aud["n_controles"],
                                     "texto_apenas_espacamento": aud["id_texto_espacamento_divergente"]}
        salvar(rel, args.saida)
        for nome, dados in rel["analise_total"].items():
            print(f"{nome.upper()}: {dados['modelo_pontuou_no_recorte']} pontuadas de 36; "
                  f"nas {dados['marcacoes_positivas_negativas_elegiveis']} marcações bivalentes, "
                  f"{dados['modelo_pontuou_nas_marcacoes_bivalentes']} pontuadas, "
                  f"{dados['coincidencias_nas_pontuadas_bivalentes']} coincidências.")
        print("Saída privada:", args.saida)
        print("AVISO: isso NÃO é acurácia validada; dados reservados não foram usados.")
    except (ValueError, FileNotFoundError, UnicodeError, OSError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
