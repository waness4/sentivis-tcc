"""Testes sintéticos do Bloco 12. Não utilizam avaliações humanas reais."""
import csv
import json
import sys
from copy import deepcopy
from pathlib import Path

import backend.metricas_exploratorias as metricas

import pytest

from backend.baseline_experimental import STATUS_PONTUADO
from backend.pares_piloto import CAMPOS, VERSAO as PILOTO_VERSAO, ler_csv
from backend.metricas_exploratorias import (
    _calcular_grupo, _metricas_qualidade, calcular, verificar, main,
)


def _par(ident, familia, particao="desenvolvimento", *, aprovado=True):
    return {
        "id_par": ident, "familia": familia, "particao": particao,
        "frase_feminina": f"A aluna {ident} foi dedicada.",
        "frase_masculina": f"O aluno {ident} foi dedicado.",
        "rotulo_revisor1": "positiva" if aprovado else "",
        "rotulo_revisor2": "positiva" if aprovado else "",
        "equivalencia_revisor1": "sim" if aprovado else "",
        "equivalencia_revisor2": "sim" if aprovado else "",
        "id_revisor1": "avaliador_A" if aprovado else "",
        "id_revisor2": "avaliador_B" if aprovado else "",
        "alvo_sentilex_feminina": "", "alvo_sentilex_masculina": "",
        "observacoes": "dados sintéticos para testes",
    }


def _dataset(tmp_path, *, aprovados=True):
    caminho = tmp_path / "pares.csv"
    itens = [_par("P001", "estudo", aprovado=aprovados),
             _par("P002", "trabalho", aprovado=aprovados),
             _par("P003", "avaliacao", particao="avaliacao", aprovado=False)]
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(itens)
    return caminho


def _resultado(ident, lexico, *, feminino=1, masculino=1, status_f=None, status_m=None,
               cobertura_f=0.25, cobertura_m=0.5):
    sf = status_f or STATUS_PONTUADO
    sm = status_m or STATUS_PONTUADO
    pf = feminino if sf == STATUS_PONTUADO else None
    pm = masculino if sm == STATUS_PONTUADO else None
    return {
        "id_par": ident,
        "familia": "estudo" if ident == "P001" else "trabalho",
        "particao": "desenvolvimento", "lexico": lexico,
        "rotulo_referencia_anotado": "positiva",
        "status_feminina": sf, "status_masculina": sm,
        "motivos_feminina": [], "motivos_masculina": [],
        "pontuacao_feminina": pf, "pontuacao_masculina": pm,
        "classe_feminina": "positiva" if pf is not None and pf > 0 else ("neutra" if pf == 0 else ("negativa" if pf is not None else None)),
        "classe_masculina": "positiva" if pm is not None and pm > 0 else ("neutra" if pm == 0 else ("negativa" if pm is not None else None)),
        "delta_feminino_masculino_exploratorio": pf - pm if pf is not None and pm is not None else None,
        "cobertura_feminina": cobertura_f, "cobertura_masculina": cobertura_m,
        "alvos_sentilex_manuais_nao_validados": lexico == "sentilex",
        "evidencia_de_vies": None,
    }


def _piloto(tmp_path, dataset, *, resultados=None):
    _, sha = ler_csv(dataset)
    if resultados is None:
        resultados = []
        for nome in ("oplexicon", "sentilex"):
            resultados += [_resultado("P001", nome),
                           _resultado("P002", nome, status_m="ABSTENCAO_CONTEXTO")]
    dados = {
        "metodo": PILOTO_VERSAO,
        "fase": "PILOTO_EXPLORATORIO_DESENVOLVIMENTO",
        "sha256_dataset": sha, "resultados": resultados,
        "avaliacao_final_executada": False, "evidencia_de_vies": None,
        "manifestos_fontes": {},
    }
    caminho = tmp_path / "piloto.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def _editar_json(path, mudanca):
    obj = json.loads(path.read_text(encoding="utf-8"))
    mudanca(obj)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def test_verificar_sem_revisao_nao_pontua(tmp_path):
    r = verificar(_dataset(tmp_path, aprovados=False))
    assert r["pares_desenvolvimento"] == 2
    assert r["pares_aprovados_dupla_revisao"] == 0
    assert r["apto_para_piloto"] is False
    assert r["avaliacao_reservada_processada"] is False


def test_verificar_apos_aprovacao(tmp_path):
    r = verificar(_dataset(tmp_path))
    assert r["pares_aprovados_dupla_revisao"] == 2
    assert r["apto_para_piloto"] is True


