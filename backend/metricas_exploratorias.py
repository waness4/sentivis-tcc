"""Bloco 12: métricas DESCRITIVAS do piloto humano de DESENVOLVIMENTO.

Não roda o classificador, não abre avaliação final e não calcula evidência de viés.
O comando 'verificar' inspeciona somente a aptidão para iniciar um piloto;
'calcular' exige CSV revisado e um JSON de piloto já produzido pelo Bloco 7.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
import json
import math
from collections import Counter
from pathlib import Path

from backend.baseline_experimental import STATUS_PONTUADO
from backend.pares_piloto import (
    ROOT, ROTULOS, VERSAO as PILOTO_VERSAO, ler_csv, status_revisao, validar_pares,
)

VERSAO = "metricas_descritivas_desenvolvimento_v0.1"
LEXICOS = ("oplexicon", "sentilex")
COLUNAS_CSV = (
    "id_par", "familia", "lexico", "rotulo_referencia", "status_feminina",
    "status_masculina", "pontuacao_feminina", "pontuacao_masculina",
    "classe_feminina", "classe_masculina", "cobertura_feminina",
    "cobertura_masculina", "delta_feminino_masculino", "classes_divergentes",
)
CAMPOS_REVISADO = (
    "rotulo_revisor1", "rotulo_revisor2", "equivalencia_revisor1",
    "equivalencia_revisor2", "id_revisor1", "id_revisor2",
    "alvo_sentilex_feminina", "alvo_sentilex_masculina",
)


def _exigir(condicao: bool, explicacao: str) -> None:
    if not condicao:
        raise ValueError(explicacao)


def _validar_dataset(entrada: Path) -> tuple[list[dict], str, list[dict]]:
    linhas, sha = ler_csv(entrada)
    auditoria = validar_pares(linhas, sha256=sha)
    _exigir(not auditoria["erros"], "CSV inválido: " + " | ".join(auditoria["erros"][:3]))
    # Não aceitar um CSV em que a parte reservada já tenha sido anotada ou liberada.
    for p in linhas:
        if p["particao"] == "avaliacao":
            _exigir(not any(p[c] for c in CAMPOS_REVISADO),
                    "Partição de avaliação anotada: operação bloqueada.")
    aprovados = [p for p in linhas if p["particao"] == "desenvolvimento" and
                 status_revisao(p) == "APROVADO_DUPLA_REVISAO"]
    return linhas, sha, aprovados


def verificar(entrada: Path) -> dict:
    """Nenhuma análise de texto; preserva a avaliação reservada."""
    linhas, sha, aprovados = _validar_dataset(entrada)
    dev = [p for p in linhas if p["particao"] == "desenvolvimento"]
    estados = Counter(status_revisao(p) for p in dev)
    return {
        "fase": "VERIFICACAO_DE_PRONTIDAO_SEM_EXPERIMENTO",
        "sha256_dataset": sha,
        "pares_desenvolvimento": len(dev),
        "pares_aprovados_dupla_revisao": len(aprovados),
        "pendentes_ou_reprovados": len(dev) - len(aprovados),
        "status_revisoes_desenvolvimento": dict(sorted(estados.items())),
        "avaliacao_reservada_processada": False,
        "apto_para_piloto": bool(aprovados),
        "aviso": "Nenhuma frase foi pontuada. Pares reservados não foram utilizados.",
    }


def _real_valido(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _classe(pontuacao: int) -> str:
    return "positiva" if pontuacao > 0 else "negativa" if pontuacao < 0 else "neutra"


def _validar_resultado(r: dict, original: dict, lexico: str) -> None:
    """Impede tratar valores ausentes/incompatíveis como zero ou resultado confiável."""
    ident = original["id_par"]
    _exigir(r.get("id_par") == ident and r.get("familia") == original["familia"],
            "Identificador ou família incompatível com o CSV revisado.")
    _exigir(r.get("particao") == "desenvolvimento" and r.get("lexico") == lexico,
            "Resultado de outra partição ou léxico: operação bloqueada.")
    _exigir(r.get("rotulo_referencia_anotado") == original["rotulo_revisor1"],
            f"Rótulo do par {ident} não corresponde à revisão humana.")
    _exigir(r.get("evidencia_de_vies") is None, "Campo de viés não pode ter conclusão.")
    if lexico == "sentilex":
        _exigir(r.get("alvos_sentilex_manuais_nao_validados") is True,
                "O SentiLex requer marcação de alvo manual não validado.")
    for lado in ("feminina", "masculina"):
        status = r.get(f"status_{lado}")
        pont = r.get(f"pontuacao_{lado}")
        classe = r.get(f"classe_{lado}")
        cobertura = r.get(f"cobertura_{lado}")
        _exigir(isinstance(status, str) and bool(status), "Status ausente no piloto.")
        _exigir(_real_valido(cobertura) and 0 <= cobertura <= 1,
                "Cobertura superficial inválida.")
        if status == STATUS_PONTUADO:
            _exigir(type(pont) is int and classe == _classe(pont),
                    "Pontuação ou classe exploratória inconsistente.")
        else:
            _exigir(pont is None and classe is None,
                    "Abstenção ou sem cobertura não pode possuir classe/pontuação.")
    ambas = r["status_feminina"] == r["status_masculina"] == STATUS_PONTUADO
    delta = r.get("delta_feminino_masculino_exploratorio")
    if ambas:
        _exigir(type(delta) is int and delta == r["pontuacao_feminina"] - r["pontuacao_masculina"],
                "Delta numérico inconsistente.")
    else:
        _exigir(delta is None, "Não se calcula delta quando há abstenção.")


def _taxa(numerador: int, denominador: int) -> float | None:
    return round(numerador / denominador, 6) if denominador else None


def _media(valores: list[float | int]) -> float | None:
    return round(sum(valores) / len(valores), 6) if valores else None


def _metricas_qualidade(previsoes: list[tuple[str, str]]) -> dict:
    """Métricas seletivas descritivas; macro-F1 sobre classes presentes em referência/previsão.

    Não usa abstenções como erros: reporta cobertura seletiva separadamente.
    """
    if not previsoes:
        return {"n_previsoes_pontuadas": 0, "acuracia_seletiva": None,
                "f1_macro_seletivo": None, "classes_calculo_f1": []}
    classes = sorted({classe for par in previsoes for classe in par})
    _exigir(set(classes).issubset(ROTULOS), "Classe fora do conjunto esperado.")
    corretas = sum(real == previsto for real, previsto in previsoes)
    f1 = []
    for classe in classes:
        tp = sum(real == previsto == classe for real, previsto in previsoes)
        fp = sum(real != classe and previsto == classe for real, previsto in previsoes)
        fn = sum(real == classe and previsto != classe for real, previsto in previsoes)
        denominador = 2 * tp + fp + fn
        f1.append(2 * tp / denominador if denominador else 0)
    return {"n_previsoes_pontuadas": len(previsoes),
            "acuracia_seletiva": _taxa(corretas, len(previsoes)),
            "f1_macro_seletivo": _media(f1), "classes_calculo_f1": classes}


def _calcular_grupo(grupo: list[dict]) -> dict:
    """Nenhuma estatística inferencial. Denominadores explícitos para abstenções."""
    n = len(grupo)
    total = 2 * n
    pont_f = sum(r["status_feminina"] == STATUS_PONTUADO for r in grupo)
    pont_m = sum(r["status_masculina"] == STATUS_PONTUADO for r in grupo)
    ambos = [r for r in grupo if r["status_feminina"] == r["status_masculina"] == STATUS_PONTUADO]
    previsoes = [(r["rotulo_referencia_anotado"], r[f"classe_{lado}"])
                for r in grupo for lado in ("feminina", "masculina")
                if r[f"status_{lado}"] == STATUS_PONTUADO]
    deltas = [r["delta_feminino_masculino_exploratorio"] for r in ambos]
    divergencias = sum(r["classe_feminina"] != r["classe_masculina"] for r in ambos)
    return {
        "pares_aprovados": n,
        "frases_no_piloto": total,
        "frases_pontuadas": pont_f + pont_m,
        "frases_sem_pontuacao": total - pont_f - pont_m,
        "taxa_abstencao_ou_sem_cobertura_frases": _taxa(total - pont_f - pont_m, total),
        "frases_femininas_pontuadas": pont_f,
        "frases_masculinas_pontuadas": pont_m,
        "pares_ambos_pontuados": len(ambos),
        "pares_com_ao_menos_uma_sem_pontuacao": n - len(ambos),
        "taxa_pares_ambos_pontuados": _taxa(len(ambos), n),
        "cobertura_superficial_media_feminina": _media([r["cobertura_feminina"] for r in grupo]),
        "cobertura_superficial_media_masculina": _media([r["cobertura_masculina"] for r in grupo]),
        "cobertura_superficial_media_frases": _media(
            [r[f"cobertura_{lado}"] for r in grupo for lado in ("feminina", "masculina")]),
        "delta_assinado_medio_pares_pontuados": _media(deltas),
        "delta_absoluto_medio_pares_pontuados": _media([abs(d) for d in deltas]),
        "pares_classes_divergentes": divergencias,
        "taxa_classes_divergentes_pares_pontuados": _taxa(divergencias, len(ambos)),
        "direcao_delta_pares_pontuados": {
            "positivo": sum(d > 0 for d in deltas),
            "negativo": sum(d < 0 for d in deltas),
            "zero": sum(d == 0 for d in deltas),
        },
        "status_feminina": dict(sorted(Counter(r["status_feminina"] for r in grupo).items())),
        "status_masculina": dict(sorted(Counter(r["status_masculina"] for r in grupo).items())),
        "qualidade_seletiva": _metricas_qualidade(previsoes),
    }


def _extrair_piloto(documento: object, sha_dataset: str) -> dict:
    """Aceita o JSON real do Bloco 7 ({auditoria, piloto}) ou o formato legado.

    Quando presente, a auditoria deve ser válida e corresponder ao mesmo CSV.
    A verificação do piloto, dos pares e da partição continua em calcular().
    """
    _exigir(isinstance(documento, dict), "Relatório do piloto deve ser um objeto JSON.")
    if "piloto" not in documento and "auditoria" not in documento:
        return documento
    auditoria, piloto = documento.get("auditoria"), documento.get("piloto")
    _exigir(isinstance(auditoria, dict) and isinstance(piloto, dict),
            "Relatório integrado exige objetos 'auditoria' e 'piloto'.")
    _exigir(auditoria.get("metodo") == PILOTO_VERSAO and
            auditoria.get("status") == "ESTRUTURA_VALIDADA_SEM_INFERENCIA_DE_VIES" and
            auditoria.get("erros") == [],
            "Auditoria do piloto inválida ou com erros estruturais.")
    _exigir(auditoria.get("sha256_dataset") == sha_dataset,
            "SHA-256 da auditoria difere do CSV de revisão humana.")
    return piloto


def calcular(entrada_csv: Path, piloto_json: Path) -> tuple[dict, list[dict]]:
    """Cruza baseline já executado com CSV humano sem pontuar novas frases.

    O relatório/CSV de saída inclui APENAS pares aprovados do desenvolvimento.
    """
    linhas, sha, aprovados = _validar_dataset(entrada_csv)
    _exigir(bool(aprovados), "Ainda não existem pares aprovados por dois revisores. Métricas bloqueadas.")
    documento = json.loads(piloto_json.read_text(encoding="utf-8"))
    piloto = _extrair_piloto(documento, sha)
    _exigir(piloto.get("metodo") == PILOTO_VERSAO,
            "JSON não foi gerado pelo protocolo do piloto esperado.")
    _exigir(piloto.get("fase") == "PILOTO_EXPLORATORIO_DESENVOLVIMENTO" and
            piloto.get("avaliacao_final_executada") is False and piloto.get("evidencia_de_vies") is None,
            "JSON não identificado como piloto exclusivo de desenvolvimento.")
    _exigir(piloto.get("sha256_dataset") == sha,
            "SHA-256 dos pares difere do piloto. Reexecute o piloto com o CSV consolidado.")
    resultados = piloto.get("resultados")
    _exigir(isinstance(resultados, list), "JSON não possui resultados de piloto válidos.")
    aprovados_por_id = {p["id_par"]: p for p in aprovados}
    esperado = {(lexico, ident) for lexico in LEXICOS for ident in aprovados_por_id}
    vistos = set()
    grupos = {lexico: [] for lexico in LEXICOS}
    linhas_csv = []
    for r in resultados:
        _exigir(isinstance(r, dict), "Resultado não é objeto.")
        lexico, ident = r.get("lexico"), r.get("id_par")
        _exigir((lexico, ident) in esperado, "Resultado não aprovado ou de partição reservada.")
        _exigir((lexico, ident) not in vistos, "Resultado duplicado no relatório.")
        vistos.add((lexico, ident))
        _validar_resultado(r, aprovados_por_id[ident], lexico)
        grupos[lexico].append(r)
        ambas = r["status_feminina"] == r["status_masculina"] == STATUS_PONTUADO
        linhas_csv.append({
            "id_par": ident, "familia": r["familia"], "lexico": lexico,
            "rotulo_referencia": r["rotulo_referencia_anotado"],
            "status_feminina": r["status_feminina"], "status_masculina": r["status_masculina"],
            "pontuacao_feminina": r["pontuacao_feminina"],
            "pontuacao_masculina": r["pontuacao_masculina"],
            "classe_feminina": r["classe_feminina"], "classe_masculina": r["classe_masculina"],
            "cobertura_feminina": r["cobertura_feminina"],
            "cobertura_masculina": r["cobertura_masculina"],
            "delta_feminino_masculino": r["delta_feminino_masculino_exploratorio"],
            "classes_divergentes": (r["classe_feminina"] != r["classe_masculina"]) if ambas else None,
        })
    _exigir(vistos == esperado, f"Resultados incompletos no JSON: esperado {len(esperado)}, encontrados {len(vistos)}.")
    linhas_csv.sort(key=lambda r: (r["id_par"], r["lexico"]))
    resumo = {
        "metodo": VERSAO,
        "fase": "METRICAS_DESCRITIVAS_DESENVOLVIMENTO_NAO_INFERENCIA",
        "sha256_dataset_revisado": sha,
        "metodo_baseline": "baseline_aditivo_exploratorio_v0.1",
        "pares_desenvolvimento_aprovados": len(aprovados),
        "pares_avaliacao_processados": 0,
        "metricas_por_lexico": {nome: _calcular_grupo(grupos[nome]) for nome in LEXICOS},
        "fontes_lexicais_manifestos": piloto.get("manifestos_fontes", {}),
        "evidencia_de_vies": None,
        "intervalos_de_confianca": None,
        "inferencia_estatistica": None,
        "limitacoes": [
            "Apenas pares com concordância de dois revisores, no desenvolvimento.",
            "Baseline aditivo não validado linguisticamente; as métricas são descritivas.",
            "Qualidade seletiva condicionada às frases pontuadas; reportar abstenção separadamente.",
            "Cobertura é média de proporções por frase, não cobertura token-ponderada global.",
            "Diferenças de pontuação não implicam causalidade, discriminação ou ausência de viés.",
            "Sem inferência, intervalo de confiança ou análise da avaliação final neste bloco.",
        ],
    }
    return resumo, linhas_csv


def _salvar_resultados(saida_json: Path, saida_csv: Path, resumo: dict, linhas: list[dict]) -> None:
    _exigir(saida_json.resolve() != saida_csv.resolve(), "Destinos JSON/CSV devem ser diferentes.")
    _exigir(not saida_json.exists() and not saida_csv.exists(),
            "Arquivos de saída já existem. Use nomes novos para preservar a rastreabilidade.")
    # Validar e serializar integralmente ambas as saídas antes de criar qualquer destino.
    conteudo_json = (json.dumps(resumo, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    buffer_csv = io.StringIO(newline="")
    writer = csv.DictWriter(buffer_csv, fieldnames=COLUNAS_CSV, delimiter=";")
    writer.writeheader()
    writer.writerows(linhas)
    conteudo_csv = buffer_csv.getvalue().encode("utf-8-sig")

    temporarios: list[Path] = []
    publicados: list[Path] = []
    try:
        for destino, conteudo in ((saida_json, conteudo_json), (saida_csv, conteudo_csv)):
            destino.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".sentivis-", suffix=".tmp",
                dir=destino.parent, delete=False,
            ) as temporario:
                temporarios.append(Path(temporario.name))
                temporario.write(conteudo)
                temporario.flush()
                os.fsync(temporario.fileno())

        # Cada hard link publica um arquivo completo sem sobrescrever destinos existentes.
        # Se a segunda publicação falhar, remover a primeira criada nesta operação.
        for origem, destino in zip(temporarios, (saida_json, saida_csv)):
            os.link(origem, destino)
            publicados.append(destino)
    except BaseException:
        for destino in reversed(publicados):
            destino.unlink(missing_ok=True)
        raise
    finally:
        for temporario in temporarios:
            temporario.unlink(missing_ok=True)


def main() -> None:
    p = argparse.ArgumentParser(description="SentiVis: verificação e métricas exploratórias SOMENTE desenvolvimento")
    sub = p.add_subparsers(dest="comando", required=True)
    verificar_cmd = sub.add_parser("verificar", help="Mostra prontidão sem pontuar frases")
    verificar_cmd.add_argument("--entrada", type=Path, default=ROOT / "data/piloto/pares_candidatos_v01.csv")
    calcular_cmd = sub.add_parser("calcular", help="Métricas condicionadas à dupla revisão e ao piloto existente")
    calcular_cmd.add_argument("--entrada", type=Path, default=ROOT / "data/piloto/restrito/pares_desenvolvimento_revisados_v01.csv")
    calcular_cmd.add_argument("--piloto", type=Path, default=ROOT / "data/piloto/restrito/resultado_piloto_v01.json")
    calcular_cmd.add_argument("--saida-json", type=Path, default=ROOT / "data/piloto/restrito/metricas_desenvolvimento_v01.json")
    calcular_cmd.add_argument("--saida-csv", type=Path, default=ROOT / "data/piloto/restrito/metricas_desenvolvimento_v01.csv")
    args = p.parse_args()
    try:
        if args.comando == "verificar":
            r = verificar(args.entrada)
            print("Verificação de desenvolvimento:")
            print(f"Pares: {r['pares_desenvolvimento']}; aprovados: {r['pares_aprovados_dupla_revisao']}; "
                  f"pendentes ou reprovados: {r['pendentes_ou_reprovados']}")
            print("Nenhuma avaliação final acessada, nenhuma métrica de sentimentos calculada.")
        else:
            for destino in (args.saida_json.resolve(), args.saida_csv.resolve()):
                _exigir(destino not in {args.entrada.resolve(), args.piloto.resolve()},
                        "Destino de saída não pode sobrescrever dados de entrada.")
            resumo, linhas = calcular(args.entrada, args.piloto)
            _salvar_resultados(args.saida_json, args.saida_csv, resumo, linhas)
            print(f"Relatório: {args.saida_json}")
            print(f"Linhas descritivas: {args.saida_csv}")
            print(f"Pares de desenvolvimento aprovados: {resumo['pares_desenvolvimento_aprovados']}")
            print("AVISO: nenhuma conclusão de viés ou avaliação final executada.")
    except (ValueError, FileNotFoundError, UnicodeError, json.JSONDecodeError) as erro:
        p.exit(1, f"ERRO: {erro}\n")


if __name__ == "__main__":
    main()
