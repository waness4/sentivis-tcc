"""Bloco 30 — auditoria prévia e ensaio sintético bloqueado por tentativa.

O módulo NÃO acessa, lê nem processa os 27 pares de avaliação final.
Não há comando de avaliação real nem CLI para importar arquivos.
Nunca usar este ensaio como autorização ou comprovação de congelamento.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import io
import json
from pathlib import Path
import re
import subprocess
import sys

from backend.avaliacao_final_preparacao_bloco29 import (
    FICHA_CAMPOS, _ficticios, simular, validar_ficha,
)

VERSAO = "bloco30_preflight_somente_sintetico_v01"
RAIZ = Path(__file__).resolve().parents[1]
SAIDA_ENSAIO = Path("data/piloto/restrito/bloco30_ensaio")
COLUNAS_FICHA = (
    "id_par", "frase_feminina", "frase_masculina", "equivalencia", "rotulo", "observacoes"
)
# Lista FIXA de caminhos públicos. Nenhum globo, diretório privado ou conjunto reservado.
ARQUIVOS_PUBLICOS = (
    "backend/preflight_avaliacao_bloco30.py",
    "backend/avaliacao_final_preparacao_bloco29.py",
    "backend/baseline_experimental.py",
    "backend/baseline_contextual_v03.py",
    "backend/baseline_contextual_v04.py",
    "docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md",
    "docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md",
    "docs/metodologia/CHECKLIST_CONGELAMENTO_BLOCO28.md",
    "docs/metodologia/MODELO_FICHA_FINAL_BLOCO28.csv",
    "docs/metodologia/PROTOCOLO_PREFLIGHT_BLOCO30.md",
)


def hash_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def ficha_sintetica_csv(pares: list[dict], *, preenchida: bool = False) -> str:
    """Gera ficha em memória sem predições, só para pares SINT* inventados."""
    if not pares or any(not isinstance(p.get("id_par"), str) or
                        not re.fullmatch(r"SINT\d{3}", p["id_par"]) for p in pares):
        raise ValueError("Somente IDs fictícios SINTNNN são aceitos")
    pares_padrao, respostas_padrao = _ficticios()
    referencia = {p["id_par"]: p for p in pares_padrao}
    if len(pares) != len(referencia) or set(p["id_par"] for p in pares) != set(referencia):
        raise ValueError("A ficha de ensaio exige a lista fictícia fixada no Bloco 29")
    for p in pares:
        for lado in ("frase_feminina", "frase_masculina"):
            if p[lado] != referencia[p["id_par"]][lado]:
                raise ValueError("Os textos sintéticos de ensaio não podem ser substituídos")
    respostas = {r["id_par"]: r for r in respostas_padrao}
    buffer = io.StringIO(newline="")
    gravador = csv.DictWriter(buffer, fieldnames=COLUNAS_FICHA, delimiter=";", lineterminator="\n")
    gravador.writeheader()
    for p in pares:
        r = respostas[p["id_par"]] if preenchida else {}
        gravador.writerow({
            "id_par": p["id_par"],
            "frase_feminina": p["frase_feminina"],
            "frase_masculina": p["frase_masculina"],
            "equivalencia": r.get("equivalencia", ""),
            "rotulo": r.get("rotulo", ""),
            "observacoes": r.get("observacoes", ""),
        })
    return buffer.getvalue()


def validar_conteudo_ficha_csv(conteudo: str, pares: list[dict]) -> dict[str, dict]:
    """Checa cabeçalho, tamanho, textos e regras de R01 em memória.

    Esta função não acessa arquivo algum. A CLI só a exercita com fixtures.
    """
    if not isinstance(conteudo, str) or not conteudo or len(conteudo) > 200_000:
        raise ValueError("Conteúdo CSV ausente ou excessivo")
    leitor = csv.DictReader(io.StringIO(conteudo.lstrip("\ufeff"), newline=""),
                            delimiter=";", restkey="__excesso__", strict=True)
    if tuple(leitor.fieldnames or ()) != COLUNAS_FICHA:
        raise ValueError("Cabeçalho da ficha deve ter exatamente seis colunas na ordem definida")
    linhas = []
    for n, bruto in enumerate(leitor, start=2):
        if "__excesso__" in bruto or any(valor is None for valor in bruto.values()):
            raise ValueError(f"Linha {n}: colunas incompletas ou excedentes")
        if not all(isinstance(valor, str) for valor in bruto.values()):
            raise ValueError(f"Linha {n}: campo inválido")
        linhas.append(bruto)
    return validar_ficha(pares, linhas)


def _versao_pacote(nome: str) -> str | None:
    try:
        return metadata.version(nome)
    except metadata.PackageNotFoundError:
        return None


def _git_head(raiz: Path) -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz,
                           capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if re.fullmatch(r"[0-9a-f]{40}", r.stdout.strip()) else None


def manifesto_publico(raiz: Path = RAIZ) -> dict:
    """Lê APENAS arquivos públicos, nunca dados/lexicos ou dados/piloto."""
    hashes = {}
    for relativo in ARQUIVOS_PUBLICOS:
        p = raiz / relativo
        if not p.is_file() or p.is_symlink():
            raise FileNotFoundError(f"Arquivo público esperado ausente/não regular: {relativo}")
        hashes[relativo] = hash_bytes(p.read_bytes())
    return {
        "versao": VERSAO,
        "estado": "NAO_CONGELADO_NAO_AUTORIZADO",
        "autorizacao_execucao_final": False,
        "dados_reservados_lidos": False,
        "git_commit_observado": _git_head(raiz),
        "python": sys.version.split()[0],
        "spacy_instalado": _versao_pacote("spacy"),
        "modelo_pt_core_news_sm_instalado": _versao_pacote("pt_core_news_sm"),
        "hashes_sha256_arquivos_publicos": hashes,
        "hashes_lexicos_originais": None,
        "hash_particao_reservada": None,
        "nota": "Registro parcial de preparação; não é manifesto completo nem congelamento.",
    }


def _escrever_novo(caminho: Path, documento: dict) -> None:
    """Criação exclusiva (x); nunca substituir resultado ou marcador anterior."""
    texto = json.dumps(documento, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with caminho.open("x", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto)


def registrar_ensaio_unico(raiz: Path = RAIZ, *, resumo: dict | None = None) -> dict:
    """Reserva a tentativa ANTES da saída; impede segunda execução silenciosa.

    O diretório de destino é fixo e privado, não fornecido pelo usuário.
    `resumo` só existe para testes artificiais (não exposto na CLI).
    """
    manifest = manifesto_publico(raiz)
    pares, _ = _ficticios()
    original_vazio = ficha_sintetica_csv(pares)
    original_respondido = ficha_sintetica_csv(pares, preenchida=True)
    assert len(validar_conteudo_ficha_csv(original_vazio, pares)) == 4
    assert len(validar_conteudo_ficha_csv(original_respondido, pares)) == 4
    dados = simular() if resumo is None else resumo
    if dados.get("fase") != "SIMULACAO_SINTETICA_SEM_ACESSO_AVALIACAO_FINAL" or dados.get("P_total") != 4:
        raise ValueError("Resumo de ensaio deve ser estritamente sintético e de quatro pares")
    # Retira quaisquer textos/observações fornecidos acidentalmente por um resumo de teste.
    if any(chave not in {"metodo", "fase", "P_total", "F_total", "P_equivalentes_R01",
                          "P_nao_elegiveis", "P_nao_elegiveis_por_motivo",
                          "P_elegiveis_com_rotulo_posneg", "P_elegiveis_com_rotulo_neutro_separado",
                          "F_elegiveis", "metodos", "concordancia_interavaliadores",
                          "acuracia_validada", "f1_validado", "evidencia_de_vies",
                          "inferencia_estatistica", "aviso"} for chave in dados):
        raise ValueError("Resumo sintético possui campos não previstos")
    pasta = raiz / SAIDA_ENSAIO
    pasta.mkdir(parents=True, exist_ok=True)
    marco = pasta / "marcador_tentativa_bloco30.json"
    relatorio = pasta / "relatorio_ensaio_bloco30.json"
    agora = datetime.now(timezone.utc).isoformat()
    reserva = {
        "fase": "TENTATIVA_ENSAIO_SINTETICO_RESERVADA",
        "iniciada_em_utc": agora,
        "versao": VERSAO,
        "manifesto_sha256": hash_bytes(json.dumps(manifest, sort_keys=True).encode("utf-8")),
        "ficha_sintetica_vazia_sha256": hash_bytes(original_vazio.encode("utf-8")),
        "ficha_sintetica_respondida_sha256": hash_bytes(original_respondido.encode("utf-8")),
        "avaliacao_final_executada": False,
    }
    # Intencionalmente NÃO apagamos o marcador se alguma falha ocorrer após sua criação.
    _escrever_novo(marco, reserva)
    _escrever_novo(relatorio, {
        "fase": "ENSAIO_SINTETICO_CONCLUIDO",
        "reserva": reserva,
        "manifesto_publico": manifest,
        "resumo_simulacao": dados,
        "avaliacao_final_executada": False,
    })
    return {"estado": "ENSAIO_SINTETICO_CONCLUIDO",
            "P_total_sinteticos": dados["P_total"],
            "caminho_privado_do_relatorio": str(relatorio.relative_to(raiz)),
            "tentativa_bloqueada_para_repeticao": True,
            "avaliacao_final_executada": False}


def main() -> None:
    cli = argparse.ArgumentParser(description="Bloco 30: preflight e ensaio FICTÍCIO. Sem avaliação real.")
    cli.add_argument("modo", choices=["verificar-ambiente", "ensaiar"])
    args = cli.parse_args()
    try:
        if args.modo == "verificar-ambiente":
            print(json.dumps(manifesto_publico(), ensure_ascii=False, indent=2))
            print("AVISO: manifesto PARCIAL. Nenhuma avaliação final liberada.")
        else:
            print(json.dumps(registrar_ensaio_unico(), ensure_ascii=False, indent=2))
            print("AVISO: apenas dados inventados; a avaliação real permanece BLOQUEADA.")
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as erro:
        cli.exit(1, f"BLOQUEADO: {erro}\n" +
                 "Preserve qualquer marcador existente; nenhuma reexecução automática.\n")


if __name__ == "__main__":
    main()
