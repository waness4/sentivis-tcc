"""Testes com dados sintéticos. Não reproduzem medições dos léxicos originais."""
from pathlib import Path
import pytest

from backend.lexicon_audit import EntradaLexical
from backend.lexicon_consulta import chave_termo, consultar_entradas, carregar_para_consulta


def e(termo, pol, *, origem='sentilex_flex', lema=None, categoria='Adj',
      alvo='HUM:N0', sem_chave=(), linha=1):
    if origem == 'oplexicon':
        pols = (('GLOBAL', pol),)
        alvo = None
    else:
        pols = (('N0', pol),)
    return EntradaLexical(
        origem=origem, arquivo='fixture.txt', linha=linha, termo=termo,
        lema=lema or termo, categoria=categoria, polaridades=pols,
        alvo=alvo, flexao='fs', anotacao='MAN', revisao=None,
        atributos_originais=(), atributos_sem_chave=tuple(sem_chave))


def test_consulta_op_lexico_sem_conflito():
    r = consultar_entradas([e('bonita', 1, origem='oplexicon')], 'BONITA', lexico='oplexicon')
    assert r['status'] == 'candidata_lexical_consistente'
    assert r['polaridade_consulta'] == 1


def test_nao_fundir_emoticons_distintos():
    assert chave_termo(':P','emot') != chave_termo(':p','emot')
    r = consultar_entradas([e(':P',1,origem='oplexicon',categoria='emot'),
                           e(':p',-1,origem='oplexicon',categoria='emot')],
                          ':P', lexico='oplexicon')
    assert len(r['candidatos']) == 1 and r['polaridade_consulta'] == 1


def test_sentilex_exige_alvo():
    r = consultar_entradas([e('bonita',1)], 'bonita', lexico='sentilex')
    assert r['status'] == 'alvo_nao_informado'
    assert r['polaridade_consulta'] is None


def test_conflito_mesmo_alvo_bloqueia():
    r = consultar_entradas([e('t',-1),e('t',1,linha=2)], 't', lexico='sentilex', alvo='N0')
    assert 'conflito_polaridade_mesmo_alvo' in r['motivos']
    assert r['polaridade_consulta'] is None


def test_diferentes_alvos_nao_sao_conflito_automatico():
    x = e('enganar',1)
    x = EntradaLexical(x.origem,x.arquivo,x.linha,x.termo,x.lema,x.categoria,
                       (('N0',1),('N1',-1)),'HUM:N0:N1',x.flexao,x.anotacao,x.revisao,
                       x.atributos_originais,x.atributos_sem_chave)
    assert consultar_entradas([x], 'enganar', lexico='sentilex', alvo='N0')['polaridade_consulta'] == 1
    assert consultar_entradas([x], 'enganar', lexico='sentilex', alvo='N1')['polaridade_consulta'] == -1


def test_polaridade_fora_padrao_bloqueia():
    r = consultar_entradas([e('intrépido',8)], 'intrépido', lexico='sentilex', alvo='N0')
    assert r['status'] == 'revisao_necessaria'
    assert 'polaridade_fora_do_padrao' in r['motivos']


def test_atributo_morfologico_pendente_bloqueia():
    r = consultar_entradas([e('acha piada a',0,sem_chave=('P2s|P4s',))],
                          'acha piada a', lexico='sentilex', alvo='N0')
    assert r['status'] == 'revisao_necessaria'
    assert r['candidatos'][0]['atributos_sem_chave'] == ['P2s|P4s']


def test_ambiguidade_lema_bloqueia():
    r = consultar_entradas([e('aborreça',-1,lema='aborrecer-se'),
                           e('aborreça',-1,lema='aborrecer')],
                          'aborreça', lexico='sentilex', alvo='N0')
    assert 'ambiguidade_lema' in r['motivos']


def test_prioridade_forma_flexionada_sem_dupla_contagem():
    a = e('bonita',1, origem='sentilex_lem')
    b = e('bonita',1, origem='sentilex_flex')
    r = consultar_entradas([a,b], 'bonita', lexico='sentilex', alvo='N0')
    assert len(r['candidatos']) == 1 and r['fonte'] == 'sentilex_flex'


def test_sem_correspondencia_nao_e_neutro():
    r = consultar_entradas([e('bom',1)], 'xyz', lexico='sentilex', alvo='N0')
    assert r['status'] == 'sem_correspondencia'
    assert r['polaridade_consulta'] is None


def test_alvo_inexistente_nao_e_neutro():
    r = consultar_entradas([e('bom',1)], 'bom', lexico='sentilex', alvo='N1')
    assert r['status'] == 'alvo_sem_entrada' and r['polaridade_consulta'] is None


def test_inconsistencia_tg_polaridade_bloqueia():
    r = consultar_entradas([e('ponto fraco',-1,alvo='HUM:N2')],
                          'ponto fraco', lexico='sentilex', alvo='N0')
    assert 'alvo_inconsistente' in r['motivos']


def test_rejeita_lexico_desconhecido():
    with pytest.raises(ValueError):
        consultar_entradas([], 'bom', lexico='outro')


def test_sem_relatorio_nao_aceita_entrada(tmp_path):
    with pytest.raises(FileNotFoundError):
        carregar_para_consulta(tmp_path, 'oplexicon')
