"""Fixtures sintéticas para V04; não representam validação científica."""
from __future__ import annotations

from backend.baseline_contextual_v03 import classificar_v03
from backend.baseline_contextual_v04 import PROTOCOLO_V04, classificar_v04, comparar_v04
from backend.baseline_experimental import STATUS_PONTUADO
from backend.tests.test_baseline_contextual_v03 import FakeNLP, idx, lexema


class NLPV04(FakeNLP):
    def __call__(self, texto):
        toks = super().__call__(texto)
        for t in toks:
            if t.text.casefold() in {"apresentou", "respondeu", "organizou"}:
                t.pos_ = "VERB"
        return toks


def exemplo(modo="nmod", polaridade=1, *, nlp=None, habilitado=True, entrada_adicional=None):
    texto = "A pesquisadora apresentou os dados com segurança."
    lexs = [lexema("dados", 0, "Adj"), lexema("segurança", polaridade, "N")]
    if entrada_adicional is not None:
        lexs += [entrada_adicional]
    nlp = nlp or NLPV04(anexacao={"segurança": (modo, "dados" if modo == "nmod" else "apresentou")})
    return classificar_v04(texto, idx(*lexs), alvo="N0", nlp=nlp,
                          hipotese_modo=habilitado, incluir_diagnostico=True)


def test_c005_descarta_dados_mas_abstem_anexacao_ambigua():
    r = exemplo()
    assert r["metodo"] == PROTOCOLO_V04
    assert r["status"] == "ABSTENCAO_ANEXACAO_AMBIGUA"
    assert r["motivos"] == ["sintagma_com_ligado_a_nome"]
    assert r["classe_exploratoria"] is None
    assert r["pontuacao_exploratoria"] is None
    assert r["filtragem_neutros_pos"]["aplicada"]
    assert [x["expressao"] for x in r["filtragem_neutros_pos"]["descartados"]] == ["dados"]
    assert r["alvo_resolvido_automaticamente"] is False
    assert r["papel_semantico_validado"] is False


def test_c006_descarta_dados_mas_nao_pontua_arrogancia():
    texto = "O pesquisador apresentou os dados com arrogância."
    nlp = NLPV04(anexacao={"arrogância": ("nmod", "dados")})
    r = classificar_v04(texto, idx(lexema("dados", 0, "Adj"), lexema("arrogância", -1)),
                       alvo="N0", nlp=nlp, hipotese_modo=True)
    assert r["status"] == "ABSTENCAO_ANEXACAO_AMBIGUA"
    assert r["pontuacao_exploratoria"] is None
    assert r["filtragem_neutros_pos"]["aplicada"]


def test_estrutura_verbal_unica_pode_ser_pontuada_com_hipotese_autorizada():
    r = exemplo(modo="obl")
    assert r["status"] == STATUS_PONTUADO
    assert r["pontuacao_exploratoria"] == 1
    assert r["classe_exploratoria"] == "positiva"
    assert len(r["termos_pontuados"]) == 1
    assert r["termos_pontuados"][0]["expressao"] == "segurança"
    assert r["papel_semantico_validado"] is False


def test_estrutura_verbal_sem_autorizacao_abstem():
    r = exemplo(modo="obl", habilitado=False)
    assert r["status"] == "ABSTENCAO_HIPOTESE_NAO_AUTORIZADA"
    assert r["pontuacao_exploratoria"] is None


def test_apenas_incompatibilidade_neutra_nao_gera_neutro():
    texto = "O pesquisador apresentou os dados."
    r = classificar_v04(texto, idx(lexema("dados", 0, "Adj")), alvo="N0", nlp=NLPV04(),
                        hipotese_modo=True)
    assert r["status"] == "ABSTENCAO_CATEGORIA_GRAMATICAL"
    assert r["classe_exploratoria"] is None
    assert not r["filtragem_neutros_pos"]["aplicada"]


def test_incompatibilidade_nao_neutra_bloqueia_mesmo_com_candidato_valido():
    r = classificar_v04("A pesquisadora apresentou os dados com segurança.",
                        idx(lexema("dados", -1, "Adj"), lexema("segurança", 1)),
                        alvo="N0", nlp=NLPV04(anexacao={"segurança": ("obl", "apresentou")}),
                        hipotese_modo=True)
    assert r["status"] == "ABSTENCAO_CATEGORIA_GRAMATICAL"
    assert not r["filtragem_neutros_pos"]["aplicada"]


