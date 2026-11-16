"""Bloco 29 — ensaio *exclusivamente sintético* da futura avaliação final.

Não há parâmetro de arquivo ou modo de avaliação reservada. Nenhuma frase real,
revisão humana real, léxico baixado ou partição de avaliação é aberta.
O módulo testa contratos, denominadores, abstenção e a integração V01/V03/V04
por meio de quatro pares inventados e entradas lexicais inteiramente fictícias.
O protocolo final continua pendente de aprovação e congelamento.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
import re
from typing import Any

VERSAO = "preparacao_avaliacao_final_bloco29_simulacao_v01"
PONTUADO = "PONTUACAO_EXPLORATORIA_NAO_VALIDADA"
METODOS = ("v01", "v03", "v04")
ROTULOS = frozenset({"positiva", "negativa", "neutra"})
FICHA_CAMPOS = frozenset({
    "id_par", "frase_feminina", "frase_masculina",
    "equivalencia", "rotulo", "observacoes",
})


def _razao(numerador: int, denominador: int) -> float | None:
    return round(numerador / denominador, 6) if denominador else None


def validar_ficha(pares: list[dict], ficha: list[dict]) -> dict[str, dict]:
    """Confere respostas de UMA pessoa sem consultar qualquer previsão.

    Uma resposta vazia não se transforma em rótulo ou equivalência válida.
    Cada par com equivalência 'sim' exige rótulo, incluindo o estrato neutro.
    """
    esperados = {p["id_par"]: p for p in pares}
    if not pares or len(esperados) != len(pares):
        raise ValueError("IDs dos pares ausentes ou duplicados")
    encontrados: dict[str, dict] = {}
    for linha in ficha:
        if set(linha) != FICHA_CAMPOS:
            raise ValueError("Esquema da ficha inválido")
        ident = linha["id_par"]
        if ident not in esperados or ident in encontrados:
            raise ValueError("ID da ficha desconhecido ou duplicado")
        original = esperados[ident]
        for lado in ("frase_feminina", "frase_masculina"):
            if linha[lado] != original[lado]:
                raise ValueError("Frase da ficha diferente do original")
        equivalencia, rotulo = linha["equivalencia"], linha["rotulo"]
        if equivalencia not in {"sim", "nao", ""} or rotulo not in ROTULOS | {""}:
            raise ValueError("Valores de anotação desconhecidos")
        if equivalencia == "sim" and not rotulo:
            raise ValueError("Par equivalente sem rótulo")
        if equivalencia != "sim" and rotulo:
            raise ValueError("Par não equivalente/com resposta pendente não pode ter rótulo")
        if equivalencia == "nao" and not linha["observacoes"].strip():
            raise ValueError("Não equivalência sem justificativa")
        encontrados[ident] = linha
    if set(encontrados) != set(esperados):
        raise ValueError("Ficha incompleta: conjunto de IDs não coincide")
    return encontrados


def _validar_saida(saida: dict) -> tuple[bool, int | None, str | None, str]:
    campos = {"status", "pontuacao_exploratoria", "classe_exploratoria"}
    if not isinstance(saida, dict) or not campos.issubset(saida):
        raise ValueError("Saída de baseline sem contrato mínimo")
    status, nota, classe = (saida[x] for x in ("status", "pontuacao_exploratoria", "classe_exploratoria"))
    if not isinstance(status, str) or not status:
        raise ValueError("Status do baseline inválido")
    pontuado = status == PONTUADO
    if pontuado:
        if type(nota) is not int or classe not in ROTULOS:
            raise ValueError("Pontuação ou classe inválida em resultado pontuado")
        classe_esperada = "positiva" if nota > 0 else "negativa" if nota < 0 else "neutra"
        if classe != classe_esperada:
            raise ValueError("Classe contradiz o sinal da pontuação")
    elif nota is not None or classe is not None:
        raise ValueError("Abstenção não pode receber pontuação nem classe")
    return pontuado, nota, classe, status


def resumir(pares: list[dict], ficha: list[dict], predicoes: dict[str, dict]) -> dict:
    """Agrega decisões sem produzir inferência estatística nem acurácia validada.

    A fonte humana deve ser preservada à parte: nenhuma frase ou observação é
    reproduzida na saída agregada. Rótulos neutros são um estrato separado.
    """
    anotacoes = validar_ficha(pares, ficha)
    if set(predicoes) != set(anotacoes):
        raise ValueError("Predições incompletas ou com IDs adicionais")
    n_pares = len(pares)
    elegiveis = {i for i, a in anotacoes.items() if a["equivalencia"] == "sim"}
    posneg = {i for i in elegiveis if anotacoes[i]["rotulo"] in ("positiva", "negativa")}
    neutros = elegiveis - posneg
    base = {
        "metodo": VERSAO,
        "fase": "SIMULACAO_SINTETICA_SEM_ACESSO_AVALIACAO_FINAL",
        "P_total": n_pares,
        "F_total": 2 * n_pares,
        "P_equivalentes_R01": len(elegiveis),
        "P_nao_elegiveis": n_pares - len(elegiveis),
        "P_nao_elegiveis_por_motivo": dict(sorted(Counter(
            "equivalencia_nao" if a["equivalencia"] == "nao" else "sem_resposta"
            for a in anotacoes.values() if a["equivalencia"] != "sim"
        ).items())),
        "P_elegiveis_com_rotulo_posneg": len(posneg),
        "P_elegiveis_com_rotulo_neutro_separado": len(neutros),
        "F_elegiveis": 2 * len(elegiveis),
        "metodos": {},
        "concordancia_interavaliadores": None,
        "acuracia_validada": None,
        "f1_validado": None,
        "evidencia_de_vies": None,
        "inferencia_estatistica": None,
        "aviso": "SIMULAÇÃO: não é avaliação final e não demonstra qualidade ou viés.",
    }
    for metodo in METODOS:
        total_pontuadas = elegiveis_pontuadas = posneg_pontuadas = coincidencias = 0
        delta_calculavel = delta_nao_nulo = 0
        distribuicao_abstencoes = Counter()
        for ident, por_metodo in predicoes.items():
            if set(por_metodo) != set(METODOS):
                raise ValueError("Métodos incompletos ou desconhecidos")
            lado = por_metodo[metodo]
            if set(lado) != {"feminina", "masculina"}:
                raise ValueError("Saída deve conter os dois lados do par")
            f, m = (_validar_saida(lado[x]) for x in ("feminina", "masculina"))
            for pontuado, _, classe, status in (f, m):
                total_pontuadas += pontuado
                if not pontuado:
                    distribuicao_abstencoes[status] += 1
                if ident in elegiveis:
                    elegiveis_pontuadas += pontuado
                if ident in posneg and pontuado:
                    posneg_pontuadas += 1
                    coincidencias += classe == anotacoes[ident]["rotulo"]
            if ident in elegiveis and f[0] and m[0]:
                delta_calculavel += 1
                delta_nao_nulo += f[1] != m[1]
        f_total = 2 * n_pares
        f_elegiveis = 2 * len(elegiveis)
        f_posneg = 2 * len(posneg)
        base["metodos"][metodo] = {
            "F_pontuadas_global": total_pontuadas,
            "F_abstidas_global": f_total - total_pontuadas,
            "taxa_pontuacao_global": _razao(total_pontuadas, f_total),
            "taxa_abstencao_global": _razao(f_total - total_pontuadas, f_total),
            "F_pontuadas_elegiveis": elegiveis_pontuadas,
            "F_abstidas_elegiveis": f_elegiveis - elegiveis_pontuadas,
            "taxa_pontuacao_elegivel": _razao(elegiveis_pontuadas, f_elegiveis),
            "F_posneg_compativeis": f_posneg,
            "F_posneg_pontuadas": posneg_pontuadas,
            "F_posneg_coincidentes": coincidencias,
            "coincidencia_nominal_seletiva_anotacao_unica": _razao(coincidencias, posneg_pontuadas),
            "P_delta_calculavel": delta_calculavel,
            "P_delta_nao_calculavel": len(elegiveis) - delta_calculavel,
            "P_delta_nao_nulo": delta_nao_nulo,
            "taxa_pares_delta_calculavel": _razao(delta_calculavel, len(elegiveis)),
            "fracao_delta_nao_nulo": _razao(delta_nao_nulo, delta_calculavel),
            "abstencoes_globais_por_status": dict(sorted(distribuicao_abstencoes.items())),
        }
    return base


# Os exemplos abaixo são INTEIRAMENTE INVENTADOS e não derivam do corpus do TCC.
# A simulação nunca carrega nenhum arquivo de entrada, nem original nem reservado.
def _ficticios() -> tuple[list[dict], list[dict]]:
    pares = [
        {"id_par": "SINT001", "frase_feminina": "A atendente tratou com gentileza.",
         "frase_masculina": "O atendente tratou com gentileza."},
        {"id_par": "SINT002", "frase_feminina": "A atendente tratou com grosseria.",
         "frase_masculina": "O atendente tratou com grosseria."},
        {"id_par": "SINT003", "frase_feminina": "A atendente entregou a ficha.",
         "frase_masculina": "O atendente entregou a ficha."},
        {"id_par": "SINT004", "frase_feminina": "A atendente tratou com gentileza.",
         "frase_masculina": "O atendente tratou com grosseria."},
    ]
    fichas = [
        {"id_par": p["id_par"], "frase_feminina": p["frase_feminina"],
         "frase_masculina": p["frase_masculina"],
         "equivalencia": "nao" if p["id_par"] == "SINT004" else "sim",
         "rotulo": {"SINT001": "positiva", "SINT002": "negativa", "SINT003": "neutra"}.get(p["id_par"], ""),
         "observacoes": "Textos semanticamente diferentes (fictício)." if p["id_par"] == "SINT004" else "",
        } for p in pares
    ]
    return pares, fichas


@dataclass
class _Token:
    text: str
    idx: int
    pos_: str
    dep_: str = "dep"
    head: Any = None
    children: list = field(default_factory=list)


class _EtiquetadorFicticio:
    """Simula exclusivamente as dependências sintáticas da fixture; não é spaCy."""
    meta = {"version": "ficticio-sem-validacao"}

    def __call__(self, texto: str) -> list[_Token]:
        tokens = [_Token(x.group(), x.start(), "NOUN")
                  for x in re.finditer(r"[^\W\d_]+", texto)]
        for t in tokens:
            t.head = t
            if t.text.casefold() in {"tratou", "entregou"}:
                t.pos_, t.dep_ = "VERB", "ROOT"
            if t.text.casefold() == "com":
                t.pos_, t.dep_ = "ADP", "case"
        for i, tok in enumerate(tokens[:-1]):
            if tok.text.casefold() == "com":
                objeto = tokens[i + 1]
                tok.head = objeto
                objeto.children.append(tok)
                cabecas = [t for t in tokens if t.text.casefold() == "tratou"]
                if cabecas:
                    objeto.head, objeto.dep_ = cabecas[0], "obl"
        return tokens


def simular() -> dict:
    """ÚNICA execução acessível via CLI; sem caminhos fornecidos pelo operador."""
    from backend.baseline_experimental import classificar_exploratoriamente
    from backend.baseline_contextual_v03 import classificar_v03
    from backend.baseline_contextual_v04 import classificar_v04
    from backend.frase_diagnostico import IndiceLexical
    from backend.lexicon_audit import EntradaLexical

    def entrada(termo: str, nota: int, linha: int) -> EntradaLexical:
        return EntradaLexical(
            origem="sentilex_flex", arquivo="FICTICIO", linha=linha,
            termo=termo, lema=termo, categoria="N",
            polaridades=(("N0", nota),), alvo="HUM:N0", flexao=None,
            anotacao="MAN", revisao=None, atributos_originais=(),
        )

    indice = IndiceLexical([entrada("gentileza", 1, 1),
                            entrada("grosseria", -1, 2)], lexico="sentilex")
    nlp = _EtiquetadorFicticio()
    pares, fichas = _ficticios()
    if len(pares) != 4 or any(not p["id_par"].startswith("SINT") for p in pares):
        raise RuntimeError("Fixture sintética inesperada")
    resultados: dict[str, dict] = {}
    for p in pares:
        resultados[p["id_par"]] = {}
        for versao in METODOS:
            resultados[p["id_par"]][versao] = {}
            for lado in ("feminina", "masculina"):
                texto = p["frase_" + lado]
                if versao == "v01":
                    r = classificar_exploratoriamente(texto, indice, alvo="N0")
                elif versao == "v03":
                    r = classificar_v03(texto, indice, alvo="N0", nlp=nlp, hipotese_modo=True)
                else:
                    r = classificar_v04(texto, indice, alvo="N0", nlp=nlp, hipotese_modo=True)
                resultados[p["id_par"]][versao][lado] = r
    return resumir(pares, fichas, resultados)


def main() -> None:
    cli = argparse.ArgumentParser(description="Ensaio somente fictício; NÃO aceita arquivos de avaliação final")
    cli.add_argument("modo", choices=["simular"])
    args = cli.parse_args()
    if args.modo == "simular":
        print(json.dumps(simular(), ensure_ascii=False, indent=2))
        print("AVISO: SIMULAÇÃO, não execução da partição reservada.")


if __name__ == "__main__":
    main()
