"""Testes de engenharia com registros artificiais (não são achados do TCC)."""
import pytest
from backend.lexicon_audit import EntradaLexical
from backend.frase_diagnostico import (
    IndiceLexical, diagnosticar_frase, diagnosticar_par, tokenizar
)


def entrada(termo, pol, *, origem='oplexicon', categoria='adj',
            lema=None, alvo='HUM:N0', sem_chave=(), linha=1):
    return EntradaLexical(
        origem=origem, arquivo='fixture.txt', linha=linha, termo=termo,
        lema=lema if lema is not None else (termo if origem != 'oplexicon' else None),
        categoria=categoria,
        polaridades=((('GLOBAL' if origem == 'oplexicon' else 'N0'), pol),),
        alvo=None if origem == 'oplexicon' else alvo, flexao=None, anotacao='MAN',
        revisao=None, atributos_originais=(), atributos_sem_chave=sem_chave
    )


def idx(*registros, lexico='oplexicon'):
    return IndiceLexical(registros, lexico=lexico)


def test_alfabeto_unicode_e_hifen():
    t = tokenizar('A aluna é bem-humorada.')
    assert [v.texto for v in t] == ['A', 'aluna', 'é', 'bem-humorada']


def test_acento_preservado_na_correspondencia():
    r = diagnosticar_frase('A estudante é ÓTIMA.', idx(entrada('ótima', 1)))
    assert r['resumo']['tokens_com_correspondencia'] == 1
    assert r['ocorrencias'][0]['expressao'] == 'ÓTIMA'


def test_expressao_mais_longa_tem_precedencia_e_sem_dupla_contagem():
    r = diagnosticar_frase('Ela tem ponto fraco.', idx(entrada('ponto', 0), entrada('ponto fraco', -1), entrada('fraco', -1)))
    assert r['resumo']['tokens_com_correspondencia'] == 2
    assert len(r['ocorrencias']) == 1
    assert r['ocorrencias'][0]['expressao'] == 'ponto fraco'


def test_nao_atravessar_virgula_para_expressao():
    r = diagnosticar_frase('ponto, fraco', idx(entrada('ponto fraco', -1)))
    assert r['resumo']['tokens_com_correspondencia'] == 0


def test_hifen_mantido_em_termo():
    r = diagnosticar_frase('É bem-humorada.', idx(entrada('bem-humorada', 1)))
    assert r['resumo']['tokens_com_correspondencia'] == 1


def test_negacao_apenas_sinalizada():
    r = diagnosticar_frase('Ela não é feliz.', idx(entrada('feliz', 1)))
    assert 'negacao_detectada_sem_interpretacao_de_escopo' in r['sinais_contextuais']
    assert 'classe' not in r and 'pontuacao' not in r


def test_sem_cobertura_nao_significa_neutro():
    r = diagnosticar_frase('A estudante chegou.', idx(entrada('feliz', 1)))
    assert r['resumo']['cobertura_superficial'] == 0
    assert r['ocorrencias'] == []
    assert 'classe' not in r


def test_oplexicon_conflito_preservado():
    r = diagnosticar_frase('É fácil.', idx(entrada('fácil', 1), entrada('fácil', 0, linha=2)))
    assert r['ocorrencias'][0]['status'] == 'revisao_necessaria'
    assert r['ocorrencias'][0]['polaridade_lexical_consultada'] is None


def test_sentilex_sem_alvo_nao_decide_polaridade():
    r = diagnosticar_frase('Ela é feliz.', idx(entrada('feliz', 1, origem='sentilex_flex'), lexico='sentilex'))
    assert r['ocorrencias'][0]['status'] == 'alvo_nao_informado'
    assert r['ocorrencias'][0]['polaridade_lexical_consultada'] is None


def test_sentilex_alvo_explicitamente_informado_mas_nao_validado():
    r = diagnosticar_frase('Ela é feliz.', idx(entrada('feliz', 1, origem='sentilex_flex'), lexico='sentilex'), alvo='N0')
    assert r['ocorrencias'][0]['polaridade_lexical_consultada'] == 1
    assert 'alvo_informado_manualmente_sem_validacao_contextual' in r['sinais_contextuais']
    assert 'classe' not in r


def test_sentilex_prioridade_forma_flexionada():
    r = diagnosticar_frase('feliz', idx(
        entrada('feliz', 1, origem='sentilex_lem'),
        entrada('feliz', -1, origem='sentilex_flex'), lexico='sentilex'), alvo='N0')
    assert r['ocorrencias'][0]['fonte'] == 'sentilex_flex'
    assert len(r['ocorrencias'][0]['candidatos']) == 1


def test_polaridade_fora_padrao_bloqueada():
    r = diagnosticar_frase('intrépido', idx(entrada('intrépido', 5, origem='sentilex_flex'), lexico='sentilex'), alvo='N0')
    assert r['ocorrencias'][0]['status'] == 'revisao_necessaria'
    assert 'polaridade_fora_do_padrao' in r['ocorrencias'][0]['motivos']


def test_emoticon_numerico_fora_do_escopo():
    i = idx(entrada(':P', 1, categoria='emot'), entrada('erro:510', -1, categoria='emot'))
    r = diagnosticar_frase('Erro:510 :P', i)
    assert not r['ocorrencias']
    assert i.entradas_ignoradas_formato == 2


def test_par_nao_conclui_vies_ou_equivalencia():
    i = idx(entrada('feliz', 1))
    r = diagnosticar_par('A aluna é feliz.', 'O aluno é feliz.', i)
    assert r['diferenca_polaridade'] is None
    assert r['equivalencia_semantica_validada'] is False
    assert r['status'] == 'COMPARACAO_DE_COBERTURA_NAO_VIES'


def test_texto_vazio_rejeitado():
    with pytest.raises(ValueError):
        diagnosticar_frase('', idx(entrada('feliz', 1)))


def test_texto_acima_limite_rejeitado():
    with pytest.raises(ValueError):
        diagnosticar_frase('a' * 5001, idx(entrada('feliz', 1)))


def test_lexico_invalido_rejeitado():
    with pytest.raises(ValueError):
        IndiceLexical([], lexico='outro')


def test_op_nao_aceita_alvo_n0():
    with pytest.raises(ValueError):
        diagnosticar_frase('feliz', idx(entrada('feliz', 1)), alvo='N0')


def test_emoticon_alfabetico_nao_gera_falso_positivo():
    i = idx(entrada('xd', 1, categoria='emot'), entrada('tag', 1, categoria='htag'))
    r = diagnosticar_frase('xd tag', i)
    assert not r['ocorrencias']
    assert i.entradas_ignoradas_formato == 2
