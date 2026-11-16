# Bloco 29 — Protocolo de ensaio sintético da futura avaliação

**Situação:** implementado apenas para dados fictícios; o protocolo final continua **NÃO CONGELADO**.

## Escopo de segurança

O comando `python -m backend.avaliacao_final_preparacao_bloco29 simular` constrói em memória quatro pares `SINT001`–`SINT004`, sem recuperar dados do piloto, da revisão R01 ou dos 27 pares reservados. O índice lexical contém apenas as entradas fictícias `gentileza` (+1) e `grosseria` (−1), e o etiquetador `_EtiquetadorFicticio` não é spaCy. Os baselines V01, V03 e V04 do projeto são executados sobre as frases inventadas, sem consultar os recursos lexicais originais. Um par propositalmente não equivalente demonstra exclusão prévia das métricas de pares elegíveis.

**Atenção:** palavras e frases artificiais semelhantes aos exemplos gerais de documentação não são registros da partição reservada. A similaridade não configura validação da gramática do português ou dos recursos originais.

Não há CLI de processamento da avaliação reservada, nem parâmetro que aceite seus arquivos, nem gravação de saída privada. O módulo não exporta fichas de anotação final.

## Contratos verificados

- Ficha de anotador único com seis colunas exatas, IDs únicos, correspondência textual integral; não equivalência exige observação e não admite rótulo. Rótulo `neutra` é permitido como estrato separado, não entra na coincidência primária positiva/negativa.
- Toda frase deve ter uma decisão em V01, V03 e V04. Resultado pontuado exige inteiro e classe coerente com o sinal; resultado abstido exige `pontuacao=None` e `classe=None`.
- Contagem global inclui pares não elegíveis; contagem elegível usa somente `equivalencia=sim` e rótulo admissível.
- Coincidência nominal individual é calculada apenas sobre frases **pontuadas** com rótulo humano `positiva`/`negativa`. Denominador zero vira `null` (não calculável).
- Delta feminino − masculino é calculável somente para pares elegíveis em que **as duas frases receberam pontuação** no mesmo baseline. Abstenção nunca é delta zero; neutralidade humana não é zero lexical.
- Relatório agregado da simulação não reproduz frases ou observações e marca `acuracia_validada`, `concordancia_interavaliadores`, `evidencia_de_vies` e `inferencia_estatistica` como `null`.

## Limitações e decisões ainda necessárias

1. Testar o adaptador real **apenas com novos dados fictícios** antes do congelamento; preservar checksums, commits, versões Python/spaCy, versão dos léxicos e protocolo.
2. Definir o processo de autorização e extração isolada da partição reservada (ainda não implementado), sem incorporar IDs e exemplos reais nos testes.
3. Definir geração da ficha cega e validação de respostas R01 sem exposição a previsões automáticas; preservar ficha original e hash antes da execução.
4. Implementar bloqueio explícito por aprovação formal do pré-registro, commit e manifestos; impedir sobrescrita ou nova execução confundida com teste independente.
5. Revisar, aprovar e datar regras de exclusão, anotação individual, tratamento de abstenções, denominadores e forma de relato; manter avaliação final sem classificação até lá.

A execução da simulação é **engenharia de teste**, não evidência de acerto, precisão, viés ou ausência de viés.
