# SentiVis — protocolo de métricas descritivas de desenvolvimento, v0.1

**Status:** implementação de engenharia para um **piloto exploratório**. Não é validação do classificador, teste inferencial, análise causal ou demonstração de viés de gênero.

## 1. População e filtro de elegibilidade

O Bloco 12 opera **exclusivamente** sobre pares na partição `desenvolvimento` com status `APROVADO_DUPLA_REVISAO` conforme `backend.pares_piloto.status_revisao`. Exige concordância `sim` dos dois revisores sobre equivalência, rótulos idênticos (`positiva`, `negativa`, `neutra`) e identificadores distintos. Esses campos apenas registram anotações: não provam que as revisões foram realmente independentes.

Os 27 pares da partição `avaliacao` do conjunto candidato inicial continuam reservados. A implementação rejeita resultados com pares não aprovados, com partição diferente de `desenvolvimento`, duplicatas e arquivos cuja origem difira pelo SHA-256. Nenhum resultado da avaliação final será produzido.

## 2. Fluxo e proveniência

1. Reunir duas fichas humanas independentes, obtidas sem consultar o classificador.
2. Consolidar anotações usando `backend.revisao_humana consolidar`, inspecionar discordâncias e encaminhar para adjudicação humana. Não preencher aprovações automaticamente.
3. Executar o piloto com `python -m backend.pares_piloto --entrada ... --piloto --saida ...`. Esse comando é o responsável pelas classificações exploratórias nos dados de desenvolvimento.
4. Executar `backend.metricas_exploratorias calcular` informando **o mesmo CSV revisado** e o JSON do piloto. Não alterar manualmente os resultados entre etapas.
5. Guardar o CSV e os relatórios JSON/CSV em `data/piloto/restrito/`, fora do GitHub, com versões imutáveis e hashes registráveis.

Antes de haver pares humanos aprovados, `backend.metricas_exploratorias verificar` informa somente o estado de prontidão, sem calcular pontuações.

## 3. Denominadores e definições

Para um léxico, seja `N` o número de pares de desenvolvimento aprovados. Existem `2N` frases. Uma frase é *pontuada* somente se o baseline retorna `PONTUACAO_EXPLORATORIA_NAO_VALIDADA`.

- `frases_pontuadas`: contagem de frases cuja pontuação foi produzida, entre `2N`.
- `taxa_abstencao_ou_sem_cobertura_frases`: `(2N - frases_pontuadas)/(2N)`. Agrega abstenções e ausência de cobertura; o relatório também preserva contagens por status para análise separada.
- `pares_ambos_pontuados`: pares em que as duas frases possuem pontuação. Diferença de pontuação e divergência de classe são **indefinidas** nos demais pares.
- `taxa_pares_ambos_pontuados`: pares com as duas frases pontuadas divididos por `N`.
- `cobertura_superficial_media`: média aritmética da proporção de tokens reconhecidos **por frase**, calculada incluindo frases que terminaram em abstenção. Não é cobertura global ponderada pelo número total de tokens.
- `delta`: pontuação feminina menos pontuação masculina para um par pontuado de ambos os lados.
- `delta_assinado_medio_pares_pontuados`: média de `delta` apenas nos pares pontuáveis em ambos os lados.
- `delta_absoluto_medio_pares_pontuados`: média de `|delta|` apenas nesses pares.
- `taxa_classes_divergentes_pares_pontuados`: fração dos pares pontuados dos dois lados com classes diferentes.
- `direcao_delta_pares_pontuados`: contagens de delta positivo, negativo e zero, sem inferência de viés.
- `acuracia_seletiva`: previsões corretas divididas por **frases pontuadas**; frases abstidas não entram nesse denominador.
- `f1_macro_seletivo`: média do F1 por classe presente na união dos rótulos de referência e das previsões pontuadas; as classes efetivamente usadas ficam registradas.

Se não há pares pontuados ou frases pontuadas, a métrica correspondente será `null`, **nunca 0 por conveniência**. Escores de qualidade são condicionados a um subconjunto selecionado pelo modelo; **não representam acurácia no conjunto completo**. Os pares compartilham família e não são necessariamente observações independentes.

## 4. Controles automáticos

O módulo:
- exige identidade de hashes entre dataset revisado e piloto;
- bloqueia anotações na parte reservada;
- verifica todos os resultados esperados dos dois léxicos, sem registros extras nem repetidos;
- rejeita pontuação/classe numérica em abstenções;
- verifica `delta` e classe coerentes com as pontuações;
- valida intervalos de cobertura entre zero e um;
- não sobrescreve resultados anteriores;
- não inclui textos de frases ou pares da avaliação final no CSV de métricas.

## 5. Limitações e próximos estudos

O baseline aditivo v0.1 permanece sem resolução completa de contexto, alvos sintáticos, ironia e ambiguidades. Atribuir N0/N1 manualmente não equivale a inferi-los da sentença. O tratamento de negação está limitado a abstenção conservadora. Esta etapa não calcula intervalo de confiança, significância, tamanho de efeito inferencial, conclusões de equidade nem resultados da avaliação final. Tais análises exigem protocolo congelado, volume apropriado de **famílias independentes**, validação linguística e revisão humana completa.
