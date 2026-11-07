# SentiVis — Protocolo da comparação descritiva SentiLex V03 × V04 (Bloco 20)

## Objetivo e hipótese

Examinar a **mudança de decisões** entre os baselines contextuais V03 e V04 no conjunto fixado de 36 controles sintáticos, sem alterar nenhum baseline. A V04 filtra apenas ocorrências de polaridade lexical zero com categoria gramatical incompatível; isso **pode** mudar a razão da abstenção sem permitir pontuação da frase. Não há compromisso de aumento de cobertura.

## Entradas e isolamento

- Corpus: `data/controles/controles_sintaticos_v01.csv`, 36 frases sem rótulo, SHA-256 `a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc`.
- A leitura aplica verificação exata de SHA-256, separador `;` e esquema de três colunas `id_controle;cenario;texto`; não aceita fichas ou pares do piloto.
- Os 27 pares de avaliação final **não são lidos**; tampouco as nove linhas de desenvolvimento revisadas.
- Léxico: SentiLex-PT02 originais já instalados localmente. Alvo `N0` (ou `N1`) **manual**, idêntico nas duas versões e não validado semanticamente. A flag `--hipotese-modo` é obrigatória.
- Etiquetador: spaCy `pt_core_news_sm`, versão registrada na saída.
- As regras V03 e V04 e dados lexicais não são modificados.

## Métricas descritivas

Para cada versão e cenário: número de frases pontuadas, sem pontuação, distribuição por status e motivos de abstenção. Por frase: status, classe/pontuação quando existentes, candidatos usados, candidatos neutros descartados e transição V03→V04. Adicionalmente: número de frases com filtragem aplicada, ocorrências neutras descartadas e status alterados. Usar transições para verificar se a mudança de status **de fato** permite mais pontuação ou apenas melhora a rastreabilidade.

## Proibições e limitações

- Sem rótulos humanos para estes controles: **não** calcular acurácia, F1, erros, ganho de qualidade, significância ou evidência de viés.
- Estes 36 controles já foram inspecionados durante a criação da V04: são **controles diagnósticos** e não um teste de generalização independente.
- Um novo status de abstenção não é uma previsão correta. Pontuação lexical não demonstra referente resolvido ou papel semântico validado.
- Não publicar relatórios ou fichas privados; manter as saídas em `data/piloto/restrito/`.
- `ler_controles` é usado para exigir a entrada pré-fixada; não abrir o arquivo da avaliação final.

## Reprodutibilidade e interpretação

Manter CSV/JSON com nome versionado sem sobrescrever, hash do conjunto de controles, manifestos dos léxicos e versão do etiquetador. Interpretar diferenças caso a caso e planejar uma avaliação humana **independente e pré-registrada** somente após congelar a versão final. Os testes de software não equivalem à validade empírica.
