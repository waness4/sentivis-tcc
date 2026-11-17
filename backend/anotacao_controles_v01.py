"""Bloco 21: fichas cegas e consolidação de dois anotadores humanos.

Somente os 36 controles fixados, já examinados durante o desenvolvimento.
Não importa previsões, léxicos ou dados do piloto; não estima acurácia nem viés.

python -m backend.anotacao_controles_v01 preparar --pasta-saida data/piloto/restrito
python -m backend.anotacao_controles_v01 consolidar --pasta-saida data/piloto/restrito
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import re
from collections import Counter
from pathlib import Path

from backend.controles_sintaticos_v03 import ARQUIVO_CONTROLES, ler_controles

METODO = "anotacao_humana_controles_diagnosticos_v01"
COLUNAS_FICHA = ("id_controle", "texto", "polaridade", "referente", "papel_com", "observacoes")
POLARIDADES = frozenset({"positiva", "negativa", "neutra", "sem_avaliacao", "mista", "indeterminada"})
REFERENTES = frozenset({"agente", "acao", "objeto", "terceiro", "multiplos", "nenhum", "indeterminado"})
PAPEIS_COM = frozenset({"modo", "instrumento", "companhia", "outro", "ambiguo", "nao_aplicavel"})


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _texto_csv(rows: list[dict], columns: tuple[str, ...]) -> str:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns, delimiter=";", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "\ufeff" + out.getvalue()


def _escrever_novo(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as f:
        try:
            f.write(txt)
            f.flush()
        except Exception:
            f.close()
            path.unlink(missing_ok=True)
            raise


def _escrever_conjunto(saidas: list[tuple[Path, str]]) -> None:
    """Publica um conjunto sem sobrescrever; desfaz saídas em falhas tratadas.

    Não oferece atomicidade entre arquivos contra término abrupto do processo.
    """
    if len({caminho.resolve() for caminho, _ in saidas}) != len(saidas):
        raise ValueError("Destinos devem ter caminhos distintos.")
    if any(caminho.exists() for caminho, _ in saidas):
        raise FileExistsError("Um dos arquivos de saída já existe; nenhuma saída sobrescrita.")
    criados: list[Path] = []
    try:
        for caminho, texto in saidas:
            _escrever_novo(caminho, texto)
            criados.append(caminho)
    except Exception:
        for caminho in reversed(criados):
            caminho.unlink(missing_ok=True)
        raise


def preparar(controles: list[dict], pasta_saida: Path, *, sha_origem: str) -> dict:
    """Gera fichas distintas sem gabarito, cenario e previsões dos baselines."""
    destinos = [pasta_saida / f"ficha_controles_{c}_v01.csv" for c in ("R01", "R02")]
    if any(p.exists() for p in destinos):
        raise FileExistsError("Há fichas existentes: nenhum arquivo de anotação será sobrescrito.")
    # Criar ambas as saídas antes de iniciar: falha se quaisquer diretórios/arquivos colidirem.
    listas = []
    for codigo in ("R01", "R02"):
        registros = [
            {"id_controle": c["id_controle"], "texto": c["texto"], "polaridade": "",
             "referente": "", "papel_com": "", "observacoes": ""}
            for c in controles
        ]
        seed = int(hashlib.sha256((sha_origem + ":" + codigo).encode()).hexdigest(), 16)
        random.Random(seed).shuffle(registros)
        listas.append(registros)
    if [x["id_controle"] for x in listas[0]] == [x["id_controle"] for x in listas[1]]:
        raise ValueError("Ordens de fichas não ficaram distintas.")
    _escrever_conjunto([
        (destino, _texto_csv(linhas, COLUNAS_FICHA))
        for destino, linhas in zip(destinos, listas)
    ])
    return {
        "metodo": METODO,
        "fase": "PREPARACAO_CEGA_CONTROLES_DIAGNOSTICOS",
        "sha256_controles": sha_origem,
        "total_controles": len(controles),
        "fichas": [str(p) for p in destinos],
        "politica": "Duas pessoas independentes, sem previsões dos classificadores e sem acesso às respostas alheias.",
        "avaliacao_final_processada": False,
    }


def _ler_ficha(path: Path, mapa: dict[str, dict], *, exigir_completa: bool) -> tuple[dict[str, dict], str]:
    if not path.is_file():
        raise FileNotFoundError(f"Ficha não encontrada: {path}")
    linhas: dict[str, dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";", restkey="__excesso__")
        if reader.fieldnames != list(COLUNAS_FICHA):
            raise ValueError(f"Cabeçalho incompatível em {path.name}; não incluir cenario ou resultados do sistema.")
        for numero, bruto in enumerate(reader, 2):
            if "__excesso__" in bruto or any(v is None for v in bruto.values()):
                raise ValueError(f"{path.name}:{numero}: quantidade incorreta de colunas.")
            row = {k: v.strip() for k, v in bruto.items()}
            ident = row["id_controle"]
            if ident not in mapa or ident in linhas:
                raise ValueError(f"{path.name}:{numero}: ID inexistente ou duplicado: {ident}")
            if row["texto"] != mapa[ident]["texto"]:
                raise ValueError(f"{path.name}:{numero}: texto alterado para {ident}.")
            for campo, valores in (("polaridade", POLARIDADES), ("referente", REFERENTES), ("papel_com", PAPEIS_COM)):
                if row[campo] not in valores | {""}:
                    raise ValueError(f"{path.name}:{numero}: {campo} inválido: {row[campo]!r}.")
                if exigir_completa and not row[campo]:
                    raise ValueError(f"{path.name}:{numero}: {campo} não preenchido ({ident}).")
            contem_com = re.search(r"\bcom\b", row["texto"], flags=re.IGNORECASE) is not None
            if row["papel_com"] and contem_com and row["papel_com"] == "nao_aplicavel":
                raise ValueError(f"{path.name}:{numero}: 'com' presente; papel_com não pode ser nao_aplicavel.")
            if row["papel_com"] and not contem_com and row["papel_com"] != "nao_aplicavel":
                raise ValueError(f"{path.name}:{numero}: sem 'com'; use nao_aplicavel em papel_com.")
            if exigir_completa and (row["polaridade"] in {"mista", "indeterminada"} or
                                     row["referente"] == "indeterminado" or row["papel_com"] == "ambiguo") and not row["observacoes"]:
                raise ValueError(f"{path.name}:{numero}: descreva a ambiguidade em observacoes ({ident}).")
            linhas[ident] = row
    if set(linhas) != set(mapa):
        raise ValueError(f"{path.name}: conjunto incompleto de IDs; faltam {len(set(mapa) - set(linhas))}.")
    return linhas, _hash(path)


def _kappa(classes_a: list[str], classes_b: list[str]) -> float | None:
    if len(classes_a) != len(classes_b) or not classes_a:
        return None
    n = len(classes_a)
    observado = sum(a == b for a, b in zip(classes_a, classes_b)) / n
    ca, cb = Counter(classes_a), Counter(classes_b)
    esperado = sum((ca[cat] / n) * (cb[cat] / n) for cat in ca.keys() | cb.keys())
    if abs(1.0 - esperado) < 1e-12:
        return None
    return round((observado - esperado) / (1 - esperado), 6)


def consolidar(controles: list[dict], ficha_a: Path, ficha_b: Path,
               saida_csv: Path, saida_json: Path, *, sha_origem: str) -> dict:
    """Concordância humana descritiva, SEM ajuste/resolução automática de divergências."""
    mapa = {c["id_controle"]: c for c in controles}
    caminhos = [ficha_a.resolve(), ficha_b.resolve(), saida_csv.resolve(), saida_json.resolve()]
    if len(set(caminhos)) != 4:
        raise ValueError("Fichas e saídas devem ter quatro caminhos distintos.")
    if saida_csv.exists() or saida_json.exists():
        raise FileExistsError("Relatório existente. Saída não sobrescrita.")
    a, ha = _ler_ficha(ficha_a, mapa, exigir_completa=True)
    b, hb = _ler_ficha(ficha_b, mapa, exigir_completa=True)
    saida = []
    completos = Counter()
    for controle in controles:
        ident = controle["id_controle"]
        linha_a, linha_b = a[ident], b[ident]
        concordam = {k: linha_a[k] == linha_b[k] for k in ("polaridade", "referente", "papel_com")}
        for k, concorda in concordam.items():
            completos[f"concordancia_{k}"] += bool(concorda)
        completos["concordancia_todos"] += all(concordam.values())
        saida.append({
            **controle,
            **{f"{k}_R01": linha_a[k] for k in ("polaridade", "referente", "papel_com", "observacoes")},
            **{f"{k}_R02": linha_b[k] for k in ("polaridade", "referente", "papel_com", "observacoes")},
            "concordancia_polaridade": "sim" if concordam["polaridade"] else "nao",
            "concordancia_referente": "sim" if concordam["referente"] else "nao",
            "concordancia_papel_com": "sim" if concordam["papel_com"] else "nao",
            "status": "CONCORDANCIA_TOTAL" if all(concordam.values()) else "DIVERGENCIA_PENDENTE",
        })
    n = len(controles)
    resumo = {
        "metodo": METODO,
        "fase": "CONSOLIDACAO_HUMANA_DIAGNOSTICA_SEM_ADJUDICACAO",
        "n_controles": n,
        "sha256_controles": sha_origem,
        "sha256_fichas": {"R01": ha, "R02": hb},
        "concordancia": {campo: {"n": completos[f"concordancia_{campo}"],
                                 "proporcao": round(completos[f"concordancia_{campo}"] / n, 6)}
                          for campo in ("polaridade", "referente", "papel_com", "todos")},
        "kappa_cohen_polaridade": _kappa([a[c["id_controle"]]["polaridade"] for c in controles],
                                          [b[c["id_controle"]]["polaridade"] for c in controles]),
        "divergencias_pendentes": [l["id_controle"] for l in saida if l["status"] == "DIVERGENCIA_PENDENTE"],
        "anotacoes_automaticas": 0,
        "n_pares_avaliacao_processados": 0,
        "comparacao_com_classificador": None,
        "acuracia": None,
        "f1_macro": None,
        "evidencia_de_vies": None,
        "limites": [
            "Controles autorais já consultados para desenvolver V04; somente avaliação diagnóstica.",
            "Concordância entre anotadores não é acurácia do classificador.",
            "A avaliação de referente da frase não valida automaticamente o alvo lexical N0/N1.",
            "Divergências ficam pendentes: nunca resolver automaticamente nem usar voto da máquina.",
            "Kappa é descritivo em amostra pequena e pode ser indefinido por prevalência constante.",
            "A auditoria não processa os 27 pares reservados, nem infere viés de gênero.",
        ],
    }
    campos = (
        "id_controle", "cenario", "texto", 
        "polaridade_R01", "referente_R01", "papel_com_R01", "observacoes_R01",
        "polaridade_R02", "referente_R02", "papel_com_R02", "observacoes_R02",
        "concordancia_polaridade", "concordancia_referente", "concordancia_papel_com", "status",
    )
    txt_csv = _texto_csv(saida, campos)
    txt_json = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    # Não sobrescreve os arquivos originais; não escreve em pasta compartilhada.
    _escrever_conjunto([(saida_csv, txt_csv), (saida_json, txt_json)])
    return resumo


def main() -> None:
    parser = argparse.ArgumentParser(description="Bloco 21: revisão humana cega dos controles diagnósticos")
    sub = parser.add_subparsers(dest="acao", required=True)
    preparar_p = sub.add_parser("preparar", help="gerar duas fichas cegas, não preenchidas")
    preparar_p.add_argument("--pasta-saida", type=Path, default=Path("data/piloto/restrito"))
    consolidar_p = sub.add_parser("consolidar", help="validar as duas fichas e medir concordância")
    consolidar_p.add_argument("--pasta-saida", type=Path, default=Path("data/piloto/restrito"))
    args = parser.parse_args()
    try:
        controles, sha = ler_controles(ARQUIVO_CONTROLES)
        pasta = args.pasta_saida
        if args.acao == "preparar":
            info = preparar(controles, pasta, sha_origem=sha)
            print(f"Fichas cegas geradas: {info['total_controles']} frases para R01 e R02.")
            for x in info["fichas"]:
                print(x)
            print("Sem previsões ou rótulos; nenhuma avaliação final acessada.")
        else:
            resumo = consolidar(
                controles,
                pasta / "ficha_controles_R01_v01.csv",
                pasta / "ficha_controles_R02_v01.csv",
                pasta / "consolidacao_controles_humana_v01.csv",
                pasta / "relatorio_concordancia_controles_v01.json",
                sha_origem=sha,
            )
            print("Controle humano consolidado:", resumo["n_controles"])
            print("Concordância de polaridade:", resumo["concordancia"]["polaridade"])
            print("Divergências pendentes:", len(resumo["divergencias_pendentes"]))
            print("Sem inferência de viés, acurácia ou consulta à avaliação final.")
    except (ValueError, FileExistsError, FileNotFoundError, UnicodeError, OSError) as error:
        parser.exit(1, f"ERRO: {error}\n")


if __name__ == "__main__":
    main()
