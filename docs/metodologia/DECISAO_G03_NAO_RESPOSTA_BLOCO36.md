# SentiVis — Bloco 36 | Deliberação G03 sobre respostas humanas ausentes

**Estado: PROPOSTA NÃO APROVADA. Avaliação final ainda bloqueada.**

## Problema identificado

O plano de análise do Bloco 28 admite respostas ausentes como **não elegíveis**, mantidas nas contagens globais, enquanto o contrato do Bloco 34 recusa fichas cuja coluna `equivalencia` ainda esteja vazia. Não é lícito escolher uma dessas regras após examinar as previsões automáticas ou o conjunto reservado. O Bloco 36 **não altera retroativamente** os contratos existentes.

## Duas opções para decisão anterior à abertura

| Aspecto | Opção A — bloquear ficha pendente | Opção B — contabilizar como não elegível |
|---|---|---|
| `equivalencia` em branco com `rotulo` em branco | Interrompe a execução antes dos modelos | Conta como `sem_resposta`, sem elegibilidade |
| Frases desse par na cobertura **global** | Não se calcula saída até regularização | Permanecem entre as 54 frases da amostra global |
| Frases desse par na cobertura **elegível** | Não se calcula saída | Não entram no denominador elegível |
| Deltas por par | Não se calcula saída | Não calculáveis para esse par |
| Pedido de resposta posterior | Pode ser solicitado **antes** de qualquer previsão e conforme plano de anotação | Não completar posteriormente com base em previsões |
| Relato de não respostas | Registrar tentativa e pendência | Registrar quantidade e motivos de exclusão |

Ambas as opções mantêm erros de formato, IDs duplicados, frases alteradas, equivalência `sim` sem rótulo e equivalência `nao` com rótulo preenchido como **erros de validação**. A opção B não autoriza corrigir automaticamente rótulos, usar marcações prévias de construção ou transformar falta de resposta em `neutra`.

**Sugestão para deliberação:** a opção B é mais alinhada à redação do Bloco 28 e permite informar explicitamente perdas de anotação sem eliminar os 27 pares da amostra global. Contudo, ela exige uma alteração **prospectiva e aprovada** do contrato do Bloco 34, com testes exclusivamente sintéticos. Uma política estrita também é defensável se registrada e aprovada antes da anotação. **Nenhuma foi aprovada aqui.**

## Exemplo numérico inteiramente artificial

A fixture de desenvolvimento repetida contém 27 pares fictícios: 21 são considerados equivalentes e 6 não equivalentes por marcações inventadas. Ao apagar artificialmente a decisão de um dos 21 pares:

- Opção A: interrompe; nenhuma classificação é realizada para esse cenário.
- Opção B: registra `P_total=27`, `P_equivalentes_R01=20`, `P_nao_elegiveis=7`, dos quais `sem_resposta=1`; `F_total=54` e `F_elegiveis=40`.

Os números são **somente testes de software**, não resultados da partição reservada nem validação de um julgamento humano.

## Campos para registro real de decisão

- Política escolhida (A/B): **PENDENTE**
- Regra para resposta incompleta/ambígua e eventual solicitação de complemento antes de previsões: **PENDENTE**
- Responsável pela revisão, função e meio de concordância: **PENDENTE**
- Data, hora e fuso, anteriores à abertura: **PENDENTE**
- Versão do protocolo e commit após adaptação aprovada: **PENDENTE**
- Evidência dos testes sintéticos após adaptação: **PENDENTE**

Esta ficha não é uma autorização de acesso, assinatura ou congelamento. O termo de aprovação do Bloco 35 e o checklist do Bloco 28 continuam exigidos.
