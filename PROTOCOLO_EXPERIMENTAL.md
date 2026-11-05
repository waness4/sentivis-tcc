# Protocolo experimental v1.0 — Sentivis

**Status:** planejamento. Nenhuma medição científica foi executada nesta entrega.

## Questão central
Em que medida substituições controladas de referências masculinas/femininas modificam as pontuações e classificações de sistemas de análise de sentimentos baseados em SentiLex-PT02 e OpLexicon 3.0, e uma mitigação lexical preservadora de sentido reduz essas diferenças sem piorar a qualidade das classificações?

## Unidade experimental
Um par de frases semanticamente equivalentes, com mudança de referência de gênero e flexões gramaticais exigidas. Registrar família/molde, contexto, polaridade de referência, mudanças realizadas e revisão humana. Não confundir flexões e erros de cobertura com evidência conclusiva de discriminação social.

## Bases e origem
Léxicos: SentiLex-PT02 e OpLexicon 3.0. Preferir originais oficiais; se usada representação do pacote R lexiconPT, registrar a transformação de diacríticos, filtro de entradas e interpretação do alvo N0/N1. Registrar URL, data, versão, licença do recurso, hash SHA-256 e contagem após importação. **GPL-2 do pacote não substitui a verificação das licenças dos léxicos.**

## Desenho de dados proposto
Meta inicial: 240 pares / 480 frases, estratificados 80 positivos, 80 negativos e 80 neutros. Esse número é meta logística e **não** cálculo de poder estatístico. O piloto pode justificar revisão de tamanho antes da análise confirmatória. Preparar pares por famílias de moldes e variedades lexicais, com validação humana independente; divergências resolvidas antes de executar os modelos. Evitar vazamento de famílias de frases entre desenvolvimento e avaliação final. Separar, em princípio, 25% das famílias para desenvolvimento e 75% para avaliação, adaptando ao total de famílias disponíveis.

## Sistema de classificação: especificação pendente de congelamento
Pré-processamento Unicode NFC, letras minúsculas preservando acentos; tokenização explícita; regras documentadas para variantes morfológicas, expressões compostas, negação e intensificação; regras da polaridade-alvo do SentiLex precisam de decisão fundamentada. Um termo ausente não é neutro; sem correspondências, a resposta é *sem cobertura*. O protótipo nesta pasta usa **apenas somatório simples para teste de engenharia** e não é o classificador científico validado.

## Métricas a registrar por léxico
- Cobertura: frases com alguma entrada reconhecida e termos reconhecidos/totais; separar ausência de neutralidade.
- Viés observado: diferença feminina-masculina com sinal, diferença absoluta, taxa de discordância das classes, direção das diferenças.
- Qualidade: acurácia e F1-macro contra rótulos revisados, com política explícita para abstenções/sem cobertura; reportar também fração de abstenção.
- Incerteza: intervalo de confiança calculado por reamostragem de famílias; inferência pareada com método justificado para dados discretos e muitos zeros. Se houver testes de múltiplas hipóteses, explicitar o ajuste (ex.: Holm). Não tratar p-valor isoladamente como prova de equidade.

## Mitigação (candidata)
Consulta complementar a lemas/flexões de gênero equivalentes **validadas e pré-especificadas** para casos de ausência de entrada. Não usar rótulos ou resultados do conjunto final de teste para projetar correções. Comparar baseline vs. mitigado nos mesmos pares, reportando viés, cobertura, qualidade e casos de degradação. Caso não haja melhoria, declarar o resultado.

## Critérios de saída do bloco 1
[ ] Origem e licença dos dois léxicos confirmadas.
[ ] Arquivos obtidos, íntegros e versões fixadas.
[ ] Estrutura e chaves dos léxicos auditadas (duplicatas, alvos, acentuação, polaridades).
[ ] Protocolo aprovado para congelamento após piloto (sem ajustes olhando dados finais).
[ ] Ambiente de projeto executa os testes de engenharia.

## Referências de base
- Kiritchenko; Mohammad (2018), https://aclanthology.org/S18-2005/
- PUCRS OpLexicon, https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/oplexicon/
- Manual lexiconPT, https://search.r-project.org/CRAN/refmans/lexiconPT/html/00Index.html
- Código da preparação lexiconPT, https://rdrr.io/github/sillasgonzaga/lexiconPT/src/data-raw/setup.R
