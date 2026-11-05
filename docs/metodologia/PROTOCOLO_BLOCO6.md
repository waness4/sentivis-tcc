# Protocolo de engenharia do baseline v0.1 — NÃO validado para pesquisa

**Objetivo**: detectar falhas de ponta a ponta, estabelecer política operacional de abstenção e deixar explícitos os pressupostos do somatório. Não produz inferência estatística ou medida de viés.

**Entradas**: fontes locais verificadas por SHA-256 na curadoria, índice do Bloco 5, consulta lexical do Bloco 4. Nenhum léxico é reescrito.

**Pareamento**: os rótulos `feminina` e `masculina` são nomes das entradas informadas pelo usuário, não uma classificação automática do texto. Delta exploratório `pontuação_feminina - pontuação_masculina` somente quando ambos os textos forem pontuáveis. O programa **não valida** equivalência semântica. Não interpretar delta zero como ausência de viés nem delta diferente de zero como discriminação.

**Abstenções**: ausência de entradas; alvo não informado; conflitos lexicais e metadados pendentes; negação e modificadores listados. Em abstenção, classe e pontuação são `null`. Faltas de cobertura são reportadas independentemente; termos ausentes nunca recebem zero implícito.

**Pontuação (se aplicável)**: `sum(polaridade_i)` para as expressões reconhecidas e não conflitantes; valores permitidos `{-1, 0, +1}`. Classes por sinal: positivo, negativo, neutro. O valor zero por soma pode significar cancelamento, indicado no campo `origem_soma_zero`.

**Limitações críticas**: Sem análise morfossintática, desambiguação contextual, detecção de ironia, construção de alvos, interpretação de negadores e intensificadores, validação de rótulos ou corpus final. Os limites impedem chamá-lo de classificador validado. Este código é base para testes exploratórios, não para os resultados finais do TCC.
