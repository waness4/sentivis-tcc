"""Testes independentes para revisão humana sem acesso à partição final."""
import csv
from pathlib import Path

import pytest

from backend.pares_piloto import CAMPOS, ler_csv, validar_pares
from backend.revisao_humana import (COLUNAS_FICHA, _ler_ficha, consolidar, preparar)


def original(id_par, familia, particao, fem, masc):
    linha = {c: "" for c in CAMPOS}
    linha.update(id_par=id_par, familia=familia, particao=particao,
                 frase_feminina=fem, frase_masculina=masc, observacoes="CANDIDATO SEM REVISAO")
    return linha


def escrever(path: Path, campos, dados):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(dados)
    return path


def ler(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


@pytest.fixture
def base(tmp_path):
    linhas = [
        original("P001", "F1", "desenvolvimento", "A aluna é dedicada.", "O aluno é dedicado."),
        original("P002", "F1", "desenvolvimento", "A aluna é gentil.", "O aluno é gentil."),
        original("P003", "F2", "avaliacao", "A médica é competente.", "O médico é competente."),
    ]
    fonte = escrever(tmp_path / "pares.csv", CAMPOS, linhas)
    destino = tmp_path / "restrito"
    preparar(fonte, destino)
    return fonte, destino


def preencher(path, *, equivalencia="sim", rotulo="positiva", observacoes=""):
    linhas = ler(path)
    for linha in linhas:
        linha.update(equivalencia=equivalencia, rotulo=rotulo, observacoes=observacoes)
    escrever(path, COLUNAS_FICHA, linhas)


def consol(base, **kw):
    fonte, restrito = base
    args = dict(
        entrada=fonte,
        ficha_a=restrito / "ficha_revisor_A_desenvolvimento.csv",
        ficha_b=restrito / "ficha_revisor_B_desenvolvimento.csv",
        id_a="REV_A", id_b="REV_B",
        saida_csv=restrito / "pares_revisados.csv",
        saida_relatorio=restrito / "relatorio_revisao.json",
    )
    args.update(kw)
    return consolidar(**args)


def test_preparacao_exclui_reservado(base):
    fonte, pasta = base
    a = ler(pasta / "ficha_revisor_A_desenvolvimento.csv")
    b = ler(pasta / "ficha_revisor_B_desenvolvimento.csv")
    assert len(a) == len(b) == 2
    assert a == b
    assert {x["id_par"] for x in a} == {"P001", "P002"}
    assert all(not x["rotulo"] and not x["equivalencia"] for x in a)


def test_preparar_nao_sobrescreve_anotacao(base):
    fonte, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    preencher(a)
    conteudo = a.read_bytes()
    with pytest.raises(FileExistsError):
        preparar(fonte, pasta)
    assert a.read_bytes() == conteudo


def test_consolidar_aprovacao_sem_alterar_avaliacao(base):
    fonte, pasta = base
    for c in "AB":
        preencher(pasta / f"ficha_revisor_{c}_desenvolvimento.csv")
    r = consol(base)
    assert r["contagem_por_status"] == {"APROVADO_DUPLA_REVISAO": 2}
    assert r["pares_avaliacao_intocados"] == 1
    pares, sha = ler_csv(pasta / "pares_revisados.csv")
    assert not validar_pares(pares, sha256=sha)["erros"]
    assert pares[-1]["particao"] == "avaliacao"
    assert not pares[-1]["rotulo_revisor1"] and not pares[-1]["id_revisor2"]
    assert pares[0]["id_revisor1"] == "REV_A"
    assert pares[0]["id_revisor2"] == "REV_B"
    assert pares[0]["rotulo_revisor1"] == pares[0]["rotulo_revisor2"] == "positiva"


def test_discordancia_nao_e_resolvida_automaticamente(base):
    _, pasta = base
    preencher(pasta / "ficha_revisor_A_desenvolvimento.csv", rotulo="positiva")
    preencher(pasta / "ficha_revisor_B_desenvolvimento.csv", rotulo="negativa")
    r = consol(base)
    assert r["contagem_por_status"] == {"PENDENTE_ADJUDICACAO": 2}
    assert all(p["status"] == "PENDENTE_ADJUDICACAO" for p in r["pares"])
    assert len(ler(pasta / "pares_revisados.csv")) == 3


def test_equivalencia_nao_requer_justificativa_e_adjudicacao(base):
    _, pasta = base
    preencher(pasta / "ficha_revisor_A_desenvolvimento.csv", equivalencia="nao", rotulo="", observacoes="Sentido não equivalente")
    preencher(pasta / "ficha_revisor_B_desenvolvimento.csv")
    r = consol(base)
    assert r["contagem_por_status"] == {"PENDENTE_ADJUDICACAO": 2}


def test_ficha_de_avaliacao_inserida_e_bloqueada(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    linhas = ler(a)
    linhas.append({"id_par": "P003", "frase_feminina": "A médica é competente.",
                   "frase_masculina": "O médico é competente.", "equivalencia": "sim", "rotulo": "positiva", "observacoes": ""})
    escrever(a, COLUNAS_FICHA, linhas)
    with pytest.raises(ValueError, match="desconhecido/reservado"):
        consol(base)


def test_frase_modificada_bloqueada(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    linhas = ler(a)
    linhas[0]["frase_feminina"] = "A aluna não é dedicada."
    escrever(a, COLUNAS_FICHA, linhas)
    with pytest.raises(ValueError, match="frases modificadas"):
        consol(base)


def test_id_faltante_bloqueado(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    escrever(a, COLUNAS_FICHA, ler(a)[:1])
    with pytest.raises(ValueError, match="conjunto de IDs incompleto"):
        consol(base)


def test_ids_dos_revisores_devem_ser_distintos(base):
    with pytest.raises(ValueError, match="distintos"):
        consol(base, id_a="REV", id_b="REV")


def test_fichas_iguais_bloqueadas(base):
    _, pasta = base
    ficha = pasta / "ficha_revisor_A_desenvolvimento.csv"
    with pytest.raises(ValueError, match="distintos"):
        consol(base, ficha_b=ficha)


def test_sim_sem_rotulo_bloqueado(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    preencher(a, equivalencia="sim", rotulo="")
    with pytest.raises(ValueError, match="exige rótulo"):
        consol(base)


def test_nao_sem_justificativa_bloqueado(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    preencher(a, equivalencia="nao", rotulo="")
    with pytest.raises(ValueError, match="exige justificativa"):
        consol(base)


def test_fichas_vazias_ficam_pendentes(base):
    _, pasta = base
    r = consol(base)
    assert r["contagem_por_status"] == {"PENDENTE_REVISAO": 2}
    assert all(not p["rotulo_revisor1"] for p in ler(pasta / "pares_revisados.csv"))


def test_nao_sobrescreve_saida(base):
    _, pasta = base
    consol(base)
    antigo = (pasta / "pares_revisados.csv").read_bytes()
    with pytest.raises(FileExistsError):
        consol(base)
    assert (pasta / "pares_revisados.csv").read_bytes() == antigo


def test_particao_final_previamente_anotada_bloqueada(base):
    fonte, pasta = base
    linhas = ler(fonte)
    linhas[-1]["rotulo_revisor1"] = "positiva"
    escrever(fonte, CAMPOS, linhas)
    with pytest.raises(ValueError, match="avaliação deve permanecer sem anotações"):
        preparar(fonte, pasta / "novas")


def test_familia_duplicada_entre_particoes_bloqueada(base):
    fonte, pasta = base
    linhas = ler(fonte)
    linhas[-1]["familia"] = "F1"
    escrever(fonte, CAMPOS, linhas)
    with pytest.raises(ValueError, match="CSV de origem inválido"):
        preparar(fonte, pasta / "novas")


def test_preparar_impede_sobrescrever_origem_mesmo_com_substituicao(tmp_path):
    fonte = escrever(
        tmp_path / "ficha_revisor_A_desenvolvimento.csv", CAMPOS,
        [original("P001", "F1", "desenvolvimento", "A aluna é gentil.", "O aluno é gentil.")],
    )
    conteudo = fonte.read_bytes()
    with pytest.raises(ValueError, match="não pode substituir o CSV de origem"):
        preparar(fonte, tmp_path, substituir=True)
    assert fonte.read_bytes() == conteudo
    assert not (tmp_path / "ficha_revisor_B_desenvolvimento.csv").exists()


def test_revisao_nao_equivalente_nao_aceita_rotulo(base):
    _, pasta = base
    a = pasta / "ficha_revisor_A_desenvolvimento.csv"
    preencher(a, equivalencia="nao", rotulo="positiva", observacoes="Sentidos diferentes.")
    with pytest.raises(ValueError, match="não equivalência não aceita rótulo"):
        consol(base)
    assert not (pasta / "pares_revisados.csv").exists()


def test_escrita_em_modo_exclusivo_impede_sobrescrita_concorrente(tmp_path):
    from backend.revisao_humana import _gravar_csv, _gravar_json
    saida_csv = tmp_path / "ficha.csv"
    saida_json = tmp_path / "relatorio.json"
    _gravar_csv(saida_csv, COLUNAS_FICHA, [])
    _gravar_json(saida_json, {"fase": "teste"})
    original_csv, original_json = saida_csv.read_bytes(), saida_json.read_bytes()
    with pytest.raises(FileExistsError):
        _gravar_csv(saida_csv, COLUNAS_FICHA, [])
    with pytest.raises(FileExistsError):
        _gravar_json(saida_json, {"fase": "outro"})
    assert saida_csv.read_bytes() == original_csv
    assert saida_json.read_bytes() == original_json
