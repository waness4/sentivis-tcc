"""Testes das fichas humanas dos controles fixados: sem avaliar dados reservados."""
import csv
import json
from pathlib import Path

import pytest

from backend.anotacao_controles_v01 import (
    COLUNAS_FICHA, _kappa, _ler_ficha, consolidar, preparar,
)
from backend.controles_sintaticos_v03 import ARQUIVO_CONTROLES, SHA256_CONTROLES, ler_controles


@pytest.fixture
def fonte():
    rows, sha = ler_controles(ARQUIVO_CONTROLES)
    assert len(rows) == 36 and sha == SHA256_CONTROLES
    return rows, sha


@pytest.fixture
def fichas(tmp_path, fonte):
    rows, sha = fonte
    pasta = tmp_path / 'privado'
    preparar(rows, pasta, sha_origem=sha)
    return pasta, rows, sha


def ler(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def alterar(path, linhas):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS_FICHA, delimiter=';')
        w.writeheader()
        w.writerows(linhas)


def preencher(path, polaridade='neutra', referente='nenhum'):
    linhas = ler(path)
    for r in linhas:
        r['polaridade'] = polaridade
        r['referente'] = referente
        r['papel_com'] = 'modo' if ' com ' in r['texto'].lower() else 'nao_aplicavel'
    alterar(path, linhas)


def teste_preparar_somente_controles_sem_gabarito(fichas):
    pasta, rows, _ = fichas
    a = ler(pasta/'ficha_controles_R01_v01.csv')
    b = ler(pasta/'ficha_controles_R02_v01.csv')
    assert len(a) == len(b) == len(rows) == 36
    assert set(a[0]) == set(COLUNAS_FICHA)
    assert [l['id_controle'] for l in a] != [l['id_controle'] for l in b]
    assert {l['id_controle'] for l in a} == {l['id_controle'] for l in rows}
    assert all(not any(l[x] for x in ('polaridade', 'referente', 'papel_com', 'observacoes')) for l in a + b)
    assert all('cenario' not in l and 'status_v04' not in l for l in a+b)


def teste_nao_sobrescreve_fichas(fichas):
    pasta, rows, sha = fichas
    before = (pasta/'ficha_controles_R01_v01.csv').read_bytes()
    with pytest.raises(FileExistsError):
        preparar(rows, pasta, sha_origem=sha)
    assert before == (pasta/'ficha_controles_R01_v01.csv').read_bytes()


