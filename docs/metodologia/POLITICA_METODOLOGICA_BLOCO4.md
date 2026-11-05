# SentiVis — Política de consulta lexical v0.1 (pré-piloto)

**Estado:** engenharia verificável, sem validade de classificador científico. Esta política só autoriza inspeção de registros; não autoriza pontuações de frases, comparação de gênero ou inferência de discriminação.

## Evidências auditadas

Entrada: `relatorio_curadoria.json` e `pendencias_curadoria.csv` de 05/11/2026.

- Registros: 121.552 (32.191 OpLexicon, 7.014 SentiLex lemas e 82.347 SentiLex flexões).
- Registros sinalizados: 9.494; 112.058 sem sinalização **não** são automaticamente validados.
- Por motivo (sobreposições): 4.568 atributos sem chave; 4.529 formas com múltiplos lemas; 3.949 registros envolvidos em divergências de polaridade do mesmo alvo; 13 registros com polaridade fora de -1/0/+1.
- 2.003 grupos conflitantes por origem, forma normalizada, categoria e alvo; não são necessariamente 2.003 erros de origem.
- Exemplo: `aborreça` pertence a `aborrecer` (N0=1; N1=-1) e `aborrecer-se` (N0=-1); só uma análise contextual e sintática poderia escolher a leitura.
- Exemplo: `:p` e `:P` não podem ser unidos por `casefold()` porque aparecem com valores distintos em OpLexicon. O índice de emoticons deve preservar maiúsculas/minúsculas.
- Os códigos de flexão verbal como `P2s|P4s|P3s|Y2s` existem na distribuição. Devem ser preservados e permanecer pendentes até interpretação morfológica documentada.

## Regras da consulta conservadora

1. Preservar cada registro com arquivo, número da linha, categoria, lema, `FLEX`, `TG`, `POL`, `ANOT` e atributos ainda não interpretados.
2. Verificar SHA-256 dos arquivos locais contra a curadoria antes de consultar; não usar dados cuja integridade difira.
3. No SentiLex, consultar primeiro o arquivo flexionado; recorrer ao de lemas somente se a forma não existir no primeiro. Não somar duas vezes a mesma ocorrência.
4. Diferenciar `N0` e `N1`. Sem identificação do alvo, fornecer os registros, mas sem polaridade de consulta. Uma consulta explicitamente marcada como N0/N1 **não comprova** que essa seja a função sintática no texto real.
5. Não resolver conflitos por média, primeiro registro, maioria ou prioridade de anotação sem validação. Polaridades fora do padrão, lema/categoria ambíguos, divergência no mesmo alvo, metadado não padronizado ou incompatibilidade de alvo bloqueiam valor único.
6. Ausência de termo/alvo significa **sem correspondência**, nunca neutralidade (0).
7. Preservar diferenças de caixa em emoticons; nas demais categorias aplicar NFC + `casefold()` apenas como chave de busca, mantendo o registro original.
8. Não executar análise de frases com essa consulta: ela é um diagnóstico lexical isolado, não um analisador de dependências, composição, negação ou ironia.

## Etapas de validação antes de congelar o classificador

1. Verificar as políticas de redistribuição e a versão oficial de ambas as bases; registrar a procedência da cópia do OpLexicon.
2. Analisar os metadados morfológicos de frases idiomáticas e verbos, incluindo variantes de `Flex=` e fragmentos que não seguem `CHAVE=VALOR`.
3. Definir e testar a identificação sintática de N0/N1 com exemplos anotados independentemente.
4. Especificar tokenização inclusiva para pontuação/emoticons, reconhecimento de expressões compostas, negação, intensificadores e resolução de conflitos.
5. Construir piloto de pares contrafactuais humanos, separar famílias de treino/validação/teste antes dos resultados, congelar regras e só depois medir cobertura, F1, diferenças de pontuação e incerteza.

## Referências técnicas

- SentiLex-PT02: https://b2share.eudat.eu/records/cbyr7-dkf18
- OpLexicon 3.0: https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/oplexicon/
- Dados auditados: `relatorio_curadoria.json` e `pendencias_curadoria.csv` (hashes nos relatórios).

**Não redistribuir os léxicos dentro deste pacote.**
