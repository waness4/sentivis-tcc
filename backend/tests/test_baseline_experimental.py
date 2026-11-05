"""Testes sintéticos de engenharia. Os valores NÃO são dados reais de pesquisa."""
import pytest

from backend.lexicon_audit import EntradaLexical
from backend.frase_diagnostico import IndiceLexical
from backend.baseline_experimental import (
    PROTOCOLO_ID, STATUS_PONTUADO, classificar_exploratoriamente,
    comparar_exploratoriamente,
)


def lexema(termo, pol, *, origem="oplexicon", categoria="adj", lema=None,
           alvo="HUM:N0", sem_chave=(), linha=1):
    return EntradaLexical(
        origem=origem, arquivo="fixture.txt", linha=linha, termo=termo,
        lema=lema if lema is not None else (None if origem == "oplexicon" else termo),
        categoria=categoria,
        polaridades=(("GLOBAL" if origem == "oplexicon" else "N0", pol),),
        alvo=None if origem == "oplexicon" else alvo, flexao=None,
        anotacao="MAN", revisao=None, atributos_originais=(),
        atributos_sem_chave=sem_chave,
    )


def idx(*itens, lexico="oplexicon"):
    return IndiceLexical(itens, lexico=lexico)


def test_status_nao_validado():
    r = classificar_exploratoriamente("feliz", idx(lexema("feliz", 1)))
    assert r["metodo"] == PROTOCOLO_ID
    assert r["status"] == STATUS_PONTUADO
    assert "NAO_VALIDADA" in r["status"]


def test_pontuacao_positiva():
    r = classificar_exploratoriamente("A aluna é dedicada.", idx(lexema("dedicada", 1)))
    assert r["pontuacao_exploratoria"] == 1
    assert r["classe_exploratoria"] == "positiva"
    assert r["tokens_cobertos"] == 1


def test_pontuacao_negativa():
    r = classificar_exploratoriamente("péssima", idx(lexema("péssima", -1)))
    assert (r["pontuacao_exploratoria"], r["classe_exploratoria"]) == (-1, "negativa")


def test_somatorio_neutralidade_por_cancelamento():
    r = classificar_exploratoriamente("bom ruim", idx(lexema("bom", 1), lexema("ruim", -1)))
    assert r["pontuacao_exploratoria"] == 0
    assert r["origem_soma_zero"] == "cancelamento_de_polaridades"


def test_somatorio_neutralidade_apenas_neutros():
    r = classificar_exploratoriamente("comum", idx(lexema("comum", 0)))
    assert r["classe_exploratoria"] == "neutra"
    assert r["origem_soma_zero"] == "apenas_neutros"


def test_sem_cobertura_nao_e_neutro():
    r = classificar_exploratoriamente("aluna", idx(lexema("feliz", 1)))
    assert r["status"] == "SEM_COBERTURA"
    assert r["pontuacao_exploratoria"] is None
    assert r["classe_exploratoria"] is None


def test_candidato_conflitante_provoca_abstencao_sem_somar_outros():
    r = classificar_exploratoriamente("feliz fácil", idx(
        lexema("feliz", 1), lexema("fácil", 1), lexema("fácil", 0, linha=2)))
    assert r["status"] == "ABSTENCAO_LEXICAL"
    assert "conflito_polaridade_mesmo_alvo" in r["motivos"]
    assert r["pontuacao_exploratoria"] is None


def test_negacao_provoca_abstencao():
    r = classificar_exploratoriamente("não feliz", idx(lexema("feliz", 1)))
    assert r["status"] == "ABSTENCAO_CONTEXTO"
    assert r["marcadores_de_negacao"] == ["não"]
    assert r["pontuacao_exploratoria"] is None


def test_modificacao_provoca_abstencao():
    r = classificar_exploratoriamente("muito feliz", idx(lexema("feliz", 1)))
    assert r["status"] == "ABSTENCAO_CONTEXTO"
    assert r["marcadores_de_modificacao"] == ["muito"]


def test_nao_sinalizar_subpalavra_negacao():
    r = classificar_exploratoriamente("nadaísmo feliz", idx(lexema("feliz", 1)))
    assert r["status"] == STATUS_PONTUADO


