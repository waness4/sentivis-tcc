"""Bloco 34 — contrato de entrada final, ensaiado APENAS em fonte fictícia.

Não abre arquivos de avaliação, não lê qualquer CSV externo pela CLI e
não disponibiliza uma rota de avaliação real. Os métodos públicos que
processam texto exigem a fixture literal e fixa do Bloco 33. A execução
final continua condicionada à aprovação metodológica e a outro release.
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
import sys
from typing import Any

from backend.avaliacao_final_preparacao_bloco29 import validar_ficha
from backend.executor_sintetico_bloco33 import (
    fixture_27, validar_lote_ficticio, executar_em_memoria,
)
from backend.preflight_avaliacao_bloco30 import (
    COLUNAS_FICHA, validar_conteudo_ficha_csv,
)

VERSAO = "bloco34_contrato_entrada_final_bloqueado_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
RAIZ = Path(__file__).resolve().parents[1]
PASTA_RELATORIO = Path("data/piloto/restrito/bloco34_ensaio")
CAMPOS_FONTE_14 = (
    "id_par", "familia", "particao", "frase_feminina", "frase_masculina",
    "rotulo_revisor1", "rotulo_revisor2", "equivalencia_revisor1",
    "equivalencia_revisor2", "id_revisor1", "id_revisor2",
    "alvo_sentilex_feminina", "alvo_sentilex_masculina", "observacoes",
)
N_PARES = 27
N_FAMILIAS = 9


def _sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def _csv_escrever(linhas: list[dict[str, str]], colunas: tuple[str, ...]) -> str:
    saida = io.StringIO(newline="")
    writer = csv.DictWriter(saida, fieldnames=colunas, delimiter=";", lineterminator="\n",
                            extrasaction="raise")
    writer.writeheader()
    for linha in linhas:
        writer.writerow(linha)
    return saida.getvalue()


def _fixture_14() -> str:
    """Simula o formato de 14 colunas, sem consultar o corpus original."""
    pares, _ = fixture_27()
    registros = []
    for par in pares:
        item = {campo: "" for campo in CAMPOS_FONTE_14}
        for campo in ("id_par", "familia", "particao", "frase_feminina", "frase_masculina"):
            item[campo] = par[campo]
        # Metadados inventados servem para provar que NÃO vão à ficha nem
        # determinam alvos dos modelos (N0 manual e fixo na simulação).
        item["rotulo_revisor1"] = "negativa"
        item["equivalencia_revisor1"] = "nao"
        item["id_revisor1"] = "REV_FICTICIO_SEM_VALOR"
        item["alvo_sentilex_feminina"] = "N1"
        item["alvo_sentilex_masculina"] = "N1"
        item["observacoes"] = "OBSERVACAO_INTERNA_FICTICIA_NAO_EXIBIR"
        registros.append(item)
    return _csv_escrever(registros, CAMPOS_FONTE_14)


def _ler_14_em_memoria(conteudo: str) -> list[dict[str, str]]:
    """Importador em memória: nunca aceita caminho ou lê do disco."""
    if not isinstance(conteudo, str) or not conteudo or len(conteudo) > 1_000_000:
        raise ValueError("CSV de origem ausente ou acima do limite")
    leitor = csv.DictReader(io.StringIO(conteudo.lstrip("\ufeff"), newline=""), delimiter=";",
                            restkey="__excesso__", strict=True)
    if tuple(leitor.fieldnames or ()) != CAMPOS_FONTE_14:
        raise ValueError("A origem deve apresentar exatamente 14 colunas na ordem definida")
    linhas: list[dict[str, str]] = []
    for numero, linha in enumerate(leitor, 2):
        if "__excesso__" in linha or any(not isinstance(x, str) for x in linha.values()):
            raise ValueError(f"Linha {numero}: faltam colunas ou existem colunas extras")
        linhas.append(linha)
        if len(linhas) > N_PARES:
            raise ValueError("Origem excede 27 pares")
    return linhas


def validar_origem_ficticia(conteudo: str) -> list[dict[str, str]]:
    """Falha fechada: qualquer registro não idêntico à fixture fica bloqueado.

    O validador do futuro estudo real terá de ser revisado separadamente
    depois da autorização; a partição de avaliação não é aceita aqui.
    """
    linhas = _ler_14_em_memoria(conteudo)
    if len(linhas) != N_PARES or any(set(item) != set(CAMPOS_FONTE_14) for item in linhas):
        raise ValueError("Origem de ensaio requer 27 registros completos")
    pares = [
        {chave: linha[chave] for chave in
         ("id_par", "familia", "particao", "frase_feminina", "frase_masculina")}
        for linha in linhas
    ]
    validar_lote_ficticio(pares)
    # A fixture de 14 colunas é literal, não apenas estrutural: nenhuma
    # referência humana real ou texto externo pode atravessar essa etapa.
    if conteudo.lstrip("\ufeff") != _fixture_14():
        raise ValueError("Conteúdo fora da origem fictícia imutável: entrada real bloqueada")
    familias = {p["familia"] for p in pares}
    if len(familias) != N_FAMILIAS:
        raise ValueError("Número de famílias diferente de nove")
    return pares


def gerar_ficha_cega_ficticia(conteudo_origem: str) -> str:
    """Projeta só as seis colunas autorizadas; nunca inclui rótulos originais."""
    pares = validar_origem_ficticia(conteudo_origem)
    linhas = [
        {"id_par": p["id_par"], "frase_feminina": p["frase_feminina"],
         "frase_masculina": p["frase_masculina"],
         "equivalencia": "", "rotulo": "", "observacoes": ""}
        for p in pares
    ]
    return _csv_escrever(linhas, COLUNAS_FICHA)


def _ficha_ficticia_preenchida(pares: list[dict[str, str]]) -> str:
    """Apenas respostas ARTIFICIAIS predefinidas, nunca coletadas de R01."""
    padrao, respostas = fixture_27()
    if pares != padrao:
        raise ValueError("Pares não correspondem à fixture sintética fixa")
    return _csv_escrever(respostas, COLUNAS_FICHA)


def validar_ficha_finalizada_ficticia(conteudo_origem: str, conteudo_ficha: str) -> list[dict[str, str]]:
    """Bloqueia lacunas antes da pontuação, sem inventar respostas humanas."""
    pares = validar_origem_ficticia(conteudo_origem)
    anotacoes = validar_conteudo_ficha_csv(conteudo_ficha, pares)
    if any(p["equivalencia"] not in {"sim", "nao"} for p in anotacoes.values()):
        raise ValueError("Ficha humana não está integralmente respondida")
    return [anotacoes[par["id_par"]] for par in pares]


def ensaio_em_memoria(conteudo_origem: str, conteudo_ficha: str, *,
                      executor=None) -> dict[str, Any]:
    """Única interface de execução: dois textos que devem ser as fixtures fixas.

    Índice e etiquetador são fictícios via Bloco 33. A CLI não os aceita.
    Erros propagam: nenhum resultado parcial é retornado como completo.
    """
    pares = validar_origem_ficticia(conteudo_origem)
    ficha = validar_ficha_finalizada_ficticia(conteudo_origem, conteudo_ficha)
    executar = executar_em_memoria if executor is None else executor
    resultado = executar(pares, ficha)
    if (not isinstance(resultado, dict)
        or resultado.get("avaliacao_final_executada") is not False
        or resultado.get("fase") != "ENSAIO_SINTETICO_SEM_AVALIACAO_FINAL"
        or not isinstance(resultado.get("resumo"), dict)
        or resultado["resumo"].get("P_total") != N_PARES
        or resultado["resumo"].get("F_total") != N_PARES * 2
        or set(resultado["resumo"].get("metodos", {})) != {"v01", "v03", "v04"}):
        raise ValueError("Executor não atestou 27 pares exclusivamente sintéticos")
    res = resultado["resumo"]
    for metodo, dados in res["metodos"].items():
        if (dados["F_pontuadas_global"] + dados["F_abstidas_global"] != 54
            or dados["P_delta_calculavel"] + dados["P_delta_nao_calculavel"] != res["P_equivalentes_R01"]):
            raise ValueError("Contagens de saída sintética inconsistentes")
    return {
        "versao": VERSAO,
        "fase": "CONTRATO_FINAL_ENSAIADO_SOMENTE_FICTICIO",
        "estado": ESTADO,
        "fonte": "FIXTURE_PUBLICA_LITERAL_DE_27_PARES_FICTICIOS",
        "sha256_fonte_ficticia": _sha256(conteudo_origem.encode("utf-8")),
        "sha256_ficha_ficticia": _sha256(conteudo_ficha.encode("utf-8")),
        "resumo_sintetico": res,
        "avaliacao_final_executada": False,
        "autorizacao_execucao_final": False,
        "protocolo_congelado": False,
        "acuracia_validada": None,
        "evidencia_de_vies": None,
        "aviso": "Engenharia de testes; não é análise do conjunto reservado.",
    }


def executar_final(*args, **kwargs):
    """Portão impossível de contornar via parâmetros: liberação exige outra versão."""
    raise PermissionError("BLOQUEADO: protocolo não congelado; execução final não implementada/autorizada")


def verificar_contrato() -> dict:
    return {
        "versao": VERSAO,
        "estado": ESTADO,
        "modos_cli": ["verificar-contrato", "ensaiar", "executar-final (sempre bloqueado)"],
        "origem_campos": len(CAMPOS_FONTE_14),
        "ficha_campos": len(COLUNAS_FICHA),
        "n_pares_sinteticos": N_PARES,
        "n_familias_sinteticas": N_FAMILIAS,
        "ficha_individual_e_validada_antes_da_pontuacao": True,
        "dados_reservados_lidos": False,
        "autorizacao_execucao_final": False,
        "executor_real_liberado": False,
        "pendencias": [
            "Revisão acadêmica dos critérios e desenho com anotador único",
            "Aprovação do congelamento, commit, versão Python/spaCy, hashes e custódia",
            "Implementação/revisão da habilitação real após aprovação",
            "Anotação independente e preservação de hash antes de pontuação",
        ],
    }


def _gravar_exclusivo(caminho: Path, documento: dict) -> None:
    fd = os.open(caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(documento, arq, ensure_ascii=False, indent=2, sort_keys=True)
        arq.write("\n")


def _pasta_segura(raiz: Path) -> Path:
    raiz = raiz.resolve(strict=True)
    pasta = raiz
    for segmento in PASTA_RELATORIO.parts:
        pasta = pasta / segmento
        if pasta.is_symlink():
            raise ValueError("Destino do ensaio contém link simbólico")
    pasta.mkdir(parents=True, exist_ok=True)
    if not pasta.resolve(strict=True).is_relative_to(raiz):
        raise ValueError("Destino fora da raiz")
    return pasta


def ensaiar_uma_vez(raiz: Path = RAIZ, *, executor=None) -> dict:
    """Marcador anterior à análise; uma falha preserva marca e bloqueia rerun."""
    pasta = _pasta_segura(raiz)
    marcador = pasta / "marcador_tentativa_bloco34.json"
    relatorio = pasta / "relatorio_contrato_bloco34.json"
    if relatorio.exists():
        raise FileExistsError("Relatório sintético do Bloco 34 já existe")
    fonte = _fixture_14()
    ficha = _ficha_ficticia_preenchida(validar_origem_ficticia(fonte))
    validar_ficha_finalizada_ficticia(fonte, ficha)
    reserva = {
        "versao": VERSAO,
        "fase": "TENTATIVA_SINTETICA_RESERVADA",
        "hora_utc": datetime.now(timezone.utc).isoformat(),
        "sha256_fonte_ficticia": _sha256(fonte.encode("utf-8")),
        "sha256_ficha_ficticia": _sha256(ficha.encode("utf-8")),
        "avaliacao_final_executada": False,
    }
    _gravar_exclusivo(marcador, reserva)
    # Ocorrências ou erros não levam a apagar o marcador.
    resposta = ensaio_em_memoria(fonte, ficha, executor=executor)
    _gravar_exclusivo(relatorio, {"reserva": reserva, "resumo": resposta})
    return {
        "estado": "ENSAIO_SINTETICO_CONCLUIDO",
        "pares_ficticios": 27,
        "familias_ficticias": 9,
        "relatorio_privado": (PASTA_RELATORIO / relatorio.name).as_posix(),
        "repeticao_bloqueada": True,
        "avaliacao_final_executada": False,
    }


def main() -> None:
    cli = argparse.ArgumentParser(
        description="Bloco 34: contrato de entrada somente FICTÍCIO; avaliação real BLOQUEADA")
    cli.add_argument("modo", choices=("verificar-contrato", "ensaiar", "executar-final"))
    args = cli.parse_args()
    try:
        if args.modo == "verificar-contrato":
            resultado = verificar_contrato()
        elif args.modo == "ensaiar":
            resultado = ensaiar_uma_vez()
        else:
            resultado = executar_final()
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("AVISO: avaliação final NÃO autorizada; nenhum dado reservado foi acessado.")
    except (PermissionError, FileExistsError, FileNotFoundError, OSError,
            RuntimeError, ValueError, csv.Error) as exc:
        cli.exit(1, f"BLOQUEADO: {exc}\nDados reservados não foram acessados por este módulo.\n")


if __name__ == "__main__":
    main()
