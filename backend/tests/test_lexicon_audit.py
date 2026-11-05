"""Testes de importadores com amostras artificiais: NÃO usam os léxicos originais."""
from pathlib import Path
import json

import pytest

from backend.lexicon_audit import (
    auditar,
    gerar_relatorio,
    interpretar_oplexicon,
    interpretar_sentilex,
    ler_entradas,
)


def test_sentilex_lema_com_dois_alvos():
    registro = interpretar_sentilex(
        "enganar.PoS=V;TG=HUM:N0:N1;POL:N0=-1;POL:N1=0;ANOT=MAN",
        arquivo="lema.txt", linha=1, flexionado=False,
    )
    assert registro.polaridades == (("N0", -1), ("N1", 0))
    assert registro.categoria == "V"
    assert registro.alvo == "HUM:N0:N1"


def test_sentilex_forma_feminina_e_masculina():
    for forma, flexao in (("bonita", "fs"), ("bonito", "ms")):
        registro = interpretar_sentilex(
            f"{forma},bonito.PoS=Adj;FLEX={flexao};TG=HUM:N0;POL:N0=1;ANOT=MAN",
            arquivo="flex.txt", linha=1, flexionado=True,
        )
        assert registro.termo == forma
        assert registro.lema == "bonito"
        assert registro.flexao == flexao


def test_sentilex_preserva_idioma_e_flex_verbal():
    registro = interpretar_sentilex(
        "engoliste em seco,engolir em seco.PoS=IDIOM;Flex=J2p|J2s;TG=HUM:N0;POL:N0=-1;ANOT=MAN",
        arquivo="flex.txt", linha=1, flexionado=True,
    )
    assert registro.flexao == "J2p|J2s"
    assert registro.termo == "engoliste em seco"
    assert registro.lema == "engolir em seco"


def test_sentilex_preserva_atributos_extras():
    registro = interpretar_sentilex(
        "abstrato.PoS=Adj;TG=HUM:N0;POL:N0=0;ANOT=MAN;REV=Amb;EXTRA=x",
        arquivo="lema.txt", linha=1, flexionado=False,
    )
    assert registro.revisao == "Amb"
    assert "EXTRA=x" in registro.atributos_originais


def test_oplexicon_quatro_campos():
    registro = interpretar_oplexicon("=P,emot,-1,A", arquivo="op.txt", linha=1)
    assert registro.termo == "=P"
    assert registro.categoria == "emot"
    assert registro.polaridades == (("GLOBAL", -1),)
    assert registro.anotacao == "A"


def test_oplexicon_termo_com_virgula_entre_aspas():
    registro = interpretar_oplexicon('"hoje, amanhã",adj,1,M', arquivo="op.txt", linha=1)
    assert registro.termo == "hoje, amanhã"


@pytest.mark.parametrize("linha", [
    "termo,adj,2,M", "termo,adj,abc,M", "termo,adj,1", "termo,adj,1,",
])
def test_oplexicon_invalido_e_detectado(linha):
    with pytest.raises(ValueError):
        interpretar_oplexicon(linha, arquivo="op.txt", linha=17)


def test_polaridade_repetida_e_detectada():
    with pytest.raises(ValueError, match="repetida"):
        interpretar_sentilex(
            "x.PoS=Adj;POL:N0=-1;POL:N0=1", arquivo="lem.txt", linha=3, flexionado=False,
        )


def test_auditoria_preserva_duplicatas_e_diferencas(tmp_path):
    caminho = tmp_path / "lexico_v3.0.txt"
    caminho.write_text("legal,adj,1,A\nlegal,adj,-1,M\nótimo,adj,1,A\n", encoding="utf-8")
    rel = auditar(caminho, tipo="oplexicon")
    assert rel["registros"] == 3
    assert rel["chaves_termo_categoria_repetidas"] == 1
    assert rel["chaves_com_polaridades_divergentes"] == 1
    assert rel["polaridades_por_alvo"]["GLOBAL:1"] == 2


def test_leitura_estrita_nao_ignora_linha_vazia(tmp_path):
    caminho = tmp_path / "op.txt"
    caminho.write_text("ótimo,adj,1,A\n\n", encoding="utf-8")
    with pytest.raises(ValueError, match="linha 2"):
        list(ler_entradas(caminho, tipo="oplexicon"))


