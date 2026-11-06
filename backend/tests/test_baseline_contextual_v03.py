"""Testes sintéticos do V03. Não constituem avaliação científica/validação do spaCy real."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pytest

from backend.baseline_contextual_v03 import (
    PROTOCOLO_V03,
    STATUS_ABSTENCAO_ANEXACAO,
    STATUS_ABSTENCAO_HIPOTESE,
    STATUS_ABSTENCAO_POS,
    STATUS_ABSTENCAO_SINTATICA,
    classificar_v03,
    comparar_v03,
)
from backend.baseline_experimental import STATUS_PONTUADO, classificar_exploratoriamente
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_audit import EntradaLexical


def lexema(termo, polaridade=1, categoria="N", *, papel="N0", origem="sentilex_flex", linha=1):
    return EntradaLexical(
        origem=origem, arquivo="fixture.txt", linha=linha,
        termo=termo, lema=termo, categoria=categoria,
        polaridades=((papel, polaridade),), alvo=f"HUM:{papel}", flexao=None,
        anotacao="MAN", revisao=None, atributos_originais=(),
    )


def idx(*args, lexico="sentilex"):
    return IndiceLexical(args, lexico=lexico)


@dataclass
class FakeToken:
    text: str
    idx: int
    pos_: str
    dep_: str = "dep"
    head: object | None = None
    children: list = field(default_factory=list)


class FakeNLP:
    meta = {"version": "fixture"}

    def __init__(self, *, anexacao=None, pos=None):
        self.anexacao = anexacao or {}
        self.pos = pos or {}

    def __call__(self, texto):
        pats = list(re.finditer(r"[^\W\d_]+", texto))
        toks = [FakeToken(m.group(), m.start(), self.pos.get(m.group().casefold(), "NOUN")) for m in pats]
        for t in toks:
            t.head = t
        for i, t in enumerate(toks):
            x = t.text.casefold()
            if x in {"tratou", "resolveu", "respondeu", "analisou", "causou"}:
                t.pos_ = "VERB"
                t.dep_ = "ROOT"
            if x in {"com"}:
                t.pos_ = "ADP"
                t.dep_ = "case"
            if x == "não":
                t.pos_ = "ADV"
        for i, t in enumerate(toks):
            x = t.text.casefold()
            if x == "com" and i + 1 < len(toks):
                proximo = toks[i + 1]
                t.head = proximo
                proximo.children.append(t)
                dep, cabeca = self.anexacao.get(proximo.text.casefold(), ("obl", "tratou"))
                proximo.dep_ = dep
                cabecas = [c for c in toks if c.text.casefold() == cabeca.casefold()]
                if cabecas:
                    proximo.head = cabecas[0]
            if x == "problema":
                t.dep_ = "obj"
        # se não existir verbo especificado como raiz, a palavra é noun; não importa aqui.
        return toks


def executar_exemplo(texto, *entradas, alvo="N0", hipotese_modo=True, nlp=None):
    return classificar_v03(texto, idx(*entradas), alvo=alvo,
                          nlp=nlp or FakeNLP(), hipotese_modo=hipotese_modo)


def test_sem_alvo_nao_inventa_n0():
    r = classificar_v03("A atendente tratou com gentileza.", idx(lexema("gentileza")))
    assert r["status"] == "ABSTENCAO_ALVO"
    assert r["alvo_resolvido_automaticamente"] is False
    assert r["pontuacao_exploratoria"] is None


def test_modo_nao_autorizado_default_abstem():
    r = executar_exemplo("A atendente tratou com gentileza.", lexema("gentileza"), hipotese_modo=False)
    assert r["status"] == STATUS_ABSTENCAO_HIPOTESE
    assert r["pontuacao_exploratoria"] is None


def test_p004_hipotese_positiva():
    r = executar_exemplo("A atendente tratou o cliente com gentileza.", lexema("gentileza"))
    assert r["status"] == STATUS_PONTUADO
    assert r["metodo"] == PROTOCOLO_V03
    assert r["classe_exploratoria"] == "positiva"
    assert r["pontuacao_exploratoria"] == 1
    assert r["termos_pontuados"][0]["expressao"] == "gentileza"
    assert r["papel_semantico_validado"] is False


def test_p005_hipotese_negativa():
    r = executar_exemplo("A atendente tratou com grosseria.", lexema("grosseria", -1))
    assert r["status"] == STATUS_PONTUADO
    assert r["classe_exploratoria"] == "negativa"


def test_p008_hipotese_nao_soma_objeto():
    nlp = FakeNLP(anexacao={"descuido": ("obl", "resolveu")})
    r = executar_exemplo("A programadora resolveu o problema com descuido.",
               lexema("problema", -1), lexema("descuido", -1), nlp=nlp)
    assert r["status"] == STATUS_PONTUADO
    assert r["pontuacao_exploratoria"] == -1  # e NÃO -2
    assert [x["expressao"] for x in r["termos_pontuados"]] == ["descuido"]
    assert len(r["checagens_contextuais"]) == 2
    assert any(x["papel_hipotetico"] == "argumento_objeto_nao_somado" for x in r["checagens_contextuais"])


def test_p007_anexacao_ambigua_abstem_sem_tentar_ajustar():
    nlp = FakeNLP(anexacao={"habilidade": ("nmod", "problema")})
    r = executar_exemplo("A programadora resolveu o problema com habilidade.",
               lexema("problema", -1), lexema("habilidade", 1), nlp=nlp)
    assert r["status"] == STATUS_ABSTENCAO_ANEXACAO
    assert r["pontuacao_exploratoria"] is None


def test_sem_com_nao_usa_substantivo_objeto():
    r = executar_exemplo("A atendente demonstrou dedicação.", lexema("dedicação", 1))
    assert r["status"] == STATUS_ABSTENCAO_SINTATICA
    assert r["classe_exploratoria"] is None


def test_com_sentido_de_instrumento_e_limite_documentado():
    # Estrutura idêntica pode representar instrumento; regra é APENAS HIPÓTESE.
    r = executar_exemplo("A atendente tratou com gentileza.", lexema("gentileza", 1))
    assert any("instrumento" in aviso for aviso in r["avisos"])
    assert not r["papel_semantico_validado"]


def test_pos_incompativel_abstem():
    r = executar_exemplo("A atendente tratou com gentileza.", lexema("gentileza", 1, "Adj"))
    assert r["status"] == STATUS_ABSTENCAO_POS
    assert "categoria_gramatical_incompativel" in r["motivos"]


def test_categoria_desconhecida_abstem():
    r = executar_exemplo("A atendente tratou com gentileza.", lexema("gentileza", 1, "X"))
    assert r["status"] == STATUS_ABSTENCAO_POS
    assert "categoria_lexical_nao_mapeada" in r["motivos"]


def test_alvo_errado_nao_pontua():
    r = executar_exemplo("A atendente tratou com gentileza.", lexema("gentileza", 1), alvo="N1")
    assert r["pontuacao_exploratoria"] is None
    assert r["status"] == "ABSTENCAO_LEXICAL"


def test_negacao_v01_preservada():
    r = executar_exemplo("A atendente não tratou com gentileza.", lexema("gentileza"))
    assert r["status"] == "ABSTENCAO_CONTEXTO"
    assert r["classe_exploratoria"] is None


def test_sem_cobertura_preservada():
    r = executar_exemplo("A atendente respondeu.", lexema("gentileza"))
    assert r["status"] == "SEM_COBERTURA"
    assert r["pontuacao_exploratoria"] is None


def test_v01_intocado_antes_e_depois():
    i = idx(lexema("problema", -1), lexema("descuido", -1))
    texto = "A programadora resolveu o problema com descuido."
    antes = classificar_exploratoriamente(texto, i, alvo="N0")
    r = classificar_v03(texto, i, alvo="N0", hipotese_modo=True, nlp=FakeNLP(
        anexacao={"descuido": ("obl", "resolveu")}
    ))
    depois = classificar_exploratoriamente(texto, i, alvo="N0")
    assert antes == depois
    assert antes["pontuacao_exploratoria"] == -2
    assert r["pontuacao_exploratoria"] == -1


def test_comparacao_par_delta_zero_nao_inferencial():
    i = idx(lexema("gentileza", 1))
    r = comparar_v03("A atendente tratou com gentileza.",
                     "O atendente tratou com gentileza.", i,
                     alvo="N0", hipotese_modo=True, nlp=FakeNLP())
    assert r["ambas_pontuaveis"] is True
    assert r["delta_feminino_masculino_exploratorio"] == 0
    assert r["evidencia_de_vies"] is None
    assert not r["equivalencia_semantica_validada"]


def test_comparacao_abstencao_delta_none():
    i = idx(lexema("gentileza", 1))
    r = comparar_v03("A atendente tratou com gentileza.",
                     "O atendente respondeu.", i,
                     alvo="N0", hipotese_modo=True, nlp=FakeNLP())
    assert r["ambas_pontuaveis"] is False
    assert r["delta_feminino_masculino_exploratorio"] is None


def test_indice_op_invalid_rejeitado():
    i = idx(lexema("gentileza", 1), lexico="oplexicon")
    with pytest.raises(ValueError, match="SentiLex"):
        classificar_v03("gentileza", i)


def test_alvo_invalido_rejeitado():
    with pytest.raises(ValueError, match="Alvo"):
        classificar_v03("gentileza", idx(lexema("gentileza")), alvo="N2")


def test_diagnostico_opcional():
    i = idx(lexema("gentileza"))
    p = "A atendente tratou com gentileza."
    r = classificar_v03(p, i, alvo="N0", nlp=FakeNLP(), hipotese_modo=True)
    s = classificar_v03(p, i, alvo="N0", nlp=FakeNLP(), hipotese_modo=True,
                       incluir_diagnostico=True)
    assert "diagnostico_lexical" not in r
    assert "diagnostico_lexical" in s


def test_lexico_polaridade_zero_nao_confunde_sem_cobertura():
    r = executar_exemplo("A atendente tratou com neutralidade.", lexema("neutralidade", 0))
    assert r["classe_exploratoria"] == "neutra"
    assert r["origem_soma_zero"] == "polaridade_lexical_zero"
