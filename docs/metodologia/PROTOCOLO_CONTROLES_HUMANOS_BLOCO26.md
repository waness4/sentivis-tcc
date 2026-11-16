# SentiVis — Protocolo de documentação e consolidação da anotação humana dos controles (Bloco 26)

**Tipo:** complemento operacional e metodológico ao `PROTOCOLO_ANOTACAO_CONTROLES_V01.md` (Bloco 21). **Status:** proposta/documentação; os rótulos humanos não foram recebidos nem consolidados. **Âmbito:** somente 36 controles de desenvolvimento. **Não** é análise final independente.

## 1. Base e objetivo

- Fonte imutável: `data/controles/controles_sintaticos_v01.csv` (36 frases).
- SHA-256 de referência: `a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc`.
- Saídas anteriores de V01, V03, V04 e suas abstenções já foram observadas durante o desenvolvimento. Por isso, os controles **não** são conjunto cego para a equipe de desenvolvimento.
- Objetivo humano: estabelecer, independentemente das previsões do sistema, anotações para `polaridade`, `referente` e `papel_com`, e estudar a concordância de R01/R02 com ressalvas de exposição.
- Escopo exclui 9 pares do piloto como substitutos destes controles, e exclui integralmente os 27 pares reservados da avaliação final.

## 2. Coleta e verificação do procedimento

As fichas previamente criadas por `backend.anotacao_controles_v01 preparar` possuem as colunas `id_controle;texto;polaridade;referente;papel_com;observacoes` e ordens embaralhadas distintas. Não criar novas fichas nem alterar as existentes sem controle de versão e justificativa.

Para cada avaliador, documentar **sem dados pessoais no repositório**: código pseudônimo R01/R02; data de envio das instruções; confirmação de que recebeu somente sua ficha; data de devolução; se teve acesso a exemplos, previsões, respostas de outra pessoa ou discussões prévias; identificação de eventual exposição de itens. Registrar as confirmações em arquivo privado, separado das respostas.

Os avaliadores devem preencher as categorias descritas no protocolo do Bloco 21:

- `polaridade`: `positiva`, `negativa`, `neutra`, `sem_avaliacao`, `mista` ou `indeterminada`.
- `referente`: `agente`, `acao`, `objeto`, `terceiro`, `multiplos`, `nenhum` ou `indeterminado`.
- `papel_com`: `modo`, `instrumento`, `companhia`, `outro`, `ambiguo` ou `nao_aplicavel`.

Não fundir `neutra` e `sem_avaliacao`. Não modificar textos/IDs. Observação é obrigatória para `mista`, `indeterminada`, referente `indeterminado` ou papel `ambiguo`, conforme o protocolo original.

## 3. Integridade antes de calcular métricas

1. Preservar cópias das duas fichas devolvidas, sem sobrescrevê-las; registrar SHA-256, data e versão.
2. Verificar 36 IDs únicos, correspondência exata de `texto`, preenchimento e categorias aceitas.
3. Conferir formalmente se R01 e R02 trabalharam sem consultar baselines, sem colaboração entre si e se viram o item C001 como exemplo. Se isso não for verificável, descrever como limitação, nunca como independência comprovada.
4. Não inspecionar ou utilizar os 27 pares reservados para a consolidação.

Com ambas as fichas completas e sem saída anterior a sobrescrever:

```powershell
python -m backend.anotacao_controles_v01 consolidar --pasta-saida .\data\piloto\restrito
```

O módulo existente verifica as fichas, gera contagens e proporções de concordância para cada campo e para os três campos simultaneamente, além do kappa de Cohen para polaridade. Também lista `DIVERGENCIA_PENDENTE`. Ele **não** adjudica, não atribui rótulos automáticos e não calcula acurácia/F1 dos baselines.

## 4. Análise da concordância humana

Relatar obrigatoriamente:

