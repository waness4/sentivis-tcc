# SentiVis — Bloco 36 | Protocolo de comparação sintética de políticas G03

**Somente teste de engenharia. Estado: NAO_CONGELADO_NAO_AUTORIZADO.**

## Entradas e isolamento

O módulo `backend.politica_ausencias_bloco36` usa exclusivamente as fixtures literais do Bloco 34 (origem fictícia de 14 colunas) e do Bloco 33 (27 pares e anotações artificiais). Para o cenário de não resposta, apaga o rótulo e a equivalência do primeiro par **inventado**. As entradas são strings em memória; a CLI não aceita `--entrada`, arquivos, caminhos, opções para aprovar ou arquivos privados. Não há leitura de originais lexicais nem do conjunto reservado neste módulo.

O programa rejeita qualquer fonte diferente da fixture imutável, mesmo que tenha 27 pares ou um nome sintético, antes de analisar a ficha. A comparação de políticas recebe somente anotações cujas frases e IDs sejam idênticos aos fictícios. Os baselines reais V01, V03 e V04 do repositório são exercitados **apenas** contra o índice lexical e o etiquetador fictícios do Bloco 33.

## Comparação técnica

A opção `bloquear_ficha_pendente` rejeita qualquer valor vazio de `equivalencia`, antes de invocar os classificadores. A opção `contabilizar_pendente_nao_elegivel` aceita `equivalencia=''` e `rotulo=''` somente como ausência de decisão, exclui o par do denominador elegível, mas conserva as duas frases na cobertura global. O conjunto de IDs, as frases, os rótulos existentes e a integridade estrutural não podem ser modificados pela execução. `sim` sem rótulo, `nao` sem justificativa e `nao` com rótulo continuam inválidos.

No cenário sintético com uma pendência: total 27 pares/54 frases, 20 pares elegíveis, 7 não elegíveis (6 marcados `nao`, 1 sem resposta), 40 frases elegíveis. A classificação e as métricas para a opção B continuam exploratórias, com os limites do Bloco 29. O resultado não deve ser rotulado como acurácia validada, concordância interavaliadores, prova de viés ou ausência de viés.

## Execução e segurança

- `python -m backend.politica_ausencias_bloco36 verificar-contrato`: contrato estático, sem leitura de dados.
- `python -m backend.politica_ausencias_bloco36 comparar-opcoes`: usa apenas as fixtures em memória, imprime resumo da comparação; não grava resultados nem cria marcadores.
- `python -m backend.politica_ausencias_bloco36 executar-final`: **sempre bloqueado**, mesmo com argumentos adicionais; não abre o conjunto reservado.

Nenhum comando modifica o Bloco 34 ou transforma qualquer opção em política aprovada. As decisões são humanas e precisam ser documentadas antes da etapa final.

## Próxima condição obrigatória

A política deve ser deliberada, implementada no futuro executor real, testada com dados fictícios, revisada e incluída em um commit e protocolo congelados. Permanecem os demais portões G01/G02/G04–G08 do Bloco 35, inclusive aprovação acadêmica e custódia dos dados. Só depois será possível cogitar a coleta de anotação reservada e pontuação automática.