def teste_identificadores_originais_sao_obrigatorios(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    registros = ler(path)
    registros[0]['id_controle'] = 'P001'
    alterar(path, registros)
    with pytest.raises(ValueError, match='ID inexistente'):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_nao_aceita_frase_editada(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    registros = ler(path)
    registros[0]['texto'] += ' alterado'
    alterar(path, registros)
    with pytest.raises(ValueError, match='texto alterado'):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_nao_aceita_ficha_com_rótulo_invalido(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    registros = ler(path)
    registros[0]['polaridade'] = 'positivo'
    alterar(path, registros)
    with pytest.raises(ValueError, match='polaridade inválido'):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_rejeita_linhas_faltantes(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    alterar(path, ler(path)[:-1])
    with pytest.raises(ValueError, match='incompleto'):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_rejeita_valores_vazios_na_consolidacao(fichas):
    pasta, rows, sha = fichas
    with pytest.raises(ValueError, match='não preenchido'):
        consolidar(rows, pasta/'ficha_controles_R01_v01.csv', pasta/'ficha_controles_R02_v01.csv',
                   pasta/'result.csv', pasta/'result.json', sha_origem=sha)


def teste_papel_com_quando_nao_ha_preposicao(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    registros = ler(path)
    nao_tem = next(x for x in registros if ' com ' not in x['texto'].lower())
    nao_tem['papel_com'] = 'modo'
    alterar(path, registros)
    with pytest.raises(ValueError, match="sem 'com'"):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_papel_com_obrigatorio_quando_tem_preposicao(fichas):
    pasta, rows, _ = fichas
    path = pasta/'ficha_controles_R01_v01.csv'
    registros = ler(path)
    tem = next(x for x in registros if ' com ' in x['texto'].lower())
    tem['papel_com'] = 'nao_aplicavel'
    alterar(path, registros)
    with pytest.raises(ValueError, match="'com' presente"):
        _ler_ficha(path, {l['id_controle']: l for l in rows}, exigir_completa=False)


def teste_exige_justificativa_de_indeterminacao(fichas):
    pasta, rows, sha = fichas
    for code in ('R01', 'R02'):
        p = pasta/f'ficha_controles_{code}_v01.csv'
        preencher(p)
        ls = ler(p)
        ls[0]['polaridade'] = 'indeterminada'
        alterar(p, ls)
    with pytest.raises(ValueError, match='observacoes'):
        consolidar(rows, pasta/'ficha_controles_R01_v01.csv', pasta/'ficha_controles_R02_v01.csv',
                   pasta/'result.csv', pasta/'result.json', sha_origem=sha)


def teste_consolida_sem_acuracia_ou_resolucao_automatica(fichas):
    pasta, rows, sha = fichas
    for code in ('R01', 'R02'):
        preencher(pasta/f'ficha_controles_{code}_v01.csv')
    resumo = consolidar(rows, pasta/'ficha_controles_R01_v01.csv', pasta/'ficha_controles_R02_v01.csv',
                       pasta/'result.csv', pasta/'result.json', sha_origem=sha)
    assert resumo['n_controles'] == 36
    assert resumo['anotacoes_automaticas'] == 0
    assert resumo['n_pares_avaliacao_processados'] == 0
    assert resumo['acuracia'] is None and resumo['evidencia_de_vies'] is None
    assert resumo['kappa_cohen_polaridade'] is None  # categorias constantes
    assert resumo['concordancia']['todos']['n'] == 36
    assert len(ler(pasta/'result.csv')) == 36
    assert json.loads((pasta/'result.json').read_text(encoding='utf-8'))['fase'].endswith('SEM_ADJUDICACAO')


def teste_mantem_divergencias_sem_eleger_gabarito(fichas):
    pasta, rows, sha = fichas
    for code in ('R01', 'R02'):
        preencher(pasta/f'ficha_controles_{code}_v01.csv')
    bpath = pasta/'ficha_controles_R02_v01.csv'
    ls = ler(bpath)
    ls[0]['polaridade'] = 'positiva'
    alterar(bpath, ls)
    resumo = consolidar(rows, pasta/'ficha_controles_R01_v01.csv', bpath,
                       pasta/'result.csv', pasta/'result.json', sha_origem=sha)
    assert resumo['concordancia']['polaridade']['n'] == 35
    assert resumo['concordancia']['todos']['n'] == 35
    assert resumo['divergencias_pendentes'] == [ls[0]['id_controle']]
    assert sum(l['status']=='DIVERGENCIA_PENDENTE' for l in ler(pasta/'result.csv')) == 1


def teste_nao_sobrescreve_consolidacao(fichas):
    pasta, rows, sha = fichas
    for code in ('R01', 'R02'):
        preencher(pasta/f'ficha_controles_{code}_v01.csv')
    args = (rows, pasta/'ficha_controles_R01_v01.csv', pasta/'ficha_controles_R02_v01.csv',
            pasta/'result.csv', pasta/'result.json')
    consolidar(*args, sha_origem=sha)
    with pytest.raises(FileExistsError):
        consolidar(*args, sha_origem=sha)


def teste_impede_fichas_no_mesmo_caminho(fichas):
    pasta, rows, sha = fichas
    p = pasta/'ficha_controles_R01_v01.csv'
    with pytest.raises(ValueError, match='distintos'):
        consolidar(rows, p, p, pasta/'out.csv', pasta/'out.json', sha_origem=sha)


def teste_kappa_nominal_exato():
    assert _kappa(['positiva', 'negativa'], ['positiva', 'negativa']) == 1.0
    assert _kappa(['positiva','negativa'], ['negativa','positiva']) == -1.0
    assert _kappa(['neutra']*3, ['neutra']*3) is None



def test_falha_na_segunda_ficha_remove_primeira(tmp_path, fonte, monkeypatch):
    import backend.anotacao_controles_v01 as modulo
    controles, sha = fonte
    saida = tmp_path / "restrito"
    original = modulo._escrever_novo
    chamadas = 0

    def falhar_segunda(path, texto):
        nonlocal chamadas
        chamadas += 1
        if chamadas == 2:
            raise OSError("falha simulada na segunda ficha")
        return original(path, texto)

    monkeypatch.setattr(modulo, "_escrever_novo", falhar_segunda)
    with pytest.raises(OSError, match="falha simulada"):
        preparar(controles, saida, sha_origem=sha)
    assert chamadas == 2
    assert not list(saida.glob("ficha_controles_*.csv"))


def test_falha_no_segundo_relatorio_remove_csv(fichas, monkeypatch):
    import backend.anotacao_controles_v01 as modulo
    pasta, controles, sha = fichas
    for codigo in ("R01", "R02"):
        preencher(pasta / f"ficha_controles_{codigo}_v01.csv")
    csv_saida, json_saida = pasta / "result.csv", pasta / "result.json"
    antes = {p.name: p.read_bytes() for p in pasta.glob("ficha_controles_*.csv")}
    original = modulo._escrever_novo

    def falhar_json(path, texto):
        if path == json_saida:
            raise OSError("falha simulada no JSON")
        return original(path, texto)

    monkeypatch.setattr(modulo, "_escrever_novo", falhar_json)
    with pytest.raises(OSError, match="falha simulada"):
        consolidar(controles, pasta / "ficha_controles_R01_v01.csv",
                   pasta / "ficha_controles_R02_v01.csv",
                   csv_saida, json_saida, sha_origem=sha)
    assert not csv_saida.exists() and not json_saida.exists()
    assert {p.name: p.read_bytes() for p in pasta.glob("ficha_controles_*.csv")} == antes


def test_conjunto_rejeita_destinos_iguais_sem_escrever(tmp_path):
    from backend.anotacao_controles_v01 import _escrever_conjunto
    destino = tmp_path / "mesmo.csv"
    with pytest.raises(ValueError, match="distintos"):
        _escrever_conjunto([(destino, "A"), (destino, "B")])
    assert not destino.exists()
