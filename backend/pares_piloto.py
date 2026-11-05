"""Validação de pares contrafactuais e piloto APENAS de desenvolvimento.

Não substitui anotação humana, não avalia viés nem acessa partição de avaliação.
Executar de C:\\TCC\\sentivis_bloco1 usando python -m backend.pares_piloto.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from backend.baseline_experimental import STATUS_PONTUADO, comparar_exploratoriamente
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta

CAMPOS = (
    "id_par", "familia", "particao", "frase_feminina", "frase_masculina",
    "rotulo_revisor1", "rotulo_revisor2", "equivalencia_revisor1",
    "equivalencia_revisor2", "id_revisor1", "id_revisor2",
    "alvo_sentilex_feminina", "alvo_sentilex_masculina", "observacoes",
)
ROTULOS = frozenset({"positiva", "negativa", "neutra"})
PARTICOES = frozenset({"desenvolvimento", "avaliacao"})
EQUIVALENCIAS = frozenset({"sim", "nao"})
ALVOS = frozenset({"N0", "N1"})
VERSAO = "piloto_pares_v0.1"


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFC", " ".join(texto.casefold().split()))


def ler_csv(caminho: Path) -> tuple[list[dict[str, str]], str]:
    """Importação estrita; não aceita cabeçalho incorreto ou CSV sem registros."""
    if not caminho.is_file():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho}")
    with caminho.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f, delimiter=";", restkey="__excesso__")
        cabecalho = tuple(leitor.fieldnames or ())
        if len(cabecalho) != len(set(cabecalho)) or set(cabecalho) != set(CAMPOS):
            raise ValueError("Cabeçalho inválido; use exatamente as 14 colunas do modelo, separadas por ponto e vírgula.")
        linhas = []
        for numero, bruto in enumerate(leitor, start=2):
            if "__excesso__" in bruto or any(v is None for v in bruto.values()):
                raise ValueError(f"Linha {numero}: quantidade de colunas incorreta.")
            if not any(v.strip() for v in bruto.values()):
                continue
            item = {chave: valor.strip() for chave, valor in bruto.items()}
            item["_linha_csv"] = numero
            linhas.append(item)
        if not linhas:
            raise ValueError("Dataset vazio; cadastre ao menos um par.")
    sha = hashlib.sha256(caminho.read_bytes()).hexdigest()
    return linhas, sha


def status_revisao(par: dict[str, str]) -> str:
    """A aprovação depende de duas anotações convergentes e identificadores distintos.

    A consistência dos IDs NÃO prova independência real dos revisores.
    """
    e1, e2 = par["equivalencia_revisor1"], par["equivalencia_revisor2"]
    r1, r2 = par["rotulo_revisor1"], par["rotulo_revisor2"]
    if "nao" in (e1, e2):
        return "REPROVADO_EQUIVALENCIA"
    if not all((e1, e2, r1, r2, par["id_revisor1"], par["id_revisor2"])):
        return "PENDENTE_REVISAO"
    if par["id_revisor1"] == par["id_revisor2"]:
        return "REVISORES_NAO_DISTINTOS"
    if e1 != "sim" or e2 != "sim":
        return "REPROVADO_EQUIVALENCIA"
    if r1 != r2:
        return "DISCORDANCIA_ROTULO"
    return "APROVADO_DUPLA_REVISAO"


def validar_pares(linhas: list[dict[str, str]], *, sha256: str) -> dict:
    erros: list[str] = []
    avisos: list[str] = []
    vistos_ids: dict[str, int] = {}
    familias: dict[str, set[str]] = defaultdict(set)
    frases_por_particao: dict[str, set[str]] = defaultdict(set)
    pares_vistos: dict[tuple[str, str], int] = {}
    estados = Counter()
    resumos = []
    for par in linhas:
        n = par["_linha_csv"]
        for coluna in ("id_par", "familia", "particao", "frase_feminina", "frase_masculina"):
            if not par[coluna]:
                erros.append(f"Linha {n}: campo obrigatório vazio: {coluna}.")
        if par["particao"] and par["particao"] not in PARTICOES:
            erros.append(f"Linha {n}: partição inválida: {par['particao']}.")
        for coluna in ("rotulo_revisor1", "rotulo_revisor2"):
            if par[coluna] and par[coluna] not in ROTULOS:
                erros.append(f"Linha {n}: {coluna} inválido: {par[coluna]}.")
        for coluna in ("equivalencia_revisor1", "equivalencia_revisor2"):
            if par[coluna] and par[coluna] not in EQUIVALENCIAS:
                erros.append(f"Linha {n}: {coluna} inválida: {par[coluna]}.")
        for coluna in ("alvo_sentilex_feminina", "alvo_sentilex_masculina"):
            if par[coluna] and par[coluna] not in ALVOS:
                erros.append(f"Linha {n}: {coluna} inválido: {par[coluna]}.")
        for coluna in ("frase_feminina", "frase_masculina"):
            if len(par[coluna]) > 5000:
                erros.append(f"Linha {n}: {coluna} ultrapassa 5000 caracteres.")
        identificador = par["id_par"]
        if identificador in vistos_ids:
            erros.append(f"Linha {n}: ID repetido '{identificador}' (linha {vistos_ids[identificador]}).")
        else:
            vistos_ids[identificador] = n
        if par["familia"] and par["particao"] in PARTICOES:
            familias[_normalizar(par["familia"])].add(par["particao"])
        f, m = _normalizar(par["frase_feminina"]), _normalizar(par["frase_masculina"])
        if f == m:
            erros.append(f"Linha {n}: frases feminina e masculina são idênticas.")
        for frase in (f, m):
            if frase:
                frases_por_particao[frase].add(par["particao"])
        chave_par = (f, m)
        if chave_par in pares_vistos:
            erros.append(f"Linha {n}: par duplicado (linha {pares_vistos[chave_par]}).")
        else:
            pares_vistos[chave_par] = n
        estado = status_revisao(par)
        estados[estado] += 1
        if estado == "REVISORES_NAO_DISTINTOS":
            erros.append(f"Linha {n}: os dois revisores usam o mesmo ID; revisão dupla não comprovada.")
        if par["particao"] == "avaliacao" and estado == "APROVADO_DUPLA_REVISAO":
            avisos.append(f"Linha {n}: par de avaliação permanecerá BLOQUEADO para este piloto.")
        resumos.append({"id_par": identificador, "familia": par["familia"], "particao": par["particao"],
                        "linha_csv": n, "status_revisao": estado})
    for familia, particoes in familias.items():
        if len(particoes) > 1:
            erros.append(f"Vazamento entre partições: família '{familia}' aparece em desenvolvimento e avaliação.")
    for frase, particoes in frases_por_particao.items():
        if "desenvolvimento" in particoes and "avaliacao" in particoes:
            erros.append(f"Frase literal repetida entre desenvolvimento e avaliação: {frase[:90]!r}.")
    return {
        "metodo": VERSAO,
        "status": "INVALIDO" if erros else "ESTRUTURA_VALIDADA_SEM_INFERENCIA_DE_VIES",
        "sha256_dataset": sha256,
        "total_pares": len(linhas),
        "pares_por_particao": dict(Counter(p["particao"] for p in linhas)),
        "pares_por_status_revisao": dict(estados),
        "familias_por_particao": {parte: sum(parte in ps for ps in familias.values()) for parte in sorted(PARTICOES)},
        "erros": erros, "avisos": avisos, "pares": resumos,
        "alerta": "Dupla anotação concordante não prova independência ou equivalência semântica real. Revisão e protocolo ainda são necessários.",
    }


def executar_piloto(linhas: list[dict[str, str]], auditoria: dict,
                    indices: dict[str, IndiceLexical], manifestos: dict[str, dict] | None = None) -> dict:
    """Somente pares aprovados de DESENVOLVIMENTO, sem inferência de viés."""
    if auditoria["erros"]:
        raise ValueError("Dataset inválido; corrija os erros antes de executar o piloto.")
    saidas = []
    totais = {}
    for lexico, indice in indices.items():
        if lexico not in ("oplexicon", "sentilex") or indice.lexico != lexico:
            raise ValueError("Índice e nome do léxico incompatíveis.")
        selecionados = [p for p in linhas if p["particao"] == "desenvolvimento" and
                        status_revisao(p) == "APROVADO_DUPLA_REVISAO"]
        pares_pontuados, abstenidos = 0, 0
        for p in selecionados:
            # OpLexicon não utiliza N0/N1. SentiLex exige alvos por frase,
            # e esses alvos são hipóteses fornecidas por revisores, não verificação sintática.
            if lexico == "sentilex":
                f = p["alvo_sentilex_feminina"] or None
                m = p["alvo_sentilex_masculina"] or None
                from backend.baseline_experimental import classificar_exploratoriamente
                resultado_f = classificar_exploratoriamente(p["frase_feminina"], indice, alvo=f)
                resultado_m = classificar_exploratoriamente(p["frase_masculina"], indice, alvo=m)
                ambas = resultado_f["status"] == resultado_m["status"] == STATUS_PONTUADO
                delta = resultado_f["pontuacao_exploratoria"] - resultado_m["pontuacao_exploratoria"] if ambas else None
            else:
                comparacao = comparar_exploratoriamente(p["frase_feminina"], p["frase_masculina"], indice)
                resultado_f, resultado_m = comparacao["feminina"], comparacao["masculina"]
                ambas, delta = comparacao["ambas_pontuaveis"], comparacao["delta_feminino_masculino_exploratorio"]
            pares_pontuados += int(ambas)
            abstenidos += int(not ambas)
            saidas.append({
                "id_par": p["id_par"], "familia": p["familia"], "particao": "desenvolvimento",
                "lexico": lexico, "rotulo_referencia_anotado": p["rotulo_revisor1"],
                "status_feminina": resultado_f["status"], "status_masculina": resultado_m["status"],
                "motivos_feminina": resultado_f["motivos"], "motivos_masculina": resultado_m["motivos"],
                "pontuacao_feminina": resultado_f["pontuacao_exploratoria"],
                "pontuacao_masculina": resultado_m["pontuacao_exploratoria"],
                "classe_feminina": resultado_f["classe_exploratoria"],
                "classe_masculina": resultado_m["classe_exploratoria"],
                "delta_feminino_masculino_exploratorio": delta,
                "cobertura_feminina": resultado_f["cobertura_superficial"],
                "cobertura_masculina": resultado_m["cobertura_superficial"],
                "alvos_sentilex_manuais_nao_validados": lexico == "sentilex",
                "evidencia_de_vies": None,
            })
        totais[lexico] = {"pares_elegiveis": len(selecionados), "pares_ambos_pontuados": pares_pontuados,
                         "pares_com_ao_menos_uma_abstencao": abstenidos}
    return {"metodo": VERSAO, "fase": "PILOTO_EXPLORATORIO_DESENVOLVIMENTO",
            "sha256_dataset": auditoria["sha256_dataset"], "resumo_por_lexico": totais,
            "resultados": saidas, "manifestos_fontes": manifestos or {},
            "avaliacao_final_executada": False, "evidencia_de_vies": None,
            "alerta": "Saídas exclusivamente exploratórias de desenvolvimento. N0/N1 não validado sintaticamente. Nenhuma conclusão de viés, acurácia ou equidade."}


def main() -> None:
    p = argparse.ArgumentParser(description="Validar pares e executar piloto apenas em desenvolvimento")
    p.add_argument("--entrada", type=Path, required=True, help="CSV UTF-8, separado por ponto e vírgula")
    p.add_argument("--saida", type=Path, default=ROOT / "data" / "piloto" / "relatorio_pares.json")
    p.add_argument("--piloto", action="store_true", help="Executa baseline apenas em pares aprovados de desenvolvimento")
    p.add_argument("--raiz", type=Path, default=ROOT)
    args = p.parse_args()
    try:
        pares, sha = ler_csv(args.entrada)
        auditoria = validar_pares(pares, sha256=sha)
        resposta = {"auditoria": auditoria}
        if args.piloto:
            if auditoria["erros"]:
                raise ValueError("Dataset inválido. Execute primeiro sem --piloto e corrija os erros.")
            indices, manifestos = {}, {}
            for nome in ("oplexicon", "sentilex"):
                entradas, fontes = carregar_para_consulta(args.raiz.resolve(), nome)
                indices[nome] = IndiceLexical(entradas, lexico=nome)
                manifestos[nome] = fontes
            resposta["piloto"] = executar_piloto(pares, auditoria, indices, manifestos)
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(json.dumps(resposta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Relatório: {args.saida}")
        print(f"Pares: {len(pares)}; erros estruturais: {len(auditoria['erros'])}; revisões: {auditoria['pares_por_status_revisao']}")
        if args.piloto:
            print(f"Piloto APENAS desenvolvimento: {resposta['piloto']['resumo_por_lexico']}")
        print("AVISO: nenhum teste de viés ou inferência estatística foi realizado.")
        if auditoria["erros"]:
            p.exit(2, "ERRO: existem problemas estruturais no CSV; consulte o relatório.\n")
    except (ValueError, FileNotFoundError, UnicodeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
