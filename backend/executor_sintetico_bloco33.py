"""Bloco 33 — contrato de execução experimental ensaiado em 27 pares INVENTADOS.

A CLI NÃO aceita caminhos nem executa avaliação real. O ensaio usa apenas
fixtures literais SINT*, léxico artificial e etiquetador artificial. A função
principal verifica cada frase contra uma fixture conhecida ANTES de pontuar.
Nenhum corpus/arquivo da partição reservada é importado ou lido.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
from typing import Callable

from backend.avaliacao_final_preparacao_bloco29 import (
    METODOS, PONTUADO, _EtiquetadorFicticio, _ficticios, _validar_saida,
    resumir, validar_ficha,
)

VERSAO = "bloco33_executor_ensaio_sintetico_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = Path("data/piloto/restrito/bloco33_ensaio")
CAMPOS_LOTE = frozenset({"id_par", "familia", "particao", "frase_feminina", "frase_masculina"})
COLUNAS_FICHA = ("id_par", "frase_feminina", "frase_masculina", "equivalencia", "rotulo", "observacoes")
N_PARES = 27
N_FAMILIAS = 9


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixture_27() -> tuple[list[dict], list[dict]]:
    """Repete 4 exemplos públicos INVENTADOS em 9 famílias artificiais.

    Não equivale a 27 exemplos linguísticos independentes; serve somente ao
    teste de estrutura/contagem. Sem leitura externa, sem varredura de arquivos.
    """
    amostras, gabarito_ficticio = _ficticios()
    pares, respostas = [], []
    for i in range(N_PARES):
        modelo = amostras[i % 4]
        resposta = gabarito_ficticio[i % 4]
        ident = f"SINT{i + 1:03d}"
        p = {
            "id_par": ident, "familia": f"SINT_FAM{i // 3 + 1:02d}",
            "particao": "sintetica",
            "frase_feminina": modelo["frase_feminina"],
            "frase_masculina": modelo["frase_masculina"],
        }
        pares.append(p)
        respostas.append({
            "id_par": ident, "frase_feminina": p["frase_feminina"],
            "frase_masculina": p["frase_masculina"],
            "equivalencia": resposta["equivalencia"],
            "rotulo": resposta["rotulo"], "observacoes": resposta["observacoes"],
        })
    return pares, respostas


def validar_lote_ficticio(pares: list[dict]) -> None:
    """Bloqueia qualquer frase/ID externo, mesmo com prefixo SINT."""
    padrao, _ = fixture_27()
    if not isinstance(pares, list) or len(pares) != N_PARES:
        raise ValueError("Lote fictício exige exatamente 27 pares")
    if any(not isinstance(p, dict) or set(p) != CAMPOS_LOTE for p in pares):
        raise ValueError("Esquema do lote fictício inválido")
    if pares != padrao:
        raise ValueError("Lote diferente da fixture fictícia fixa: entrada externa BLOQUEADA")
    ids = {p["id_par"] for p in pares}
    familias = {p["familia"] for p in pares}
    if len(ids) != N_PARES or len(familias) != N_FAMILIAS or any(
        not re.fullmatch(r"SINT\d{3}", p["id_par"]) or p["particao"] != "sintetica"
        for p in pares
    ):
        raise ValueError("IDs, partição ou famílias fictícias divergentes")
    for familia in familias:
        if sum(p["familia"] == familia for p in pares) != 3:
            raise ValueError("Cada família fictícia deve possuir 3 pares")


def ficha_cega_csv(pares: list[dict]) -> str:
    """Somente ficha sem previsões; não contém família, gabarito ou resultados."""
    validar_lote_ficticio(pares)
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=COLUNAS_FICHA, delimiter=";", lineterminator="\n")
    writer.writeheader()
    for p in pares:
        writer.writerow({chave: p[chave] if chave in p else "" for chave in COLUNAS_FICHA})
    return buf.getvalue()


def validar_ficha_ficticia(pares: list[dict], ficha: list[dict]) -> dict:
    validar_lote_ficticio(pares)
    # Exigir que a anotação anteceda as predições; não exigir resposta para simular
    # falhas de preenchimento, mas jamais completar lacunas por inferência.
    return validar_ficha(pares, ficha)


def _modelo_ficticio():
    from backend.frase_diagnostico import IndiceLexical
    from backend.lexicon_audit import EntradaLexical

    def entrada(termo: str, nota: int, linha: int) -> EntradaLexical:
        return EntradaLexical(
            origem="sentilex_flex", arquivo="FICTICIO", linha=linha,
            termo=termo, lema=termo, categoria="N", polaridades=(("N0", nota),),
            alvo="HUM:N0", flexao=None, anotacao="MAN", revisao=None,
            atributos_originais=(),
        )

    return (IndiceLexical([
        entrada("gentileza", 1, 1), entrada("grosseria", -1, 2),
    ], lexico="sentilex"), _EtiquetadorFicticio())


def _classificadores():
    from backend.baseline_experimental import classificar_exploratoriamente
    from backend.baseline_contextual_v03 import classificar_v03
    from backend.baseline_contextual_v04 import classificar_v04
    return {"v01": classificar_exploratoriamente,
            "v03": classificar_v03, "v04": classificar_v04}


def _somente_contrato(saida: dict) -> dict:
    """Faz validação rigorosa e remove diagnóstico, textos e metadados livres."""
    pontuado, nota, classe, status = _validar_saida(saida)
    return {"status": status, "pontuacao_exploratoria": nota,
            "classe_exploratoria": classe}


def executar_em_memoria(
    pares: list[dict], ficha: list[dict], *,
    indice=None, nlp=None, classificadores: dict[str, Callable] | None = None,
) -> dict:
    """Executa os 3 baselines APENAS nos 27 pares inventados.

    Qualquer erro é propagado. Falhas não são convertidas em abstenções e não
    produzem resumo parcial com aparência de ensaio completo.
    """
    validar_lote_ficticio(pares)
    anotacoes = validar_ficha_ficticia(pares, ficha)  # antes de QUALQUER predição
    if indice is None or nlp is None:
        if indice is not None or nlp is not None:
            raise ValueError("Índice e etiquetador devem ser fornecidos juntos")
        indice, nlp = _modelo_ficticio()
    if getattr(indice, "lexico", None) != "sentilex":
        raise ValueError("Ensaio requer índice SentiLex fictício")
    funcs = _classificadores() if classificadores is None else classificadores
    if set(funcs) != set(METODOS) or any(not callable(f) for f in funcs.values()):
        raise ValueError("Conjunto de baselines divergente de V01/V03/V04")

    predicoes = {}
    for par in pares:
        ident = par["id_par"]
        predicoes[ident] = {}
        for metodo in METODOS:
            por_lado = {}
            for lado in ("feminina", "masculina"):
                texto = par["frase_" + lado]
                if metodo == "v01":
                    bruto = funcs[metodo](texto, indice, alvo="N0", incluir_diagnostico=False)
                else:
                    bruto = funcs[metodo](texto, indice, alvo="N0", nlp=nlp,
                                           hipotese_modo=True, incluir_diagnostico=False)
                por_lado[lado] = _somente_contrato(bruto)
            predicoes[ident][metodo] = por_lado
    resumo = resumir(pares, list(anotacoes.values()), predicoes)
    if resumo["P_total"] != N_PARES or resumo["F_total"] != 2 * N_PARES:
        raise ValueError("Contagens de ensaio inconsistentes")
    for metodo in METODOS:
        r = resumo["metodos"][metodo]
        if r["F_pontuadas_global"] + r["F_abstidas_global"] != 2 * N_PARES:
            raise ValueError("Pontuadas e abstidas não somam 54")
        if r["F_pontuadas_elegiveis"] + r["F_abstidas_elegiveis"] != resumo["F_elegiveis"]:
            raise ValueError("Contagens elegíveis inconsistentes")
        if r["P_delta_calculavel"] + r["P_delta_nao_calculavel"] != resumo["P_equivalentes_R01"]:
            raise ValueError("Contagens de pares com delta inconsistentes")
    return {
        "versao": VERSAO,
        "fase": "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL",
        "estado": ESTADO,
        "avaliacao_final_executada": False,
        "avaliacao_final_autorizada": False,
        "protocolo_congelado": False,
        "fonte": "FIXTURE_FICTICIA_FIXA_27_PARES_9_FAMILIAS",
        "etiquetador": "_EtiquetadorFicticio_NAO_SPACY",
        "lexico": "GENTILEZA_E_GROSSERIA_FICTICIOS_NAO_SENTILEX_REAL",
        "parametros": {"alvo_manual": "N0", "hipotese_modo_v03": True,
                       "hipotese_modo_v04": True, "diagnostico": False},
        "resumo": resumo,
        "resultados_por_par_somente_sinteticos": predicoes,
        "concordancia_interavaliadores": None,
        "acuracia_validada": None,
        "evidencia_de_vies": None,
        "aviso": "A repetição de exemplos inventados e os resultados de testes não validam modelos ou vieses.",
    }


def verificar_contrato() -> dict:
    """Consulta estática de configuração: não lê nem grava entradas."""
    pares, _ = fixture_27()
    validar_lote_ficticio(pares)
    return {
        "versao": VERSAO, "estado": ESTADO,
        "modos_cli": ["verificar-contrato", "ensaiar"],
        "n_pares_sinteticos": N_PARES,
        "n_familias_sinteticas": N_FAMILIAS,
        "analise_primaria_proposta": "SentiLex-PT02 V01/V03/V04",
        "alvo_manual": "N0", "hipotese_modo_v03_v04": True,
        "dados_reservados_lidos": False, "autorizacao_execucao_final": False,
        "programa_real_implementado": False,
        "nota": "Contrato experimental sintético. Um fluxo real exige aprovação e implementação específica.",
    }


def _criar_exclusivo(path: Path, dados: dict):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
        json.dump(dados, out, indent=2, ensure_ascii=False, sort_keys=True)
        out.write("\n")


def _pasta_segura(raiz: Path) -> Path:
    raiz = raiz.resolve(strict=True)
    if not raiz.is_dir():
        raise ValueError("Raiz inválida")
    destino = raiz
    for parte in DESTINO.parts:
        destino = destino / parte
        if destino.is_symlink():
            raise ValueError("Destino do ensaio não pode conter link simbólico")
    destino.mkdir(parents=True, exist_ok=True)
    if not destino.resolve(strict=True).is_relative_to(raiz):
        raise ValueError("Destino fora da raiz")
    return destino


def ensaiar_unica_vez(raiz: Path = RAIZ, *, executor=None) -> dict:
    """Marca a tentativa ANTES de pontuar; nunca sobrescreve nem libera rerun."""
    raiz = Path(raiz).resolve(strict=True)
    pasta = _pasta_segura(raiz)
    marcador = pasta / "marcador_tentativa_bloco33.json"
    relatorio = pasta / "relatorio_sintetico_bloco33.json"
    if relatorio.exists():
        raise FileExistsError("Relatório já existe; execução bloqueada")
    pares, ficha = fixture_27()
    validar_ficha_ficticia(pares, ficha)
    ficha_cega = ficha_cega_csv(pares)
    # Registrar apenas hashes inventados, sem frases/observações no relatório.
    sha_ficha_cega = _hash(ficha_cega.encode("utf-8"))
    digest_anotacoes_ficticias = _hash(json.dumps(ficha, ensure_ascii=False,
                                                   sort_keys=True).encode("utf-8"))
    reserva = {
        "fase": "TENTATIVA_SINTETICA_RESERVADA",
        "versao": VERSAO,
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "sha256_ficha_cega_ficticia": sha_ficha_cega,
        "sha256_anotacoes_ficticias": digest_anotacoes_ficticias,
        "avaliacao_final_executada": False,
    }
    _criar_exclusivo(marcador, reserva)
    # Uma falha a seguir preserva o marcador e não permite fingir primeiro ensaio.
    resultado = executar_em_memoria(pares, ficha) if executor is None else executor(pares, ficha)
    if (not isinstance(resultado, dict) or
            resultado.get("fase") != "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL" or
            resultado.get("avaliacao_final_executada") is not False or
            resultado.get("resumo", {}).get("P_total") != N_PARES):
        raise ValueError("Executor retornou contrato incompatível com ensaio fictício")
    _criar_exclusivo(relatorio, {"reserva": reserva, "ensaio": resultado})
    return {
        "estado": "ENSAIO_SINTETICO_CONCLUIDO",
        "n_pares_ficticios": N_PARES,
        "n_familias_ficticias": N_FAMILIAS,
        "relatorio_privado": DESTINO.joinpath(relatorio.name).as_posix(),
        "reexecucao_bloqueada": True,
        "avaliacao_final_executada": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bloco 33: somente ensaio artificial, sem avaliação real ou arquivos externos"
    )
    parser.add_argument("modo", choices=("verificar-contrato", "ensaiar"))
    args = parser.parse_args()
    try:
        resposta = verificar_contrato() if args.modo == "verificar-contrato" else ensaiar_unica_vez()
        print(json.dumps(resposta, indent=2, ensure_ascii=False))
        print("AVISO: avaliação final e acesso aos 27 pares reservados NÃO autorizados.")
    except (ValueError, FileExistsError, FileNotFoundError, OSError, RuntimeError) as erro:
        parser.exit(1, f"BLOQUEADO: {erro}\nPreserve os registros; não repita um ensaio após falha.\n")


if __name__ == "__main__":
    main()
