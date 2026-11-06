# SentiVis — Protocolo de comparação descritiva V01 x V02 (Bloco 15)

## Objetivo

Medir o efeito do filtro de categoria gramatical (PoS) aplicado ao baseline lexical aditivo do OpLexicon 3.0, sem confundir redução de previsões erradas com capacidade de classificação ou evidência de viés de gênero.

## Dados e seleção

Fonte: CSV consolidado da revisão humana V02, com hash SHA-256 gravado no JSON de saída. O programa chama a validação estrutural já existente e seleciona exclusivamente linhas cuja `particao` é `desenvolvimento` e cujo `status_revisao` é `APROVADO_DUPLA_REVISAO`. A partição `avaliacao` é lida somente para a auditoria estrutural já existente; suas frases não são submetidas aos baselines e não aparecem nos resultados.

Os dois baselines analisam exatamente as mesmas frases, em ordem fixa. As anotações humanas são o rótulo de referência descritivo, ainda sujeito às limitações de independência da revisão.

## Modelos

- V01: `baseline_aditivo_exploratorio_v0.1`, usando OpLexicon e correspondência lexical ortográfica.
- V02: `baseline_aditivo_filtro_pos_v0.2_experimental`, que primeiro roda V01 e então examina categoria prevista pelo spaCy (`pt_core_news_sm`) para termos pontuados. Se a categoria for incompatível ou não puder ser avaliada com segurança, abstém-se.
- N0/N1 do SentiLex não é tratado aqui, portanto **não é correto comparar V02 com o SentiLex**.

## Métricas, denominadores e mudanças

Cada par possui duas frases. Para cada versão:

- `frases_pontuadas` e `frases_abstidas`, em relação ao total de frases de desenvolvimento aceitas;
- `previsoes_corretas` e `previsoes_incorretas` **somente entre as pontuadas**;
- `acuracia_seletiva = previsoes_corretas / frases_pontuadas`, ou `null` se não houver previsões;
- `pares_ambos_pontuados` e `pares_classes_divergentes` **somente nos pares com ambas pontuadas**.

Na comparação pareada, registrar transições (`pontuacao_preservada`, `pontuacao_para_abstencao`, `abstencao_preservada`) e discriminar previsões incorretas que passaram a abstenção das previsões corretas perdidas por abstenção.

Uma diminuição de previsões incorretas provocada por mais abstenções **não deve ser apresentada como melhoria de acurácia geral**. O filtro não introduz previsões novas e não converte abstenção em neutralidade. Se a V02 não pontuar frases, sua acurácia seletiva é indefinida, não 0% nem 100%.

## Limitações e reprodutibilidade

Gravar SHA do CSV, método, versão dos baselines, manifesto lexical e versões de spaCy/modelo. Os arquivos de saída são privados e não devem integrar o GitHub. Não alterar o V01 nem as anotações humanas. Testes com etiquetas gramaticais simuladas verificam engenharia, **não a acurácia real do spaCy**. O estudo permanece exploratório, descritivo, sem intervalos de confiança, inferência estatística ou conclusão sobre viés de gênero.

Se correções futuras usarem o mesmo desenvolvimento, documentar as escolhas e reservar os pares de `avaliacao` para uma única avaliação conforme protocolo pré-definido; não ajustar regras depois de examiná-los.
