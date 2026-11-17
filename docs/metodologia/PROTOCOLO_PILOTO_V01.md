# SentiVis — Protocolo operacional do piloto v0.1

**Estado:** proposta para revisão, sujeita à aprovação antes da anotação. Complementa, mas não substitui, o procedimento documentado em [`PROTOCOLO_EXECUCAO_REVISAO_DESENVOLVIMENTO.md`](PROTOCOLO_EXECUCAO_REVISAO_DESENVOLVIMENTO.md).

## Pergunta

O conjunto candidato contém pares contrafactuais de gênero com alterações de artigo e/ou substantivo profissional. A revisão avalia se cada par mantém interpretação e avaliação afetiva equivalentes. Os exemplos foram criados pelo pesquisador, não extraídos de interações com pessoas.

## Amostragem

12 famílias, cada uma com três exemplos de polaridade *pretendida*: positiva, negativa e neutra. 3 famílias (9 pares) para desenvolvimento e 9 famílias (27 pares) para avaliação reservada. A classe planejada é apenas informação de construção, não gabarito. Os revisores não recebem esta informação. A distribuição garante contagens planejadas iguais por classe, não garante que os rótulos reais sejam equilibrados.

## Instruções independentes aos revisores

1. Ler somente `ficha_revisor_A.csv` ou `ficha_revisor_B.csv`, sem consultar classificador, léxicos, plano de amostragem ou respostas do outro revisor.
2. Para cada par, registrar `equivalencia=sim` somente quando o significado avaliativo se mantiver, alterando a referência de gênero e concordância; caso contrário `nao`. Na dúvida, registrar `nao` e justificar.
3. Registrar um rótulo comum de sentimento (`positiva`, `negativa`, `neutra`) interpretado pelo humano; se não houver equivalência comprovada, registrar `equivalencia=nao`, **deixar `rotulo` obrigatoriamente vazio** e justificar em `observacoes`. A rotina `backend.revisao_humana._ler_ficha` rejeita a combinação `equivalencia=nao` com rótulo preenchido.
4. Registrar problemas de naturalidade, ambiguidade de referente, ironia, polaridade dependente de contexto, formas invariáveis e quaisquer outras dúvidas.
5. Entregar as fichas separadamente antes da comparação das respostas.

## Resolução de discordâncias (proposta a aprovar ANTES da anotação)

- Se ambos marcaram `sim` e atribuíram o mesmo rótulo, o par fica elegível à análise de desenvolvimento, após verificação técnica.
- Se qualquer revisor marcou `nao` ou se os rótulos divergiram, classificar como `pendente_adjudicacao` e registrar as duas respostas originais.
- Um terceiro avaliador humano deve decidir, sem consultar saídas do SentiVis; registrar justificativa e data em arquivo separado, sem sobrescrever respostas originais.
- A ausência de adjudicação mantém o par sem aprovação para análises que exigem equivalência validada. Documentar as exclusões; a consolidação atual registra `PENDENTE_ADJUDICACAO` e não executa adjudicação por conta própria.

## Partições e congelamento

- Nenhuma família pode pertencer simultaneamente às partições desenvolvimento e avaliação.
- Não usar frases de avaliação para criar regras, selecionar hiperparâmetros, redigir exceções lexicais ou escolher exemplos da apresentação.
- Revisar adequação linguística dos pares *antes* da execução do classificador; mudanças geram nova versão com IDs/hashes documentados.
- Congelar léxicos, regras, código, corpus e critérios de exclusão antes de abrir a avaliação.
- Revisões humanas não validam por si só o classificador: além de concordância e cobertura, serão necessárias métricas de qualidade em dados independentes e incerteza por famílias.

## Limitações

Amostra pequena e sintética. Não mede viés real nem poder estatístico. Neutro planejado significa ausência intencional de avaliação emocional explícita, e não ausência de palavras no léxico. Profissões não representam a diversidade de construções linguísticas e sociais. Revisar distribuição final após anotação.
