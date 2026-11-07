# SentiVis — Protocolo de controles sintáticos V03 (Bloco 18)

**Estado:** diagnóstico de robustez exploratório, **não** validação científica, externa ou inferência sobre viés de gênero.

## Objetivo

Verificar como a mesma implementação já existente de SentiLex V01 (com alvo N0 manual) e V03 (com hipótese sintática explicitamente ativada) reage a **36 frases de controle inéditas em relação aos nove pares usados no desenvolvimento**. Não modificar os classificadores durante este bloco.

## Definição dos dados

Arquivo versionado: `data/controles/controles_sintaticos_v01.csv`.

Colunas estritas: `id_controle;cenario;texto`, sem sexo de comparação, sem partição de avaliação e sem rótulos humanos. O conjunto é fixado pelo SHA-256 presente no código e verificado antes de carregar os léxicos.

Os controles foram **criados após a implementação e análise do baseline V03**. Por isso, são adequados para sondar generalização aparente, robustez e falhas novas, mas **não** são independentes do conhecimento dos desenvolvedores nem estimam desempenho populacional. Não reutilizam os 27 pares reservados do projeto.

Seis grupos de situações (não correspondem a classes de sentimento):

| Cenário | N | Questão diagnóstica |
|---|---:|---|
| `modo_potencial` | 12 | construções com `com + substantivo` passíveis de leitura de modo |
| `objeto_e_adjunto` | 6 | potencial concorrência entre objeto e sintagma preposicional |
| `avaliacao_sem_com` | 6 | expressões avaliativas e descrições sem a construção escolhida pela V03 |
| `companhia_instrumento` | 4 | preposição `com` em leituras não necessariamente avaliativas |
| `negacao_modificacao` | 4 | ausência de tratamento validado de escopo/intensificação |
| `construcoes_complexas` | 4 | mais de uma pista sintática ou discursiva |
| **Total** | **36** | |

## Procedimento pré-definido

1. Registrar checksum e verificar integridade das três colunas; **não** ler arquivos do piloto.
2. Carregar SentiLex original por `carregar_para_consulta` e o mesmo modelo `pt_core_news_sm` instalado.
3. Para cada controle, rodar V01 com **N0 manual** e V03 com **N0 manual + `hipotese_modo=True`**.
4. Registrar por texto: status, pontuação quando permitida, classe exploratória, termos usados, motivos de abstenção e transição V01→V03.
5. Resumir por cenário: número de frases pontuadas e não pontuadas e motivos/status; registrar versões dos métodos, modelo, manifesto dos léxicos e checksum do conjunto.
6. **Não calcular acurácia, F1, intervalos de confiança ou diferença de gênero**, pois não há referência humana e não se trata de pares contrafactuais equivalentes validados.
7. Se houver necessidade de modificar V03 após observar os resultados, declarar os controles usados como **dados adicionais de desenvolvimento**. Não reivindicar validação independente ou comparar uma V04 ajustada aos mesmos controles como avaliação final.

## Riscos e limites

- `N0` é selecionado manualmente para todos os textos: não representa resolução automática do alvo semântico.
- A regra `NOUN` ligado a `VERB` por `obl` é apenas uma pista. Também pode capturar companhia, instrumento, meio ou outras interpretações.
- O parser spaCy pode discordar da análise gramatical humana; algumas palavras podem nem constar nos recursos lexicais.
- A diferença entre `status` pode expressar somente maior cautela, não melhor previsão.
- **Zero previsões incorretas** não pode ser afirmado sem rótulos independentes.
- Os resultados são diagnósticos; os 27 pares de avaliação final permanecem isolados para uma futura aplicação de protocolo pré-fixado.

## Para eventual validação humana subsequente

Entregar somente frases (sem as pontuações do SentiLex), a pessoas independentes, com instruções para julgar polaridade, referente e papel da expressão `com`. Antes de calcular qualidade, definir concordância, adjudicação e separação entre conjuntos. O desenho dessa validação é uma etapa futura, **não realizada** neste bloco.
