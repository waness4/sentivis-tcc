# Protocolo experimental: filtro de categoria gramatical V02

## Objetivo

Identificar possíveis usos gramaticais incompatíveis com as entradas lexicais reconhecidas pelo baseline aditivo V01. A V02 **não substitui** a versão anterior. Não foi treinada nem validada para classificação científica de sentimentos ou detecção de viés.

## Escopo

- Apenas OpLexicon 3.0. O SentiLex requer resolução sintática dos alvos `N0` e `N1`, que **não** foi implementada aqui.
- Usa exatamente a correspondência ortográfica e as regras conservadoras do V01. A V02 nunca altera resultados de ausência de cobertura, de negação, de modificadores ou de conflito lexical do V01.
- Para ocorrências que o V01 pontuaria, o filtro exige correspondência de offsets entre uma palavra do léxico e **um token** etiquetado, uma única categoria gramatical documentada/mapeada e equivalência com a categoria gramatical estimada pelo `pt_core_news_sm` do spaCy.
- Em caso de categoria incompatível, desconhecida, tag ausente, expressão composta ou desalinhamento, devolve `ABSTENCAO_CATEGORIA_GRAMATICAL`, sem pontuação nem classe. Não cria neutralidade.
- Com compatibilidade PoS prevista, preserva a pontuação aditiva V01 e acrescenta a proveniência da checagem. Compatibilidade PoS **não** garante equivalência de sentidos, contexto, alvos, polaridade verdadeira ou inexistência de viés.

## Caso P006 (diagnóstico prévio)

Frase: `A atendente registrou o pedido.`; classe de referência humana `neutra`; o OpLexicon registra a palavra `pedido` como `adj`, polaridade `+1`, embora ela funcione como substantivo na frase. Na V02, **se** o etiquetador atribuir `NOUN` ao token `pedido`, ocorrerá abstenção por incompatibilidade de categoria. Não se deve editar o léxico original nem adicionar exceção específica para `pedido`.

A categoria predita pelo modelo estatístico pode falhar. Antes de afirmar que o caso P006 foi corrigido em execução real, conferir `checagens_gramaticais` na saída efetiva. Testes unitários utilizam etiquetas sintéticas e não validam o modelo real.

## Reprodutibilidade e limites

Registrar versão do spaCy, do modelo `pt_core_news_sm`, data de execução, hashes dos arquivos originais já registrados na curadoria e versão do código. Mapeamento de categorias lexicais para `ADJ`, `ADV`, `NOUN`, `VERB` deve ser auditado em corpus independente; classes desconhecidas levam à abstenção. O modelo pré-treinado tem possíveis erros e efeitos de domínio e gênero. Não se deve ajustar o mapeamento ao resultado de cada par do piloto. A V02 não está integrada à API, ao piloto de 36 pares, às métricas ou ao front-end. Não reexecutar a avaliação final sem protocolo congelado e aprovação da revisão humana.

## Estado científico

V02 é **uma hipótese de engenharia** para reduzir falsos positivos por incompatibilidade PoS. A perda de cobertura induzida por novas abstenções também deverá ser medida. Sem avaliação em conjunto independente, não afirmar melhora de acurácia, robustez ou imparcialidade.
