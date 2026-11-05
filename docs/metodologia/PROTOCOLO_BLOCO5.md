# Protocolo de diagnóstico lexical — SentiVis, Bloco 5

**Status**: engenharia e inspeção, não validação científica de sentimento ou viés.

## Unidade observável

A ocorrência ortográfica de uma forma lexical dentro de uma frase.

## Procedimento

1. Confere SHA-256 dos léxicos locais contra o relatório de curadoria existente (rotina herdada).
2. Indexa somente palavras com letras Unicode, hífen/apóstrofo e expressões com espaços.
3. Percorre a frase preservando deslocamentos dos caracteres; prioriza a expressão contígua mais longa.
4. Obtém todas as entradas lexicais para o trecho, com prioridade documental para `sentilex_flex` quando a forma está presente nas duas representações.
5. Propaga `revisao_necessaria`, `alvo_nao_informado` e demais bloqueios para a ocorrência.
6. Relata fração de tokens cobertos, sem converter polaridades lexicais em score da frase.

## Interpretação

`candidata_lexical_consistente` significa somente acordo entre registros consultados sob as regras do Bloco 4. **Não significa que o termo tenha o mesmo sentido na frase ou que a anotação original esteja validada.**

A diferença de cobertura feminina–masculina é um diagnóstico exploratório, sujeito a equivalência textual, gramática e cobertura desigual. **Não é estimativa de viés.**

## Pendências

- Formalizar segmentação de frases, pontuação, entidades e variantes da língua portuguesa.
- Escolher uma política justificada de semântica de alvos N0/N1.
- Estabelecer corpus piloto e dupla revisão humana independente com adjudicação.
- Implementar regras de negação, escopo, intensificação e construções com argumentos.
- Construir baseline classificador e testar contra rótulos independentes.
- Comparar versões com diferentes políticas, isolando taxa de abstenção.