def test_gera_relatorio_em_json_sem_mexer_nos_originais(tmp_path):
    origem = tmp_path / "data" / "lexicos" / "originais" / "SentiLex-PT02" / "SentiLex-PT02"
    origem.mkdir(parents=True)
    (origem / "SentiLex-lem-PT02.txt").write_text(
        "bonito.PoS=Adj;TG=HUM:N0;POL:N0=1;ANOT=MAN\n", encoding="utf-8"
    )
    (origem / "SentiLex-flex-PT02.txt").write_text(
        "bonita,bonito.PoS=Adj;FLEX=fs;TG=HUM:N0;POL:N0=1;ANOT=MAN\n", encoding="utf-8"
    )
    (tmp_path / "data" / "lexicos" / "originais" / "lexico_v3.0.txt").write_text(
        "ótimo,adj,1,A\n", encoding="utf-8"
    )
    (tmp_path / "data" / "lexicos" / "originais" / "SentiLex-PT02.zip").write_bytes(b"fixture")
    destino, relatorio = gerar_relatorio(tmp_path)
    assert json.loads(destino.read_text(encoding="utf-8"))["arquivos"]["sentilex_flex"]["registros"] == 1
    assert relatorio["sentilex_zip"]["md5_coincide_com_publicado"] is False


def test_sentilex_excecoes_reais_preservadas_somente_na_auditoria(tmp_path):
    caminho = tmp_path / "SentiLex-lem-PT02.txt"
    caminho.write_text(
        "intrépido e sereno.PoS=Adj;TG=HUM:N0;POL:N0=8;ANOT=MAN;REV=POL\n"
        "intrépido.PoS=Adj;TG=HUM:N0;POL:N0=7;ANOT=MAN;REV=POL\n"
        "bonito.PoS=Adj;TG=HUM:N0;POL:N0=1;ANOT=MAN\n",
        encoding="utf-8",
    )
    # Uso normal exige polaridades válidas; nada de converter 8/7 em 1.
    with pytest.raises(ValueError, match="fora de -1/0/1: 8"):
        list(ler_entradas(caminho, tipo="sentilex_lem"))
    relatorio = auditar(caminho, tipo="sentilex_lem")
    assert relatorio["registros"] == 3
    assert relatorio["registros_com_polaridade_fora_padrao"] == 2
    assert relatorio["ocorrencias_polaridade_fora_padrao"] == 2
    assert relatorio["polaridades_por_alvo"]["N0:8"] == 1
    assert relatorio["polaridades_por_alvo"]["N0:7"] == 1
    assert [ex["linha"] for ex in relatorio["exemplos_polaridade_fora_padrao"]] == [1, 2]
    assert relatorio["exemplos_polaridade_fora_padrao"][0]["polaridades_invalidas"] == [
        {"alvo": "N0", "valor_original": 8}
    ]


def test_sentilex_flex_fora_padrao_nao_impede_auditoria(tmp_path):
    caminho = tmp_path / "SentiLex-flex-PT02.txt"
    caminho.write_text(
        "intrépida,intrépido.PoS=Adj;FLEX=fs;TG=HUM:N0;POL:N0=7;ANOT=MAN\n",
        encoding="utf-8",
    )
    relatorio = auditar(caminho, tipo="sentilex_flex")
    assert relatorio["registros_com_polaridade_fora_padrao"] == 1
    assert relatorio["flexoes"]["fs"] == 1


def test_oplexicon_permanece_estrito_na_auditoria(tmp_path):
    caminho = tmp_path / "lexico_v3.0.txt"
    caminho.write_text("termo,adj,8,A\n", encoding="utf-8")
    with pytest.raises(ValueError, match="fora de -1/0/1"):
        list(ler_entradas(caminho, tipo="oplexicon"))
    resumo = auditar(caminho, tipo="oplexicon")
    assert resumo["linhas_nao_interpretaveis"] == 1
    assert resumo["registros"] == 0