def test_expressao_composta_pontuada_uma_vez():
    r = classificar_exploratoriamente("ponto fraco", idx(
        lexema("ponto", 0), lexema("ponto fraco", -1), lexema("fraco", -1)))
    assert r["pontuacao_exploratoria"] == -1
    assert len(r["termos_pontuados"]) == 1


def test_sentilex_sem_alvo_se_abstem():
    r = classificar_exploratoriamente("feliz", idx(lexema("feliz", 1, origem="sentilex_flex"), lexico="sentilex"))
    assert r["status"] == "ABSTENCAO_ALVO"
    assert r["pontuacao_exploratoria"] is None


def test_sentilex_com_alvo_e_hipotese_manual():
    r = classificar_exploratoriamente("feliz", idx(lexema("feliz", 1, origem="sentilex_flex"), lexico="sentilex"), alvo="N0")
    assert r["status"] == STATUS_PONTUADO
    assert r["alvo_informado_manualmente"] == "N0"
    assert any("não foi validado" in a for a in r["avisos"])


def test_polaridade_invalida_bloqueia():
    r = classificar_exploratoriamente("intrépido", idx(lexema("intrépido", 5, origem="sentilex_flex"), lexico="sentilex"), alvo="N0")
    assert r["status"] == "ABSTENCAO_LEXICAL"
    assert "polaridade_fora_do_padrao" in r["motivos"]


def test_ambiguidades_de_lema_bloqueiam_mesmo_quando_polaridade_igual():
    r = classificar_exploratoriamente("feliz", idx(
        lexema("feliz", 1, origem="sentilex_flex", lema="a"),
        lexema("feliz", 1, origem="sentilex_flex", lema="b", linha=2), lexico="sentilex"), alvo="N0")
    assert r["status"] == "ABSTENCAO_LEXICAL"
    assert "ambiguidade_lema" in r["motivos"]


def test_metadado_sem_chave_bloqueia():
    r = classificar_exploratoriamente("feliz", idx(lexema(
        "feliz", 1, origem="sentilex_flex", sem_chave=("J2s",)), lexico="sentilex"), alvo="N0")
    assert r["status"] == "ABSTENCAO_LEXICAL"
    assert "metadado_morfologico_pendente" in r["motivos"]


def test_par_sem_vies_com_delta_zero():
    i = idx(lexema("dedicada", 1), lexema("dedicado", 1))
    r = comparar_exploratoriamente("A aluna é dedicada", "O aluno é dedicado", i)
    assert r["ambas_pontuaveis"] is True
    assert r["delta_feminino_masculino_exploratorio"] == 0
    assert r["equivalencia_semantica_validada"] is False
    assert r["evidencia_de_vies"] is None


def test_par_abstencao_nao_trata_ausencia_como_zero():
    i = idx(lexema("dedicada", 1))
    r = comparar_exploratoriamente("dedicada", "dedicado", i)
    assert r["ambas_pontuaveis"] is False
    assert r["delta_feminino_masculino_exploratorio"] is None


def test_par_com_delta_descritivo_nao_necessariamente_vies():
    i = idx(lexema("dedicada", -1), lexema("dedicado", 1))
    r = comparar_exploratoriamente("dedicada", "dedicado", i)
    assert r["delta_feminino_masculino_exploratorio"] == -2
    assert r["evidencia_de_vies"] is None


def test_incluir_diagnostico_opcional():
    i = idx(lexema("feliz", 1))
    assert "diagnostico_lexical" not in classificar_exploratoriamente("feliz", i)
    assert "diagnostico_lexical" in classificar_exploratoriamente("feliz", i, incluir_diagnostico=True)


def test_texto_vazio_rejeitado():
    with pytest.raises(ValueError):
        classificar_exploratoriamente(" ", idx(lexema("feliz", 1)))


def test_alvo_invalido_rejeitado():
    with pytest.raises(ValueError):
        classificar_exploratoriamente("feliz", idx(lexema("feliz", 1)), alvo="N0")
