# SentiVis — Parecer de revisão metodológica antes do congelamento (Bloco 35)

**Estado: RASCUNHO PARA DELIBERAÇÃO. NÃO ASSINADO. NÃO CONGELADO. SEM AUTORIZAÇÃO PARA ACESSAR A PARTIÇÃO FINAL.**

## 1. Escopo e proveniência

Esta revisão usa o pré-registro do Bloco 26, os adendos de anotação individual e o plano de análise do Bloco 28, a matriz do Bloco 32, o executor sintético do Bloco 33 e o contrato bloqueado do Bloco 34. A integridade dos originais de OpLexicon e SentiLex foi conferida no Bloco 31 contra os relatórios locais de auditoria/curadoria. Esta conferência não atesta validade linguística ou ausência de viés.

Os **27 pares reservados** (54 frases, 9 famílias) **não foram acessados por este bloco**. O programa `backend.revisao_congelamento_bloco35` calcula apenas hashes de caminhos públicos pré-definidos, reutiliza o inventário lexical do Bloco 31 e inspeciona o estado estático do contrato do Bloco 34. Não existe modo de classificação final nem de geração de ficha reservada.

## 2. Proposta explícita para aprovação

- **Objetivo:** análise exploratória descritiva da cobertura, das abstenções, da coincidência nominal condicionada a uma anotação individual e das diferenças de pontuação em pares contrafactuais. Sem teste causal, inferência estatística de viés ou afirmação de acurácia validada.
- **Baselines primários:** SentiLex-PT02 em V01 (aditivo), V03 e V04 (contextuais) — saídas reportadas separadamente. OpLexicon apenas em estudo suplementar futuro com protocolo próprio, se houver.
- **Parâmetros:** `alvo=N0` fornecido manualmente para as três versões; `hipotese_modo=True` em V03 e V04; V01 sem esse parâmetro. Atribuir N0 manualmente não reconhece nem valida referente.
- **Unidade de comparação:** o par, não cada uma das 54 frases como observações independentes. O delta é `pontuacao_feminina - pontuacao_masculina`, somente entre pares elegíveis com ambas as frases efetivamente pontuadas.
- **Anotação:** uma única pessoa, identificada por pseudônimo e instruída sem acessar previsões; equivalência `sim`/`nao`, rótulo comum `positiva`/`negativa`/`neutra` se equivalente; se `nao`, rótulo vazio e justificativa. Neutralidade humana não equivale a pontuação lexical zero.
- **Métricas:** cobertura global por método sobre 54 frases; cobertura elegível sobre 2 × pares elegíveis; coincidência apenas entre frases pontuadas e rótulo humano positivo/negativo; deltas apenas quando ambas pontuadas. Denominador zero = não calculável. Abstenção nunca vira pontuação zero, nem é descartada silenciosamente.
- **Limites:** amostra pequena, artificial/intencional, possível dependência entre famílias, referência humana única, PoS prevista estatisticamente, cobertura baixa no desenvolvimento e ausência de generalização.

## 3. Impedimentos que exigem decisão verificável

**G01 — Mudança do desenho:** o Bloco 26 previa revisão humana dupla; somente R01 realizou a revisão de desenvolvimento. A mudança para anotador único é posterior à coleta de desenvolvimento, não deve ser apresentada como pré-registrada originalmente. É necessária aprovação datada de responsáveis acadêmicos.

**G02 — Independência e C001:** confirmar se o controle C001 foi mostrado previamente como exemplo; registrar limitação dos 36 controles e instruções da pessoa avaliadora final. Caso R01 faça também a etapa final, declarar sua participação anterior. Não atribuir contaminação dos 27 pares sem evidência.

**G03 — Conflito de tratamento de faltantes:** o Bloco 28 prevê contar respostas ausentes ou inválidas como pares não elegíveis, com motivos; o Bloco 34, por sua vez, recusa uma ficha que não esteja integralmente respondida, antes de pontuar. É preciso **escolher e documentar previamente** uma política coerente e implementar/testar o contrato conforme a decisão. Alternativas a deliberar: (a) ficha completa obrigatória antes de executar, com tentativas de esclarecimento cegas e registro de lacunas sem inspeção de previsões; (b) permitir decisões ausentes e tratá-las como não elegíveis, mantendo os 27 pares no denominador global e motivo de exclusão. Não implementar qualquer alternativa por conveniência posterior aos resultados.

**G04 — Ambiguidade, neutralidade e exclusões:** aprovar exemplos abstratos de instrução (sem frases reservadas), diferença entre `neutra`, ausência de avaliação e indeterminação, necessidade de observações, exclusões e contagens. O esquema atual só aceita `positiva/negativa/neutra`; outras categorias não poderão surgir implicitamente como rótulos.

**G05 — Executor real ausente:** o Bloco 34 possui a função `executar_final` que **sempre lança `PermissionError`** e testa somente fixtures inventadas. Não existe ainda um fluxo real autorizado para a partição reservada. É obrigatório revisar, implementar e testar integralmente a versão definitiva **sem consultar nenhuma frase reservada**. Não trocar apenas um booleano ou retirar o bloqueio do Bloco 34.

**G06 — Segurança residual e custódia:** dois testes de symlink foram ignorados por limitação do Windows. Essa proteção não foi efetivamente exercitada nesse ambiente; revisar risco, alternativas técnicas e local de guarda com controle de acesso. Preservar arquivos privados fora do Git e não os anexar ao dossiê de revisão.

**G07 — Reprodutibilidade definitiva:** a verificação de hashes do Bloco 31 indica integridade dos originais. Ainda falta congelar o **commit do executor final definitivo**, SHA-256 de código e protocolo aprovados, versões do ambiente e dos recursos e política de tratamento de falhas. O SHA observado durante a criação do Bloco 35 não equivale ao commit congelado. Conservar histórico de quaisquer alterações após aprovação como revisão posterior, nunca execução confirmatória original.

**G08 — Autorização humana:** revisão de responsáveis acadêmicos com data/hora/fuso, versão, decisão expressa, ressalvas, assinatura/identificação e evidências; o código não concede aprovação. Somente depois preparar ficha cega reservada, obter anotação humana e preservar o hash da ficha **antes** de rodar os modelos. A avaliação final deverá executar uma única vez; reexecuções técnicas devem ser identificadas e relatadas.

## 4. Interpretação dos testes

Os testes automatizados demonstram propriedades das rotinas sob entradas simuladas. Não demonstram a qualidade científica dos dados reservados, validade da anotação nem desempenho real dos baselines. O dossiê pode identificar coerência preliminar e hashes, mas **todos os portões G01–G08 permanecem abertos** até comprovação específica, não automaticamente resolvidos por um teste `passed`.

## 5. Próximas decisões

Encaminhar este parecer e `MODELO_ATA_REVISAO_BLOCO35.md` para revisão acadêmica. Para evitar circularidade, decidir a política G03 e revisar o executor real antes de assinar o congelamento. Após commit definitivo, registrar o manifesto e a aprovação. Enquanto houver qualquer pendência crítica, **não usar a partição final para testar, anotar ou classificar**.
