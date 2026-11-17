"""Bloco 31 — inventário reproduzível sem acesso à partição reservada.

Comandos permitidos: verificar, registrar. Lê APENAS uma lista fixa de arquivos
públicos, relatórios lexicais e os quatro originais dos léxicos. Não executa
classificadores, não abre dados do piloto ou de avaliação e NÃO autoriza avaliação.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]
VERSAO = "bloco31_manifesto_integridade_lexical_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
MD5_SENTILEX_PUBLICADO = "026e1dceeaa506cc048d6ce7e0174cd0"
ORIGINAIS = {
    "oplexicon": "lexico_v3.0.txt",
    "sentilex_lem": "SentiLex-lem-PT02.txt",
    "sentilex_flex": "SentiLex-flex-PT02.txt",
    "sentilex_zip": "SentiLex-PT02.zip",
}
CODIGO_E_PROTOCOLOS = (
    "backend/manifesto_lexicos_bloco31.py",
    "backend/baseline_experimental.py",
    "backend/baseline_contextual_v03.py",
    "backend/baseline_contextual_v04.py",
    "backend/baseline_gramatical_v02.py",
    "backend/lexicon_audit.py",
    "backend/lexicon_triage.py",
    "backend/lexicon_consulta.py",
    "backend/frase_diagnostico.py",
    "backend/avaliacao_final_preparacao_bloco29.py",
    "backend/preflight_avaliacao_bloco30.py",
    "docs/metodologia/PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md",
    "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md",
    "docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md",
    "docs/metodologia/CHECKLIST_CONGELAMENTO_BLOCO28.md",
    "docs/metodologia/PROTOCOLO_MANIFESTO_BLOCO31.md",
)
DESTINO_RELATIVO = Path("data/piloto/restrito/bloco31_manifesto/manifesto_preliminar_bloco31.json")


def _hash(caminho: Path, algoritmo: str = "sha256") -> str:
    h = hashlib.new(algoritmo)
    with caminho.open("rb") as f:
        for parte in iter(lambda: f.read(1024 * 1024), b""):
            h.update(parte)
    return h.hexdigest()


def _arquivo_local_regular(path: Path, limite: Path) -> Path:
    """Rejeita links simbólicos, inclusive pais, e caminhos fora da raiz prevista."""
    base = limite.resolve(strict=True)
    if not limite.is_dir() or limite.is_symlink():
        raise ValueError("Pasta autorizada ausente ou simbólica")
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo autorizado ausente: {path.name}")
    alvo = path.resolve(strict=True)
    if not alvo.is_relative_to(base):
        raise ValueError(f"Arquivo fora da pasta autorizada: {path.name}")
    cursor = path
    while cursor != limite:
        if cursor.is_symlink():
            raise ValueError(f"Link simbólico não permitido: {path.name}")
        cursor = cursor.parent
        if not cursor.is_relative_to(limite):
            raise ValueError("Caminho inesperado")
    return path


def _unico(originais: Path, nome: str) -> Path:
    if not originais.is_dir() or originais.is_symlink():
        raise FileNotFoundError("Diretório de léxicos originais não disponível")
    encontrados = list(originais.rglob(nome))
    if len(encontrados) != 1:
        raise FileNotFoundError(f"Esperado um único original '{nome}'; encontrados {len(encontrados)}")
    return _arquivo_local_regular(encontrados[0], originais)


def _relatorio(raiz: Path, relativo: str) -> tuple[dict, str]:
    p = _arquivo_local_regular(raiz / relativo, raiz)
    dados = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(dados, dict):
        raise ValueError(f"Relatório inválido: {relativo}")
    return dados, _hash(p)


def _versao_pacote(nome: str) -> str | None:
    try:
        return metadata.version(nome)
    except metadata.PackageNotFoundError:
        return None


def _git_head(raiz: Path) -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz,
                                capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    sha = result.stdout.strip()
    return sha if re.fullmatch(r"[a-f0-9]{40}", sha) else None


def preparar_manifesto(raiz: Path = RAIZ) -> dict:
    """Somente leitura dos léxicos (hash de bytes) e documentos explicitamente autorizados.

    Não acessa dados/piloto nem diretórios de avaliação, e não importa baselines.
    O uso dos originais neste estágio serve à integridade, não à pontuação.
    """
    raiz = raiz.resolve(strict=True)
    curadoria, sha_curadoria = _relatorio(raiz, "data/lexicos/relatorio_curadoria.json")
    auditoria, sha_auditoria = _relatorio(raiz, "data/lexicos/relatorio_auditoria.json")
    if curadoria.get("total_falhas_de_leitura") != 0:
        raise ValueError("Curadoria não atesta zero falhas de leitura")
    base = raiz / "data/lexicos/originais"
    hashes = {}
    for tipo, nome in ORIGINAIS.items():
        original = _unico(base, nome)
        sha = _hash(original)
        if tipo != "sentilex_zip":
            esperado = curadoria.get("fontes", {}).get(tipo, {}).get("sha256")
            auditado = auditoria.get("arquivos", {}).get(tipo, {}).get("sha256")
            if not isinstance(esperado, str) or not isinstance(auditado, str) or not (
                re.fullmatch(r"[0-9a-fA-F]{64}", esperado) and re.fullmatch(r"[0-9a-fA-F]{64}", auditado)
            ):
                raise ValueError(f"SHA de curadoria/auditoria ausente ou inválido: {tipo}")
            if esperado.lower() != sha or auditado.lower() != sha:
                raise ValueError(f"DIVERGÊNCIA SHA-256 original/curadoria/auditoria: {tipo}")
            hashes[tipo] = {"arquivo": nome, "sha256": sha, "tamanho_bytes": original.stat().st_size,
                            "confere_com_curadoria_e_auditoria": True}
        else:
            md5 = _hash(original, "md5")
            base_zip = auditoria.get("sentilex_zip", {})
            if not isinstance(base_zip, dict) or base_zip.get("sha256", "").lower() != sha:
                raise ValueError("SHA-256 do ZIP diverge da auditoria")
            if base_zip.get("md5", "").lower() != md5 or md5 != MD5_SENTILEX_PUBLICADO:
                raise ValueError("MD5 do ZIP diverge da auditoria ou do checksum publicado")
            hashes[tipo] = {"arquivo": nome, "sha256": sha, "md5": md5,
                            "tamanho_bytes": original.stat().st_size, "confere_com_auditoria_e_md5_publicado": True}

    codigos = {}
    for relativo in CODIGO_E_PROTOCOLOS:
        caminho = _arquivo_local_regular(raiz / relativo, raiz)
        codigos[relativo] = _hash(caminho)

    return {
        "versao": VERSAO,
        "estado": ESTADO,
        "autorizacao_execucao_final": False,
        "dados_reservados_lidos": False,
        "hash_particao_reservada": None,
        "git_commit_observado": _git_head(raiz),
        "ambiente": {"python": sys.version.split()[0], "spacy": _versao_pacote("spacy"),
                     "pt_core_news_sm": _versao_pacote("pt_core_news_sm")},
        "configuracao_proposta_nao_aprovada": {
            "analise_primaria": "SentiLex-PT02",
            "baselines": ["V01", "V03", "V04"],
            "alvo_manual": "N0",
            "hipotese_modo_v01": "nao_aplicavel",
            "hipotese_modo_v03": True,
            "hipotese_modo_v04": True,
            "avaliadores_previstos_final": 1,
            "metodo_resultados": "descritivo; sem inferencia de vies"
        },
        "hashes_lexicos_originais": hashes,
        "hashes_relatorios": {"relatorio_curadoria.json": sha_curadoria,
                              "relatorio_auditoria.json": sha_auditoria},
        "hashes_codigo_protocolos": codigos,
        "integridade_lexicos": "CONFERIDA_COM_RELATORIOS_LOCAIS",
        "pendencias": [
            "Revisar/aprovar o desenho com anotador único e critérios de exclusão antes da abertura",
            "Validar o programa da avaliação real em dados fictícios e congelar seu contrato",
            "Fixar commit final, hashes, dependências e execução única após revisão",
            "Registrar responsável, decisão, versão e data de aprovação formal do protocolo",
            "Obter ficha individual reservada antes de classificações, depois de autorização",
        ],
        "nota": "Manifesto preliminar de integridade: não é pré-registro congelado nem autorização."
    }


def registrar_manifesto(raiz: Path = RAIZ) -> dict:
    manifesto = preparar_manifesto(raiz)
    raiz = raiz.resolve(strict=True)
    destino = raiz / DESTINO_RELATIVO
    pasta = destino.parent
    if (raiz / "data/piloto").is_symlink() or (raiz / "data/piloto/restrito").is_symlink():
        raise ValueError("Pasta privada é link simbólico; gravação recusada")
    pasta.mkdir(parents=True, exist_ok=True)
    if pasta.is_symlink():
        raise ValueError("Destino de relatório é link simbólico")
    documento = {"criado_em_utc": datetime.now(timezone.utc).isoformat(), **manifesto}
    # Criação exclusiva: não sobrescreve nem apaga o manifesto, mesmo se falhar.
    fd = os.open(destino, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(documento, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    return {"estado": ESTADO, "manifesto_privado": DESTINO_RELATIVO.as_posix(),
            "lexicos_verificados": len(ORIGINAIS), "registro_sem_sobrescrita": True,
            "avaliacao_final_executada": False}


def main() -> None:
    cli = argparse.ArgumentParser(description="Bloco 31: integridade sem execução da avaliação final")
    cli.add_argument("modo", choices=("verificar", "registrar"))
    args = cli.parse_args()
    try:
        if args.modo == "verificar":
            print(json.dumps(preparar_manifesto(), ensure_ascii=False, indent=2))
            print("AVISO: integridade verificada; protocolo NÃO congelado.")
        else:
            print(json.dumps(registrar_manifesto(), ensure_ascii=False, indent=2))
            print("AVISO: manifesto preliminar privado criado; nenhuma avaliação final executada.")
    except (FileNotFoundError, ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        cli.exit(1, f"BLOQUEADO: {exc}\nSem alterar dados originais ou acessar a avaliação reservada.\n")


if __name__ == "__main__":
    main()
