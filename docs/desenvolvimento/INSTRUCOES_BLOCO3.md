# SentiVis — Bloco 3: triagem documental dos léxicos

## Objetivo

Analisar o que o relatório estrutural sinalizou: inconsistências de polaridade,
metadados sem chave e conflitos **no mesmo alvo de sentimento**. O programa não
modifica os léxicos, não modifica `backend/core.py` nem `backend/main.py`, não
classifica frases e não corrige dados automaticamente.

## Instalação

Salve o ZIP em `C:\TCC` e execute, com o ambiente virtual ativo e a pasta
`C:\TCC\sentivis_bloco1` aberta:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco3_curadoria.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m backend.lexicon_triage
```

## Saídas

- `data\lexicos\relatorio_curadoria.json`: resumo, contagens por motivo e fontes/hashes.
- `data\lexicos\pendencias_curadoria.csv`: linhas com pelo menos uma sinalização,
  separadas por arquivo/linha, incluindo os atributos originais (UTF-8 com BOM,
  delimitador `;`, compatível com Excel/Calc).

## Interpretação

- **Polaridade inválida**: não converter valores fora de -1, 0 ou +1.
- **Atributo sem chave**: pode ser uma convenção morfológica, ainda não validada.
- **Divergência no mesmo alvo**: pode ser polissemia ou duplicação, não
  automaticamente erro.
- **Mesmo termo/categoria com lemas diferentes**: colisão morfológica a revisar.
- Um registro não sinalizado NÃO está automaticamente validado cientificamente.
- O relatório é uma triagem para preparar critérios pré-especificados de uso,
  métricas de cobertura e análise pareada. Não produz medida de viés.

## Cuidados

Mantenha os arquivos originais e o relatório anterior intactos. Não adicione
arquivos de léxicos ao repositório público sem confirmar as licenças de cada fonte.
