# SentiVis — Bloco 26: metodologia de anotação e plano de avaliação final

**Estado:** documentação proposta, NÃO é congelamento formal do protocolo e NÃO é resultado de avaliação final.

## Objetivo

Documentar os procedimentos para consolidar a revisão humana dos 36 controles, registrar a exposição potencial de C001 e preparar o plano de avaliação independente dos 27 pares reservados. Este bloco **não altera classificadores, interface, léxicos, corpus nem testes**.

## Instalação

1. Colocar `sentivis_bloco26_metodologia.zip` em `C:\TCC`.
2. No PowerShell, dentro de `C:\TCC\sentivis_bloco1`, executar:

```powershell
Expand-Archive -Path 'C:\TCC\sentivis_bloco26_metodologia.zip' -DestinationPath 'C:\TCC\sentivis_bloco1' -Force
```

3. Consultar os documentos:

```powershell
notepad .\docs\metodologia\PROTOCOLO_CONTROLES_HUMANOS_BLOCO26.md
notepad .\docs\metodologia\PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md
notepad .\docs\resultados\REGISTRO_RASTREABILIDADE_BLOCO25.md
```

4. Conferir apenas os arquivos novos:

```powershell
git status --short
```

**Não executar a avaliação final.** Também não rodar `anotacao_controles_v01 consolidar` enquanto as fichas originais de R01 e R02 não estiverem completas; as fichas existentes não devem ser sobrescritas.

## Conteúdo

- `docs/metodologia/PROTOCOLO_CONTROLES_HUMANOS_BLOCO26.md`: operação das duas fichas, integridade, concordância, adjudicação e exposição de C001.
- `docs/metodologia/PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md`: proposta de critérios, métricas, parâmetros e travas antes do uso do conjunto reservado.
- `docs/resultados/REGISTRO_RASTREABILIDADE_BLOCO25.md`: resultados numéricos verificados pelo terminal, com as ressalvas necessárias.

## Regras de proteção

- Não anexar as fichas humanas, registros individuais ou resultados em `data/piloto/restrito/` ao commit público.
- A partição reservada com 27 pares permanece isolada; não ler, pontuar ou utilizar como exemplos de demonstração.
- Não tratar os 36 controles como validação independente: foram inspecionados para desenvolver V04.
- Os testes de software (345 aprovados até o Bloco 24) não validam a classificação linguística.

## Quando houver as fichas completas dos 36 controles

O comando existente, **somente depois de recebidas**, é:

```powershell
python -m backend.anotacao_controles_v01 consolidar --pasta-saida .\data\piloto\restrito
```

Ele valida e calcula concordância; não resolve divergências automaticamente. Os arquivos de saída previstos são `consolidacao_controles_humana_v01.csv` e `relatorio_concordancia_controles_v01.json`, na pasta restrita. Se já existirem, não sobrescrever: preservar e revisar a situação primeiro.

## Publicação

Depois da revisão do conteúdo, adicionar **somente** estes arquivos de documentação, se desejado; o `INSTRUCOES_REVISAO_V02.md` permanece fora do commit salvo decisão explícita. A publicação não equivale a congelamento da análise final.
