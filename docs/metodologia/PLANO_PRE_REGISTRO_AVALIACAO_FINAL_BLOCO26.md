# SentiVis — Plano de pré-registro da avaliação final (Bloco 26)

**Status: RASCUNHO PARA REVISÃO. NÃO CONGELADO. NÃO EXECUTADO.** Este plano é independente do resultado dos 27 pares reservados e não contém suas frases ou rótulos. Elaborado em 16/11/2026 com base nos protocolos de desenvolvimento.

## 1. Objetivo e limites

Realizar **uma única avaliação descritiva previamente fixada** dos baselines e das diferenças de pontuação em pares contrafactuais de referência de gênero, sem usar esse conjunto para treinamento, ajuste, seleção de regras, escolha de frases demonstrativas ou inspeção iterativa. A amostra reservada possui **27 pares distribuídos em 9 famílias**. Os critérios de elegibilidade e os hashes precisam ser congelados *antes da abertura*. Amostra pequena e sintética impede generalização populacional e conclusões causais fortes.

**Perguntas separadas:** (a) que fração das frases é pontuada/abstida? (b) entre as frases pontuadas e com referência humana elegível, que proporção coincide com o rótulo humano? (c) em quantos pares **elegíveis e com duas pontuações** as pontuações feminina e masculina diferem? A terceira pergunta é descritiva, não equivale a uma medida validada de viés.

## 2. Condições obrigatórias ANTES de abrir os 27 pares

Documentar em arquivo datado, assinado/aprovado pelos responsáveis e com hash do commit:

1. Versões exatas do código, baselines comparados, léxicos e modelo `pt_core_news_sm`, parâmetros `alvo=N0` manual ou alternativa explicitamente escolhida, `hipotese_modo` e regras de abstenção. Uma seleção manual não representa reconhecimento do referente.
2. Script de análise final, interface de entrada/saída, verificações de integridade, teste sintético e critérios para falha de execução. Testar somente com dados fictícios/desenvolvimento, não com avaliação final.
3. Esquema de referência humana, avaliação da equivalência semântica, tratamento de discordâncias e regras de inclusão/exclusão **sem conhecer resultados da avaliação final**.
4. Definição das métricas, denominadores e do tratamento de valores ausentes/abstenções abaixo, incluindo apresentação de itens excluídos.
5. Procedimento de acesso e custódia do conjunto reservado, hash do conjunto, saída versionada sem sobrescrita e registro de execução único.
6. Formato das tabelas do TCC, distinção entre hipóteses e resultados, declaração de que não haverá ajuste após observar o teste.

**Bloqueio:** até todos os itens acima estarem completos, nenhuma execução ou inspeção do conjunto reservado está autorizada por este documento.

## 3. Revisão humana da partição reservada (após congelamento)

- A ficha de cada revisor deve omitir a polaridade planejada, a classificação dos baselines e os julgamentos do outro revisor; mostrar somente o necessário para julgar equivalência e polaridade.
- Em cada par: declarar se houve equivalência semântica avaliativa entre versões de gênero (`sim`/`nao`) e, quando possível, o rótulo comum (`positiva`/`negativa`/`neutra`). Preservar observações de ambiguidade, naturalidade e referência.
- Adjudicação humana: discordâncias e não equivalências não serão corrigidas por saída automática. Regras de exclusão devem estar fixadas e suas quantidades publicadas.
- Nenhuma definição de rótulos humanos deve ser feita ou alterada depois de consultar as pontuações dos baselines. O acesso humano aos pares reservados, se autorizado, é uma **etapa de avaliação**, não de desenvolvimento de regras.
- Não se pode pressupor que `neutra` signifique `sem_avaliacao`; aplicar somente categorias definidas na ficha de cada partição.

## 4. Unidades de análise e denominadores

**Unidade frase:** cada par contém uma versão com referência feminina e uma masculina. Para cada baseline e léxico aplicável, registrar `N_frases_recebidas`, `N_frases_eligiveis`, `N_pontuadas`, `N_abstidas`, `N_com_rotulo_compativel` e `N_pontuadas_com_rotulo_compativel`.

**Unidade par:** distinguir `N_pares_recebidos=27`, `N_pares_com_equivalencia_confirmada`, `N_pares_com_dois_resultados_pontuados` e `N_pares_com_delta_calculavel`. Não interpretar duas frases como duas observações independentes para inferência estatística. Estratificar por família apenas para apresentação, se o número de casos permitir.