| Campo | Definição | Interpretação |
|---|---|---|
| `polaridade` | número e proporção de respostas idênticas em 36 | acordo entre duas pessoas, não correção do modelo |
| `referente` | número e proporção de respostas idênticas em 36 | acordo sobre o alvo semântico, não validação automática de N0/N1 |
| `papel_com` | número e proporção de respostas idênticas em 36 | acordo sobre função da construção `com` |
| todos | número e proporção com coincidência simultânea dos três campos | concordância integral estrita |
| kappa de Cohen | kappa nominal da coluna `polaridade` | coeficiente descritivo; pode ser indefinido por prevalências extremas |

Apresentar `n=36`, as contagens por categoria e a quantidade de divergências. Não descrever acordo como acurácia de V01/V03/V04. Não tratar um kappa isolado em uma amostra pequena de controles autorais como demonstração de validade externa.

## 5. Registro de exposição do controle C001

O item **C001**, “A fisioterapeuta explicou a tarefa com clareza.”, foi utilizado em uma orientação anterior elaborada no desenvolvimento. A exposição efetiva a R01/R02 **ainda precisa ser confirmada** e não deve ser presumida.

Registrar privadamente: se a mensagem foi enviada, a qual avaliador, em que data e se ofereceu interpretação/rótulo. Caso algum avaliador tenha recebido o exemplo, marcar `C001` como potencialmente exposto, independentemente do seu julgamento. Não apagar o item, nem alterar seus rótulos.

Se houver exposição, apresentar resultados de concordância: (a) nos 36 controles (descritivo completo), e (b) nos **35 controles excluindo C001** (análise de sensibilidade). Calcular ambas sobre o mesmo conjunto de campos, com denominadores explícitos. A aplicação atual gera automaticamente o relatório de 36; a análise de 35 exigirá processamento adicional *após receber as fichas*, em saída distinta, e não deve ser inventada agora. Se a exposição não puder ser determinada, declarar a incerteza e, por prudência, também apresentar a sensibilidade, sem afirmar cegamento completo.

## 6. Divergências e adjudicação

- Preservar sem alterações as duas anotações originais.
- Não escolher o rótulo concordante com o SentiVis ou preferir o avaliador cujas respostas aumentem a acurácia.
- Toda divergência em qualquer uma das três dimensões permanece `DIVERGENCIA_PENDENTE` até procedimento humano previamente documentado.
- Para adjudicação, preferir terceiro avaliador independente, sem acesso às saídas do modelo, que registre decisão, motivos, data, categoria de cada campo e referência a IDs. Usar documento **privado e versionado**, sem sobrescrever fichas.
- Se não houver terceiro avaliador, não simular consenso. Pode-se relatar concordância e divergências sem adjudicação; para métricas de qualidade dependentes de rótulo único, restringir aos casos consensuais **com viés de seleção explicitado**, ou adiar as métricas conforme decisão metodológica pré-registrada.

## 7. Comparação diagnóstica posterior com os baselines

Somente depois da revisão humana e definição escrita dos casos elegíveis, registrar para V01/V03/V04: frases pontuadas, abstenções, distribuição de status, proporção pontuada (denominador completo) e proporção de correspondências entre as **pontuadas e rotuladas com classe compatível**. Usar sempre denominadores explícitos. Não converter automaticamente `sem_avaliacao`, `mista` ou `indeterminada` para `neutra`.

Diferenciar nitidamente: **concordância humana**, **cobertura de decisão** e **acurácia seletiva diagnóstica**. Nenhum desses resultados, nesse conjunto já utilizado no desenvolvimento, confirma viés de gênero, generalização ou superioridade estatística.

## 8. Arquivos privados e acesso

- Original R01: `data/piloto/restrito/ficha_controles_R01_v01.csv`.
- Original R02: `data/piloto/restrito/ficha_controles_R02_v01.csv`.
- Saídas propostas do programa existente: `data/piloto/restrito/consolidacao_controles_humana_v01.csv` e `data/piloto/restrito/relatorio_concordancia_controles_v01.json`.
- Registro de exposição/adjudicação: manter na mesma pasta restrita ou em destino institucional protegido, sem publicar conteúdo pessoal.

Verificar `.gitignore` e `git status` antes de qualquer commit. A documentação metodológica pública pode conter somente estatísticas agregadas e procedimentos sem fichas/respostas individuais.
