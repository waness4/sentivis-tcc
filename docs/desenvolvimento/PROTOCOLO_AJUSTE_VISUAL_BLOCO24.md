# Bloco 24 — Ajuste visual de tabelas diagnósticas

## Escopo

Corrige a quebra de termos como `gentileza` e do cabeçalho `Termo` em uma tabela com quatro colunas quando exibida nos dois cartões comparativos. Mantém a legibilidade das descrições com quebra entre palavras e permite rolagem horizontal local no contêiner `.context-table-wrap`, sem alargar a página. Atualiza apenas o texto estático da identificação para `Interface experimental · baselines V01 e V04`.

## Arquivos modificados no projeto

- `frontend/styles.css`: novas regras CSS no final.
- `frontend/index.html`: rótulo da interface, sem alterar controles nem comportamento.

O script de aplicação é idempotente e verifica a estrutura anterior antes de escrever. Os testes são sintéticos e não consultam léxicos ou fichas privadas.

## Critérios de aceitação

1. `python -m pytest .\backend\tests -q` concluído sem falhas.
2. Na comparação V04 de duas frases com `gentileza`, nenhuma palavra aparece partida no meio na primeira coluna da tabela contextual.
3. Em cartão estreito, a rolagem horizontal fica limitada à tabela.
4. Em telas pequenas, formulários e resultados continuam utilizáveis.
5. O rótulo da demonstração não confunde a interface com o baseline V04.

A mudança não reavalia hipóteses sintáticas nem fornece evidência de viés.