def test_calcular_sem_revisao_bloqueado(tmp_path):
    d = _dataset(tmp_path, aprovados=False)
    p = _piloto(tmp_path, d)
    with pytest.raises(ValueError, match="Ainda não existem"):
        calcular(d, p)


def test_calcular_metricas_sem_abrir_avaliacao(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    resumo, linhas = calcular(d, p)
    assert len(linhas) == 4  # 2 pares * 2 léxicos
    assert all(x["id_par"] != "P003" for x in linhas)
    assert all("frase" not in x for x in linhas)  # CSV sem frases da reserva
    assert resumo["pares_avaliacao_processados"] == 0
    assert resumo["evidencia_de_vies"] is None
    for lexico in ("oplexicon", "sentilex"):
        g = resumo["metricas_por_lexico"][lexico]
        assert g["pares_aprovados"] == 2
        assert g["frases_pontuadas"] == 3
        assert g["pares_ambos_pontuados"] == 1
        assert g["taxa_abstencao_ou_sem_cobertura_frases"] == 0.25
        assert g["delta_assinado_medio_pares_pontuados"] == 0
        assert g["taxa_classes_divergentes_pares_pontuados"] == 0
        assert g["qualidade_seletiva"]["acuracia_seletiva"] == 1


def test_todo_mundo_abstem_sem_delta_falso(tmp_path):
    d = _dataset(tmp_path)
    itens = [_resultado(x, l, status_f="ABSTENCAO_CONTEXTO", status_m="ABSTENCAO_CONTEXTO")
             for l in ("oplexicon", "sentilex") for x in ("P001", "P002")]
    r, _ = calcular(d, _piloto(tmp_path, d, resultados=itens))
    g = r["metricas_por_lexico"]["oplexicon"]
    assert g["taxa_abstencao_ou_sem_cobertura_frases"] == 1
    assert g["delta_assinado_medio_pares_pontuados"] is None
    assert g["taxa_classes_divergentes_pares_pontuados"] is None
    assert g["qualidade_seletiva"]["f1_macro_seletivo"] is None


def test_qualidade_macro_f1_descreve_classes_usadas():
    q = _metricas_qualidade([("positiva", "positiva"), ("negativa", "positiva")])
    assert q["acuracia_seletiva"] == 0.5
    assert q["classes_calculo_f1"] == ["negativa", "positiva"]
    assert q["f1_macro_seletivo"] == 0.333333


def test_qualidade_ausente_retorna_nulos():
    assert _metricas_qualidade([])["acuracia_seletiva"] is None


def test_cobertura_e_centralidade_de_delta():
    g = _calcular_grupo([_resultado("P001", "oplexicon", feminino=2, masculino=1, cobertura_f=0.5, cobertura_m=0)])
    assert g["delta_assinado_medio_pares_pontuados"] == 1
    assert g["delta_absoluto_medio_pares_pontuados"] == 1
    assert g["cobertura_superficial_media_frases"] == 0.25


@pytest.mark.parametrize("campo,valor", [
    ("fase", "AVALIACAO_FINAL"), ("avaliacao_final_executada", True),
    ("evidencia_de_vies", True), ("metodo", "outro")
])
def test_bloqueia_piloto_inadequado(tmp_path, campo, valor):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x.__setitem__(campo, valor))
    with pytest.raises(ValueError):
        calcular(d, p)


def test_bloqueia_hash_diferente(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x.__setitem__("sha256_dataset", "nao-corresponde"))
    with pytest.raises(ValueError, match="SHA-256"):
        calcular(d, p)


def test_bloqueia_pares_de_avaliacao_no_piloto(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x["resultados"].append(_resultado("P003", "oplexicon")))
    with pytest.raises(ValueError, match="não aprovado ou de partição reservada"):
        calcular(d, p)


def test_bloqueia_resultado_duplicado(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x["resultados"].append(deepcopy(x["resultados"][0])))
    with pytest.raises(ValueError, match="duplicado"):
        calcular(d, p)


def test_bloqueia_lacuna_no_piloto(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x["resultados"].pop())
    with pytest.raises(ValueError, match="incompletos"):
        calcular(d, p)


