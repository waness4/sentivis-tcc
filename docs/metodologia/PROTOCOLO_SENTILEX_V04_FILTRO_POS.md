# SentiVis — protocolo exploratório V04 (filtro de correspondência neutra incompatível)

**Fase:** desenvolvimento, sem inferência estatística ou evidência de viés.

## Motivação e exemplo

Nos controles C005 e C006, `dados` foi identificado pelo SentiLex como adjetivo com polaridade N0=0, enquanto o etiquetador o analisou como substantivo. A expressão `com segurança` / `com arrogância` permanece candidata lexicalmente consistente, mas é analisada como `nmod` anexado a `dados`. Na V03, o erro de PoS em `dados` encerra a análise antes de reportar a ambiguidade de anexação.

## Regra pré-definida V04

1. Executar a V03 sem qualquer alteração e registrar o resultado original.
2. Somente se a V03 se absteve **por categoria gramatical**, avaliar as ocorrências registradas.
3. Permitir desconsiderar uma ocorrência cuja **polaridade lexical é exatamente zero**, cuja categoria difere da PoS prevista pelo etiquetador e que não apresenta outros erros. Exigir pelo menos uma ocorrência válida restante. Esta é uma filtragem da evidência lexical, **não** uma interpretação da frase como neutra.
4. Não filtrar candidatos com polaridade diferente de zero, categoria desconhecida, múltipla ou análise inconclusiva; manter abstenção.
5. Se qualquer ocorrência restante for `nmod` associada a `com`, registrar `ABSTENCAO_ANEXACAO_AMBIGUA`; não inferir que o modificador se refere ao verbo.
6. Se houver exatamente um candidato `NOUN` + `com` + `obl` de verbo, gerar **hipótese** de pontuação apenas mediante seleção explícita de `--alvo N0|N1` e `--hipotese-modo`; caso contrário, abster-se. Essa hipótese **não identifica automaticamente modo, companhia, instrumento nem alvo**.
7. Preservar bloqueios anteriores por ausência de cobertura, conflito lexical, negação, modificadores sem escopo, alvo ausente e falha de alinhamento.

## Predições e limites esperados

- C005 e C006: **ainda sem pontuação**, mas o motivo principal pode passar de `ABSTENCAO_CATEGORIA_GRAMATICAL` para `ABSTENCAO_ANEXACAO_AMBIGUA`; `dados` fica registrado como candidato filtrado.
- P007: `com habilidade` continua ambíguo; não pontuar automaticamente.
- A filtragem pode alterar algumas outras decisões sintéticas, mas **não** constitui prova de ganho de acurácia. Antes de comparações quantitativas, registrar a taxa de pontuação e o custo das abstenções. Nenhum dado da partição de avaliação final foi usado para selecionar essas regras.
- A PoS do spaCy é predita e pode estar errada. `nmod` e `obl` não resolvem semântica. O alvo N0/N1 permanece informado manualmente. Rótulos humanos dos controles ainda não foram obtidos; portanto, não calcular acurácia/F1 para eles.

## Reprodutibilidade

Código: `backend/baseline_contextual_v04.py` (separado das versões anteriores).

Teste: `backend/tests/test_baseline_contextual_v04.py` com etiquetas sintéticas para correspondência, abstenção, hipótese autorizada, preservação de bloqueios e não regressão da V03.

Dependências operacionais já usadas na V03: `spacy` e `pt_core_news_sm`. Registrar a versão exata do modelo e dos léxicos em cada relatório. Arquivos de dados e resultados de desenvolvimento devem permanecer em `data/piloto/restrito/`, não enviados ao repositório público.

**Natureza da mudança:** refinamento de explicabilidade e filtragem conservadora de candidatos, sem validação linguística externa, sem acesso a pares da avaliação final e sem demonstração de viés.
