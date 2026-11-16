"""Bloco 27 — diagnóstico conservador de uma única ficha humana.

Somente lê o corpus público fixado de 36 controles e uma ficha recebida.
Não importa ou executa baselines; não toca a partição de avaliação final.
Não altera o arquivo recebido, não inventa anotações e não calcula acurácia.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

SHA_CONTROLES = "a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc"
COLUNAS = ["id_controle", "texto", "polaridade", "referente", "papel_com", "observacoes"]
CATEGORIAS = {"positiva", "negativa", "neutra", "sem_avaliacao", "mista", "indeterminada"}
REFERENTES = {"agente", "acao", "objeto", "terceiro", "multiplos", "nenhum", "indeterminado"}
PAPEIS = {"modo", "instrumento", "companhia", "outro", "ambiguo", "nao_aplicavel"}
FORMAS_COLQUIAIS = {"positivo": "positiva", "negativo": "negativa"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ler_controles(path: Path) -> tuple[dict[str, str], str]:
    original = path.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != SHA_CONTROLES:
        raise ValueError("Hash do corpus de controles não corresponde à versão fixada.")
    txt = original.decode("utf-8-sig")
    r = csv.DictReader(io.StringIO(txt, newline=""), delimiter=";")
    if r.fieldnames != ["id_controle", "cenario", "texto"]:
        raise ValueError("Cabeçalho inesperado no corpus de controles.")
    linhas = list(r)
    if len(linhas) != 36 or any(None in x or any(y is None for y in x.values()) for x in linhas):
        raise ValueError("Corpus de controles incompleto ou malformado.")
    mapa = {x["id_controle"]: x["texto"] for x in linhas}
    if len(mapa) != len(linhas):
        raise ValueError("IDs duplicados no corpus de controles.")
    return mapa, digest


def ler_ficha(path: Path) -> tuple[list[dict[str, str]], str, str]:
    txt = path.read_bytes().decode("utf-8-sig")
    primeira = txt.splitlines()[0].strip() if txt.splitlines() else ""
    if primeira == ",".join(COLUNAS):
        sep = ","
    elif primeira == ";".join(COLUNAS):
        sep = ";"
    else:
        raise ValueError("Cabeçalho inesperado; a ficha deve ter seis colunas conhecidas.")
    reader = csv.DictReader(io.StringIO(txt, newline=""), delimiter=sep)
    linhas = list(reader)
    if not linhas:
        raise ValueError("Ficha vazia.")
    if any(None in x or any(y is None for y in x.values()) for x in linhas):
        raise ValueError("Ficha contém linha malformada, com colunas a mais ou a menos.")
    return linhas, sha(path), ("virgula" if sep == "," else "ponto_e_virgula")


def descrever(controles: dict[str, str], linhas: list[dict[str, str]], *,
              sha_controles: str, sha_ficha: str, separador: str) -> dict:
    ids = [r["id_controle"].strip() for r in linhas]
    repetidos = sorted(x for x, n in Counter(ids).items() if n > 1)
    if repetidos:
        raise ValueError("IDs repetidos: " + ", ".join(repetidos))
    if set(ids) != set(controles):
        falta = sorted(set(controles) - set(ids))
        extras = sorted(set(ids) - set(controles))
        raise ValueError(f"IDs não correspondem aos controles. Faltantes: {falta}; extras: {extras}.")
    texto_diferente = []
    texto_so_espacos = []
    for row in linhas:
        ident, atual = row["id_controle"].strip(), row["texto"]
        esperado = controles[ident]
        if atual != esperado:
            norm = lambda x: re.sub(r"\s+", " ", x).strip()
            (texto_so_espacos if norm(atual) == norm(esperado) else texto_diferente).append(ident)
    if texto_diferente:
        raise ValueError("Textos com diferença substantiva: " + ", ".join(texto_diferente))
    polaridades = Counter(row["polaridade"].strip().lower() for row in linhas)
    campos_vazios = {k: sum(not row[k].strip() for row in linhas)
                     for k in ("polaridade", "referente", "papel_com", "observacoes")}
    forma_nao_prevista = [x for x in polaridades if x not in CATEGORIAS and x not in FORMAS_COLQUIAIS and x != "neutro"]
    if forma_nao_prevista:
        raise ValueError("Categorias de polaridade desconhecidas: " + repr(forma_nao_prevista))
    referentes_fora_categorias = sorted(row["id_controle"] for row in linhas
                                       if row["referente"].strip() not in REFERENTES)
    papeis_invalidos = sorted(row["id_controle"] for row in linhas
                              if row["papel_com"].strip() and row["papel_com"].strip() not in PAPEIS)
    return {
        "bloco": 27,
        "fase": "ANALISE_DESCRITIVA_UNICO_AVALIADOR_FORA_DO_PROTOCOLO_ORIGINAL",
        "origem": {"ficha_sha256": sha_ficha, "controles_sha256": sha_controles,
                    "separador_ficha": separador},
        "avaliadores_com_resposta": 1,
        "n_controles": len(linhas),
        "ids_duplicados": repetidos,
        "id_texto_espacamento_divergente": sorted(texto_so_espacos),
        "polaridade_informada": dict(sorted(polaridades.items())),
        "polaridade_positiva_negativa_com_normalizacao_morfologica_possivel": sum(
            x in {"positivo", "negativo", "positiva", "negativa"}
            for x in (r["polaridade"].strip().lower() for r in linhas)),
        "neutro_generico_a_revisar": polaridades.get("neutro", 0),
        "campos_sem_preenchimento": campos_vazios,
        "referentes_fora_do_vocabulario_controlado": len(referentes_fora_categorias),
        "ids_referentes_fora_do_vocabulario": referentes_fora_categorias,
        "ids_papel_com_invalido": papeis_invalidos,
        "itens_para_conferir_por_pessoa": {
            "C001": "Verificar exposição prévia do exemplo ao avaliador; documentar possível contaminação.",
            "C003": "Texto do referente menciona outra profissão; confirmar se houve erro de preenchimento.",
            "C013": "Polaridade informada como neutro em 'com perícia'; confirmar leitura, sem substituí-la.",
            "C030": "Texto do referente menciona outra profissão; confirmar se houve erro de preenchimento.",
            "C033": "A frase contém sinais avaliativos diferentes; confirmar decisão de valência e texto com espaço duplicado.",
        },
        "kappa_cohen": None,
        "concordancia_entre_avaliadores": None,
        "acuracia": None,
        "f1_macro": None,
        "evidencia_de_vies": None,
        "dados_da_avaliacao_final_lidos": False,
        "decisao": "Aproveitar como anotação descritiva individual, não como referência humana consensual ou avaliação confirmatória.",
        "observacoes": [
            "As 36 polaridades são registros de um avaliador; não equivalem a 36 rótulos protocolarmente válidos.",
            "As formas positivo/negativo admitem normalização morfológica DOCUMENTADA, sem modificar os originais.",
            "Neutro genérico não é automaticamente igual a neutra ou sem_avaliacao do protocolo.",
            "Referente livre não substitui a categoria controlada. Papel de 'com' permaneceu sem anotação.",
            "Sem segundo avaliador, não há como estimar concordância interavaliadores ou adjudicar divergências.",
            "Este adendo foi elaborado após observar a primeira ficha, portanto é pós-coleta, não pré-registro.",
        ],
    }


def salvar(n: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(n, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Bloco 27: auditar uma ficha R01; nenhuma avaliação final.")
    p.add_argument("--entrada", type=Path, default=Path("data/piloto/restrito/ficha_controles_R01_recebida.csv"))
    p.add_argument("--controles", type=Path, default=Path("data/controles/controles_sintaticos_v01.csv"))
    p.add_argument("--saida", type=Path, default=Path("data/piloto/restrito/relatorio_r01_unica_bloco27.json"))
    args = p.parse_args()
    try:
        mapa, hc = ler_controles(args.controles)
        rows, ha, sep = ler_ficha(args.entrada)
        resumo = descrever(mapa, rows, sha_controles=hc, sha_ficha=ha, separador=sep)
        salvar(resumo, args.saida)
        print("Ficha auditada:", resumo["n_controles"], "respostas; avaliadores:", resumo["avaliadores_com_resposta"])
        print("Polaridades informadas:", resumo["polaridade_informada"])
        print("Campos sem resposta:", resumo["campos_sem_preenchimento"])
        print("Texto com espaçamento divergente:", resumo["id_texto_espacamento_divergente"])
        print("Saída privada:", args.saida)
        print("AVISO: nenhuma concordância, acurácia, F1 ou evidência de viés foi calculada.")
    except (ValueError, UnicodeError, OSError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
