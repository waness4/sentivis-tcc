"""Bloco 36 — ensaio sintético de decisão G03 sobre anotações incompletas.

NENHUM modo lê dados de avaliação, recebe caminhos, congela ou executa o estudo.
O lote de 27 pares é a fixture imutável do Bloco 33; a entrada de 14 colunas
é a fixture literal do Bloco 34. A política real AINDA NÃO FOI APROVADA.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from typing import Any, Callable

from backend.executor_final_bloqueado_bloco34 import (
    _fixture_14, _ficha_ficticia_preenchida, validar_origem_ficticia,
)
from backend.executor_sintetico_bloco33 import executar_em_memoria
from backend.preflight_avaliacao_bloco30 import COLUNAS_FICHA, validar_conteudo_ficha_csv

VERSAO = "bloco36_ensaio_politicas_nao_resposta_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
POLITICA_ESTRITA = "bloquear_ficha_pendente"
POLITICA_CONTABILIZAR = "contabilizar_pendente_nao_elegivel"
POLITICAS = frozenset({POLITICA_ESTRITA, POLITICA_CONTABILIZAR})
POLITICA_APROVADA = None  # exige deliberação humana verificável; nunca inferir do código


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _csv(linhas: list[dict[str, str]]) -> str:
    destino = io.StringIO(newline="")
    writer = csv.DictWriter(destino, fieldnames=COLUNAS_FICHA,
                            delimiter=";", lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(linhas)
    return destino.getvalue()


def cenario_ficticio(*, inserir_pendencia: bool) -> tuple[str, str]:
    """Produz somente dois textos sintéticos de origem/ficha, sem arquivo de entrada."""
    fonte = _fixture_14()
    pares = validar_origem_ficticia(fonte)
    ficha = _ficha_ficticia_preenchida(pares)
    if not inserir_pendencia:
        return fonte, ficha
    leitor = csv.DictReader(io.StringIO(ficha), delimiter=";", strict=True)
    linhas = list(leitor)
    if len(linhas) != 27 or linhas[0]["equivalencia"] != "sim":
        raise RuntimeError("Fixture de anotação inesperada")
    linhas[0]["equivalencia"] = ""
    linhas[0]["rotulo"] = ""
    linhas[0]["observacoes"] = ""  # não inventar julgamento de R01
    return fonte, _csv(linhas)


def preparar_anotacoes_sinteticas(conteudo_fonte: str, conteudo_ficha: str, *,
                                 politica: str) -> tuple[list[dict], list[dict], int]:
    """Validação humana ANTES da classificação; só aceita fonte sintética fixa.

    Estrita: qualquer par sem equivalência impede TODO o processamento.
    Contabilizar: equivalência vazia fica não elegível, mas permanece no total.
    Valores malformados, textos alterados, IDs repetidos e sim sem rótulo
    são sempre erros, independentemente da política.
    """
    if politica not in POLITICAS:
        raise ValueError("Política G03 desconhecida ou ainda não deliberada")
    pares = validar_origem_ficticia(conteudo_fonte)
    anotacoes = validar_conteudo_ficha_csv(conteudo_ficha, pares)
    pendentes = sum(a["equivalencia"] == "" for a in anotacoes.values())
    if politica == POLITICA_ESTRITA and pendentes:
        raise ValueError(f"Ficha incompleta: {pendentes} par(es) sem decisão humana")
    # Preservar a ordem original; jamais completar a anotação.
    return pares, [anotacoes[p["id_par"]] for p in pares], pendentes


def executar_ensaio_sintetico(conteudo_fonte: str, conteudo_ficha: str, *,
                              politica: str, executor: Callable | None = None) -> dict[str, Any]:
    """Sempre usa a mesma fixture sintética do Bloco 33.

    Nunca lê arquivos, não salva relatório nem executa o estudo real. A
    política é um parâmetro do ENSAIO e NÃO registra escolha acadêmica.
    """
    pares, anotacoes, pendentes = preparar_anotacoes_sinteticas(
        conteudo_fonte, conteudo_ficha, politica=politica,
    )
    classificar = executar_em_memoria if executor is None else executor
    resultado = classificar(pares, anotacoes)
    if (not isinstance(resultado, dict)
            or resultado.get("fase") != "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL"
            or resultado.get("avaliacao_final_executada") is not False
            or not isinstance(resultado.get("resumo"), dict)):
        raise ValueError("Executor de ensaio não retornou contrato sintético")
    resumo = resultado["resumo"]
    if (resumo.get("fase") != "SIMULACAO_SINTETICA_SEM_ACESSO_AVALIACAO_FINAL"
            or resumo.get("P_total") != 27 or resumo.get("F_total") != 54
            or resumo.get("P_nao_elegiveis_por_motivo", {}).get("sem_resposta", 0) != pendentes
            or set(resumo.get("metodos", {})) != {"v01", "v03", "v04"}):
        raise ValueError("Métricas do ensaio não representam as anotações sintéticas")
    for metodo, m in resumo["metodos"].items():
        if (m["F_pontuadas_global"] + m["F_abstidas_global"] != 54
                or m["F_pontuadas_elegiveis"] + m["F_abstidas_elegiveis"] != resumo["F_elegiveis"]
                or m["P_delta_calculavel"] + m["P_delta_nao_calculavel"] != resumo["P_equivalentes_R01"]):
            raise ValueError("Contagem inconsistente no método " + metodo)
    return {
        "versao": VERSAO,
        "fase": "SIMULACAO_POLITICAS_G03_FICTICIA",
        "estado": ESTADO,
        "politica_simulada_nao_aprovada": politica,
        "P_sem_resposta": pendentes,
        "sha256_fonte_sintetica": _sha(conteudo_fonte),
        "sha256_ficha_sintetica": _sha(conteudo_ficha),
        "resumo_sintetico": resumo,
        "aprovacao_academica_registrada": False,
        "protocolo_congelado": False,
        "autorizacao_execucao_final": False,
        "avaliacao_final_executada": False,
        "dados_reservados_lidos": False,
        "acuracia_validada": None,
        "concordancia_interavaliadores": None,
        "evidencia_de_vies": None,
        "nota": "Somente comparação técnica de opções; exige escolha metodológica antes da abertura.",
    }


def comparar_opcoes() -> dict[str, Any]:
    """Apresenta impacto da lacuna artificial sem escolher política definitiva."""
    fonte, completa = cenario_ficticio(inserir_pendencia=False)
    _, incompleta = cenario_ficticio(inserir_pendencia=True)
    completa_resultado = executar_ensaio_sintetico(
        fonte, completa, politica=POLITICA_ESTRITA,
    )
    try:
        executar_ensaio_sintetico(fonte, incompleta, politica=POLITICA_ESTRITA)
    except ValueError as erro:
        bloqueio = str(erro)
    else:
        raise RuntimeError("Política estrita não bloqueou ficha incompleta")
    resultado_contabilizado = executar_ensaio_sintetico(
        fonte, incompleta, politica=POLITICA_CONTABILIZAR,
    )
    return {
        "versao": VERSAO,
        "estado": ESTADO,
        "politica_aprovada": POLITICA_APROVADA,
        "ensaio_somente_ficticio": True,
        "cenario_ficha_completa": {
            "P_equivalentes": completa_resultado["resumo_sintetico"]["P_equivalentes_R01"],
            "P_nao_elegiveis": completa_resultado["resumo_sintetico"]["P_nao_elegiveis"],
        },
        "cenario_uma_resposta_ausente": {
            "opcao_bloquear": {"pontuacao_iniciada": False, "motivo": bloqueio},
            "opcao_contabilizar": {
                "P_total": resultado_contabilizado["resumo_sintetico"]["P_total"],
                "F_total": resultado_contabilizado["resumo_sintetico"]["F_total"],
                "P_equivalentes": resultado_contabilizado["resumo_sintetico"]["P_equivalentes_R01"],
                "P_nao_elegiveis": resultado_contabilizado["resumo_sintetico"]["P_nao_elegiveis"],
                "P_sem_resposta": resultado_contabilizado["P_sem_resposta"],
                "F_elegiveis": resultado_contabilizado["resumo_sintetico"]["F_elegiveis"],
                "resultados_gerados_apenas_ficticios": True,
            },
        },
        "protocolo_congelado": False,
        "autorizacao_execucao_final": False,
        "avaliacao_final_executada": False,
        "dados_reservados_lidos": False,
        "decisao_g03": "PENDENTE_DE_REVISAO_E_APROVACAO_HUMANA",
    }


def verificar_contrato() -> dict[str, Any]:
    """Descrição estática; não lê fontes, léxicos nem diretórios privados."""
    return {
        "versao": VERSAO,
        "estado": ESTADO,
        "modos_cli": ["verificar-contrato", "comparar-opcoes", "executar-final (bloqueado)"],
        "politicas_g03_somente_propostas": sorted(POLITICAS),
        "politica_aprovada": POLITICA_APROVADA,
        "fonte_sintetica": "FIXTURE_LITERAL_BLOCO34",
        "ficha_sintetica": "FIXTURE_LITERAL_BLOCO33",
        "programa_real_autorizado": False,
        "aprovacao_academica_registrada": False,
        "protocolo_congelado": False,
        "autorizacao_execucao_final": False,
        "avaliacao_final_executada": False,
        "dados_reservados_lidos": False,
        "pendencias": [
            "Aprovar a política G03 antes de consultar a avaliação final",
            "Implementar e revisar fluxo real após fixar contrato, versões e custódia",
            "Registrar aprovação acadêmica e congelamento antes do acesso reservado",
        ],
    }


def executar_final(*args, **kwargs):
    """Nenhum parâmetro pode converter este release em avaliador real."""
    raise PermissionError("BLOQUEADO: avaliação final não implementada/autorizada neste release")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bloco 36: comparação de opções G03 exclusivamente com dados fictícios"
    )
    parser.add_argument("modo", choices=("verificar-contrato", "comparar-opcoes", "executar-final"))
    args = parser.parse_args()
    try:
        saida = (verificar_contrato() if args.modo == "verificar-contrato"
                 else comparar_opcoes() if args.modo == "comparar-opcoes" else executar_final())
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        print("AVISO: nenhum dado reservado acessado; nenhuma política foi aprovada.")
    except (ValueError, PermissionError, RuntimeError, FileNotFoundError, OSError) as erro:
        parser.exit(1, f"BLOQUEADO: {erro}\nAvaliação final não executada.\n")


if __name__ == "__main__":
    main()
