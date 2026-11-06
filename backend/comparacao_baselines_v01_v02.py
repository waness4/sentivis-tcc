"""SentiVis: comparação descritiva pareada V01 x V02, APENAS desenvolvimento.

Executa exclusivamente o OpLexicon. Não usa a avaliação final para classificação,
não estima viés, não realiza inferência e não modifica os baselines.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.baseline_experimental import (
    PROTOCOLO_ID as PROTOCOLO_V01,
    STATUS_PONTUADO,
    classificar_exploratoriamente,
)
from backend.baseline_gramatical_v02 import (
    PROTOCOLO_V02,
    STATUS_ABSTENCAO_POS,
    carregar_etiquetador,
    classificar_v02,
)
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_consulta import ROOT, carregar_para_consulta
from backend.pares_piloto import ler_csv, status_revisao, validar_pares

METODO = "comparacao_baseline_pos_desenvolvimento_v0.1"
COLUNAS = (
    "id_par", "familia", "sexo_frase", "rotulo_referencia",
    "status_v01", "classe_v01", "pontuacao_v01", "acerto_v01",
    "status_v02", "classe_v02", "pontuacao_v02", "acerto_v02",
    "motivos_v02", "transicao", "cobertura_superficial",
)


def _status_predito(resultado: dict[str, Any]) -> bool:
    return resultado["status"] == STATUS_PONTUADO


def _contabilizar(linhas: list[dict[str, Any]], versao: str) -> dict[str, Any]:
    pontuadas = [r for r in linhas if r[f"status_{versao}"] == STATUS_PONTUADO]
    corretas = sum(r[f"acerto_{versao}"] is True for r in pontuadas)
    incorretas = len(pontuadas) - corretas
    statuses = Counter(r[f"status_{versao}"] for r in linhas)
    return {
        "frases_total": len(linhas),
        "frases_pontuadas": len(pontuadas),
        "frases_abstidas": len(linhas) - len(pontuadas),
        "taxa_pontuadas": round(len(pontuadas) / len(linhas), 6) if linhas else None,
        "previsoes_corretas": corretas,
        "previsoes_incorretas": incorretas,
        "acuracia_seletiva": round(corretas / len(pontuadas), 6) if pontuadas else None,
        "distribuicao_status": dict(sorted(statuses.items())),
    }


def _checar_relacao(v01: dict[str, Any], v02: dict[str, Any]) -> None:
    """A V02 pode apenas manter o resultado ou abster-se por PoS."""
    if not _status_predito(v01):
        if (v01["status"] != v02["status"] or
                v01["pontuacao_exploratoria"] != v02["pontuacao_exploratoria"] or
                v01["classe_exploratoria"] != v02["classe_exploratoria"]):
            raise ValueError("V02 modificou abstenção prévia da V01; comparação interrompida.")
    elif _status_predito(v02):
        if (v01["pontuacao_exploratoria"] != v02["pontuacao_exploratoria"] or
                v01["classe_exploratoria"] != v02["classe_exploratoria"]):
            raise ValueError("V02 modificou pontuação V01 sem abster-se; comparação interrompida.")
    elif v02["status"] != STATUS_ABSTENCAO_POS or v02["pontuacao_exploratoria"] is not None:
        raise ValueError("Transição V01 -> V02 inesperada; comparação interrompida.")


def comparar_desenvolvimento(
    todos: list[dict[str, str]], auditoria: dict, indice: IndiceLexical,
    *, nlp: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Nunca envia uma frase da partição avaliação para classificadores."""
    if indice.lexico != "oplexicon":
        raise ValueError("Bloco 15 compara apenas OpLexicon; SentiLex sem V02.")
    if auditoria.get("erros") or auditoria.get("status") != "ESTRUTURA_VALIDADA_SEM_INFERENCIA_DE_VIES":
        raise ValueError("Dataset não validado estruturalmente.")
    selecionados = [p for p in todos if p["particao"] == "desenvolvimento" and
                   status_revisao(p) == "APROVADO_DUPLA_REVISAO"]
    if not selecionados:
        raise ValueError("Não existem pares aprovados de desenvolvimento.")
    linhas: list[dict[str, Any]] = []
    pares_duplos = {"v01": 0, "v02": 0}
    pares_divergentes = {"v01": 0, "v02": 0}
    transicoes = Counter()
    for par in selecionados:
        resultados: dict[str, dict[str, tuple[dict[str, Any], dict[str, Any]]]] = {
            "feminina": {}, "masculina": {}
        }
        for sexo, campo in (("feminina", "frase_feminina"), ("masculina", "frase_masculina")):
            texto = par[campo]
            v01 = classificar_exploratoriamente(texto, indice)
            v02 = classificar_v02(texto, indice, nlp=nlp)
            _checar_relacao(v01, v02)
            resultados[sexo] = {"v01": v01, "v02": v02}
            antes, depois = _status_predito(v01), _status_predito(v02)
            transicao = "pontuacao_preservada" if antes and depois else (
                "pontuacao_para_abstencao" if antes else "abstencao_preservada"
            )
            transicoes[transicao] += 1
            rotulo = par["rotulo_revisor1"]
            linhas.append({
                "id_par": par["id_par"], "familia": par["familia"],
                "sexo_frase": sexo, "rotulo_referencia": rotulo,
                "status_v01": v01["status"], "classe_v01": v01["classe_exploratoria"],
                "pontuacao_v01": v01["pontuacao_exploratoria"],
                "acerto_v01": v01["classe_exploratoria"] == rotulo if antes else None,
                "status_v02": v02["status"], "classe_v02": v02["classe_exploratoria"],
                "pontuacao_v02": v02["pontuacao_exploratoria"],
                "acerto_v02": v02["classe_exploratoria"] == rotulo if depois else None,
                "motivos_v02": list(v02["motivos"]), "transicao": transicao,
                "cobertura_superficial": v01["cobertura_superficial"],
            })
        for versao in ("v01", "v02"):
            f, m = resultados["feminina"][versao], resultados["masculina"][versao]
            if _status_predito(f) and _status_predito(m):
                pares_duplos[versao] += 1
                if f["classe_exploratoria"] != m["classe_exploratoria"]:
                    pares_divergentes[versao] += 1

    por_id = Counter(p["id_par"] for p in selecionados)
    assert len(por_id) == len(selecionados)  # validacao estrutural já garante IDs únicos
    perdidas_corretas = sum(x["acerto_v01"] is True and x["status_v02"] != STATUS_PONTUADO for x in linhas)
    evitadas_incorretas = sum(x["acerto_v01"] is False and x["status_v02"] != STATUS_PONTUADO for x in linhas)
    resumo = {
        "metodo": METODO,
        "fase": "COMPARACAO_DESCRITIVA_DE_DESENVOLVIMENTO_SEM_INFERENCIA",
        "sha256_dataset_revisado": auditoria["sha256_dataset"],
        "lexico": "oplexicon", "baseline_v01": PROTOCOLO_V01,
        "baseline_v02": PROTOCOLO_V02,
        "pares_desenvolvimento_aprovados": len(selecionados),
        "pares_avaliacao_classificados": 0,
        "metricas": {
            "v01": {**_contabilizar(linhas, "v01"),
                    "pares_ambos_pontuados": pares_duplos["v01"],
                    "pares_classes_divergentes": pares_divergentes["v01"]},
            "v02": {**_contabilizar(linhas, "v02"),
                    "pares_ambos_pontuados": pares_duplos["v02"],
                    "pares_classes_divergentes": pares_divergentes["v02"]},
        },
        "transicoes_v01_para_v02": dict(sorted(transicoes.items())),
        "previsoes_incorretas_v01_retiradas_por_abstencao": evitadas_incorretas,
        "previsoes_corretas_v01_perdidas_por_abstencao": perdidas_corretas,
        "evidencia_de_vies": None,
        "inferencia_estatistica": None,
        "limitacoes": [
            "Somente OpLexicon; a V02 nao implementa alvos N0/N1 do SentiLex.",
            "Comparacao exclusivamente no conjunto de desenvolvimento; sem teste final.",
            "Acuracia seletiva considera apenas frases pontuadas; nao implica acuracia geral.",
            "Reduzir falsos positivos por abstencao nao equivale a classificar corretamente frases neutras.",
            "PoS fornecida por modelo estatistico e sujeita a erros.",
            "Dados de anotacao humana e independência devem ser documentados.",
            "Nenhum resultado comprova presenca ou ausencia de vies de genero.",
        ],
    }
    return resumo, linhas


