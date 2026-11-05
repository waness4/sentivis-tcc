"""Importação fiel e auditoria estrutural de OpLexicon 3.0 e SentiLex-PT02.

Esta rotina NÃO implementa um classificador nem valida resultados científicos.
Os arquivos de entrada nunca são modificados.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
MD5_SENTILEX_OFICIAL = "026e1dceeaa506cc048d6ce7e0174cd0"
PADRAO_POS = re.compile(r"[.;]PoS=", re.IGNORECASE)
PADRAO_POL = re.compile(r"^POL:(N\d+)=(-?\d+)$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class EntradaLexical:
    origem: str
    arquivo: str
    linha: int
    termo: str
    lema: str | None
    categoria: str
    polaridades: tuple[tuple[str, int], ...]
    alvo: str | None
    flexao: str | None
    anotacao: str | None
    revisao: str | None
    atributos_originais: tuple[str, ...]
    atributos_sem_chave: tuple[str, ...] = ()


def _normalizar(termo: str) -> str:
    """Normalização apenas para chaves de auditoria; não altera o registro."""
    return unicodedata.normalize("NFC", termo.strip().casefold())


def _erro(arquivo: str, linha: int, motivo: str) -> ValueError:
    return ValueError(f"{arquivo}, linha {linha}: {motivo}")


def interpretar_sentilex(
    texto: str,
    *,
    arquivo: str,
    linha: int,
    flexionado: bool,
    permitir_polaridade_fora_padrao: bool = False,
    permitir_atributos_sem_chave: bool = False,
) -> EntradaLexical:
    """Preserva diferentes POL:N0/N1, categoria, alvo, anotação, FLEX e atributos."""
    texto = texto.strip()
    separador = PADRAO_POS.search(texto)
    if separador is None:
        raise _erro(arquivo, linha, "marcador .PoS= (ou ;PoS=) ausente")

    inicio = texto[: separador.start()]
    atributos = ("PoS=" + texto[separador.end() :]).split(";")
    if flexionado:
        if "," not in inicio:
            raise _erro(arquivo, linha, "forma flexionada sem separador de lema")
        termo, lema = inicio.split(",", 1)
    else:
        termo, lema = inicio, inicio

    if not termo.strip() or not lema.strip():
        raise _erro(arquivo, linha, "termo/lema vazio")

    categoria = None
    alvo = None
    flexao = None
    anotacao = None
    revisao = None
    polaridades = []
    atributos_sem_chave = []
    vistos = set()

    for atributo in atributos:
        atributo = atributo.strip()
        if not atributo:
            raise _erro(arquivo, linha, "atributo vazio")
        # O SentiLex-PT02 documenta explicitamente REV:POL (sem '=').
        # Equivale semanticamente a revisão de polaridade, não a uma
        # entrada POL:N0/N1; o texto literal continua preservado abaixo.
        # Não relaxar a validação para atributos desconhecidos sem '='.
        if atributo.upper() == "REV:POL":
            revisao = "POL"
            continue
        k, separador_igual, valor = atributo.partition("=")
        if separador_igual != "=":
            if permitir_atributos_sem_chave:
                # A distribuição contém fragmentos sem CHAVE=valor. NÃO presumir
                # que pertençam a FLEX: registrar literalmente a anomalia.
                atributos_sem_chave.append(atributo)
                continue
            raise _erro(arquivo, linha, f"atributo malformado: {atributo!r}")
        chave = k.upper()
        if chave == "POS":
            categoria = valor
        elif chave == "TG":
            alvo = valor
        elif chave == "FLEX":
            flexao = valor
        elif chave == "ANOT":
            anotacao = valor
        elif chave == "REV":
            revisao = valor
        elif chave.startswith("POL:"):
            match = PADRAO_POL.fullmatch(atributo)
            if match is None:
                raise _erro(arquivo, linha, f"polaridade malformada: {atributo!r}")
            papel, valor_polaridade = match.groups()
            papel = papel.upper()
            if papel in vistos:
                raise _erro(arquivo, linha, f"polaridade repetida para {papel}")
            vistos.add(papel)
            valor_int = int(valor_polaridade)
            # A distribuição original contém exceções documentáveis, como valores 8 e 7.
            # A leitura estrita (padrão) continua rejeitando esses valores para impedir
            # sua utilização acidental como polaridade válida de um classificador.
            # Somente a auditoria estrutural os lê, preserva e contabiliza.
            if valor_int not in (-1, 0, 1) and not permitir_polaridade_fora_padrao:
                raise _erro(arquivo, linha, f"polaridade fora de -1/0/1: {valor_int}")
            polaridades.append((papel, valor_int))
        # Atributos não reconhecidos ficam preservados em atributos_originais.

    if not categoria or not polaridades:
        raise _erro(arquivo, linha, "categoria ou polaridade ausente")
    return EntradaLexical(
        origem="sentilex_flex" if flexionado else "sentilex_lem",
        arquivo=arquivo,
        linha=linha,
        termo=termo,
        lema=lema,
        categoria=categoria,
        polaridades=tuple(polaridades),
        alvo=alvo,
        flexao=flexao,
        anotacao=anotacao,
        revisao=revisao,
        atributos_originais=tuple(atributos),
        atributos_sem_chave=tuple(atributos_sem_chave),
    )


def interpretar_oplexicon(texto: str, *, arquivo: str, linha: int) -> EntradaLexical:
    """Interpreta os quatro campos originais, sem perder termo ou categoria."""
    try:
        campos = next(csv.reader([texto], delimiter=",", strict=True))
    except csv.Error as exc:
        raise _erro(arquivo, linha, f"CSV inválido: {exc}") from exc
    if len(campos) != 4:
        raise _erro(arquivo, linha, f"esperados 4 campos; encontrados {len(campos)}")
    termo, categoria, pol, anotacao = (campo.strip() for campo in campos)
    if not termo or not categoria or not anotacao:
        raise _erro(arquivo, linha, "termo/categoria/origem da anotação vazio")
    try:
        valor = int(pol)
    except ValueError as exc:
        raise _erro(arquivo, linha, f"polaridade não numérica: {pol!r}") from exc
    if valor not in (-1, 0, 1):
        raise _erro(arquivo, linha, f"polaridade fora de -1/0/1: {valor}")
    return EntradaLexical(
        origem="oplexicon",
        arquivo=arquivo,
        linha=linha,
        termo=termo,
        lema=None,
        categoria=categoria,
        polaridades=(("GLOBAL", valor),),
        alvo=None,
        flexao=None,
        anotacao=anotacao,
        revisao=None,
        atributos_originais=tuple(campos),
    )


def ler_entradas(
    caminho: Path, *, tipo: str, permitir_polaridade_fora_padrao: bool = False,
    permitir_atributos_sem_chave: bool = False,
) -> Iterator[EntradaLexical]:
    """Leitura estrita UTF-8: falhas não são descartadas silenciosamente."""
    with Path(caminho).open("r", encoding="utf-8-sig", newline="") as stream:
        for numero, linha in enumerate(stream, start=1):
            if not linha.strip():
                raise _erro(caminho.name, numero, "linha vazia")
            if tipo == "oplexicon":
                yield interpretar_oplexicon(linha, arquivo=caminho.name, linha=numero)
            elif tipo in ("sentilex_lem", "sentilex_flex"):
                yield interpretar_sentilex(
                    linha,
                    arquivo=caminho.name,
                    linha=numero,
                    flexionado=(tipo == "sentilex_flex"),
                    permitir_polaridade_fora_padrao=permitir_polaridade_fora_padrao,
                    permitir_atributos_sem_chave=permitir_atributos_sem_chave,
                )
            else:
                raise ValueError(f"Tipo de léxico desconhecido: {tipo}")


def _hash_arquivo(caminho: Path, algoritmo: str = "sha256") -> str:
    resumo = hashlib.new(algoritmo)
    with caminho.open("rb") as stream:
        for bloco in iter(lambda: stream.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def auditar(caminho: Path, *, tipo: str) -> dict:
    categorias: Counter[str] = Counter()
    polaridades: Counter[str] = Counter()
    anotacoes: Counter[str] = Counter()
    flexoes: Counter[str] = Counter()
    alvos: Counter[str] = Counter()
    revisoes: Counter[str] = Counter()
    termos = set()
    linhas = 0  # registros interpretados e auditados
    linhas_totais = 0  # linhas físicas no arquivo de origem
    linhas_nao_interpretaveis = 0
    exemplos_erros_estrutura: list[dict] = []
    registros_com_atributos_sem_chave = 0
    ocorrencias_atributos_sem_chave = 0
    exemplos_atributos_sem_chave: list[dict] = []
    multilavra = 0
    ocorrencias_por_chave: Counter[tuple[str, str]] = Counter()
    polaridades_por_chave: dict[tuple[str, str], set[tuple[tuple[str, int], ...]]] = defaultdict(set)
    registros_com_polaridade_fora_padrao = 0
    ocorrencias_polaridade_fora_padrao = 0
    exemplos_polaridade_fora_padrao: list[dict] = []

    # A auditoria examina TODAS as linhas e registra as malformadas.
    # A leitura operacional (ler_entradas) continua estrita e rejeita anomalias.
    with Path(caminho).open("r", encoding="utf-8-sig", newline="") as stream:
      for numero, texto in enumerate(stream, start=1):
        linhas_totais += 1
        try:
            if not texto.strip():
                raise _erro(caminho.name, numero, "linha vazia")
            if tipo == "oplexicon":
                entrada = interpretar_oplexicon(texto, arquivo=caminho.name, linha=numero)
            elif tipo in ("sentilex_lem", "sentilex_flex"):
                entrada = interpretar_sentilex(
                    texto, arquivo=caminho.name, linha=numero,
                    flexionado=(tipo == "sentilex_flex"),
                    permitir_polaridade_fora_padrao=True,
                    permitir_atributos_sem_chave=True,
                )
            else:
                raise ValueError(f"Tipo de léxico desconhecido: {tipo}")
        except ValueError as exc:
            linhas_nao_interpretaveis += 1
            if len(exemplos_erros_estrutura) < 50:
                exemplos_erros_estrutura.append({
                    "arquivo": caminho.name, "linha": numero,
                    "erro": str(exc), "registro_original": texto.rstrip("\r\n"),
                })
            continue
        linhas += 1
        if entrada.atributos_sem_chave:
            registros_com_atributos_sem_chave += 1
            ocorrencias_atributos_sem_chave += len(entrada.atributos_sem_chave)
            if len(exemplos_atributos_sem_chave) < 50:
                exemplos_atributos_sem_chave.append({
                    "arquivo": entrada.arquivo, "linha": entrada.linha,
                    "termo": entrada.termo,
                    "atributos_sem_chave": list(entrada.atributos_sem_chave),
                    "registro_original": texto.rstrip("\r\n"),
                })
        chave = (_normalizar(entrada.termo), entrada.categoria)
        termos.add(chave[0])
        categorias[entrada.categoria] += 1
        anotacoes[entrada.anotacao or "NÃO_INFORMADO"] += 1
        alvos[entrada.alvo or "NÃO_INFORMADO"] += 1
        flexoes[entrada.flexao or "NÃO_INFORMADO"] += 1
        revisoes[entrada.revisao or "NÃO_INFORMADO"] += 1
        ocorrencias_por_chave[chave] += 1
        polaridades_por_chave[chave].add(tuple(sorted(entrada.polaridades)))
        if " " in entrada.termo.strip():
            multilavra += 1
        for papel, valor in entrada.polaridades:
            polaridades[f"{papel}:{valor}"] += 1
        fora_padrao = [
            {"alvo": papel, "valor_original": valor}
            for papel, valor in entrada.polaridades
            if valor not in (-1, 0, 1)
        ]
        if fora_padrao:
            registros_com_polaridade_fora_padrao += 1
            ocorrencias_polaridade_fora_padrao += len(fora_padrao)
            if len(exemplos_polaridade_fora_padrao) < 30:
                exemplos_polaridade_fora_padrao.append({
                    "arquivo": entrada.arquivo,
                    "linha": entrada.linha,
                    "termo": entrada.termo,
                    "polaridades_invalidas": fora_padrao,
                    "atributos_originais": list(entrada.atributos_originais),
                })

    chaves_conflitantes = [chave for chave, versoes in polaridades_por_chave.items() if len(versoes) > 1]
    return {
        "arquivo": caminho.name,
        "tipo": tipo,
        "tamanho_bytes": caminho.stat().st_size,
        "sha256": _hash_arquivo(caminho),
        "registros": linhas,
        "linhas_totais": linhas_totais,
        "linhas_nao_interpretaveis": linhas_nao_interpretaveis,
        "exemplos_erros_estrutura": exemplos_erros_estrutura,
        "registros_com_atributos_sem_chave": registros_com_atributos_sem_chave,
        "ocorrencias_atributos_sem_chave": ocorrencias_atributos_sem_chave,
        "exemplos_atributos_sem_chave": exemplos_atributos_sem_chave,
        "alerta_estrutura": (
            "Há dados fora do esquema esperado. Preservados/contabilizados para "
            "auditoria, NÃO utilizar sem decisão metodológica documentada."
            if linhas_nao_interpretaveis or registros_com_atributos_sem_chave else None
        ),
        "formas_unicas_normalizadas": len(termos),
        "expressoes_multiplas_palavras": multilavra,
        "chaves_termo_categoria_repetidas": sum(n - 1 for n in ocorrencias_por_chave.values() if n > 1),
        "chaves_com_polaridades_divergentes": len(chaves_conflitantes),
        "exemplos_de_chaves_divergentes": [
            {"termo": termo, "categoria": categoria} for termo, categoria in chaves_conflitantes[:10]
        ],
        "categorias": dict(sorted(categorias.items())),
        "polaridades_por_alvo": dict(sorted(polaridades.items())),
        "registros_com_polaridade_fora_padrao": registros_com_polaridade_fora_padrao,
        "ocorrencias_polaridade_fora_padrao": ocorrencias_polaridade_fora_padrao,
        "exemplos_polaridade_fora_padrao": exemplos_polaridade_fora_padrao,
        "alerta_polaridades": (
            "Polaridades fora de -1/0/1 preservadas apenas para auditoria; "
            "NÃO usar essas entradas em classificação sem regra científica pré-especificada."
            if registros_com_polaridade_fora_padrao else None
        ),
        "anotacoes": dict(sorted(anotacoes.items())),
        "alvos": dict(sorted(alvos.items())),
        "flexoes": dict(sorted(flexoes.items())),
        "revisoes": dict(sorted(revisoes.items())),
    }


def _encontrar_unico(pasta: Path, nome: str) -> Path:
    encontrados = sorted(pasta.rglob(nome))
    if len(encontrados) != 1:
        raise FileNotFoundError(
            f"Esperado exatamente um arquivo {nome!r} em {pasta}; encontrados: {len(encontrados)}"
        )
    return encontrados[0]


def gerar_relatorio(raiz: Path) -> tuple[Path, dict]:
    originais = raiz / "data" / "lexicos" / "originais"
    if not originais.is_dir():
        raise FileNotFoundError(f"Pasta inexistente: {originais}")

    nomes = {
        "oplexicon": "lexico_v3.0.txt",
        "sentilex_lem": "SentiLex-lem-PT02.txt",
        "sentilex_flex": "SentiLex-flex-PT02.txt",
    }
    auditorias = {
        tipo: auditar(_encontrar_unico(originais, nome), tipo=tipo)
        for tipo, nome in nomes.items()
    }
    zip_sentilex = _encontrar_unico(originais, "SentiLex-PT02.zip")
    md5_zip = _hash_arquivo(zip_sentilex, "md5")
    relatorio = {
        "fase": "auditoria_estrutural_nao_validacao_cientifica",
        "metodo": "Preservação de registros originais, múltiplos alvos e metadados; sem classificação de frases.",
        "sentilex_zip": {
            "nome": zip_sentilex.name,
            "sha256": _hash_arquivo(zip_sentilex),
            "md5": md5_zip,
            "md5_publicado_b2share": MD5_SENTILEX_OFICIAL,
            "md5_coincide_com_publicado": md5_zip == MD5_SENTILEX_OFICIAL,
            "fonte": "https://b2share.eudat.eu/records/cbyr7-dkf18",
        },
        "oplexicon_fonte_copia": "https://github.com/marlovss/OpLexicon/blob/main/lexico_v3.0.txt",
        "aviso": "Comparar a cópia do OpLexicon com a distribuição oficial quando disponível e confirmar direitos de redistribuição.",
        "arquivos": auditorias,
    }
    destino = raiz / "data" / "lexicos" / "relatorio_auditoria.json"
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino, relatorio


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria estrutural dos léxicos originais do SentiVis")
    parser.add_argument("--raiz", type=Path, default=ROOT, help="Raiz do projeto SentiVis")
    args = parser.parse_args()
    try:
        destino, relatorio = gerar_relatorio(args.raiz.resolve())
    except (FileNotFoundError, UnicodeError, ValueError) as exc:
        parser.exit(status=1, message=f"ERRO: {exc}\n")
    print(f"Relatório salvo em: {destino}")
    for tipo, dados in relatorio["arquivos"].items():
        print(
            f"{tipo}: {dados['registros']}/{dados['linhas_totais']} registros interpretados; "
            f"{dados['linhas_nao_interpretaveis']} linhas não interpretáveis; "
            f"{dados['registros_com_atributos_sem_chave']} registros com atributos sem chave; "
            f"{dados['chaves_com_polaridades_divergentes']} chaves com polaridades divergentes; "
            f"{dados['expressoes_multiplas_palavras']} expressões com múltiplas palavras; "
            f"{dados['registros_com_polaridade_fora_padrao']} registros com polaridade fora do padrão"
        )
    zip_info = relatorio["sentilex_zip"]
    print("SentiLex ZIP — MD5 oficial confere:", zip_info["md5_coincide_com_publicado"])
    print("IMPORTANTE: auditoria estrutural concluída; classificador ainda NÃO está validado.")
    print("Anomalias de formato e polaridades não autorizam classificação científica.")


if __name__ == "__main__":
    main()
