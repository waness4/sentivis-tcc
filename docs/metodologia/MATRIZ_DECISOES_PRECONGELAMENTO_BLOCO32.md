# SentiVis — Bloco 32: matriz de decisões anteriores à avaliação final

**Estado: PROPOSTA PARA REVISÃO. NÃO CONGELADO. NÃO AUTORIZADO.**

Este texto complementa, sem substituir retroativamente, o pré-registro do Bloco 26, o adendo de anotador único e o plano de análise do Bloco 28, o ensaio sintético do Bloco 29, o preflight do Bloco 30 e o manifesto de integridade do Bloco 31. As 27 unidades reservadas (9 famílias, 54 frases) **não foram abertas ou executadas nesta etapa**.

## A. O que já é verificável

1. O Bloco 31 confere as cópias originais de OpLexicon v3 e SentiLex-PT02 contra os relatórios locais de auditoria e curadoria, com SHA-256 e MD5 no ZIP. O resultado `CONFERIDA_COM_RELATORIOS_LOCAIS` significa integridade, não validade linguística.
2. Contratos sintéticos de ficha, pontuação, abstenção, deltas e saída agregada foram exercitados nos Blocos 29–30. Eles **não são** o executor real da partição reservada.
3. No ambiente informado em 16/11/2026, 401 testes passaram, 2 foram ignorados por impossibilidade de criar symlinks no Windows e nenhum falhou. A proteção contra symlinks nesses dois testes não ficou comprovada *nesse ambiente*.
4. A anotação dos 36 controles diagnósticos tem apenas R01 e é pós-coleta/adaptada; isso não gera consenso, kappa nem avaliação externa dos baselines. A possível exposição de C001 continua **a confirmar**.

## B. Decisões propostas para aprovação antes de qualquer acesso reservado

| Item | Proposta explícita | Estado |
|---|---|---|
| Questão da avaliação | Descrever cobertura/abstenções, coincidência condicional com R01 e deltas pareados | Proposta |
| Corpus reservado | 27 pares em 9 famílias; análise de diferença no nível de **par** | Proposta |
| Recursos | SentiLex-PT02, fonte original conferida com curadoria | Proposta |
| Baselines primários | V01 aditivo, V03 contextual, V04 contextual, cada um com sua própria saída | Proposta |
| Parâmetros | `alvo=N0` manual para os três; `hipotese_modo=True` somente V03/V04 | Proposta |
| Etiquetador | spaCy `pt_core_news_sm` na versão congelada | Pendente de fixação final |
| Avaliação humana | Um anotador pseudonimizado, ficha sem previsões; declarar histórico e limitações | Proposta |
| Equivalência | `sim` apenas se mudar gênero/concordâncias sem mudar sentido avaliativo; `nao` + motivo caso contrário ou dúvida relevante | Proposta |
| Rótulo humano | `positiva`, `negativa`, `neutra` apenas em pares equivalentes; não equivalentes sem rótulo | Proposta |
| Neutralidade | Registrar separadamente; não equiparar automaticamente à ausência de avaliação ou pontuação lexical zero | Proposta |
| Não resposta | Não preencher por inferência; contar e justificar exclusões conforme plano | Proposta |
| Cobertura global | Frases pontuadas / 54, abstenções / 54, por método | Proposta |
| Cobertura elegível | Frases pontuadas elegíveis / (2 × pares equivalentes com rótulo permitido) | Proposta |
| Coincidência descritiva | Apenas `positiva/negativa` entre frases efetivamente pontuadas; numerador/denominador explícitos | Proposta |
| Delta por par | `pontuação_feminina − pontuação_masculina` somente com equivalência humana e duas pontuações | Proposta |
| Falhas/abstenções | Não atribuir zero a abstenção e não repetir avaliação corrigida como teste independente | Proposta |
| Inferência | Sem inferência causal, significância ou alegação de presença/ausência de viés de gênero | Proposta |
| OpLexicon | Fora da comparação primária; avaliação suplementar exigiria contrato separado congelado | Proposta |

Os rótulos humanos dos pares e as classes dos baselines não representam o mesmo tipo de evidência. Um julgamento de R01 é uma referência **individual**; mesmo uma coincidência alta, com abstenção elevada, não equivale à acurácia validada nem a um modelo robusto.

## C. Ordem de execução que ainda precisa ser implementada e aprovada

1. Concluir **programa exclusivo** da partição final: validação de partição por família, geração de ficha cega, validação de ficha devolvida, preservação de hashes, bloqueio de execução repetida e tratamento de falhas; testar **somente em dados artificiais**.
2. Rever o programa e as regras sem consultar os 27 pares; registrar também o resultado dos testes de symlink que não puderam ser exercitados no Windows ou justificativa do risco residual.
3. Conferir a metodologia de anotação: identidade operacional de R01, independência em relação às predições, instruções, origem da possível exposição C001 e regras para não resposta ou ambiguidade.
4. Registrar commit exato após publicação do código final, versões completas do ambiente, hashes dos léxicos, configuração imutável e versão do protocolo. O commit **observado** do Bloco 31 não é automaticamente o commit congelado.
5. Colher e registrar a aprovação formal do responsável acadêmico conforme exigências institucionais, **antes de abrir a avaliação reservada**.
6. Somente com autorização formal, permitir custódia dos dados reservados, preparar ficha sem modelos, receber anotação R01, preservar original e hash **antes** de qualquer pontuação.
7. Executar a comparação **uma vez**, preservar saídas e auditar métricas predefinidas. Qualquer alteração posterior deve ser descrita como pós-hoc.

**Este Bloco 32 não implementa a etapa 1 acima, não altera regras de classificação e não concede autorização.**

## D. Critério de conclusão do Bloco 32

O Bloco 32 está concluído tecnicamente quando seu comando de verificação documental funcionar e os testes associados passarem; sua conclusão **não implica** conclusão dos itens A–C do congelamento. A decisão de congelar depende do documento de aprovação e do programa específico da avaliação final.
