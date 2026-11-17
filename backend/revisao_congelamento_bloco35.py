"""Bloco 35 — dossiê de revisão *anterior* ao congelamento do SentiVis.

Não congela nem autoriza protocolo. Não gera fichas finais, não lê dados
reservados, não importa classificadores nem executa resultados experimentais.
A única entrada externa é a lista FIXA de fontes públicas do projeto,
verificada juntamente com a integridade dos léxicos pelo Bloco 31.

CLI: verificar (somente leitura) ou registrar (único dossiê PRIVADO preliminar).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

VERSAO = "bloco35_dossie_revisao_precongelamento_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = Path("data/piloto/restrito/bloco35_dossie/dossie_preliminar_bloco35.json")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")

# Somente código e documentos versionáveis. Não adicionar dados, fichas nem CSV
# da partição reservada nesta lista. As fontes lexicais são verificadas pelo
# manifesto do Bloco 31, que lê apenas originais e relatórios autorizados.
ARQUIVOS_PUBLICOS = (
    "backend/revisao_congelamento_bloco35.py",
    "backend/baseline_experimental.py",
    "backend/baseline_contextual_v03.py",
    "backend/baseline_contextual_v04.py",
    "backend/baseline_gramatical_v02.py",
    "backend/lexicon_consulta.py",
    "backend/frase_diagnostico.py",
    "backend/avaliacao_final_preparacao_bloco29.py",
    "backend/preflight_avaliacao_bloco30.py",
    "backend/manifesto_lexicos_bloco31.py",
    "backend/precongelamento_bloco32.py",
    "backend/executor_sintetico_bloco33.py",
    "backend/executor_final_bloqueado_bloco34.py",
    "docs/metodologia/PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md",
    "docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md",
    "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md",
    "docs/metodologia/CHECKLIST_CONGELAMENTO_BLOCO28.md",
    "docs/metodologia/MATRIZ_DECISOES_PRECONGELAMENTO_BLOCO32.md",
    "docs/metodologia/TERMO_REVISAO_PROTOCOLO_BLOCO32.md",
    "docs/metodologia/CONTRATO_EXECUTOR_FINAL_BLOCO34.md",
    "docs/metodologia/PARECER_PENDENCIAS_BLOCO35.md",
    "docs/metodologia/MODELO_ATA_REVISAO_BLOCO35.md",
    "docs/instrucoes/INSTRUCOES_BLOCO35.md",
)

# Todos os portões são AÇÕES HUMANAS ou de um release futuro.
# Nunca transformá-los em marcados/concluídos por executar este programa.
PORTOES = (
    ("G01", "Aprovar e datar a mudança para anotador único após a etapa de desenvolvimento"),
    ("G02", "Registrar independência e instruções do anotador; investigar possível exposição do controle C001"),
    ("G03", "Decidir incompatibilidade entre não resposta elegível no Bloco 28 e bloqueio de ficha incompleta no Bloco 34"),
    ("G04", "Aprovar critérios de equivalência, ambiguidade, neutralidade, exclusão, denominadores e abstenção"),
    ("G05", "Implementar/revisar executor final real e salvaguardas; testá-lo SOMENTE com fixtures artificiais"),
    ("G06", "Revisar risco residual dos dois testes de symlink não executados no Windows e custódia privada"),
    ("G07", "Fixar commit, versões, SHA-256, configurações, regras de falha e execução única da versão definitiva"),
    ("G08", "Obter aprovação acadêmica verificável, com responsável, data e decisão, ANTES de abrir dados reservados"),
)


def _sha_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as arq:
        for bloco in iter(lambda: arq.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def _publico_regular(raiz: Path, relativo: str) -> Path:
    """Restringe a arquivo regular, sem symlink, dentro de uma lista fixa."""
    if relativo not in ARQUIVOS_PUBLICOS or ".." in Path(relativo).parts or not relativo.startswith(("backend/", "docs/")):
        raise ValueError("Entrada não pertence à lista autorizada de arquivos públicos")
    destino = raiz / relativo
    if not destino.is_file():
        raise FileNotFoundError(f"Arquivo público necessário ausente: {relativo}")
    if not destino.resolve(strict=True).is_relative_to(raiz.resolve(strict=True)):
        raise ValueError("Arquivo público aponta para fora do repositório")
    atual = destino
    while atual != raiz:
        if atual.is_symlink():
            raise ValueError(f"Link simbólico não permitido na trilha pública: {relativo}")
        atual = atual.parent
        if not atual.is_relative_to(raiz):
            raise ValueError("Caminho público fora da raiz")
    return destino


def _validar_inventario(inventario: dict) -> None:
    from backend.precongelamento_bloco32 import CONFIGURACAO_PREVISTA

    if not isinstance(inventario, dict) or (
        inventario.get("estado") != ESTADO or
        inventario.get("autorizacao_execucao_final") is not False or
        inventario.get("dados_reservados_lidos") is not False or
        inventario.get("hash_particao_reservada") is not None
    ):
        raise ValueError("Inventário não atesta bloqueio de avaliação final")
    if inventario.get("integridade_lexicos") != "CONFERIDA_COM_RELATORIOS_LOCAIS":
        raise ValueError("Originais lexicais não conferidos")
    if inventario.get("configuracao_proposta_nao_aprovada") != CONFIGURACAO_PREVISTA:
        raise ValueError("Configuração declarada diverge da proposta registrada")
    env = inventario.get("ambiente")
    if not isinstance(env, dict) or any(not isinstance(env.get(k), str) or not env[k]
                                        for k in ("python", "spacy", "pt_core_news_sm")):
        raise ValueError("Falta registrar versões do ambiente")
    d = inventario.get("hashes_lexicos_originais")
    if not isinstance(d, dict) or set(d) != {"oplexicon", "sentilex_lem", "sentilex_flex", "sentilex_zip"}:
        raise ValueError("Lista lexical incompleta")
    for nome, info in d.items():
        chave = "confere_com_auditoria_e_md5_publicado" if nome == "sentilex_zip" else "confere_com_curadoria_e_auditoria"
        if (not isinstance(info, dict) or info.get(chave) is not True or
                not isinstance(info.get("sha256"), str) or not SHA256.fullmatch(info["sha256"])):
            raise ValueError(f"Original lexical não confirmado: {nome}")
    refs = inventario.get("hashes_codigo_protocolos")
    if not isinstance(refs, dict) or any(not isinstance(x, str) or not SHA256.fullmatch(x)
                                           for x in refs.values()):
        raise ValueError("Checksums de arquivos-base inválidos")
    # A versão B31 pode não cobrir B34/B35; são inventariadas separadamente.
    if not all(chave in refs for chave in (
        "backend/baseline_experimental.py", "backend/baseline_contextual_v03.py",
        "backend/baseline_contextual_v04.py", "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md"
    )):
        raise ValueError("Hashes essenciais do Bloco 31 ausentes")


def _validar_contrato(contrato: dict) -> None:
    if (not isinstance(contrato, dict) or contrato.get("estado") != ESTADO or
        contrato.get("dados_reservados_lidos") is not False or
        contrato.get("autorizacao_execucao_final") is not False or
        contrato.get("executor_real_liberado") is not False or
        contrato.get("origem_campos") != 14 or contrato.get("ficha_campos") != 6 or
        contrato.get("n_pares_sinteticos") != 27 or contrato.get("n_familias_sinteticas") != 9 or
        contrato.get("ficha_individual_e_validada_antes_da_pontuacao") is not True):
        raise ValueError("Contrato B34 não corresponde ao executor real bloqueado")


def preparar_dossie(raiz: Path = RAIZ, *, inventario: dict | None = None,
                     contrato: dict | None = None) -> dict:
    """Produz snapshot de revisão, nunca estado de aprovação.

    `inventario` e `contrato` são injetáveis SOMENTE para os testes fictícios.
    A CLI sempre consulta os dois módulos reais em modo leitura.
    """
    raiz = Path(raiz).resolve(strict=True)
    if inventario is None:
        from backend.manifesto_lexicos_bloco31 import preparar_manifesto
        inventario = preparar_manifesto(raiz)
    if contrato is None:
        from backend.executor_final_bloqueado_bloco34 import verificar_contrato
        contrato = verificar_contrato()
    _validar_inventario(inventario)
    _validar_contrato(contrato)
    checksums: dict[str, str] = {}
    for relativo in ARQUIVOS_PUBLICOS:
        checksums[relativo] = _sha_arquivo(_publico_regular(raiz, relativo))
    # O commit B34 é apenas histórico; com B35 não publicado ainda, o SHA
    # observado não identifica os arquivos B35 recém-criados no disco.
    return {
        "versao": VERSAO,
        "fase": "DOSSIÊ_PRELIMINAR_PARA_REVISAO_HUMANA",
        "estado": ESTADO,
        "protocolo_congelado": False,
        "autorizacao_execucao_final": False,
        "aprovacao_academica_registrada": False,
        "avaliacao_final_executada": False,
        "dados_reservados_lidos": False,
        "hash_particao_reservada": None,
        "commit_apenas_observado": inventario.get("git_commit_observado"),
        "configuracao_proposta_nao_aprovada": inventario["configuracao_proposta_nao_aprovada"],
        "ambiente": inventario["ambiente"],
        "integridade_lexicos": inventario["integridade_lexicos"],
        "hashes_lexicos_originais": {nome: {"sha256": d["sha256"], "arquivo": d["arquivo"]}
                                    for nome, d in inventario["hashes_lexicos_originais"].items()},
        "hashes_sha256_codigo_documentos_publicos": checksums,
        "contrato_final_atual": "B34_SOMENTE_SINTETICO_EXECUCAO_REAL_BLOQUEADA",
        "questoes_pendentes": [{"id": ident, "descricao": descricao, "concluida": False}
                               for ident, descricao in PORTOES],
        "n_pendencias": len(PORTOES),
        "concordancia_interavaliadores": None,
        "acuracia_validada": None,
        "evidencia_de_vies": None,
        "nota": "Somente pré-revisão. Nenhuma saída de software assina, aprova ou congela o protocolo.",
    }


def _pasta_privada_segura(raiz: Path) -> Path:
    raiz = Path(raiz).resolve(strict=True)
    caminho = raiz
    for parte in DESTINO.parent.parts:
        caminho = caminho / parte
        if caminho.is_symlink():
            raise ValueError("Caminho privado contém link simbólico")
        if caminho.exists() and not caminho.is_dir():
            raise ValueError("Caminho privado não é pasta")
        caminho.mkdir(exist_ok=True)
    if not caminho.resolve(strict=True).is_relative_to(raiz):
        raise ValueError("Destino privado fora do projeto")
    return caminho


def registrar_dossie(raiz: Path = RAIZ, *, inventario: dict | None = None,
                      contrato: dict | None = None) -> dict:
    """Criação exclusiva de snapshot preliminar; repetir NÃO substitui registro."""
    documento = preparar_dossie(raiz, inventario=inventario, contrato=contrato)
    pasta = _pasta_privada_segura(raiz)
    destino = pasta / DESTINO.name
    fd = os.open(destino, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as arq:
        json.dump({"registrado_em_utc": datetime.now(timezone.utc).isoformat(), **documento},
                  arq, indent=2, sort_keys=True, ensure_ascii=False)
        arq.write("\n")
    return {"estado": ESTADO, "registro_preliminar": DESTINO.as_posix(),
            "sobrescrita_bloqueada": True, "avaliacao_final_executada": False,
            "protocolo_congelado": False}


def main() -> None:
    cli = argparse.ArgumentParser(description="Bloco 35: preparar revisão; NÃO autoriza avaliação final")
    cli.add_argument("modo", choices=("verificar", "registrar"))
    args = cli.parse_args()
    try:
        d = preparar_dossie() if args.modo == "verificar" else registrar_dossie()
        print(json.dumps(d, ensure_ascii=False, indent=2))
        print("AVISO: dossiê preliminar. Aprovação acadêmica e congelamento NÃO realizados.")
    except (ValueError, FileNotFoundError, PermissionError, OSError, json.JSONDecodeError) as erro:
        cli.exit(1, f"BLOQUEADO: {erro}\nAvaliação reservada não autorizada.\n")


if __name__ == "__main__":
    main()
