# SentiVis — Solicitação de revisão metodológica preliminar

**Situação: encaminhamento para análise; não constitui aprovação nem autorização para acessar a avaliação reservada.**

## 1. Finalidade

Solicitar revisão do desenho exploratório antes da finalização do executor e do congelamento metodológico. A partição reservada tem 27 pares (54 frases) em 9 famílias e **não deve ser aberta, inspecionada, classificada nem usada para ajustar regras** nesta etapa.

O núcleo experimental dos Blocos 33–37 foi ensaiado com exemplos inteiramente fictícios. Os testes não demonstram validade científica, acurácia ou viés. O módulo do Bloco 37 mantém `executar-final` bloqueado; não há fluxo de custódia e execução real autorizado.

## 2. Escolhas propostas para revisão

| Código | Questão | Proposta a revisar | Situação |
|---|---|---|---|
| G01 | Um avaliador humano | Registrar formalmente a mudança **posterior à etapa de desenvolvimento**: a revisão dupla era prevista no pré-registro original, mas só R01 anotou os controles. Não relatar concordância interavaliadores. | PENDENTE |
| G02 | Independência e treinamento | Documentar quem receberá a ficha cega, instruções dadas, eventual participação anterior de R01 e esclarecer a possível exposição do controle C001, sem pressupor contaminação da partição reservada. | PENDENTE |
| G03 | Respostas ausentes | **Sugestão:** contabilizar decisão de equivalência ausente como `sem_resposta`, par não elegível, preservando os totais globais; não imputar rótulo. Alternativa: bloquear a execução até completar a ficha. A escolha exige aprovação antes da anotação e testes da implementação correspondente. | PENDENTE |
| G04 | Equivalência e métricas | `sim` exige rótulo `positiva/negativa/neutra`; `nao` exige justificativa e rótulo vazio. Neutralidade humana não equivale automaticamente a soma lexical zero. Informar denominadores e abstenções; nenhum teste inferencial de viés. | PENDENTE |
| G05 | Executor definitivo | Inspecionar e testar **com dados inventados** o transporte privado, hashes dos bytes originais, validação de fonte/ficha, marcador de tentativa única e tratamento de falhas. | NÃO CONCLUÍDO |
| G06 | Custódia e links simbólicos | Definir acesso privado, armazenamento fora do Git e análise do risco residual dos dois testes de symlink ignorados no Windows. | PENDENTE |
| G07 | Congelamento técnico | Fixar **após** o executor definitivo: commit de 40 caracteres, SHA-256 do código/protocolo/léxicos, Python/spaCy/modelo, parâmetros e regras de execução/erros. | NÃO CONCLUÍDO |
| G08 | Aprovação formal | Decisão acadêmica datada, identificada e verificável, após atender às condições anteriores e **antes de acessar os pares reservados**. | NÃO CONCLUÍDO |

## 3. Tratamento descritivo proposto

Recursos principais: SentiLex-PT02 com V01, V03 e V04; `alvo=N0` informado manualmente, sem validação automática do referente; hipótese de modo habilitada apenas em V03/V04. O OpLexicon não integra a comparação principal.

A cobertura/abstenção global é informada sobre 54 frases por método; cobertura elegível sobre duas vezes o número de pares elegíveis. A coincidência nominal com a referência de uma única pessoa é calculada **somente** entre rótulos humanos positivo/negativo e frases efetivamente pontuadas. Para cada par elegível com ambas as frases pontuadas, `delta = pontuação_feminina − pontuação_masculina`. Sem pontuação em qualquer lado, delta é não calculável, nunca zero imputado. Denominador zero resulta em indicador não calculável.

Esses indicadores **não** constituem acurácia validada, concordância interavaliadores, teste de significância ou comprovação de presença/ausência de viés de gênero.

## 4. Resposta solicitada

Pede-se parecer preliminar sobre G01–G04 e diretrizes para G06, com ressalvas e correções. **Ainda não se solicita assinatura de congelamento ou autorização de abertura.** Após a implementação e auditoria de G05/G07, será apresentada a versão final para decisão formal G08.

Documentos de apoio já existentes no repositório:

- `docs/metodologia/PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md`
- `docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md`
- `docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md`
- `docs/metodologia/PARECER_PENDENCIAS_BLOCO35.md`
- `docs/metodologia/DECISAO_G03_NAO_RESPOSTA_BLOCO36.md`
- `docs/metodologia/PROTOCOLO_NUCLEO_EXECUTOR_BLOCO37.md`
- `docs/metodologia/MODELO_ATA_REVISAO_BLOCO35.md` (modelo, **não assinado**)

Nenhum dado reservado, ficha real, previsão ou rótulo individual deve ser incluído em mensagens ou arquivos públicos de revisão.
