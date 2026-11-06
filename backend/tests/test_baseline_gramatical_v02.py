"""Testes sintéticos e determinísticos de engenharia; não validam o spaCy real."""
from dataclasses import dataclass
import re

import pytest

from backend.baseline_experimental import STATUS_PONTUADO, classificar_exploratoriamente
from backend.baseline_gramatical_v02 import (
    PROTOCOLO_V02, STATUS_ABSTENCAO_POS, classificar_v02, comparar_v02,
)
from backend.frase_diagnostico import IndiceLexical
from backend.lexicon_audit import EntradaLexical


@dataclass
class Token:
    text: str
    idx: int
    pos_: str


class EtiquetadorFalso:
    def __init__(self, categorias: dict[str, str], *, desalinhar=False):
        self.categorias = categorias
        self.desalinhar = desalinhar

    def __call__(self, texto):
        tokens = [Token(m.group(), m.start(), self.categorias.get(m.group().casefold(), ""))
                  for m in re.finditer(r"\w+", texto)]
        if self.desalinhar:
            for t in tokens:
                t.idx += 1
        return tokens


def entrada(termo, pol=1, categoria="adj", origem="oplexicon"):
    return EntradaLexical(
        origem=origem, arquivo="fixture_op.txt", linha=1, termo=termo,
        lema=None if origem == "oplexicon" else termo,
        categoria=categoria, polaridades=(("GLOBAL" if origem == "oplexicon" else "N0", pol),),
        alvo=None if origem == "oplexicon" else "HUM:N0", flexao=None,
        anotacao="MAN", revisao=None, atributos_originais=(),
    )


def indice(*itens, lexico="oplexicon"):
    return IndiceLexical(itens, lexico=lexico)


def test_p006_substantivo_nao_recebe_adjetivo_positivo():
    texto = "A atendente registrou o pedido."
    i = indice(entrada("pedido", 1, "adj"))
    r = classificar_v02(texto, i, nlp=EtiquetadorFalso({"pedido": "NOUN"}))
    assert r["metodo"] == PROTOCOLO_V02
    assert r["status"] == STATUS_ABSTENCAO_POS
    assert r["motivos"] == ["categoria_gramatical_incompativel"]
    assert r["pontuacao_exploratoria"] is None
    assert r["classe_exploratoria"] is None
    assert r["cobertura_superficial"] == .2
    assert r["checagens_gramaticais"][0]["tokens_spacy"][0]["pos"] == "NOUN"


def test_v01_permanece_intocado():
    i = indice(entrada("pedido", 1, "adj"))
    texto = "A atendente registrou o pedido."
    assert classificar_exploratoriamente(texto, i)["pontuacao_exploratoria"] == 1
    assert classificar_v02(texto, i, nlp=EtiquetadorFalso({"pedido": "NOUN"}))["pontuacao_exploratoria"] is None
    assert classificar_exploratoriamente(texto, i)["pontuacao_exploratoria"] == 1


def test_adjetivo_compativel_permanece_pontuado():
    r = classificar_v02("A aluna é dedicada.", indice(entrada("dedicada")),
                       nlp=EtiquetadorFalso({"dedicada": "ADJ"}))
    assert r["status"] == STATUS_PONTUADO
    assert r["pontuacao_exploratoria"] == 1
    assert r["validacao_gramatical"] == "compativel_pos_predita"


def test_nome_compativel_permanece_pontuado():
    r = classificar_v02("pedido", indice(entrada("pedido", 1, "noun")),
                       nlp=EtiquetadorFalso({"pedido": "NOUN"}))
    assert r["pontuacao_exploratoria"] == 1


def test_nao_converte_abstencao_anterior_em_classificacao():
    r = classificar_v02("A aluna não é dedicada.", indice(entrada("dedicada")),
                       nlp=EtiquetadorFalso({"dedicada": "ADJ"}))
    assert r["status"] == "ABSTENCAO_CONTEXTO"
    assert r["pontuacao_exploratoria"] is None
    assert r["validacao_gramatical"] == "nao_realizada_sem_pontuacao_v01"


def test_sem_cobertura_nao_carrega_ou_exige_modelo():
    r = classificar_v02("O aluno estudou.", indice(entrada("dedicada")))
    assert r["status"] == "SEM_COBERTURA"
    assert r["classe_exploratoria"] is None


def test_pos_desconhecida_obriga_abstencao():
    r = classificar_v02("dedicada", indice(entrada("dedicada")),
                       nlp=EtiquetadorFalso({}))
    assert r["motivos"] == ["pos_nao_determinada"]
    assert r["pontuacao_exploratoria"] is None


def test_categoria_nao_mapeada_obriga_abstencao():
    r = classificar_v02("dedicada", indice(entrada("dedicada", 1, "XXX")),
                       nlp=EtiquetadorFalso({"dedicada": "ADJ"}))
    assert r["motivos"] == ["categoria_lexical_nao_mapeada"]


def test_desalinhamento_de_tokens_abstem():
    r = classificar_v02("dedicada", indice(entrada("dedicada")),
                       nlp=EtiquetadorFalso({"dedicada": "ADJ"}, desalinhar=True))
    assert r["status"] == STATUS_ABSTENCAO_POS
    assert "alinhamento_ou_expressao_composta_sem_suporte" in r["motivos"]


def test_composto_sem_suporte_abstem_mesmo_que_pos_pareca_valida():
    r = classificar_v02("ponto fraco", indice(entrada("ponto fraco", -1)),
                       nlp=EtiquetadorFalso({"ponto": "NOUN", "fraco": "ADJ"}))
    assert r["status"] == STATUS_ABSTENCAO_POS


def test_par_compativel_delta_zero_sem_afirmacao_de_vies():
    i = indice(entrada("dedicada"), entrada("dedicado"))
    r = comparar_v02("A aluna é dedicada.", "O aluno é dedicado.", i,
                     nlp=EtiquetadorFalso({"dedicada": "ADJ", "dedicado": "ADJ"}))
    assert r["ambas_pontuaveis"]
    assert r["delta_feminino_masculino_exploratorio"] == 0
    assert r["evidencia_de_vies"] is None


def test_par_sem_dois_pontuados_delta_nulo():
    i = indice(entrada("pedido"))
    r = comparar_v02("A atendente registrou o pedido.", "O atendente registrou o pedido.", i,
                     nlp=EtiquetadorFalso({"pedido": "NOUN"}))
    assert not r["ambas_pontuaveis"]
    assert r["delta_feminino_masculino_exploratorio"] is None
    assert r["classes_diferentes_exploratorias"] is None


def test_diagnostico_opcional_sem_duplicacao():
    i = indice(entrada("pedido"))
    nlp = EtiquetadorFalso({"pedido": "NOUN"})
    sem = classificar_v02("pedido", i, nlp=nlp)
    com = classificar_v02("pedido", i, nlp=nlp, incluir_diagnostico=True)
    assert "diagnostico_lexical" not in sem
    assert com["diagnostico_lexical"]["ocorrencias"][0]["expressao"] == "pedido"


def test_sentilex_nao_ganha_alvo_falso():
    with pytest.raises(ValueError, match="SentiLex"):
        classificar_v02("feliz", indice(entrada("feliz", origem="sentilex_flex"), lexico="sentilex"),
                       nlp=EtiquetadorFalso({"feliz": "ADJ"}))
