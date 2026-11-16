# SentiVis — Plano de análise descritiva final com anotador único

**Bloco 28 | PROPOSTA, NÃO CONGELADA | Sem uso dos 27 pares reservados**

## 1. Perguntas e desenho

Amostra pré-existente: 27 pares (54 frases), distribuídos em 9 famílias reservadas. A unidade do contraste feminino–masculino é o **par**, não 54 observações independentes. O objetivo é descrever: (1) quantas frases recebem pontuação ou abstenção; (2) em quantos casos classificados com referência individual positiva/negativa o rótulo coincide; (3) em quantos pares semanticamente elegíveis é calculável um delta de pontuação, e qual sua distribuição. Nenhuma questão permite confirmar ou rejeitar viés de gênero com esta amostra.

## 2. Baselines propostos e separação de recursos

**Análise primária proposta:** SentiLex-PT02 V01 aditiva com `N0` manual, SentiLex V03 contextual com `N0` manual e hipótese de modo explícita, e SentiLex V04 contextual com os mesmos parâmetros. Usar léxico, etiquetador, versão e regras congeladas antes da abertura. `N0` escolhido manualmente é um pressuposto, **não** identificação correta de alvo; todo resultado permanece exploratório.

**OpLexicon V01/V02** deve ser considerado estudo suplementar distinto **apenas se** seu protocolo, configuração, implementação e testes forem congelados antes de qualquer acesso. Não misturar resultados de OpLexicon com os do SentiLex como se fossem a mesma comparação. Nenhuma alteração ou otimização de modelos será feita usando a avaliação final.

A versão exata do executável de avaliação final, parâmetros e lista dos baselines permanecem **pendentes de verificação/aprovação**; esta proposta não os congela automaticamente.

## 3. Ordem obrigatória da futura operação

1. Aprovar e datar o protocolo e o adendo de anotador único; escolher formalmente baselines e parâmetros; registrar commit e versões exatas dos artefatos.
2. Desenvolver um **script exclusivo de avaliação final** (não adaptar silenciosamente o programa de desenvolvimento), incluindo validação da partição, proteção de arquivos e processamento único. Testar com pares **inteiramente fictícios**, sem consultar os reservados.
3. Congelar script, regras, critérios, formato das saídas e procedimentos de recuperação em caso de falha, com hashes e registro de revisão dos responsáveis.
4. Só então permitir acesso autorizado à partição reservada para produzir a ficha **sem previsões** para a pessoa avaliadora. Registrar hash da fonte e da ficha sem divulgar conteúdo.
5. Receber a ficha, preservar original imutável, validar esquema e preenchimento, decidir elegibilidade com base apenas na anotação, e congelar o registro de decisões humanas **antes** de qualquer pontuação dos baselines.
6. Executar a análise automática final **uma vez** com as versões congeladas; preservar saídas brutas e logs privados, hashes, ambiente, data e hora.
7. Calcular apenas as métricas pré-definidas. Analisar qualitativamente diferenças depois de encerrar a execução, sem ajustar e rerodar os classificadores como se o segundo resultado fosse independente.

Se for detectado erro, preservar o resultado original; documentar correção e qualquer reexecução como **análise pós-hoc**, não novo teste independente.

## 4. Elegibilidade e denominadores

Tabela mínima da avaliação por método:

| Variável | Definição |
|---|---|
| `P_total` | 27 pares apresentados, sem exclusão invisível |
| `F_total` | 54 frases, duas por par |
| `P_equivalentes_R01` | Pares com `equivalencia=sim` e rótulo comum válido informado antes das pontuações |
| `P_nao_elegiveis` | 27 − `P_equivalentes_R01`, com motivos |
| `F_elegiveis` | 2 × `P_equivalentes_R01` |
| `F_pontuadas_global` | Frases pontuadas entre as 54, com denominador 54 |
| `F_abstidas_global` | 54 − `F_pontuadas_global` |
| `F_pontuadas_elegiveis` | Frases pontuadas entre as elegíveis, com denominador `F_elegiveis` |
| `F_posneg_compativeis` | Frases elegíveis cujo rótulo humano é `positiva` ou `negativa` |
| `F_posneg_pontuadas` | Frases de `F_posneg_compativeis` que receberam classe do baseline |
| `F_posneg_coincidentes` | Entre `F_posneg_pontuadas`, classe do baseline idêntica à marcação individual |
| `P_delta_calculavel` | Pares elegíveis nos quais ambas as frases receberam pontuação com o mesmo baseline |
| `P_delta_nao_nulo` | Pares de `P_delta_calculavel` cujo delta feminino−masculino não é zero |

## 5. Indicadores pré-propostos

- **Taxa global de pontuação** = `F_pontuadas_global / 54`, e **taxa global de abstenção** = `F_abstidas_global / 54`.
- **Taxa de pontuação elegível** = `F_pontuadas_elegiveis / F_elegiveis`, se `F_elegiveis > 0`; separar das taxas globais.
- **Coincidência nominal seletiva com uma anotação individual** = `F_posneg_coincidentes / F_posneg_pontuadas`, se `F_posneg_pontuadas > 0`; nunca denominar acurácia validada, nem usar os não pontuados como acertos.
- **Cobertura de pares com delta calculável** = `P_delta_calculavel / P_equivalentes_R01`, se `P_equivalentes_R01 > 0`.
- **Fração de deltas não nulos** = `P_delta_nao_nulo / P_delta_calculavel`, se `P_delta_calculavel > 0`.
- `delta = pontuação_feminina − pontuação_masculina`; apenas quando ambas pontuadas. **Abstenção não é delta zero**. Reportar número de pares elegíveis sem delta e, se aplicável, os deltas por família apenas descritivamente.
- Rótulos `neutra` e casos marcados como sem avaliação/ambíguos nas observações: tabular separadamente; não imputar equivalência entre neutralidade do leitor e soma lexical zero.

Se o denominador for zero, mostrar **não calculável**, não 0%. Apresentar numerador e denominador explicitamente. Não aplicar testes de hipótese, significância ou estimativa de efeito causal de gênero: não há potência, referência humana dupla ou delineamento adequados.

## 6. Proveniência, limites e relatório final

A saída deverá citar data/hora, commit hash, SHA-256 do corpus e da ficha, checksums dos léxicos, versão do spaCy e `pt_core_news_sm`, versão do sistema e dos baselines, parâmetros de `alvo` e `hipotese_modo`, total por classe de decisão, exclusões e seus motivos, relatório de anomalias e status de execução única.

Limitações a apresentar: corpus pequeno, sintético e escolhido intencionalmente, possível viés de seleção das 9 famílias, comparações pareadas dependentes, apenas um avaliador, nenhuma confiabilidade interavaliador, referente N0 manual, análise sintática preditiva, alta abstenção observada no desenvolvimento e ausência de desfecho independente confirmatório de viés. Uma proporção zero de deltas diferentes não é evidência de ausência de viés quando poucas frases são pontuadas.

**Status:** somente planejamento. Não classificar nenhum par reservado antes do checklist de congelamento estar totalmente preenchido e aprovado.
