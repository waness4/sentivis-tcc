# SentiVis — Matriz de coerência entre código e método

**Revisão documental: 17/11/2026.** Esta matriz distingue os contratos técnicos implementados dos procedimentos científicos ainda dependentes de autorização. Não contém resultados empíricos nem autoriza a avaliação reservada.

| Etapa | Implementação verificável | Documento de referência | Situação |
| --- | --- | --- | --- |
| Pares e piloto de desenvolvimento | `backend/pares_piloto.py` valida partições, revisões e utiliza exclusivamente pares elegíveis de desenvolvimento para o piloto | [Protocolo do piloto](PROTOCOLO_PILOTO_V01.md) | Exploratório; não confirmatório |
| Fichas de dois revisores no desenvolvimento | `backend/revisao_humana.py` prepara duas fichas, conserva as respostas e não resolve discordâncias automaticamente | [Revisão de desenvolvimento](PROTOCOLO_EXECUCAO_REVISAO_DESENVOLVIMENTO.md) | Procedimento do piloto; exige revisão humana efetiva |
| Validação de anotações de desenvolvimento | `equivalencia=sim` exige rótulo válido; `equivalencia=nao` exige justificativa e rótulo vazio; casos pendentes não viram aprovações | [Protocolo do piloto](PROTOCOLO_PILOTO_V01.md) | Regra técnica implementada; não equivale a concordância científica |
| Métricas descritivas do desenvolvimento | `backend/metricas_exploratorias.py` cruza apenas pares aprovados, verifica proveniência e mantém abstenções separadas de zero | [Protocolo de métricas](PROTOCOLO_METRICAS_V01.md) | Qualidade seletiva exploratória, sem avaliação final |
| Controles sintáticos de desenvolvimento | `backend/anotacao_controles_v01.py` usa 36 controles fixados; não lê a reserva de 27 pares | [Protocolo dos controles](PROTOCOLO_ANOTACAO_CONTROLES_V01.md) | Diagnóstico, não conjunto de avaliação independente |
| Avaliação final proposta | `backend/executor_avaliacao_bloco37.py` aceita simulação artificial e mantém `executar_final` bloqueado | [Plano de análise final](PLANO_ANALISE_FINAL_BLOCO28.md) e [contrato do núcleo](PROTOCOLO_NUCLEO_EXECUTOR_BLOCO37.md) | **Não executada; não autorizada** |
| Aprovações e congelamento | Não podem ser produzidos por testes automatizados | [Pendências G01–G08](PARECER_PENDENCIAS_BLOCO35.md) e [encaminhamento acadêmico](ENCAMINHAMENTO_ORIENTADOR_BLOCO37.md) | **Pendentes** |

## Distinção obrigatória entre desenhos

O protocolo inicial do piloto de desenvolvimento descreve **dois revisores**. A proposta de análise final posterior considera **anotador único**, alteração que exige decisão acadêmica expressa (G01). O fato de um fluxo de software exigir dois revisores no desenvolvimento não significa que existam duas anotações independentes efetivamente coletadas. Não atribuir ao experimento final regras e resultados do piloto.

A redação do TCC deve separar **método proposto**, **funcionalidade implementada**, **teste sintético aprovado** e **resultado empírico efetivamente obtido**. Até a autorização documentada, a avaliação final dos 27 pares (54 frases) permanece bloqueada. A presença de testes automatizados aprovados não demonstra acurácia validada nem viés de gênero.

## Conferência antes da banca

- Comparar esta matriz com a versão vigente do manuscrito acadêmico, ainda não verificada por esta auditoria de repositório.
- Confirmar com documentação datada o que realmente foi executado, a identidade pseudonimizada e independência das anotações e eventuais decisões metodológicas.
- Atualizar contagens de testes somente a partir das execuções vinculadas a commits identificados e nunca como substituto de validação científica.