**Relato:** apresentar contagens e proporções com numeradores/denominadores visíveis e motivo de cada exclusão. Não misturar taxas de decisão em todas as frases com taxas só nas elegíveis sem rotular os universos.

## 5. Métricas pré-especificadas propostas

| Métrica | Numerador / denominador | Interpretação |
|---|---|---|
| Taxa de pontuação | `N_pontuadas / N_frases_eligiveis` | cobertura de **decisão**, não cobertura lexical superficial |
| Taxa de abstenção | `N_abstidas / N_frases_eligiveis` | custo da cautela; investigar razões de abstenção |
| Acurácia seletiva | `N_corretas_entre_pontuadas_e_rotuladas / N_pontuadas_com_rotulo_compativel` | qualidade condicional somente entre os casos decididos e comparáveis; indefinida se denominador zero |
| Concordância humana sobre equivalência | `N_acordos / N_pares_efetivamente_revisados` | consistência dos dois revisores, não qualidade do classificador |
| Pares com delta calculável | `N_pares_com_duas_pontuacoes / N_pares_com_equivalencia_confirmada` | cobertura no nível do par; indefinido se não houver pares elegíveis |
| Pares com diferença não nula | `N_pares_com_delta_diferente_de_zero / N_pares_com_delta_calculavel` | diferença lexical **descritiva**, não evidência isolada de viés |

Para cada par com equivalência confirmada e **ambos resultados pontuados**, registrar `delta = pontuacao_feminina - pontuacao_masculina`, sinal e magnitude, com método idêntico para ambas. Quando alguma frase se abstiver, `delta` é **não calculável**; nunca imputar zero. Para casos que diferem, inspecionar somente **após a execução final única** para discussão de erros e limitações, sem alterar os baselines ou rerodar a avaliação como se fosse independente.

**Regra de mapeamento a fechar antes do congelamento:** somente classes humanas e do baseline com equivalência explícita serão comparadas. Manter `sem_avaliacao`, `mista` e `indeterminada` fora do denominador de acurácia seletiva quando não houver mapeamento validado; reportar essas exclusões. As categorias dos controles e dos pares do piloto são diferentes e não devem ser mescladas.

## 6. Avaliações complementares e incerteza

- Relatar distribuição das abstenções e motivos, com diferenças entre V01/V03/V04 separadas por método/lexico, evitando comparação indevida de recursos distintos.
- Considerar tabelas descritivas por família, mas não anunciar teste estatístico de viés ou significância **sem plano estatístico, unidades de agrupamento e justificativa anteriores à avaliação**.
- Se for decidido calcular intervalos de confiança ou testar hipóteses, o método deve ser formalizado antes de qualquer acesso à partição reservada e respeitar a dependência intrapar/família. Em caso contrário, limitar-se a frequências e proporções com ressalva de amostra pequena.
- Reportar itens não pontuados e divergências humanas. Não declarar “ausência de viés” quando o delta for zero ou quando quase todos os casos se abstiverem.

## 7. Trilha de auditoria da execução final

O registro final deverá conter: data/hora; commit/hash do código; hashes do corpus e manifestos dos léxicos; versão do spaCy; versões e parâmetros exatos dos baselines; confirmação da revisão humana; números de elegibilidade/abstenção; um único relatório agregado de execução com `N_pares_avaliacao_processados`; e trilha documentada de falhas ou interrupções. Evitar logs com frases/respostas privadas em repositório público.

Caso surja um defeito após a primeira execução, preservar a saída original e registrar o desvio. Uma reexecução de versão corrigida passa a ser análise **pós-hoc**, não uma segunda validação independente. O problema pode exigir nova amostra externa para inferências confirmatórias.

## 8. Checklist de congelamento (PENDENTE)

- [ ] Dupla revisão humana dos 36 controles concluída e limitações de C001 registradas.
- [ ] Decisões sobre adjudicação, mapeamento de classes e critérios de exclusão assinadas.
- [ ] Baselines/lexicos/etiquetador e parâmetros fixados com hashes/versões.
- [ ] Script de avaliação final definido, revisado e testado apenas com dados não reservados.
- [ ] Plano de métricas, denominadores e apresentação aprovado e datado.
- [ ] Critérios de acesso, preservação das saídas e falhas de execução definidos.
- [ ] Nenhuma regra escolhida a partir dos 27 pares reservados.

**Este documento não marca nenhum item como concluído. Não autoriza, por si só, abrir ou executar a partição final.**
