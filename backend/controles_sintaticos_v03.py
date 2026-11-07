"""Bloco 18: diagnóstico de robustez V01/V03 em controles sintéticos pré-fixados.

Não calcula acurácia/F1 nem utiliza pares do piloto. Os controles não possuem
rótulo humano e N0 é informado manualmente. Não representa validação externa.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from backend.baseline_contextual_v03 import PROTOCOLO_V03, classificar_v03
from backend.baseline_experimental import STATUS_PONTUADO, classificar_exploratoriamente
from backend.baseline_gramatical_v02 import carregar_etiquetador
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

METODO = "diagnostico_controles_sintaticos_v03_sem_rotulos_v01"
ARQUIVO_CONTROLES = Path("data/controles/controles_sintaticos_v01.csv")
SHA256_CONTROLES = "a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc"
CABECALHO = ("id_controle", "cenario", "texto")
CENARIOS = frozenset({
    "modo_potencial", "objeto_e_adjunto", "avaliacao_sem_com",
    "companhia_instrumento", "negacao_modificacao", "construcoes_complexas",
})
COLUNAS = (
    "id_controle", "cenario", "texto", "alvo_manual",
    "status_v01", "classe_v01", "pontuacao_v01", "termos_v01",
    "status_v03", "classe_v03", "pontuacao_v03", "motivos_v03",
    "termos_v03", "transicao",
)


def ler_controles(arquivo: Path, *, sha256_esperado: str = SHA256_CONTROLES) -> tuple[list[dict[str, str]], str]:
    """Apenas o arquivo fixado pelo protocolo: falha fechada para entradas diferentes.

    O schema de três colunas é propositalmente incompatível com os CSVs do
    piloto (que contêm partição e rótulos), impedindo ingestão acidental.
    """
    dados = arquivo.read_bytes()
    sha = hashlib.sha256(dados).hexdigest()
    if sha != sha256_esperado:
        raise ValueError("Controles diferentes do conjunto fixado (SHA-256 divergente).")
    try:
        conteudo = dados.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("Arquivo de controles deve estar em UTF-8.") from exc
    reader = csv.DictReader(io.StringIO(conteudo, newline=""), delimiter=";")
    if reader.fieldnames != list(CABECALHO):
        raise ValueError("Schema de controles inválido: somente id_controle;cenario;texto.")
    controles = []
    ids, frases = set(), set()
    for n, linha in enumerate(reader, 2):
        if None in linha or any(v is None for v in linha.values()):
            raise ValueError(f"Linha {n}: quantidade de campos incorreta.")
        ident, cenario, frase = (linha[c] for c in CABECALHO)
        if not re.fullmatch(r"C\d{3}", ident):
            raise ValueError(f"Linha {n}: ID inválido.")
        if ident in ids:
            raise ValueError(f"Linha {n}: ID de controle repetido.")
        if cenario not in CENARIOS:
            raise ValueError(f"Linha {n}: cenário não reconhecido.")
        if not (12 <= len(frase) <= 240) or "\n" in frase or "\r" in frase:
            raise ValueError(f"Linha {n}: frase ausente, grande ou multilinha.")
        if frase.casefold() in frases:
            raise ValueError(f"Linha {n}: frase duplicada.")
        ids.add(ident)
        frases.add(frase.casefold())
        controles.append(dict(linha))
    if not controles:
        raise ValueError("Arquivo de controles vazio.")
    return controles, sha


def _numeros(linhas: list[dict], versao: str) -> dict:
    n = len(linhas)
    pontuadas = sum(l[f"status_{versao}"] == STATUS_PONTUADO for l in linhas)
    return {
        "n_frases": n,
        "pontuadas": pontuadas,
        "sem_pontuacao": n-pontuadas,
        "taxa_pontuadas": round(pontuadas / n, 6) if n else None,
        "status": dict(sorted(Counter(l[f"status_{versao}"] for l in linhas).items())),
        # Não existem rótulos humanos para este conjunto.
        "acuracia": None,
        "f1_macro": None,
    }


def analisar_controles(
    controles: list[dict[str, str]], indice: IndiceLexical, *, nlp: Any,
    alvo: str, hipotese_modo: bool,
) -> tuple[dict, list[dict]]:
    if indice.lexico != "sentilex":
        raise ValueError("Diagnóstico restrito ao SentiLex.")
    if alvo not in ("N0", "N1"):
        raise ValueError("Alvo manual N0 ou N1 obrigatório.")
    if hipotese_modo is not True:
        raise ValueError("Ative explicitamente --hipotese-modo.")
    if not controles:
        raise ValueError("Não há controles para analisar.")
    # Mesmo quando invocado via API, não aceita o formato de pares do piloto.
    for c in controles:
        if set(c) != set(CABECALHO):
            raise ValueError("Somente controles sem rótulo ou partição podem ser analisados.")
        if c["cenario"] not in CENARIOS or not re.fullmatch(r"C\d{3}", c["id_controle"]):
            raise ValueError("Controle inválido.")
    linhas: list[dict] = []
    for controle in controles:
        frase = controle["texto"]
        a = classificar_exploratoriamente(frase, indice, alvo=alvo)
        b = classificar_v03(frase, indice, nlp=nlp, alvo=alvo, hipotese_modo=True)
        antes, depois = a["status"] == STATUS_PONTUADO, b["status"] == STATUS_PONTUADO
        transicao = ("pontuadas_ambas" if antes and depois else
                     "pontuada_para_abstencao" if antes else
                     "abstencao_para_pontuada" if depois else "abstencoes_ambas")
        linhas.append({
            **controle, "alvo_manual": alvo,
            "status_v01": a["status"], "classe_v01": a["classe_exploratoria"],
            "pontuacao_v01": a["pontuacao_exploratoria"],
            "termos_v01": [x["expressao"] for x in a["termos_pontuados"]],
            "status_v03": b["status"], "classe_v03": b["classe_exploratoria"],
            "pontuacao_v03": b["pontuacao_exploratoria"],
            "motivos_v03": list(b["motivos"]),
            "termos_v03": [x["expressao"] for x in b["termos_pontuados"]],
            "transicao": transicao,
        })
    grupos = defaultdict(list)
    for linha in linhas:
        grupos[linha["cenario"]].append(linha)
    resumo = {
        "metodo": METODO,
        "fase": "CONTROLES_AUTORAIS_SEM_ROTULOS_HUMANOS_NAO_VALIDACAO",
        "baseline_v01": "baseline_aditivo_exploratorio_v0.1",
        "baseline_v03": PROTOCOLO_V03,
        "n_controles": len(linhas),
        "n_pares_avaliacao_processados": 0,
        "alvo_manual_nao_validado": alvo,
        "hipotese_sintatica_ativada": True,
        "metricas": {"v01": _numeros(linhas, "v01"), "v03": _numeros(linhas, "v03")},
        "por_cenario": {k: {"v01": _numeros(v,"v01"), "v03": _numeros(v,"v03")}
                        for k,v in sorted(grupos.items())},
        "transicoes": dict(sorted(Counter(l["transicao"] for l in linhas).items())),
        "acuracia": None, "f1_macro": None, "evidencia_de_vies": None,
        "limites": [
            "Controles sintéticos criados após desenvolvimento da V03; não equivalem a validação externa independente.",
            "Nenhuma classificação humana de referência foi coletada; acurácia e F1 indefinidas.",
            "Alvo N0/N1 é hipótese manual uniforme, não interpretação de referente.",
            "Heurística com+NOUN não distingue semanticamente modo, companhia, instrumento ou outras relações.",
            "Qualquer ajuste feito após examinar estes controles os transforma em dados de desenvolvimento.",
            "Nenhum par do conjunto reservado de avaliação final é consultado ou classificado.",
        ],
    }
    return resumo, linhas


def salvar(resumo: dict, linhas: list[dict], destino_json: Path, destino_csv: Path) -> None:
    if destino_json.resolve() == destino_csv.resolve():
        raise ValueError("Saídas JSON e CSV devem ser distintas.")
    if destino_json.exists() or destino_csv.exists():
        raise FileExistsError("Arquivo de saída já existe. Use um novo nome; não sobrescreva resultados.")
    if not linhas:
        raise ValueError("Não há resultados para salvar.")
    csvbuf = io.StringIO(newline="")
    w = csv.DictWriter(csvbuf, fieldnames=COLUNAS, delimiter=";", lineterminator="\n")
    w.writeheader()
    for l in linhas:
        w.writerow({**l, "termos_v01": "|".join(l["termos_v01"]),
                    "motivos_v03": "|".join(l["motivos_v03"]),
                    "termos_v03": "|".join(l["termos_v03"])})
    # Gera dados antes de criar arquivos para prevenir saída parcial por erro de serialização.
    json_texto = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    csv_texto = csvbuf.getvalue()
    destino_json.parent.mkdir(parents=True, exist_ok=True)
    destino_csv.parent.mkdir(parents=True, exist_ok=True)
    with destino_json.open("x", encoding="utf-8") as f:
        f.write(json_texto)
    with destino_csv.open("x", encoding="utf-8-sig", newline="") as f:
        f.write(csv_texto)


def main() -> None:
    p = argparse.ArgumentParser(description="Controles sintáticos SentiLex V01 x V03; NÃO validação")
    p.add_argument("--modo", required=True, choices=("verificar", "executar"))
    p.add_argument("--entrada", type=Path, default=ARQUIVO_CONTROLES)
    p.add_argument("--alvo", choices=("N0", "N1"))
    p.add_argument("--hipotese-modo", action="store_true")
    p.add_argument("--raiz", type=Path, default=ROOT)
    p.add_argument("--saida-json", type=Path)
    p.add_argument("--saida-csv", type=Path)
    args = p.parse_args()
    try:
        controles, sha = ler_controles(args.entrada)
        if args.modo == "verificar":
            if args.saida_json or args.saida_csv or args.alvo or args.hipotese_modo:
                p.error("No modo verificar, informe apenas --entrada opcional.")
            print(f"Conjunto pré-fixado: {len(controles)} controles; SHA-256: {sha}")
            print("Sem rótulos humanos, sem avaliação final, sem classificador executado.")
            return
        if args.alvo not in ("N0", "N1") or not args.hipotese_modo:
            p.error("Para executar, informe --alvo N0|N1 e --hipotese-modo.")
        if args.saida_json is None or args.saida_csv is None:
            p.error("Informe --saida-json e --saida-csv.")
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "sentilex")
        indice = IndiceLexical(entradas, lexico="sentilex")
        nlp = carregar_etiquetador()
        resumo, linhas = analisar_controles(controles, indice, nlp=nlp, alvo=args.alvo,
                                           hipotese_modo=True)
        resumo["sha256_controles"] = sha
        resumo["manifesto_lexical"] = fontes
        resumo["etiquetador"] = {"nome": "pt_core_news_sm", "versao": nlp.meta.get("version", "nao_informada")}
        salvar(resumo, linhas, args.saida_json, args.saida_csv)
        print(f"Controles: {len(linhas)} | V01 pontuadas: {resumo['metricas']['v01']['pontuadas']} "
              f"| V03 pontuadas: {resumo['metricas']['v03']['pontuadas']}")
        print(f"Saídas: {args.saida_json} | {args.saida_csv}")
        print("ATENÇÃO: sem rótulos humanos, não calcular acurácia, F1 ou inferir viés.")
    except (ValueError, FileNotFoundError, FileExistsError, UnicodeError, RuntimeError, OSError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
