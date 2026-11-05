"""Bloco 9: preparação e consolidação conservadora da revisão humana.

Não consulta léxicos, não executa classificação e não abre a avaliação final.
Execute com: python -m backend.revisao_humana preparar|consolidar --help
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from backend.pares_piloto import CAMPOS, ROOT, ler_csv, validar_pares, status_revisao

COLUNAS_FICHA = (
    "id_par", "frase_feminina", "frase_masculina", "equivalencia", "rotulo", "observacoes"
)
ROTULOS = {"positiva", "negativa", "neutra"}
EQUIVALENCIAS = {"sim", "nao"}


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _validar_fonte(entrada: Path) -> tuple[list[dict[str, str]], str, list[dict[str, str]]]:
    pares, sha = ler_csv(entrada)
    auditoria = validar_pares(pares, sha256=sha)
    if auditoria["erros"]:
        raise ValueError("CSV de origem inválido: " + " | ".join(auditoria["erros"][:4]))
    # Nunca aceitar rótulos ou IDs preenchidos na parte reservada durante este piloto.
    campos_revisao = (
        "rotulo_revisor1", "rotulo_revisor2", "equivalencia_revisor1",
        "equivalencia_revisor2", "id_revisor1", "id_revisor2",
        "alvo_sentilex_feminina", "alvo_sentilex_masculina"
    )
    if any(any(p[c] for c in campos_revisao) for p in pares if p["particao"] == "avaliacao"):
        raise ValueError("A partição de avaliação deve permanecer sem anotações neste piloto.")
    desenvolvimento = [p for p in pares if p["particao"] == "desenvolvimento"]
    if not desenvolvimento:
        raise ValueError("Não há pares da partição desenvolvimento.")
    return pares, sha, desenvolvimento


def _gravar_csv(caminho: Path, campos: tuple[str, ...], linhas: list[dict], *, substituir: bool = False) -> None:
    if caminho.exists() and not substituir:
        raise FileExistsError(f"Arquivo existente (não sobrescrito): {caminho}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(linhas)


def _gravar_json(caminho: Path, valor: dict, *, substituir: bool = False) -> None:
    if caminho.exists() and not substituir:
        raise FileExistsError(f"Arquivo existente (não sobrescrito): {caminho}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(valor, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def preparar(entrada: Path, pasta_saida: Path, *, substituir: bool = False) -> dict:
    """Prepara duas fichas IDÊNTICAS, somente de desenvolvimento, sem gabarito."""
    _, origem_hash, dev = _validar_fonte(entrada)
    a = pasta_saida / "ficha_revisor_A_desenvolvimento.csv"
    b = pasta_saida / "ficha_revisor_B_desenvolvimento.csv"
    if not substituir and (a.exists() or b.exists()):
        raise FileExistsError("Fichas já existem. Não sobrescrevemos anotações por padrão.")
    fichas = [
        {"id_par": p["id_par"], "frase_feminina": p["frase_feminina"],
         "frase_masculina": p["frase_masculina"], "equivalencia": "",
         "rotulo": "", "observacoes": ""}
        for p in dev
    ]
    _gravar_csv(a, COLUNAS_FICHA, fichas, substituir=substituir)
    _gravar_csv(b, COLUNAS_FICHA, fichas, substituir=substituir)
    return {
        "status": "FICHAS_GERADAS_SEM_ANOTACOES",
        "sha256_dataset_origem": origem_hash,
        "pares_desenvolvimento": len(dev),
        "pares_avaliacao_exportados": 0,
        "fichas": [str(a), str(b)],
        "aviso": "Entregar cada ficha a pessoa distinta. Não compartilhar plano de amostragem, avaliações alheias ou saída do classificador."
    }


def _ler_ficha(caminho: Path, esperado: dict[str, dict[str, str]]) -> tuple[dict[str, dict[str, str]], str]:
    if not caminho.is_file():
        raise FileNotFoundError(f"Ficha ausente: {caminho}")
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";", restkey="__excesso__")
        campos = reader.fieldnames or []
        if len(campos) != len(set(campos)) or set(campos) != set(COLUNAS_FICHA):
            raise ValueError(f"Cabeçalho inválido na ficha {caminho.name}.")
        saida: dict[str, dict[str, str]] = {}
        for num, bruto in enumerate(reader, start=2):
            if "__excesso__" in bruto or any(v is None for v in bruto.values()):
                raise ValueError(f"{caminho.name}, linha {num}: colunas incorretas.")
            linha = {k: v.strip() for k, v in bruto.items()}
            id_par = linha["id_par"]
            if id_par not in esperado:
                raise ValueError(f"{caminho.name}, linha {num}: ID desconhecido/reservado: {id_par}")
            if id_par in saida:
                raise ValueError(f"{caminho.name}, linha {num}: ID repetido: {id_par}")
            original = esperado[id_par]
            if (linha["frase_feminina"] != original["frase_feminina"] or
                    linha["frase_masculina"] != original["frase_masculina"]):
                raise ValueError(f"{caminho.name}, linha {num}: frases modificadas: {id_par}")
            if linha["equivalencia"] not in EQUIVALENCIAS | {""}:
                raise ValueError(f"{caminho.name}, linha {num}: equivalência inválida.")
            if linha["rotulo"] not in ROTULOS | {""}:
                raise ValueError(f"{caminho.name}, linha {num}: rótulo inválido.")
            if linha["equivalencia"] == "sim" and not linha["rotulo"]:
                raise ValueError(f"{caminho.name}, linha {num}: equivalência 'sim' exige rótulo.")
            if linha["equivalencia"] == "nao" and not linha["observacoes"]:
                raise ValueError(f"{caminho.name}, linha {num}: equivalência 'nao' exige justificativa.")
            if not linha["equivalencia"] and linha["rotulo"]:
                raise ValueError(f"{caminho.name}, linha {num}: rótulo sem decisão de equivalência.")
            saida[id_par] = linha
    if set(saida) != set(esperado):
        raise ValueError(f"{caminho.name}: conjunto de IDs incompleto; faltam {len(set(esperado) - set(saida))}.")
    return saida, _sha256(caminho)


def consolidar(
    entrada: Path, ficha_a: Path, ficha_b: Path,
    *, id_a: str, id_b: str, saida_csv: Path, saida_relatorio: Path,
    substituir: bool = False
) -> dict:
    """Reúne respostas independentes; não arbitra e não acessa resultados de modelos."""
    id_a, id_b = id_a.strip(), id_b.strip()
    if not id_a or not id_b or id_a == id_b:
        raise ValueError("Informe dois identificadores pseudônimos, não vazios e distintos.")
    if ficha_a.resolve() == ficha_b.resolve():
        raise ValueError("Fichas A e B devem ser arquivos distintos.")
    caminhos = {entrada.resolve(), ficha_a.resolve(), ficha_b.resolve()}
    if saida_csv.resolve() in caminhos or saida_relatorio.resolve() in caminhos:
        raise ValueError("Não substituir os dados ou fichas de entrada.")
    if saida_csv.resolve() == saida_relatorio.resolve():
        raise ValueError("CSV e relatório precisam ter destinos distintos.")
    if not substituir and (saida_csv.exists() or saida_relatorio.exists()):
        raise FileExistsError("Saída existente. Use um novo nome ou --substituir-saida conscientemente.")
    todos, origem_sha, dev = _validar_fonte(entrada)
    mapa_dev = {p["id_par"]: p for p in dev}
    a, hash_a = _ler_ficha(ficha_a, mapa_dev)
    b, hash_b = _ler_ficha(ficha_b, mapa_dev)
    consolidado = []
    descricoes = []
    estados = Counter()
    for original in todos:
        p = {k: original[k] for k in CAMPOS}
        if p["particao"] == "desenvolvimento":
            x, y = a[p["id_par"]], b[p["id_par"]]
            p.update({
                "rotulo_revisor1": x["rotulo"], "rotulo_revisor2": y["rotulo"],
                "equivalencia_revisor1": x["equivalencia"],
                "equivalencia_revisor2": y["equivalencia"],
                "id_revisor1": id_a if x["equivalencia"] else "",
                "id_revisor2": id_b if y["equivalencia"] else "",
            })
            # Não inserir observações individuais num CSV de um campo: mantê-las nas fichas.
            situacao = status_revisao(p)
            if situacao in {"REPROVADO_EQUIVALENCIA", "DISCORDANCIA_ROTULO"}:
                status_operacional = "PENDENTE_ADJUDICACAO"
            else:
                status_operacional = situacao
            estados[status_operacional] += 1
            descricoes.append({"id_par": p["id_par"], "status": status_operacional})
        consolidado.append(p)
    # A saída inclui os pares reservados SEM ANOTAÇÕES; nenhuma frase reservada vai no relatório.
    auditoria = validar_pares([{**p, "_linha_csv": n} for n, p in enumerate(consolidado, 2)], sha256=origem_sha)
    if auditoria["erros"]:
        raise ValueError("Consolidação gerou dataset inválido: " + " | ".join(auditoria["erros"][:3]))
    _gravar_csv(saida_csv, CAMPOS, consolidado, substituir=substituir)
    relatorio = {
        "fase": "REVISAO_HUMANA_DESENVOLVIMENTO_SEM_INFERENCIA",
        "sha256_origem": origem_sha,
        "sha256_ficha_A": hash_a,
        "sha256_ficha_B": hash_b,
        "sha256_consolidado": _sha256(saida_csv),
        "pares_desenvolvimento": len(dev),
        "pares_avaliacao_intocados": len(todos) - len(dev),
        "contagem_por_status": dict(estados),
        "pares": descricoes,
        "aviso": "Não é revisão automática. Adjudicação humana necessária para discordâncias. Nenhum modelo foi consultado e nenhum resultado final foi calculado."
    }
    _gravar_json(saida_relatorio, relatorio, substituir=substituir)
    return relatorio


def main() -> None:
    parser = argparse.ArgumentParser(description="Preparar/consolidar dupla revisão humana somente de desenvolvimento")
    sub = parser.add_subparsers(dest="comando", required=True)
    p_prep = sub.add_parser("preparar")
    p_prep.add_argument("--entrada", type=Path, default=ROOT / "data/piloto/pares_candidatos_v01.csv")
    p_prep.add_argument("--pasta-saida", type=Path, default=ROOT / "data/piloto/restrito")
    p_prep.add_argument("--substituir-saida", action="store_true")
    p_cons = sub.add_parser("consolidar")
    p_cons.add_argument("--entrada", type=Path, default=ROOT / "data/piloto/pares_candidatos_v01.csv")
    p_cons.add_argument("--ficha-a", type=Path, default=ROOT / "data/piloto/restrito/ficha_revisor_A_desenvolvimento.csv")
    p_cons.add_argument("--ficha-b", type=Path, default=ROOT / "data/piloto/restrito/ficha_revisor_B_desenvolvimento.csv")
    p_cons.add_argument("--id-a", required=True)
    p_cons.add_argument("--id-b", required=True)
    p_cons.add_argument("--saida-csv", type=Path, default=ROOT / "data/piloto/restrito/pares_desenvolvimento_revisados_v01.csv")
    p_cons.add_argument("--saida-relatorio", type=Path, default=ROOT / "data/piloto/restrito/relatorio_revisao_v01.json")
    p_cons.add_argument("--substituir-saida", action="store_true")
    args = parser.parse_args()
    try:
        if args.comando == "preparar":
            resultado = preparar(args.entrada, args.pasta_saida, substituir=args.substituir_saida)
            print(f"Fichas criadas: {resultado['pares_desenvolvimento']} pares de desenvolvimento; avaliação exportada: 0.")
            for f in resultado["fichas"]:
                print(f)
        else:
            r = consolidar(args.entrada, args.ficha_a, args.ficha_b, id_a=args.id_a, id_b=args.id_b,
                          saida_csv=args.saida_csv, saida_relatorio=args.saida_relatorio,
                          substituir=args.substituir_saida)
            print(f"Revisões de desenvolvimento consolidadas: {r['contagem_por_status']}")
            print(f"Relatório: {args.saida_relatorio}")
            print("AVISO: avaliação final não analisada; revisão humana não equivale a validação do classificador.")
    except (ValueError, FileNotFoundError, FileExistsError, UnicodeError) as exc:
        parser.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
