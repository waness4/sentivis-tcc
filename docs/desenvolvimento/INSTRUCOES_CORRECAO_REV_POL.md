# SentiVis — ajuste do parser SentiLex-PT02: REV:POL

## Motivo
A documentação do repositório B2SHARE descreve duas formas de revisão: `REV=AMB` e `REV:POL`. O código anterior exigia `=` para todo atributo e falhava com `REV:POL` na linha 216 do arquivo flexionado.

## O que muda
- Reconhece **apenas** `REV:POL` sem sinal de igual e registra `revisao="POL"`.
- Preserva a grafia `REV:POL` em `atributos_originais` para rastreabilidade.
- Mantém a leitura estrita dos demais campos e a política de auditoria das polaridades inválidas.
- Não altera arquivos de dados, motor de classificação, API nem protocolo.

## Instalação
Com o PowerShell aberto em `C:\TCC\sentivis_bloco1` e ambiente `.venv` ativado, salvar o ZIP em `C:\TCC` e executar:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco2_correcao_revpol.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m backend.lexicon_audit
```

Os testes devem somar **26**, considerando os 23 testes aprovados anteriormente e os 3 acrescentados nesta correção. O relatório gerado, se a auditoria terminar, estará em `data\lexicos\relatorio_auditoria.json`.

**Atenção:** uma falha posterior pode revelar uma nova particularidade da distribuição; a conclusão da auditoria não equivale à validação científica do classificador. Não utilizar polaridades 7/8 na classificação sem regra científica pré-especificada.

## Fonte
https://b2share.eudat.eu/records/cbyr7-dkf18 — documentação oficial da notação `REV:POL`.
