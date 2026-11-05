# SentiVis – Bloco 2: auditoria robusta de estruturas originais

Esta correção substitui `backend/lexicon_audit.py` e `backend/tests/test_lexicon_audit.py` sem modificar `core.py`, `main.py` ou os arquivos originais dos léxicos.

## Windows PowerShell

1. Salve o ZIP em `C:\TCC\sentivis_bloco2_auditoria_completa.zip`.
2. Dentro de `C:\TCC\sentivis_bloco1`, com `.venv` ativado, execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco2_auditoria_completa.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m backend.lexicon_audit
```

## Como interpretar

O JSON `data/lexicos/relatorio_auditoria.json` informa por léxico `linhas_totais`, `registros` interpretados, `linhas_nao_interpretaveis` e `registros_com_atributos_sem_chave` com amostras contendo linha e texto original (até 50 de cada classe). Registros com polaridades fora de -1,0,1 também continuam documentados.

Fragmentos sem `CHAVE=valor`, como `P2s|P4s|P3s|Y2s`, **não são convertidos automaticamente** em FLEX. Eles permanecem como anomalias a revisar. Importação científica estrita continua rejeitando a notação até decisão metodológica fundamentada.

Caso haja erros de estrutura no relatório, a auditoria **não equivale à validação dos dados**; o classificador permanece provisório.
