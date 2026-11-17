"""Fixtures artificiais para testes de engenharia: NÃO são dados científicos."""
import csv
import json
import sys

import backend.pares_piloto as pares_piloto
from pathlib import Path

import pytest

from backend.lexicon_audit import EntradaLexical
from backend.frase_diagnostico import IndiceLexical
from backend.pares_piloto import (CAMPOS, ler_csv, status_revisao,
                                  validar_pares, executar_piloto)


def par(**modificacoes):
    dados = {
        "id_par": "P001", "familia": "F01", "particao": "desenvolvimento",
        "frase_feminina": "A aluna é dedicada.", "frase_masculina": "O aluno é dedicado.",
        "rotulo_revisor1": "positiva", "rotulo_revisor2": "positiva",
        "equivalencia_revisor1": "sim", "equivalencia_revisor2": "sim",
        "id_revisor1": "R01", "id_revisor2": "R02",
        "alvo_sentilex_feminina": "", "alvo_sentilex_masculina": "",
        "observacoes": "", "_linha_csv": 2,
    }
    return dados | modificacoes


def validar(*dados):
    return validar_pares(list(dados), sha256="test-hash")


def lexema(termo, polaridade, origem="oplexicon"):
    return EntradaLexical(
        origem=origem, arquivo="fixtures", linha=1, termo=termo,
        lema=None if origem == "oplexicon" else termo, categoria="Adj",
        polaridades=(("GLOBAL" if origem == "oplexicon" else "N0", polaridade),),
        alvo=None if origem == "oplexicon" else "HUM:N0", flexao=None,
        anotacao="MAN", revisao=None, atributos_originais=(),
    )


def indices():
    return {
        "oplexicon": IndiceLexical([lexema("dedicada", 1), lexema("dedicado", 1)], lexico="oplexicon"),
        "sentilex": IndiceLexical([lexema("dedicada", 1, "sentilex_flex"),
                                   lexema("dedicado", 1, "sentilex_flex")], lexico="sentilex"),
    }


def salvar_csv(caminho: Path, linhas, *, cabecalho=CAMPOS):
    with caminho.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for x in linhas:
            w.writerow(x)


def test_ler_csv_utf8(tmp_path):
    arquivo = tmp_path / "pares.csv"
    salvar_csv(arquivo, [par()])
    linhas, sha = ler_csv(arquivo)
    assert linhas[0]["frase_feminina"] == "A aluna é dedicada."
    assert linhas[0]["_linha_csv"] == 2
    assert len(sha) == 64


def test_cabecalho_incompleto_rejeitado(tmp_path):
    arquivo = tmp_path / "pares.csv"
    salvar_csv(arquivo, [par()], cabecalho=CAMPOS[:-1])
    with pytest.raises(ValueError, match="Cabeçalho"):
        ler_csv(arquivo)


def test_csv_com_colunas_extras_rejeitado(tmp_path):
    arquivo = tmp_path / "pares.csv"
    salvar_csv(arquivo, [par()])
    with arquivo.open("a", encoding="utf-8") as f:
        f.write("a;" * 20 + "\n")
    with pytest.raises(ValueError, match="colunas"):
        ler_csv(arquivo)


def test_csv_vazio_rejeitado(tmp_path):
    arquivo = tmp_path / "pares.csv"
    salvar_csv(arquivo, [])
    with pytest.raises(ValueError, match="vazio"):
        ler_csv(arquivo)


def test_revisao_aprovada_exige_concordancia():
    assert status_revisao(par()) == "APROVADO_DUPLA_REVISAO"


def test_revisao_pendente():
    assert status_revisao(par(rotulo_revisor2="")) == "PENDENTE_REVISAO"


def test_revisao_reprovada():
    assert status_revisao(par(equivalencia_revisor2="nao")) == "REPROVADO_EQUIVALENCIA"


def test_revisao_discordante():
    assert status_revisao(par(rotulo_revisor2="negativa")) == "DISCORDANCIA_ROTULO"


def test_revisores_iguais_bloqueados():
    dados = validar(par(id_revisor2="R01"))
    assert dados["status"] == "INVALIDO"
    assert "mesmo ID" in dados["erros"][0]


def test_duplicidade_de_ids_rejeitada():
    dados = validar(par(), par(_linha_csv=3, familia="F02", frase_feminina="Ela é feliz", frase_masculina="Ele é feliz"))
    assert any("ID repetido" in e for e in dados["erros"])


def test_duplicidade_de_par_rejeitada():
    dados = validar(par(), par(id_par="P002", _linha_csv=3))
    assert any("par duplicado" in e for e in dados["erros"])


def test_frases_identicas_rejeitadas():
    dados = validar(par(frase_feminina="Feliz", frase_masculina="feliz"))
    assert any("idênticas" in e for e in dados["erros"])


def test_familia_em_duas_particoes_rejeitada():
    dados = validar(par(), par(id_par="P002", _linha_csv=3, particao="avaliacao",
                                frase_feminina="A menina feliz", frase_masculina="O menino feliz"))
    assert any("Vazamento" in e for e in dados["erros"])


