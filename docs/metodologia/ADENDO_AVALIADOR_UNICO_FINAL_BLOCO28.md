# SentiVis — Adendo ao pré-registro: um avaliador humano na partição final

**Bloco 28 | 16/11/2026 | PROPOSTA A APROVAR ANTES DE QUALQUER ACESSO À PARTIÇÃO FINAL**

Este documento complementa, **sem sobrescrever ou retroagir**, `PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md` e `ADENDO_ANOTADOR_UNICO_BLOCO27.md`. O Bloco 26 previa revisão dupla; apenas R01 devolveu a ficha dos 36 controles. A opção por anotador único é uma **modificação do desenho após a coleta de desenvolvimento**, anterior à avaliação final e deve ser apresentada como tal no TCC. A decisão não deve ser disfarçada como escolha metodológica pré-existente.

## 1. Finalidade e classificação do estudo

O objetivo da etapa futura é descrever o comportamento dos baselines lexicais numa partição reservada de **27 pares de referência de gênero**, em 9 famílias, mantendo a divisão por família e evitando ajuste posterior. Não será calculada concordância entre avaliadores, consenso, adjudicação, acurácia validada nem evidência causal/estatística de viés. Uma concordância descritiva com a marcação de uma pessoa pode ser informada com seu denominador, mas não substitui validação linguística independente.

O anotador da etapa final deve ser identificado por pseudônimo operacional; caso seja R01, declarar que também respondeu aos controles diagnósticos. A exposição anterior do controle C001 (se confirmada) deve ser documentada **nos controles**, sem atribuir contaminação dos 27 pares sem evidência. O histórico de instruções, treinamento, consulta a outros recursos e independência em relação às previsões precisa ser registrado.

## 2. Regra para o único anotador — antes de gerar resultados dos modelos

Após aprovação do pré-registro e preparação segura de uma ficha exclusiva da partição final, fornecer somente:
`id_par`, `frase_feminina`, `frase_masculina`, `equivalencia`, `rotulo`, `observacoes`.
Não mostrar `familia`, partição, classe planejada, rótulos de outros trabalhos, saídas dos baselines, candidatos lexicais ou justificativas automáticas.

Para cada par:
- `equivalencia=sim` somente se as duas frases conservarem conteúdo e avaliação afetiva equivalente, variando referência de gênero e concordâncias necessárias; `nao` em caso de diferença, dúvida relevante ou falta de equivalência demonstrável, com justificativa.
- `rotulo`: `positiva`, `negativa` ou `neutra` quando `equivalencia=sim` e houver um único julgamento comum sustentável. Quando `nao`, deixar vazio; registrar nas observações ambiguidades, ironia, diferença de sentido e problema de naturalidade.
- `neutra` significa ausência de orientação afetiva positiva ou negativa dominante no juízo do anotador; este rótulo **não comprova neutralidade lexical**, nem se equipara automaticamente ao zero do classificador. Se for descrição sem avaliação ou se o referente não puder ser decidido, usar observação explícita; esses itens ficam fora da comparação primária de rótulos, embora possam ser contados e discutidos.
- Manter texto e IDs sem alterações. Não recorrer à saída automática, ao léxico nem a ajustes orientados pelo modelo. Não solicitar que o anotador corrija respostas depois de ver as previsões.

O arquivo da ficha deve ser preservado como recebido, com SHA-256 e data de entrega. Caso falte resposta, erro ou dúvida, registrar caso não elegível ou incompleto seguindo regras pré-definidas; não inventar respostas, substituí-las por labels de construção ou completar por heurística.

## 3. Elegibilidade, contagens e ausência de desempate

- `equivalencia=sim` e `rotulo` admissível: par humano elegível para análise descritiva de pares.
- `equivalencia=nao`, decisão faltante, texto alterado, rótulo não permitido ou `sim` sem rótulo: par não elegível, com motivo e contagem. Nunca excluir silenciosamente da amostra global de 27.
- No subconjunto de rótulos `positiva/negativa`, pode-se apresentar **coincidência nominal entre pontuação do baseline e marcação individual**, **somente entre frases pontuadas**. Informar também os casos não pontuados.
- `neutra` fica em estrato descritivo próprio, sem transformá-la automaticamente em `sem_avaliacao`, nem contabilizá-la no denominador primário de coincidência positiva/negativa.
- Sem R02 não há coeficiente kappa, consenso, adjudicação humana ou medição da discordância entre pessoas. Uma análise de sensibilidade que exclua pares ambíguos só é válida se critérios de exclusão estiverem definidos e documentados *antes* de consultar resultados dos baselines.

## 4. Proteções

As 27 unidades reservadas permanecem sem acesso nesta fase. O script atual `backend.revisao_humana` prepara fichas **somente** de desenvolvimento e não autoriza sua reutilização para a partição final. A futura geração da ficha e análise final necessitam de implementação específica, inspeção do código, testes em dados sintéticos e congelamento prévio. O arquivo de rótulos não será publicado no GitHub.

## 5. Declaração apropriada para o TCC (rascunho)

> Devido à indisponibilidade de uma segunda avaliação humana, a etapa reservada foi planejada como análise exploratória de anotação individual, com avaliação de equivalência semântica e polaridade por um único anotador, registrada antes da inspeção das pontuações automáticas. Não foram estimadas concordância interavaliadores, acurácia validada ou inferência estatística de viés. As métricas descritivas distinguem pares elegíveis, respostas ausentes, classificações efetuadas e abstenções. A mudança em relação à revisão dupla inicialmente prevista foi documentada previamente à abertura da partição final.

**Atenção:** o parágrafo acima descreve o procedimento *planejado*; somente mudar para tempo passado na versão final após comprovar que ocorreu.
