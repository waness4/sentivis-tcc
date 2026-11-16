# Protocolo: Interface demonstrativa com V01 e V04 — Bloco 22

## Escopo

Integração demonstrativa do método exploratório aditivo V01 e do método contextual SentiLex V04 em rotas já existentes da API (`POST /api/ui/analisar` e `POST /api/ui/comparar`). O parâmetro `metodo` aceita `aditivo_v01` (padrão) e `contextual_v04`.

A interface V04 exige simultaneamente: `lexico=sentilex`, `alvo=N0` ou `N1` **informado pelo usuário**, e `hipotese_modo=true` **explicitamente ativado pelo usuário**. Parâmetros incompatíveis retornam HTTP 422. Falha ao carregar o modelo sintático retorna HTTP 503. O etiquetador é carregado apenas no uso da V04.

## Interpretação científica

- O método V01 permanece inalterado e continua sendo o padrão para ambos os léxicos.
- V04 é hipótese sintática: spaCy atribui categorias e dependências gramaticais estimadas; não valida papéis semânticos, referentes N0/N1 nem o significado de construções com `com`.
- A interface apresenta status de abstenção, termos identificados, checagens sintáticas, itens neutros descartados, versão de etiquetador, hashes de fontes lexicais e avisos de limitação.
- Pontuação ausente continua `null`: jamais convertê-la em zero ou em ausência de viés. Diferença numérica só é apresentada se os dois lados foram pontuados; não é métrica de viés.
- O resultado de 36 controles já examinados no desenvolvimento foi V03=1/36 e V04=1/36 classificados, com duas mudanças de status (C005, C006). Não usar como prova de generalização.
- Os 27 pares reservados não são consultados, importados ou exibidos; nenhuma ficha humana é exposta por novos endpoints.
- A frase C001 foi usada como exemplo nas orientações de anotação anteriores; se entregue aos avaliadores, registrar sua exposição ao interpretar concordância humana.

## Ensaios

Executar `python -m pytest .\backend\tests -q`. Testes específicos usam índices lexicais e etiquetadores sintéticos; não simulam validação científica. Na preparação local do pacote, 317 testes foram aprovados e o JavaScript passou pela checagem sintática (`node --check`). A integração final precisa ser observada no navegador e com os léxicos presentes na máquina de execução.
