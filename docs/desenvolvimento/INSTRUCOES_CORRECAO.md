# SentiVis — correção da auditoria de valores fora do padrão (Bloco 2)

## Problema identificado
A distribuição do SentiLex-PT02 contém, entre outras, as linhas 4319 e 4320 do arquivo de lemas com `POL:N0=8` e `POL:N0=7`, valores incompatíveis com o domínio documentado `{-1, 0, 1}`.

## Alteração
- `backend/lexicon_audit.py`: a auditoria registra os valores fora do padrão, mantendo-os no relatório e preservando os arquivos de origem. Ela não converte valores inválidos em 1, 0 ou -1. O modo padrão de leitura do SentiLex continua estrito para evitar usar indevidamente esses valores em classificadores.
- `backend/tests/test_lexicon_audit.py`: adiciona três testes de regressão.
- `backend/core.py`, `backend/main.py` e os arquivos originais não são modificados.

## Instalação (PowerShell na pasta do projeto, com .venv ativado)

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco2_correcao.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m backend.lexicon_audit
```

## Verificações
O relatório será salvo em `data\lexicos\relatorio_auditoria.json`. Procure `registros_com_polaridade_fora_padrao` e `exemplos_polaridade_fora_padrao`.

A auditoria estrutural não equivale à validação científica do classificador. Antes de usar as entradas marcadas, será necessário estabelecer uma regra explícita no protocolo de pesquisa e documentar o número de entradas excluídas ou revisadas.
