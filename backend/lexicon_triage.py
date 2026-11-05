"""Etapa de curadoria documental dos léxicos originais do SentiVis.

NÃO corrige polaridades, não descarta linhas silenciosamente e NÃO classifica frases.
Produz artefatos de diagnóstico sem alterar os arquivos de origem.

Uso: python -m backend.lexicon_triage
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from backend.lexicon_audit import EntradaLexical, interpretar_oplexicon, interpretar_sentilex

ROOT = Path(__file__).resolve().parent.parent
NOMES = {
    "oplexicon": "lexico_v3.0.txt",
    "sentilex_lem": "SentiLex-lem-PT02.txt",
    "sentilex_flex": "SentiLex-flex-PT02.txt",
}


def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFC", texto.strip().casefold())


def localizar_unico(base: Path, nome: str) -> Path:
    encontrados = sorted(p for p in base.rglob(nome) if p.is_file())
    if len(encontrados) != 1:
        raise FileNotFoundError(f"Esperado exatamente um arquivo {nome!r} em {base}; encontrados: {len(encontrados)}")
    return encontrados[0]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_para_curadoria(path: Path, tipo: str) -> tuple[list[EntradaLexical], list[dict]]:
    """Leitura permissiva para inspeção, sinalizando linhas estruturalmente ilegíveis."""
    entradas: list[EntradaLexical] = []
    falhas: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for n, bruto in enumerate(f, 1):
            try:
                if not bruto.strip():
                    raise ValueError("linha vazia")
                if tipo == "oplexicon":
                    entrada = interpretar_oplexicon(bruto, arquivo=path.name, linha=n)
                else:
                    entrada = interpretar_sentilex(
                        bruto, arquivo=path.name, linha=n,
                        flexionado=(tipo == "sentilex_flex"),
                        permitir_polaridade_fora_padrao=True,
                        permitir_atributos_sem_chave=True,
                    )
                entradas.append(entrada)
            except (ValueError, UnicodeError, csv.Error) as exc:
                falhas.append({"arquivo": path.name, "linha": n,
                               "motivo": "linha_nao_interpretavel", "detalhes": str(exc),
                               "registro_original": bruto.rstrip("\r\n")})
    return entradas, falhas


def analisar_entradas(entradas: list[EntradaLexical]) -> tuple[dict, list[dict]]:
    """Conflitos são por termo+categoria+alvo de polaridade, não por N0 versus N1.

    A flag 'pendente_de_revisao' não atesta erro na fonte; impede inferências
    indevidas e indica onde documentação linguística adicional é necessária.
    """
    polos: dict[tuple[str, str, str, str], set[int]] = defaultdict(set)
    grupos: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for e in entradas:
        chave = (e.origem, normalizar(e.termo), normalizar(e.categoria))
        grupos[chave].add(normalizar(e.lema or ""))
        for alvo, polaridade in e.polaridades:
            polos[(*chave, alvo)].add(polaridade)

    conflitos_por_alvo = {chave for chave, valores in polos.items() if len(valores) > 1}
    lemas_multiplos = {chave for chave, lemas in grupos.items() if len(lemas) > 1}
    detalhamento = []
    por_motivo: Counter[str] = Counter()
    por_tipo: Counter[str] = Counter()
    tokens_sem_chave: Counter[str] = Counter()

    for e in entradas:
        motivos = set()
        invalidas = {alvo: val for alvo, val in e.polaridades if val not in (-1, 0, 1)}
        if invalidas:
            motivos.add("polaridade_fora_do_padrao")
        if e.atributos_sem_chave:
            motivos.add("atributo_sem_chave")
            for x in e.atributos_sem_chave:
                tokens_sem_chave[x] += 1
        chave = (e.origem, normalizar(e.termo), normalizar(e.categoria))
        conflitos_da_entrada = [alvo for alvo, val in e.polaridades if (*chave, alvo) in conflitos_por_alvo]
        if conflitos_da_entrada:
            motivos.add("polaridade_divergente_mesmo_alvo")
        if chave in lemas_multiplos:
            motivos.add("mesma_forma_categorias_e_lemas_diferentes")
        if not motivos:
            continue
        for motivo in motivos:
            por_motivo[motivo] += 1
        por_tipo[e.origem] += 1
        detalhamento.append({
            "arquivo": e.arquivo, "origem": e.origem, "linha": e.linha,
            "termo": e.termo, "lema": e.lema or "", "categoria": e.categoria,
            "alvo": e.alvo or "", "flexao": e.flexao or "",
            "polaridades": ";".join(f"{a}={v}" for a, v in e.polaridades),
            "alvos_divergentes": ";".join(conflitos_da_entrada),
            "atributos_sem_chave": ";".join(e.atributos_sem_chave),
            "motivos": "|".join(sorted(motivos)),
            "atributos_originais": ";".join(e.atributos_originais),
        })
    resumo = {
        "registros_interpretados": len(entradas),
        "registros_sinalizados_para_revisao": len(detalhamento),
        "registros_sem_sinalizacoes_de_curadoria": len(entradas) - len(detalhamento),
        "registros_por_motivo": dict(sorted(por_motivo.items())),
        "registros_sinalizados_por_fonte": dict(sorted(por_tipo.items())),
        "grupos_conflitantes_por_termo_categoria_alvo": len(conflitos_por_alvo),
        "grupos_de_forma_categoria_com_lemas_distintos": len(lemas_multiplos),
        "exemplos_de_conflitos_por_alvo": [
            {"origem": tipo, "termo_normalizado": termo, "categoria_normalizada": cat,
             "alvo": alvo, "polaridades": sorted(polos[(tipo, termo, cat, alvo)])}
            for tipo, termo, cat, alvo in sorted(conflitos_por_alvo)[:25]
        ],
        "top_atributos_sem_chave": [
            {"valor": nome, "quantidade": n}
            for nome, n in tokens_sem_chave.most_common(25)
        ],
    }
    return resumo, detalhamento


def gerar(raiz: Path) -> tuple[Path, Path, dict]:
    base = raiz / "data" / "lexicos"
    originais = base / "originais"
    if not originais.is_dir():
        raise FileNotFoundError(f"Pasta não encontrada: {originais}")
    entradas: list[EntradaLexical] = []
    falhas: list[dict] = []
    fontes = {}
    for tipo, nome in NOMES.items():
        path = localizar_unico(originais, nome)
        lidas, falhas_desta = ler_para_curadoria(path, tipo)
        entradas.extend(lidas)
        falhas.extend(falhas_desta)
        fontes[tipo] = {"arquivo": nome, "sha256": sha256(path),
                        "registros_lidos": len(lidas),
                        "linhas_nao_interpretaveis": len(falhas_desta)}
    resumo, pendencias = analisar_entradas(entradas)
    out = {
        "status": "CURADORIA_DOCUMENTAL_PRELIMINAR_SEM_CLASSIFICACAO",
        "criterio": "Sinalizações conservadoras para revisão, não confirmação de erro ou viés.",
        "fontes": fontes,
        **resumo,
        "falhas_de_leitura": falhas[:100],
        "total_falhas_de_leitura": len(falhas),
        "politica": [
            "Não modificar arquivos originais.",
            "Não converter ou truncar polaridades fora de -1/0/+1.",
            "Não resolver colisões por maioria, primeira ocorrência ou média arbitrária.",
            "Não confundir N0 e N1: conflitos são comparados dentro do mesmo alvo.",
            "Não classificar textos nem afirmar viés com estas contagens.",
            "Registros sem sinalizações não estão semanticamente validados.",
        ],
    }
    base.mkdir(parents=True, exist_ok=True)
    destino_json = base / "relatorio_curadoria.json"
    destino_csv = base / "pendencias_curadoria.csv"
    destino_json.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    colunas = ["arquivo", "origem", "linha", "termo", "lema", "categoria", "alvo",
               "flexao", "polaridades", "alvos_divergentes", "atributos_sem_chave",
               "motivos", "atributos_originais"]
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";")
        w.writeheader()
        w.writerows(pendencias)
    return destino_json, destino_csv, out


def main() -> None:
    parser = argparse.ArgumentParser(description="Triagem documental, sem classificação")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        rel, csv_path, dados = gerar(args.raiz.resolve())
    except (FileNotFoundError, ValueError, UnicodeError) as exc:
        parser.exit(status=1, message=f"ERRO: {exc}\n")
    print(f"Relatório: {rel}")
    print(f"Pendências: {csv_path}")
    print(f"Registros interpretados: {dados['registros_interpretados']}")
    print(f"Registros sinalizados para revisão: {dados['registros_sinalizados_para_revisao']}")
    print(f"Conflitos por termo/categoria/alvo: {dados['grupos_conflitantes_por_termo_categoria_alvo']}")
    print("AVISO: nenhum resultado de classificação ou viés foi produzido.")


if __name__ == "__main__":
    main()
