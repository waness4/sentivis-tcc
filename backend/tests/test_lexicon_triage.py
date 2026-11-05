"""Testes usando entradas sintéticas, não o conjunto científico final."""
import csv
import json

from backend.lexicon_audit import interpretar_sentilex, interpretar_oplexicon
from backend.lexicon_triage import analisar_entradas, gerar, ler_para_curadoria


def sent(texto, n, flex=False, **kwargs):
    return interpretar_sentilex(texto, arquivo="senti.txt", linha=n,
                                flexionado=flex, **kwargs)


def op(texto, n):
    return interpretar_oplexicon(texto, arquivo="op.txt", linha=n)


def test_alvos_diferentes_nao_sao_conflito():
    a = sent("bom.PoS=Adj;TG=HUM:N0:N1;POL:N0=1;POL:N1=-1;ANOT=MAN", 1)
    b = sent("bom.PoS=Adj;TG=HUM:N0:N1;POL:N0=1;POL:N1=-1;ANOT=MAN", 2)
    resumo, detalhe = analisar_entradas([a, b])
    assert resumo["grupos_conflitantes_por_termo_categoria_alvo"] == 0
    assert detalhe == []


def test_conflito_para_mesmo_alvo_e_detectado():
    a = sent("feliz.PoS=Adj;TG=HUM:N0;POL:N0=1;ANOT=MAN", 1)
    b = sent("feliz.PoS=Adj;TG=HUM:N0;POL:N0=-1;ANOT=MAN", 2)
    resumo, detalhes = analisar_entradas([a, b])
    assert resumo["grupos_conflitantes_por_termo_categoria_alvo"] == 1
    assert len(detalhes) == 2
    assert all("polaridade_divergente_mesmo_alvo" in d["motivos"] for d in detalhes)


def test_polaridade_invalida_nunca_e_modificada():
    a = sent("intrépido.PoS=Adj;TG=HUM:N0;POL:N0=7;ANOT=MAN", 1,
             permitir_polaridade_fora_padrao=True)
    resumo, detalhes = analisar_entradas([a])
    assert resumo["registros_por_motivo"]["polaridade_fora_do_padrao"] == 1
    assert detalhes[0]["polaridades"] == "N0=7"


def test_atributo_sem_chave_preservado():
    a = sent("acho,achar.PoS=V;P1s;TG=HUM:N0;POL:N0=1;ANOT=MAN", 1, flex=True,
             permitir_atributos_sem_chave=True)
    resumo, detalhes = analisar_entradas([a])
    assert detalhes[0]["atributos_sem_chave"] == "P1s"
    assert resumo["registros_por_motivo"]["atributo_sem_chave"] == 1


def test_categorias_diferentes_nao_geram_conflito():
    a = op("legal,adj,1,M", 1)
    b = op("legal,vb,-1,M", 2)
    resumo, detalhes = analisar_entradas([a,b])
    assert resumo["grupos_conflitantes_por_termo_categoria_alvo"] == 0
    assert detalhes == []


def test_leitura_registra_linha_invalida_sem_descartar_outras(tmp_path):
    p = tmp_path / "lexico_v3.0.txt"
    p.write_text("bonito,adj,1,M\nmalformado\nruim,adj,-1,M\n", encoding="utf8")
    entries, erros = ler_para_curadoria(p, "oplexicon")
    assert len(entries) == 2
    assert len(erros) == 1
    assert erros[0]["linha"] == 2


def test_gera_arquivos_e_mantem_original(tmp_path):
    originais = tmp_path / "data" / "lexicos" / "originais"
    sub = originais / "SentiLex-PT02"
    sub.mkdir(parents=True)
    orig_lex = originais / "lexico_v3.0.txt"
    orig_lex.write_text("positivo,adj,1,A\n", encoding="utf8")
    (sub / "SentiLex-lem-PT02.txt").write_text(
        "intrépido.PoS=Adj;TG=HUM:N0;POL:N0=7;ANOT=MAN\n", encoding="utf8"
    )
    (sub / "SentiLex-flex-PT02.txt").write_text(
        "bonita,bonito.PoS=Adj;FLEX=fs;TG=HUM:N0;POL:N0=1;ANOT=MAN\n", encoding="utf8"
    )
    original = orig_lex.read_bytes()
    path_json, path_csv, data = gerar(tmp_path)
    assert orig_lex.read_bytes() == original
    assert json.loads(path_json.read_text(encoding="utf8"))["registros_interpretados"] == 3
    with path_csv.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert len(rows) == 1
    assert rows[0]["termo"] == "intrépido"
    assert data["registros_sinalizados_para_revisao"] == 1