def test_sentilex_rev_dois_pontos_pol_e_notacao_oficial():
    entrada = interpretar_sentilex(
        "admirável.PoS=Adj;TG=HUM:N0;POL:N0=1;ANOT=MAN;REV:POL",
        arquivo="SentiLex-lem-PT02.txt", linha=216, flexionado=False,
    )
    assert entrada.revisao == "POL"
    assert entrada.polaridades == (("N0", 1),)
    assert "REV:POL" in entrada.atributos_originais


def test_sentilex_rev_dois_pontos_pol_no_arquivo_flexionado(tmp_path):
    caminho = tmp_path / "SentiLex-flex-PT02.txt"
    linha = "admirável,admirável.PoS=Adj;FLEX=ms;TG=HUM:N0;POL:N0=1;ANOT=MAN;REV:POL\n"
    caminho.write_text(linha, encoding="utf-8")
    entrada = next(ler_entradas(caminho, tipo="sentilex_flex"))
    assert entrada.revisao == "POL"
    assert entrada.flexao == "ms"
    assert "REV:POL" in entrada.atributos_originais
    assert auditar(caminho, tipo="sentilex_flex")["revisoes"]["POL"] == 1
    assert caminho.read_text(encoding="utf-8") == linha


def test_sentilex_continua_rejeitando_atributo_malformado_desconhecido():
    with pytest.raises(ValueError, match="atributo malformado"):
        interpretar_sentilex(
            "x.PoS=Adj;POL:N0=1;REV:DESCONHECIDO",
            arquivo="lem.txt", linha=9, flexionado=False,
        )


def test_sentilex_fragmento_morfologico_sem_chave_e_preservado():
    trecho = "P2s|P4s|P3s|Y2s"
    linha = f"afirma,afirmar.PoS=V;FLEX=P3s;{trecho};TG=HUM:N0;POL:N0=1;ANOT=MAN"
    with pytest.raises(ValueError, match="atributo malformado"):
        interpretar_sentilex(linha, arquivo="flex.txt", linha=1107, flexionado=True)
    entrada = interpretar_sentilex(
        linha, arquivo="flex.txt", linha=1107, flexionado=True,
        permitir_atributos_sem_chave=True,
    )
    assert entrada.flexao == "P3s"
    assert entrada.atributos_sem_chave == (trecho,)
    assert trecho in entrada.atributos_originais
    assert entrada.polaridades == (("N0", 1),)


def test_auditoria_nao_para_em_atributos_sem_chave_e_gera_trilha(tmp_path):
    caminho = tmp_path / "SentiLex-flex-PT02.txt"
    linha1 = "afirma,afirmar.PoS=V;FLEX=P3s;P2s|P4s|P3s|Y2s;TG=HUM:N0;POL:N0=1;ANOT=MAN"
    linha2 = "bonita,bonito.PoS=Adj;FLEX=fs;TG=HUM:N0;POL:N0=1;ANOT=MAN"
    caminho.write_text(linha1+"\n"+linha2+"\n", encoding="utf-8")
    d=auditar(caminho,tipo="sentilex_flex")
    assert d["registros"] == d["linhas_totais"] == 2
    assert d["registros_com_atributos_sem_chave"] == 1
    assert d["exemplos_atributos_sem_chave"][0]["linha"] == 1
    assert d["exemplos_atributos_sem_chave"][0]["registro_original"] == linha1
    assert d["linhas_nao_interpretaveis"] == 0


def test_auditoria_registra_todas_linhas_invalidas_sem_descartar_contagem(tmp_path):
    caminho=tmp_path/"SentiLex-flex-PT02.txt"
    caminho.write_text(
        "bonita,bonito.PoS=Adj;FLEX=fs;POL:N0=1;ANOT=MAN\n"
        "invalida sem POS\n"
        "\n"
        "intrépida,intrépido.PoS=Adj;FLEX=fs;POL:N0=8;ANOT=MAN\n",
        encoding="utf-8",
    )
    d=auditar(caminho,tipo="sentilex_flex")
    assert d["linhas_totais"] == 4
    assert d["registros"] == 2
    assert d["linhas_nao_interpretaveis"] == 2
    assert [e["linha"] for e in d["exemplos_erros_estrutura"]] == [2, 3]
    assert d["registros_com_polaridade_fora_padrao"] == 1
