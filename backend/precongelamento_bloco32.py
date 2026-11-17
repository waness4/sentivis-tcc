"""Bloco 32 — verificação documental de pré-congelamento (somente leitura).

NÃO lê dados/piloto, não aceita arquivos de entrada, não classifica frases,
não congela protocolo e não autoriza avaliação final. Reutiliza o inventário
restrito aos léxicos e documentos públicos implementado no Bloco 31.

Uso: python -m backend.precongelamento_bloco32 verificar
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from backend.manifesto_lexicos_bloco31 import RAIZ, preparar_manifesto

VERSAO = "bloco32_precongelamento_documental_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")

CONFIGURACAO_PREVISTA = {
    "analise_primaria": "SentiLex-PT02",
    "baselines": ["V01", "V03", "V04"],
    "alvo_manual": "N0",
    "hipotese_modo_v01": "nao_aplicavel",
    "hipotese_modo_v03": True,
    "hipotese_modo_v04": True,
    "avaliadores_previstos_final": 1,
    "metodo_resultados": "descritivo; sem inferencia de vies",
}

HASHES_NECESSARIOS = (
    "backend/baseline_experimental.py",
    "backend/baseline_contextual_v03.py",
    "backend/baseline_contextual_v04.py",
    "backend/avaliacao_final_preparacao_bloco29.py",
    "backend/preflight_avaliacao_bloco30.py",
    "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md",
    "docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md",
    "docs/metodologia/CHECKLIST_CONGELAMENTO_BLOCO28.md",
)


def validar_inventario(inventario: dict) -> dict:
    """Confere o contrato do Bloco 31 sem acessar dados adicionais."""
    if not isinstance(inventario, dict):
        raise ValueError("Inventário ausente ou inválido")
    if (inventario.get("estado") != ESTADO
            or inventario.get("autorizacao_execucao_final") is not False
            or inventario.get("dados_reservados_lidos") is not False
            or inventario.get("hash_particao_reservada") is not None):
        raise ValueError("Inventário não indica inequivocamente a avaliação bloqueada")
    if inventario.get("integridade_lexicos") != "CONFERIDA_COM_RELATORIOS_LOCAIS":
        raise ValueError("Integridade lexical ainda não foi conferida")
    if inventario.get("configuracao_proposta_nao_aprovada") != CONFIGURACAO_PREVISTA:
        raise ValueError("Configuração proposta divergente; revisão metodológica exigida")
    ambiente = inventario.get("ambiente")
    if not isinstance(ambiente, dict) or any(
        not isinstance(ambiente.get(k), str) or not ambiente[k].strip()
        for k in ("python", "spacy", "pt_core_news_sm")
    ):
        raise ValueError("Versões essenciais do ambiente não registradas")
    originais = inventario.get("hashes_lexicos_originais")
    if not isinstance(originais, dict) or set(originais) != {
        "oplexicon", "sentilex_lem", "sentilex_flex", "sentilex_zip"
    }:
        raise ValueError("Inventário lexical incompleto")
    for nome, info in originais.items():
        if not isinstance(info, dict) or not isinstance(info.get("sha256"), str) or not SHA_RE.fullmatch(info["sha256"]):
            raise ValueError(f"Hash lexical ausente ou inválido: {nome}")
        chave = ("confere_com_auditoria_e_md5_publicado" if nome == "sentilex_zip"
                 else "confere_com_curadoria_e_auditoria")
        if info.get(chave) is not True or type(info.get("tamanho_bytes")) is not int or info["tamanho_bytes"] <= 0:
            raise ValueError(f"Arquivo lexical não verificado: {nome}")
    fontes = inventario.get("hashes_codigo_protocolos")
    if not isinstance(fontes, dict) or any(
        not isinstance(fontes.get(p), str) or not SHA_RE.fullmatch(fontes[p])
        for p in HASHES_NECESSARIOS
    ):
        raise ValueError("Hashes do código/protocolo essenciais incompletos")

    return {
        "versao": VERSAO,
        "estado": ESTADO,
        "revisao_documental": "CONTRATOS_PRELIMINARES_COHERENTES",
        "integridade_lexicos": "CONFERIDA_COM_RELATORIOS_LOCAIS",
        "commit_apenas_observado": inventario.get("git_commit_observado"),
        "ambiente": {k: ambiente[k] for k in ("python", "spacy", "pt_core_news_sm")},
        "configuracao_proposta_nao_aprovada": dict(CONFIGURACAO_PREVISTA),
        "n_arquivos_originais_conferidos": len(originais),
        "n_hashes_codigo_minimos_conferidos": len(HASHES_NECESSARIOS),
        "criterios_propostos": {
            "unidade_primaria_delta": "par",
            "total_planejado": "27 pares / 54 frases / 9 familias (nao lidos)",
            "coincidencia_primaria": "somente rotulos humana positiva/negativa e frases pontuadas",
            "rotulo_neutro": "estrato separado, sem conversao para zero",
            "abstencao": "nao imputar pontuacao nem delta zero",
            "delta": "feminina - masculina, somente quando ambas pontuadas",
            "inferencia_vies": "nao autorizada",
        },
        "portoes_pendentes": [
            "Revisao e aprovacao formal do desenho com anotador unico e da alteracao pos-coleta",
            "Identificacao das instrucoes e condicoes de independencia de R01 e esclarecimento de C001",
            "Executor exclusivo da avaliacao real e geracao de ficha cega implementados e testados apenas em dados artificiais",
            "Revisao do tratamento de ambiguidade, neutralidade, exclusoes, abstenções e falhas de execucao",
            "Congelamento de commit, manifesto, dependencias, regras e contrato de execucao apos codigo definitivo",
            "Registro datado da aprovacao por responsavel habilitado; somente depois custodia e anotacao final",
        ],
        "aprovacao_academica_registrada": False,
        "programa_real_autorizado": False,
        "protocolo_congelado": False,
        "autorizacao_execucao_final": False,
        "dados_reservados_lidos": False,
        "hash_particao_reservada": None,
        "acuracia_validada": None,
        "evidencia_de_vies": None,
        "nota": "A verificação de integridade e a proposta metodológica não substituem revisão e aprovação formal.",
    }


def verificar(raiz: Path = RAIZ) -> dict:
    """Reutiliza a lista fechada de entradas do Bloco 31; nenhuma outra leitura."""
    return validar_inventario(preparar_manifesto(raiz))


def main() -> None:
    cli = argparse.ArgumentParser(description="Bloco 32: revisão documental; avaliação final bloqueada")
    cli.add_argument("modo", choices=("verificar",))
    args = cli.parse_args()
    if args.modo == "verificar":
        try:
            print(json.dumps(verificar(), indent=2, ensure_ascii=False))
            print("AVISO: verificação documental somente; protocolo NÃO congelado.")
        except (ValueError, FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError) as erro:
            cli.exit(1, f"BLOQUEADO: {erro}\nNenhuma avaliação final autorizada.\n")


if __name__ == "__main__":
    main()