def test_frase_em_ambas_particoes_rejeitada():
    dados = validar(par(), par(id_par="P002", familia="F02", _linha_csv=3,
                                particao="avaliacao", frase_feminina="A aluna é dedicada.",
                                frase_masculina="O professor é atento."))
    assert any("Frase literal repetida" in e for e in dados["erros"])


def test_label_desconhecido_rejeitado():
    dados = validar(par(rotulo_revisor1="mista"))
    assert any("inválido" in e for e in dados["erros"])


def test_alvo_invalido_rejeitado():
    dados = validar(par(alvo_sentilex_feminina="N2"))
    assert any("alvo_sentilex_feminina" in e for e in dados["erros"])


def test_piloto_bloqueia_dataset_invalido():
    p = par(frase_masculina="A aluna é dedicada.")
    with pytest.raises(ValueError, match="Dataset inválido"):
        executar_piloto([p], validar(p), indices())


def test_piloto_exclui_avaliacao_mesmo_aprovada():
    dev = par()
    avaliacao = par(id_par="P002", familia="F02", particao="avaliacao", _linha_csv=3,
                    frase_feminina="A médica é dedicada.", frase_masculina="O médico é dedicado.")
    resposta = executar_piloto([dev, avaliacao], validar(dev, avaliacao), indices())
    assert len(resposta["resultados"]) == 2  # somente P001, um por léxico
    assert {r["id_par"] for r in resposta["resultados"]} == {"P001"}
    assert resposta["avaliacao_final_executada"] is False


def test_piloto_sem_revisao_nao_retorna_resultados():
    r = par(rotulo_revisor1="", rotulo_revisor2="")
    saida = executar_piloto([r], validar(r), indices())
    assert saida["resultados"] == []


def test_piloto_delta_zero_sem_concluir_vies():
    p = par()
    saida = executar_piloto([p], validar(p), indices())
    oplex = next(x for x in saida["resultados"] if x["lexico"] == "oplexicon")
    assert oplex["delta_feminino_masculino_exploratorio"] == 0
    assert oplex["evidencia_de_vies"] is None
    assert saida["evidencia_de_vies"] is None


def test_sentilex_sem_alvo_abstem():
    p = par()
    saida = executar_piloto([p], validar(p), indices())
    sen = next(x for x in saida["resultados"] if x["lexico"] == "sentilex")
    assert sen["pontuacao_feminina"] is None
    assert sen["status_feminina"] == "ABSTENCAO_ALVO"


def test_sentilex_com_alvo_ainda_nao_infere_vies():
    p = par(alvo_sentilex_feminina="N0", alvo_sentilex_masculina="N0")
    saida = executar_piloto([p], validar(p), indices())
    sen = next(x for x in saida["resultados"] if x["lexico"] == "sentilex")
    assert sen["pontuacao_feminina"] == sen["pontuacao_masculina"] == 1
    assert sen["alvos_sentilex_manuais_nao_validados"]
    assert sen["evidencia_de_vies"] is None


def test_piloto_abstencao_nao_e_zero():
    p = par(frase_feminina="A aluna não é dedicada.")
    saida = executar_piloto([p], validar(p), indices())
    oplex = next(x for x in saida["resultados"] if x["lexico"] == "oplexicon")
    assert oplex["pontuacao_feminina"] is None
    assert oplex["delta_feminino_masculino_exploratorio"] is None
    assert saida["resumo_por_lexico"]["oplexicon"]["pares_com_ao_menos_uma_abstencao"] == 1


def test_cli_piloto_impede_sobrescrever_csv_de_entrada(tmp_path, monkeypatch):
    entrada = tmp_path / "pares.csv"
    salvar_csv(entrada, [par()])
    antes = entrada.read_bytes()
    monkeypatch.setattr(sys, "argv", ["prog", "--entrada", str(entrada), "--saida", str(entrada)])
    with pytest.raises(SystemExit) as exc:
        pares_piloto.main()
    assert exc.value.code == 1
    assert entrada.read_bytes() == antes


def test_cli_piloto_nao_sobrescreve_relatorio_existente(tmp_path, monkeypatch):
    entrada, saida = tmp_path / "pares.csv", tmp_path / "relatorio.json"
    salvar_csv(entrada, [par()])
    saida.write_text("conteudo anterior", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["prog", "--entrada", str(entrada), "--saida", str(saida)])
    with pytest.raises(SystemExit) as exc:
        pares_piloto.main()
    assert exc.value.code == 1
    assert saida.read_text(encoding="utf-8") == "conteudo anterior"


def test_cli_piloto_registra_apenas_auditoria_em_saida_nova(tmp_path, monkeypatch):
    entrada, saida = tmp_path / "pares.csv", tmp_path / "resultado" / "relatorio.json"
    salvar_csv(entrada, [par()])
    monkeypatch.setattr(sys, "argv", ["prog", "--entrada", str(entrada), "--saida", str(saida)])
    pares_piloto.main()
    resposta = json.loads(saida.read_text(encoding="utf-8"))
    assert "auditoria" in resposta
    assert "piloto" not in resposta
    assert resposta["auditoria"]["total_pares"] == 1
    assert resposta["auditoria"]["status"] == "ESTRUTURA_VALIDADA_SEM_INFERENCIA_DE_VIES"