def salvar_relatorios(json_saida: Path, csv_saida: Path, resumo: dict, linhas: list[dict]) -> None:
    if json_saida.resolve() == csv_saida.resolve():
        raise ValueError("Saídas JSON e CSV devem ser arquivos distintos.")
    if json_saida.exists() or csv_saida.exists():
        raise FileExistsError("Relatório já existente; escolha outro nome (não sobrescrever).")
    json_saida.parent.mkdir(parents=True, exist_ok=True)
    csv_saida.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(resumo, ensure_ascii=False, indent=2) + "\n"
    # Prepara CSV na memória antes de escrever qualquer relatório.
    import io
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, delimiter=";", fieldnames=COLUNAS)
    writer.writeheader()
    for r in linhas:
        writer.writerow({**r, "motivos_v02": "|".join(r["motivos_v02"])})
    with json_saida.open("x", encoding="utf-8") as f:
        f.write(texto)
    with csv_saida.open("x", encoding="utf-8-sig", newline="") as f:
        f.write(buf.getvalue())


def main() -> None:
    p = argparse.ArgumentParser(description="Comparar OpLexicon V01 x V02 somente no desenvolvimento revisado")
    p.add_argument("--entrada", type=Path, required=True)
    p.add_argument("--saida-json", type=Path, required=True)
    p.add_argument("--saida-csv", type=Path, required=True)
    p.add_argument("--raiz", type=Path, default=ROOT)
    args = p.parse_args()
    try:
        todos, sha = ler_csv(args.entrada)
        auditoria = validar_pares(todos, sha256=sha)
        if auditoria["erros"]:
            raise ValueError("Dataset reprovado: " + " | ".join(auditoria["erros"][:3]))
        # A lista de avaliação é lida apenas para checagens estruturais do protocolo.
        # Nenhuma frase reservada é enviada ao V01 ou V02.
        entradas, fontes = carregar_para_consulta(args.raiz.resolve(), "oplexicon")
        indice = IndiceLexical(entradas, lexico="oplexicon")
        nlp = carregar_etiquetador()  # modelo real, nunca etiquetas simuladas na execução CLI
        resumo, linhas = comparar_desenvolvimento(todos, auditoria, indice, nlp=nlp)
        resumo["fontes_lexicais"] = fontes
        try:
            import spacy
            resumo["modelo_pos"] = {"nome": nlp.meta.get("name", "pt_core_news_sm"),
                                    "versao": nlp.meta.get("version", "indeterminada"),
                                    "spacy": spacy.__version__}
        except (ImportError, AttributeError):
            resumo["modelo_pos"] = {"status": "metadados_indisponiveis"}
        salvar_relatorios(args.saida_json, args.saida_csv, resumo, linhas)
        a, b = resumo["metricas"]["v01"], resumo["metricas"]["v02"]
        print(f"Comparacao OpLexicon; desenvolvimento aprovado: {resumo['pares_desenvolvimento_aprovados']} pares")
        print(f"V01: {a['frases_pontuadas']} pontuadas, {a['previsoes_incorretas']} incorretas, {a['frases_abstidas']} sem pontuacao")
        print(f"V02: {b['frases_pontuadas']} pontuadas, {b['previsoes_incorretas']} incorretas, {b['frases_abstidas']} sem pontuacao")
        print(f"Relatorios: {args.saida_json} | {args.saida_csv}")
        print("AVISO: zero frases da avaliacao classificadas; nenhuma inferencia sobre vies.")
    except (FileNotFoundError, FileExistsError, ValueError, UnicodeError, RuntimeError) as exc:
        p.exit(1, f"ERRO: {exc}\n")


if __name__ == "__main__":
    main()