def test_bloqueia_valor_nao_nulo_na_abstencao(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    def editar(x):
        x["resultados"][1]["pontuacao_masculina"] = 0
    _editar_json(p, editar)
    with pytest.raises(ValueError, match="Abstenção"):
        calcular(d, p)


def test_bloqueia_delta_incompativel(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x["resultados"][0].__setitem__("delta_feminino_masculino_exploratorio", 999))
    with pytest.raises(ValueError, match="Delta"):
        calcular(d, p)


def test_bloqueia_cobertura_invalida(tmp_path):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    _editar_json(p, lambda x: x["resultados"][0].__setitem__("cobertura_feminina", 3))
    with pytest.raises(ValueError, match="Cobertura"):
        calcular(d, p)


def test_bloqueia_anotacao_da_reserva(tmp_path):
    d = _dataset(tmp_path)
    texto = d.read_text(encoding="utf-8-sig").replace(
        "P003;avaliacao;avaliacao;", "P003;avaliacao;avaliacao;")
    # Manipula CSV sem alterar outros campos.
    with d.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    linhas[-1]["rotulo_revisor1"] = "positiva"
    with d.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, delimiter=";", fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(linhas)
    with pytest.raises(ValueError, match="avaliação anotada"):
        verificar(d)


def test_cli_verificar_nao_cria_resultados(tmp_path, capsys, monkeypatch):
    d = _dataset(tmp_path, aprovados=False)
    monkeypatch.setattr(sys, "argv", ["prog", "verificar", "--entrada", str(d)])
    main()
    assert "aprovados: 0" in capsys.readouterr().out
    assert len(list(tmp_path.iterdir())) == 1


def test_cli_calcular_gera_json_csv_somente_desenvolvimento(tmp_path, capsys, monkeypatch):
    d = _dataset(tmp_path)
    p = _piloto(tmp_path, d)
    j, c = tmp_path / "saida" / "metricas.json", tmp_path / "saida" / "metricas.csv"
    monkeypatch.setattr(sys, "argv", ["prog", "calcular", "--entrada", str(d),
                                     "--piloto", str(p), "--saida-json", str(j), "--saida-csv", str(c)])
    main()
    dados = json.loads(j.read_text(encoding="utf-8"))
    assert dados["pares_avaliacao_processados"] == 0
    assert "P003" not in c.read_text(encoding="utf-8-sig")
    assert "Pares de desenvolvimento aprovados: 2" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        main()  # nunca sobrescreve resultados anteriores por padrão


def test_salvar_resultados_publica_par_completo(tmp_path):
    json_path = tmp_path / "json" / "resultado.json"
    csv_path = tmp_path / "csv" / "resultado.csv"
    metricas._salvar_resultados(json_path, csv_path, {"fase": "teste_sintetico"}, [])
    assert json.loads(json_path.read_text(encoding="utf-8"))["fase"] == "teste_sintetico"
    with csv_path.open(encoding="utf-8-sig", newline="") as arquivo:
        assert list(csv.DictReader(arquivo, delimiter=";")) == []
    assert not list(tmp_path.rglob(".sentivis-*.tmp"))


def test_salvar_resultados_rejeita_csv_malformado_sem_criar_destinos(tmp_path):
    json_path, csv_path = tmp_path / "resultado.json", tmp_path / "resultado.csv"
    with pytest.raises(ValueError):
        metricas._salvar_resultados(json_path, csv_path, {"fase": "teste"}, [{"campo_indevido": 1}])
    assert not json_path.exists() and not csv_path.exists()
    assert not list(tmp_path.rglob(".sentivis-*.tmp"))


def test_salvar_resultados_falha_na_segunda_publicacao_reverte_a_primeira(tmp_path, monkeypatch):
    json_path, csv_path = tmp_path / "resultado.json", tmp_path / "resultado.csv"
    original_link = metricas.os.link
    chamadas = 0

    def falhar_no_segundo_link(origem, destino):
        nonlocal chamadas
        chamadas += 1
        if chamadas == 2:
            raise OSError("falha simulada ao publicar CSV")
        return original_link(origem, destino)

    monkeypatch.setattr(metricas.os, "link", falhar_no_segundo_link)
    with pytest.raises(OSError, match="falha simulada"):
        metricas._salvar_resultados(json_path, csv_path, {"fase": "teste"}, [])
    assert chamadas == 2
    assert not json_path.exists() and not csv_path.exists()
    assert not list(tmp_path.rglob(".sentivis-*.tmp"))


def test_salvar_resultados_nao_sobrescreve_destino_existente(tmp_path):
    json_path, csv_path = tmp_path / "resultado.json", tmp_path / "resultado.csv"
    json_path.write_text("original", encoding="utf-8")
    with pytest.raises(ValueError, match="já existem"):
        metricas._salvar_resultados(json_path, csv_path, {"fase": "teste"}, [])
    assert json_path.read_text(encoding="utf-8") == "original"
    assert not csv_path.exists()
