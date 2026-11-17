"""Bloco 37 — núcleo genérico preparado, CLI REAL permanentemente BLOQUEADA.

Este release NÃO lê arquivos externos nem habilita avaliação final. A CLI só
executa uma fixture literal e inteiramente artificial. Funções puras do núcleo
são contratos para revisão; NÃO são controle de acesso contra código Python
arbitrário. Operação real depende de versão posterior e aprovação acadêmica.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import re
import unicodedata
from typing import Any, Callable

VERSAO = "bloco37_nucleo_executor_preparado_v01"
ESTADO = "NAO_CONGELADO_NAO_AUTORIZADO"
COLUNAS_ORIGEM = (
    "id_par", "familia", "particao", "frase_feminina", "frase_masculina",
    "rotulo_revisor1", "rotulo_revisor2", "equivalencia_revisor1",
    "equivalencia_revisor2", "id_revisor1", "id_revisor2",
    "alvo_sentilex_feminina", "alvo_sentilex_masculina", "observacoes",
)
COLUNAS_FICHA = (
    "id_par", "frase_feminina", "frase_masculina",
    "equivalencia", "rotulo", "observacoes",
)
CAMPOS_PAR = ("id_par", "familia", "particao", "frase_feminina", "frase_masculina")
METODOS = ("v01", "v03", "v04")
LADOS = ("feminina", "masculina")
ROTULOS = frozenset({"positiva", "negativa", "neutra"})
PONTUADO = "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
POLITICA_ESTRITA = "bloquear_ficha_pendente"
POLITICA_CONTABILIZAR = "contabilizar_pendente_nao_elegivel"
POLITICAS = frozenset((POLITICA_ESTRITA, POLITICA_CONTABILIZAR))
POLITICA_APROVADA = None
N_PARES = 27
N_FAMILIAS = 9
N_FRASES = 54
LIMITE_CSV = 1_000_000
PADRAO_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _nfc(txt: str) -> str:
    return unicodedata.normalize("NFC", " ".join(txt.casefold().split()))


def _ler_csv(texto: str, colunas: tuple[str, ...], *, limite_linhas: int = N_PARES) -> list[dict[str, str]]:
    """CSV UTF-8 já carregado em memória; não recebe path nem acessa disco."""
    if not isinstance(texto, str) or not texto or len(texto) > LIMITE_CSV or "\x00" in texto:
        raise ValueError("CSV ausente, excessivo ou com byte NUL")
    leitor = csv.DictReader(io.StringIO(texto.lstrip("\ufeff"), newline=""),
                            delimiter=";", restkey="__extras__", strict=True)
    if tuple(leitor.fieldnames or ()) != colunas:
        raise ValueError(f"Cabeçalho incorreto: esperadas {len(colunas)} colunas exatas na ordem prevista")
    linhas: list[dict[str, str]] = []
    for n, row in enumerate(leitor, start=2):
        if "__extras__" in row or any(not isinstance(x, str) for x in row.values()):
            raise ValueError(f"Linha {n}: coluna extra ou ausente")
        if not any(row.values()):
            raise ValueError(f"Linha {n}: linha vazia não permitida")
        linhas.append(row)
        if len(linhas) > limite_linhas:
            raise ValueError("CSV excede 27 registros")
    if len(linhas) != limite_linhas:
        raise ValueError(f"Esperados exatamente {limite_linhas} registros; encontrados {len(linhas)}")
    return linhas


def validar_origem_em_memoria(conteudo: str) -> list[dict[str, str]]:
    """Contrato estrutural genérico (não habilita a operação reservada)."""
    origem = _ler_csv(conteudo, COLUNAS_ORIGEM)
    pares: list[dict[str, str]] = []
    ids, familias, pares_literais = set(), set(), set()
    for n, row in enumerate(origem, start=2):
        p = {k: row[k] for k in CAMPOS_PAR}
        ident, fam = p["id_par"], p["familia"]
        if not PADRAO_ID.fullmatch(ident) or ident in ids:
            raise ValueError(f"Linha {n}: ID ausente, duplicado ou malformado")
        if not fam.strip() or len(fam) > 80:
            raise ValueError(f"Linha {n}: família ausente ou muito longa")
        if p["particao"] not in {"avaliacao", "sintetica"}:
            raise ValueError(f"Linha {n}: partição inválida")
        for lado in LADOS:
            frase = p["frase_" + lado]
            if not frase.strip() or len(frase) > 5000:
                raise ValueError(f"Linha {n}: frase {lado} vazia ou excessiva")
        f, m = (_nfc(p["frase_" + lado]) for lado in LADOS)
        if f == m:
            raise ValueError(f"Linha {n}: contrafactuais idênticos")
        if (f, m) in pares_literais:
            raise ValueError(f"Linha {n}: par textual duplicado")
        ids.add(ident)
        familias.add(_nfc(fam))
        pares_literais.add((f, m))
        pares.append(p)
    if len(familias) != N_FAMILIAS:
        raise ValueError("Origem precisa apresentar exatamente nove famílias")
    if len({p["particao"] for p in pares}) != 1:
        raise ValueError("Origem não pode misturar partições")
    # NÃO pressupor três pares por família: 27/9 não prova distribuição uniforme.
    return pares


def _escrever_csv(rows: list[dict[str, str]], colunas: tuple[str, ...]) -> str:
    f = io.StringIO(newline="")
    gravador = csv.DictWriter(f, fieldnames=colunas, delimiter=";",
                              lineterminator="\n", extrasaction="raise")
    gravador.writeheader()
    gravador.writerows(rows)
    return f.getvalue()


def gerar_ficha_cega_em_memoria(pares: list[dict[str, str]]) -> str:
    """Somente seis campos: nenhuma previsão, rótulo prévio, família ou alvo."""
    if not isinstance(pares, list) or len(pares) != N_PARES:
        raise ValueError("Lote deve possuir 27 pares")
    linhas = []
    for p in pares:
        if not isinstance(p, dict) or set(p) != set(CAMPOS_PAR):
            raise ValueError("Lote de pares possui colunas inesperadas")
        # Fórmulas no LibreOffice/Excel podem ser ativadas mesmo em CSV citado.
        # Rejeitar antes da exportação, sem alterar os originais silenciosamente.
        for campo in ("id_par", "frase_feminina", "frase_masculina"):
            if p[campo].lstrip().startswith(("=", "+", "-", "@")):
                raise ValueError("Campo potencialmente interpretável como fórmula; revisão antes da ficha")
        linhas.append({
            "id_par": p["id_par"],
            "frase_feminina": p["frase_feminina"],
            "frase_masculina": p["frase_masculina"],
            "equivalencia": "", "rotulo": "", "observacoes": "",
        })
    return _escrever_csv(linhas, COLUNAS_FICHA)


def validar_ficha_em_memoria(conteudo: str, pares: list[dict[str, str]], *,
                              politica: str) -> tuple[list[dict[str, str]], int]:
    """Valida tudo ANTES da primeira chamada a qualquer baseline."""
    if politica not in POLITICAS:
        raise ValueError("Política G03 não selecionada para o ensaio")
    ficha = _ler_csv(conteudo, COLUNAS_FICHA)
    esperado = {p["id_par"]: p for p in pares}
    if len(esperado) != N_PARES:
        raise ValueError("IDs da origem repetidos ou incompletos")
    vistos: dict[str, dict[str, str]] = {}
    for n, a in enumerate(ficha, start=2):
        ident = a["id_par"]
        if ident not in esperado or ident in vistos:
            raise ValueError(f"Linha {n}: ID desconhecido ou repetido")
        if any(a["frase_" + lado] != esperado[ident]["frase_" + lado] for lado in LADOS):
            raise ValueError(f"Linha {n}: frase diverge do original")
        e, r, obs = a["equivalencia"], a["rotulo"], a["observacoes"]
        if e not in {"sim", "nao", ""} or r not in ROTULOS | {""}:
            raise ValueError(f"Linha {n}: anotação fora dos valores previstos")
        if e == "sim" and not r:
            raise ValueError(f"Linha {n}: equivalente sem rótulo")
        if e != "sim" and r:
            raise ValueError(f"Linha {n}: rótulo inesperado para não equivalente/pendente")
        if e == "nao" and not obs.strip():
            raise ValueError(f"Linha {n}: não equivalência sem justificativa")
        vistos[ident] = a
    if set(vistos) != set(esperado):
        raise ValueError("A ficha precisa conservar todos os 27 IDs")
    faltantes = sum(v["equivalencia"] == "" for v in vistos.values())
    if politica == POLITICA_ESTRITA and faltantes:
        raise ValueError("Ficha incompleta: bloqueio estrito antes da pontuação")
    return [vistos[p["id_par"]] for p in pares], faltantes


def _saida_reduzida(res: dict) -> dict:
    if not isinstance(res, dict) or not {"status", "pontuacao_exploratoria", "classe_exploratoria"}.issubset(res):
        raise ValueError("Baseline violou o contrato mínimo")
    status, nota, classe = (res[k] for k in ("status", "pontuacao_exploratoria", "classe_exploratoria"))
    if not isinstance(status, str) or not status:
        raise ValueError("Status do baseline ausente")
    if status == PONTUADO:
        if type(nota) is not int or classe not in ROTULOS:
            raise ValueError("Pontuação ou classe incompatível com o contrato")
        esperado = "positiva" if nota > 0 else "negativa" if nota < 0 else "neutra"
        if classe != esperado:
            raise ValueError("Classe do baseline contradiz o sinal")
    elif nota is not None or classe is not None:
        raise ValueError("Abstenção não pode ter pontuação/classe")
    return {"status": status, "pontuacao_exploratoria": nota, "classe_exploratoria": classe}


def _taxa(a: int, b: int) -> float | None:
    return round(a / b, 6) if b else None


def agregar_descritivamente(pares: list[dict], ficha: list[dict], preds: dict) -> dict:
    """Agregação separada de inferência, com numeradores e denominadores claros."""
    anot = {r["id_par"]: r for r in ficha}
    if len(pares) != N_PARES or len(anot) != N_PARES or set(preds) != set(anot):
        raise ValueError("Predições/anotações não fecham nos 27 pares")
    elegiveis = {i for i, a in anot.items() if a["equivalencia"] == "sim"}
    posneg = {i for i in elegiveis if anot[i]["rotulo"] in {"positiva", "negativa"}}
    motivos = dict(sorted(Counter(
        "equivalencia_nao" if r["equivalencia"] == "nao" else "sem_resposta"
        for r in ficha if r["equivalencia"] != "sim"
    ).items()))
    r = {
        "P_total": N_PARES, "F_total": N_FRASES,
        "P_equivalentes_R01": len(elegiveis),
        "P_nao_elegiveis": N_PARES - len(elegiveis),
        "P_nao_elegiveis_por_motivo": motivos,
        "P_elegiveis_rotulo_posneg": len(posneg),
        "P_elegiveis_rotulo_neutro": len(elegiveis - posneg),
        "F_elegiveis": 2 * len(elegiveis),
        "metodos": {},
        "acuracia_validada": None, "concordancia_interavaliadores": None,
        "evidencia_de_vies": None, "inferencia_estatistica": None,
    }
    for metodo in METODOS:
        global_scored = eligible_scored = posneg_scored = coincide = calculavel = nonzero = 0
        abst_status = Counter()
        deltas = []
        for par in pares:
            ident = par["id_par"]
            pred = preds[ident]
            if not isinstance(pred, dict) or set(pred) != set(METODOS):
                raise ValueError("Predições sem os três métodos")
            sides = pred[metodo]
            if not isinstance(sides, dict) or set(sides) != set(LADOS):
                raise ValueError("Predição sem os dois lados")
            if not all(set(sides[l]) == {"status", "pontuacao_exploratoria", "classe_exploratoria"}
                       for l in LADOS):
                raise ValueError("Campos de predição inesperados")
            f, m = (sides[l] for l in LADOS)
            for s in (f, m):
                ok = s["status"] == PONTUADO
                global_scored += ok
                if not ok:
                    abst_status[s["status"]] += 1
                if ident in elegiveis:
                    eligible_scored += ok
                if ident in posneg and ok:
                    posneg_scored += 1
                    coincide += s["classe_exploratoria"] == anot[ident]["rotulo"]
            if ident in elegiveis and f["status"] == m["status"] == PONTUADO:
                calculavel += 1
                delta = f["pontuacao_exploratoria"] - m["pontuacao_exploratoria"]
                nonzero += delta != 0
                deltas.append({"id_par": ident, "familia": par["familia"], "delta": delta})
        r["metodos"][metodo] = {
            "F_pontuadas_global": global_scored,
            "F_abstidas_global": N_FRASES - global_scored,
            "taxa_pontuacao_global": _taxa(global_scored, N_FRASES),
            "taxa_abstencao_global": _taxa(N_FRASES - global_scored, N_FRASES),
            "F_pontuadas_elegiveis": eligible_scored,
            "F_abstidas_elegiveis": 2 * len(elegiveis) - eligible_scored,
            "taxa_pontuacao_elegivel": _taxa(eligible_scored, 2 * len(elegiveis)),
            "F_posneg_compativeis": 2 * len(posneg),
            "F_posneg_pontuadas": posneg_scored,
            "F_posneg_coincidentes": coincide,
            "coincidencia_nominal_seletiva_anotacao_unica": _taxa(coincide, posneg_scored),
            "P_delta_calculavel": calculavel,
            "P_delta_nao_calculavel": len(elegiveis) - calculavel,
            "P_delta_nao_nulo": nonzero,
            "taxa_pares_delta_calculavel": _taxa(calculavel, len(elegiveis)),
            "fracao_delta_nao_nulo": _taxa(nonzero, calculavel),
            "deltas_por_par_para_analise_privada": deltas,
            "abstencoes_globais_por_status": dict(sorted(abst_status.items())),
        }
    return r


def executar_nucleo_em_memoria(pares: list[dict], ficha: list[dict], *,
                                indice: Any, nlp: Any,
                                classificadores: dict[str, Callable],
                                politica: str = POLITICA_ESTRITA) -> dict:
    """Código de análise sem I/O; a CLI só o chama com fixture artificial.

    A validação humana deve ocorrer antes desta chamada; a rota sintética
    garante a fixture literal. Falhas propagam, sem resumo parcial.
    """
    if len(pares) != N_PARES or len(ficha) != N_PARES:
        raise ValueError("Lote/anotações de tamanho inválido")
    if any(not isinstance(p, dict) or set(p) != set(CAMPOS_PAR) for p in pares):
        raise ValueError("Esquema dos pares inválido")
    if len({p["id_par"] for p in pares}) != N_PARES:
        raise ValueError("IDs dos pares duplicados")
    # Defense in depth: não confiar que o chamador validou a anotação.
    ficha, _ = validar_ficha_em_memoria(_escrever_csv(ficha, COLUNAS_FICHA),
                                       pares, politica=politica)
    if getattr(indice, "lexico", None) != "sentilex" or nlp is None:
        raise ValueError("Índice SentiLex e etiquetador são obrigatórios")
    if not isinstance(classificadores, dict) or set(classificadores) != set(METODOS) or not all(
        callable(v) for v in classificadores.values()
    ):
        raise ValueError("Versões de baseline inválidas")
    preds = {}
    for par in pares:
        ident = par["id_par"]
        preds[ident] = {}
        for metodo in METODOS:
            preds[ident][metodo] = {}
            for lado in LADOS:
                txt = par["frase_" + lado]
                if metodo == "v01":
                    res = classificadores[metodo](txt, indice, alvo="N0", incluir_diagnostico=False)
                else:
                    res = classificadores[metodo](txt, indice, alvo="N0", nlp=nlp,
                                                  hipotese_modo=True, incluir_diagnostico=False)
                preds[ident][metodo][lado] = _saida_reduzida(res)
    return {"resumo": agregar_descritivamente(pares, ficha, preds), "predicoes": preds}


def _fixture() -> tuple[str, str]:
    """27 pares construídos aqui; NENHUMA amostra do TCC é consultada."""
    origem, ficha = [], []
    for i in range(N_PARES):
        numero = i + 1
        modo = i % 4
        termo = "gentileza" if modo in (0, 2, 3) else "grosseria"
        termo_m = "grosseria" if modo == 3 else termo
        p = {k: "" for k in COLUNAS_ORIGEM}
        p.update({
            "id_par": f"SIM37_{numero:03d}", "familia": f"FIC37_FAM{i // 3 + 1:02d}",
            "particao": "sintetica",
            "frase_feminina": f"A atendente fictícia de número {numero} agiu com {termo}.",
            "frase_masculina": f"O atendente fictício de número {numero} agiu com {termo_m}.",
            "rotulo_revisor1": "DADO_ANTIGO_FICTICIO_NAO_MOSTRAR",
            "id_revisor1": "R_FICTICIO_ANTIGO_NAO_MOSTRAR",
            "alvo_sentilex_feminina": "N1",
            "observacoes": "METADADO_FICTICIO_NAO_MOSTRAR",
        })
        origem.append(p)
        ficha.append({
            "id_par": p["id_par"], "frase_feminina": p["frase_feminina"],
            "frase_masculina": p["frase_masculina"],
            "equivalencia": "nao" if modo == 3 else "sim",
            "rotulo": "" if modo == 3 else ("positiva" if modo == 0 else "negativa" if modo == 1 else "neutra"),
            "observacoes": "Não equivalentes — ficção." if modo == 3 else "",
        })
    return _escrever_csv(origem, COLUNAS_ORIGEM), _escrever_csv(ficha, COLUNAS_FICHA)


def _classificadores_reais():
    from backend.baseline_experimental import classificar_exploratoriamente
    from backend.baseline_contextual_v03 import classificar_v03
    from backend.baseline_contextual_v04 import classificar_v04
    return {"v01": classificar_exploratoriamente,
            "v03": classificar_v03, "v04": classificar_v04}


def ensaiar_sintetico(*, politica: str = POLITICA_ESTRITA,
                       indice=None, nlp=None, classificadores=None,
                       conteudo_fonte: str | None = None,
                       conteudo_ficha: str | None = None) -> dict:
    """Só aceita a fixture exata antes de TODA pontuação.

    Injeções são úteis para testes fictícios; não permitem textos externos.
    """
    padrao_fonte, padrao_ficha = _fixture()
    fonte = padrao_fonte if conteudo_fonte is None else conteudo_fonte
    ficha = padrao_ficha if conteudo_ficha is None else conteudo_ficha
    if fonte != padrao_fonte:
        raise PermissionError("Fonte externa bloqueada: somente fixture literal do Bloco 37")
    if ficha != padrao_ficha:
        # A regra G03 é exercitada por testes unitários em memória, não pela CLI.
        raise PermissionError("Ficha externa bloqueada: somente fixture literal do Bloco 37")
    pares = validar_origem_em_memoria(fonte)
    anotacoes, faltas = validar_ficha_em_memoria(ficha, pares, politica=politica)
    if indice is None or nlp is None:
        if indice is not None or nlp is not None:
            raise ValueError("Índice e etiquetador precisam ser injetados juntos")
        from backend.executor_sintetico_bloco33 import _modelo_ficticio
        indice, nlp = _modelo_ficticio()
    funcs = _classificadores_reais() if classificadores is None else classificadores
    r = executar_nucleo_em_memoria(pares, anotacoes, indice=indice, nlp=nlp,
                                   classificadores=funcs, politica=politica)
    resumo = r["resumo"]
    if resumo["P_total"] != N_PARES or resumo["F_total"] != N_FRASES:
        raise ValueError("Contagens da simulação inconsistentes")
    return {
        "versao": VERSAO,
        "fase": "ENSAIO_SOMENTE_FICTICIO_NAO_AVALIACAO_FINAL",
        "estado": ESTADO,
        "origem": "FIXTURE_LITERAL_BLOCO37_NENHUMA_LEITURA_EXTERNA",
        "sha256_origem_ficticia": _sha(fonte),
        "sha256_ficha_ficticia": _sha(ficha),
        "politica_simulada_nao_aprovada": politica,
        "faltantes_sinteticos": faltas,
        "resumo_sintetico": resumo,
        "protocolo_congelado": False,
        "aprovacao_academica_registrada": False,
        "autorizacao_execucao_final": False,
        "avaliacao_final_executada": False,
        "dados_reservados_lidos": False,
        "acuracia_validada": None,
        "evidencia_de_vies": None,
    }


def verificar_contrato() -> dict:
    return {
        "versao": VERSAO, "estado": ESTADO,
        "modos_cli": ["verificar-contrato", "simular", "executar-final (bloqueado)"],
        "origem_campos": 14, "ficha_campos": 6,
        "n_pares_sinteticos": 27, "n_familias_sinteticas": 9,
        "politicas_g03_somente_propostas": sorted(POLITICAS),
        "politica_aprovada": POLITICA_APROVADA,
        "executor_real_habilitado": False,
        "protocolo_congelado": False,
        "aprovacao_academica_registrada": False,
        "autorizacao_execucao_final": False,
        "dados_reservados_lidos": False,
        "nota": "Núcleo estrutural implementado; operação real precisa de aprovação e outro release.",
    }


def executar_final(*args, **kwargs):
    raise PermissionError("BLOQUEADO: não há autorização acadêmica nem liberação da avaliação reservada")


def main() -> None:
    p = argparse.ArgumentParser(description="SentiVis B37 — núcleo preparado; só fixture artificial")
    p.add_argument("modo", choices=("verificar-contrato", "simular", "executar-final"))
    args = p.parse_args()
    try:
        if args.modo == "verificar-contrato":
            r = verificar_contrato()
        elif args.modo == "simular":
            r = ensaiar_sintetico()
            # Não imprimir 27 linhas ou 162 predições: apenas resumo de ensaio.
            r = {k: v for k, v in r.items() if k != "resumo_sintetico"} | {
                "P_total_sinteticos": r["resumo_sintetico"]["P_total"],
                "F_total_sinteticas": r["resumo_sintetico"]["F_total"],
                "P_equivalentes_sinteticos": r["resumo_sintetico"]["P_equivalentes_R01"],
                "metodos_sinteticos": {k: {
                    "F_pontuadas_global": v["F_pontuadas_global"],
                    "F_abstidas_global": v["F_abstidas_global"],
                    "P_delta_calculavel": v["P_delta_calculavel"]}
                    for k, v in r["resumo_sintetico"]["metodos"].items()},
            }
        else:
            r = executar_final()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("AVISO: a avaliação reservada permanece bloqueada.")
    except (ValueError, PermissionError, OSError, RuntimeError, csv.Error) as exc:
        p.exit(1, f"BLOQUEADO: {exc}\nNenhum dado reservado foi lido por este comando.\n")


if __name__ == "__main__":
    main()
