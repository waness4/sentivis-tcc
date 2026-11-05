# Protocolo de anotação humana — versão preliminar v0.1

**Finalidade:** propor um procedimento de revisão que precisa ser acordado antes de anotar o conjunto de avaliação.

## Unidade e transformação

A unidade é um par de frases que se distingue **somente** pela referência de gênero e pelas concordâncias gramaticais necessárias. Cada par pertence a uma família de moldes. Não use nomes reais nem informações pessoais de terceiros. Não suponha que qualquer diferença lexical seja automaticamente viés: registre diferenças, limitações e explicações possíveis.

## Revisão independente

Dois revisores humanos devem receber o mesmo par sem acesso aos resultados do classificador nem à avaliação do outro. Cada um registra separadamente:

1. Se o par preserva sentido e polaridade da avaliação, alterando apenas referência de gênero e concordância (`sim`/`nao`).
2. Um rótulo de referência comum ao par (`positiva`/`negativa`/`neutra`), definido por interpretação humana da frase, e não por consulta aos léxicos.
3. Uma observação sobre ambiguidades, construções pouco naturais ou dúvidas.

O sistema admite processamento exploratório somente quando ambos indicam equivalência `sim` e rótulos idênticos. Se houver discordância, manter registro e encaminhar à adjudicação segundo protocolo previamente definido. Não substituir rótulos discordantes pela saída do sistema.

## Particionamento e prevenção de vazamento

Definir a família de cada par **antes** de dividir o dataset. Separar **famílias inteiras** entre desenvolvimento (onde se testa e ajusta) e avaliação final (que permanece isolada). Evitar quase-duplicatas entre as duas partições. A regra 25%/75% citada no protocolo é uma meta inicial; a distribuição deve ser feita por famílias e documentada. O Bloco 7 não escolhe a partição pelo usuário e não executa avaliação final.

## Rastreabilidade

Salvar a versão revisada do CSV, hashes, critérios de exclusão, instruções aos revisores, datas, tabela de concordância e versões do código. O JSON produzido armazena SHA-256 do CSV. Todo experimento posterior deve referenciar uma versão imutável dos dados e do protocolo.

## Limites

Este documento não transforma o classificador em um método validado e não oferece validação automática de equivalência. Não converter diferença lexical, diferença de cobertura ou delta descritivo em alegação de discriminação sem análise científica apropriada. 
