# SentiVis — Bloco 2: auditoria estrutural dos léxicos

## Instalação

1. Salve o ZIP `sentivis_bloco2_auditoria.zip` em `C:\TCC`.
2. Abra o PowerShell com o ambiente virtual ativado no projeto.
3. Execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco2_auditoria.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m backend.lexicon_audit
```

Os arquivos adicionados são `backend/lexicon_audit.py` e `backend/tests/test_lexicon_audit.py`. Os arquivos `backend/core.py` e `backend/main.py` permanecem intactos. O script procura automaticamente as subpastas duplicadas do SentiLex.

O relatório JSON fica em `data/lexicos/relatorio_auditoria.json`.

## Limitações

- Os dados reais são auditados estruturalmente, mas não são classificados.
- Os dados originais nunca são modificados nem redistribuídos neste pacote.
- O `SentiLex-PT02.zip` é confrontado com o MD5 divulgado no B2SHARE. A origem e a licença de redistribuição da cópia OpLexicon ainda exigem verificação independente.
- Duplicatas e polaridades divergentes **não são apagadas**. Precisam de revisão antes de fixar uma regra de consulta.
- As regras de alvo N0/N1, negação, expressões compostas, desambiguação e experimentos confirmatórios ainda não foram implementadas.