def test_categoria_desconhecida_falha_fechada():
    r = classificar_v04("A pesquisadora apresentou os dados com segurança.",
                        idx(lexema("dados", 0, "X"), lexema("segurança", 1)),
                        alvo="N0", nlp=NLPV04(anexacao={"segurança": ("obl", "apresentou")}),
                        hipotese_modo=True)
    assert r["status"] == "ABSTENCAO_CATEGORIA_GRAMATICAL"
    assert not r["filtragem_neutros_pos"]["aplicada"]


def test_negacao_preservada_sem_aplicar_filtro():
    texto = "A pesquisadora não apresentou os dados com segurança."
    r = classificar_v04(texto, idx(lexema("dados", 0, "Adj"), lexema("segurança", 1)),
                        alvo="N0", nlp=NLPV04(), hipotese_modo=True)
    assert r["status"] == "ABSTENCAO_CONTEXTO"
    assert not r["filtragem_neutros_pos"]["aplicada"]


def test_sem_alvo_permanece_abstencao_alvo():
    r = classificar_v04("A pesquisadora apresentou os dados com segurança.",
                        idx(lexema("dados", 0, "Adj"), lexema("segurança", 1)))
    assert r["status"] == "ABSTENCAO_ALVO"
    assert r["pontuacao_exploratoria"] is None


def test_leitura_v03_preservada_sem_mudanca_de_estado():
    texto = "A pesquisadora apresentou os dados com segurança."
    indice = idx(lexema("dados", 0, "Adj"), lexema("segurança", 1))
    nlp = NLPV04(anexacao={"segurança": ("nmod", "dados")})
    antes = classificar_v03(texto, indice, alvo="N0", nlp=nlp, hipotese_modo=True)
    _ = classificar_v04(texto, indice, alvo="N0", nlp=nlp, hipotese_modo=True)
    depois = classificar_v03(texto, indice, alvo="N0", nlp=nlp, hipotese_modo=True)
    assert antes == depois
    assert antes["status"] == "ABSTENCAO_CATEGORIA_GRAMATICAL"


def test_p007_anexacao_continua_ambigua():
    texto = "A programadora resolveu o problema com habilidade."
    r = classificar_v04(texto, idx(lexema("problema", -1), lexema("habilidade", 1)),
                        alvo="N0", hipotese_modo=True,
                        nlp=NLPV04(anexacao={"habilidade": ("nmod", "problema")}))
    assert r["status"] == "ABSTENCAO_ANEXACAO_AMBIGUA"
    assert r["pontuacao_exploratoria"] is None


def test_diagnostico_opcional():
    i = idx(lexema("dados", 0, "Adj"), lexema("segurança", 1))
    r = classificar_v04("A pesquisadora apresentou os dados com segurança.",
                        i, alvo="N0", hipotese_modo=True, nlp=NLPV04())
    assert "diagnostico_lexical" not in r
    assert "checagens_contextuais" in r


def test_comparacao_nao_infere_vies():
    i = idx(lexema("dados", 0, "Adj"), lexema("segurança", 1))
    nlp = NLPV04(anexacao={"segurança": ("nmod", "dados")})
    r = comparar_v04("A pesquisadora apresentou os dados com segurança.",
                     "O pesquisador apresentou os dados com segurança.",
                     i, nlp=nlp, alvo="N0", hipotese_modo=True)
    assert r["evidencia_de_vies"] is None
    assert not r["ambas_pontuaveis"]
    assert r["delta_feminino_masculino_exploratorio"] is None


def test_incompatibilidade_multipla_candidata_selecionada_nao_e_automatizada():
    indice = idx(lexema("dados", 0, "Adj"), lexema("segurança", 1),
                 lexema("pesquisadora", 0, "Adj"))
    nlp = NLPV04(anexacao={"segurança": ("obl", "apresentou")})
    r = classificar_v04("A pesquisadora apresentou os dados com segurança.", indice,
                        alvo="N0", nlp=nlp, hipotese_modo=False)
    assert r["status"] == "ABSTENCAO_HIPOTESE_NAO_AUTORIZADA"
    assert len(r["filtragem_neutros_pos"]["descartados"]) == 2
