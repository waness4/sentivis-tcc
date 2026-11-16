# SentiVis — Registro de verificação numérica e integridade (Bloco 25)

**Data de referência:** 16/11/2026. **Origem:** saídas dos comandos locais fornecidas pela equipe. Não incorpora os JSON/CSV integrais ou dados privados. **Escopo:** desenvolvimento e controles diagnósticos, sem avaliação final.

## 1. Auditoria e curadoria confirmadas

| Indicador | Valor | Relatório local |
|---|---:|---|
| OpLexicon — registros | 32.191 | `data/lexicos/relatorio_auditoria.json` |
| SentiLex-lem — registros | 7.014 | `data/lexicos/relatorio_auditoria.json` |
| SentiLex-flex — registros | 82.347 | `data/lexicos/relatorio_auditoria.json` |
| Registros interpretados, total | 121.552 | `data/lexicos/relatorio_curadoria.json` |
| Registros sinalizados para revisão | 9.494 | `data/lexicos/relatorio_curadoria.json` |
| Registros sem sinalização de curadoria | 112.058 | `data/lexicos/relatorio_curadoria.json` |
| Grupos conflitantes por termo/categoria/alvo | 2.003 | `data/lexicos/relatorio_curadoria.json` |

Por motivo: 4.568 atributos sem chave; 4.529 registros sinalizados com mesma forma/categoria e lemas diferentes; 3.949 com polaridade divergente no mesmo alvo; 13 registros com polaridade fora do padrão. **Os motivos se sobrepõem e não devem ser somados**. Os 2.003 conflitos são grupos, não necessariamente registros distintos.

## 2. Revisão e resultados do desenvolvimento

A revisão `relatorio_revisao_v02.json` registra **9 pares de desenvolvimento** como `APROVADO_DUPLA_REVISAO`. Isso registra o status operacional, não comprova por si só a independência real das avaliações.

| Indicador — SentiLex nos 18 textos de desenvolvimento | V01 (N0 manual) | V03 (N0 manual + hipótese de modo) |
|---|---:|---:|
| Pontuadas | 10 | 6 |
| Não pontuadas | 8 | 12 |
| Correspondências com referência do desenvolvimento | 8 | 6 |
| Divergências com referência entre as pontuadas | 2 | 0 |
| Taxa de pontuação | 55,6% | 33,3% |
| Acurácia seletiva | 80,0% | 100,0% |

Fonte: `data/piloto/restrito/comparacao_sentilex_v01_v03.json`. A acurácia seletiva não equivale à acurácia populacional ou a uma avaliação independente: os mesmos pares foram usados no desenvolvimento.

## 3. Resultados dos 36 controles sintáticos

| Indicador | V01 | V03 | V04 |
|---|---:|---:|---:|
| Pontuadas | 14 | 1 | 1 |
| Não pontuadas | 22 | 35 | 35 |
| Taxa de pontuação | 38,9% | 2,8% | 2,8% |

Fontes: `data/piloto/restrito/controles_sintaticos_v03_resultado.json` (V01/V03) e `data/piloto/restrito/comparacao_controles_v03_v04.json` (V03/V04). O segundo registra **2 frases com filtro neutro aplicado, 2 ocorrências neutras descartadas e 2 frases com status alterado**, mantendo 1 frase pontuada. Sem rótulos humanos consolidados, **não calcular acurácia, F1 ou ganho de precisão** neste conjunto.

SHA-256 de ambos os relatórios para o conjunto de controles: `a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc`.

## 4. Rastreabilidade da revisão e isolamento

- SHA-256 do conjunto consolidado de desenvolvimento na revisão: `575278756f25ee590dce03e6b1e1fd7b594b946a3de802ef7de9dd5e5605c8de`.
- SHA-256 do dataset usado em `comparacao_sentilex_v01_v03.json`: **mesmo valor** (`Hashes correspondem: True`).
- Pares de avaliação intactos registrados em `relatorio_revisao_v02.json`: **27**.
- Pares de avaliação classificados em `comparacao_sentilex_v01_v03.json`: **0**.
- Pares de avaliação processados em `comparacao_controles_v03_v04.json`: **0**.

Esses campos demonstram isolamento declarado por esses processos e coerência dos relatórios, mas **não equivalem a auditoria global de acesso**, nem comprovam que nenhum processo externo leu os arquivos.

## 5. Estado do software e limites

- Bloco 24 publicado no commit `dc08f10` da branch `main`.
- Última execução informada: **345 testes automatizados aprovados**.
- Testes de software não são medidas de acurácia científica.
- A anotação humana dos 36 controles ainda não foi consolidada. A possível exposição de C001 deve ser confirmada.
- Nenhum resultado da partição final de 27 pares consta deste registro.

## 6. Texto apropriado para o TCC

> Em 121.552 registros interpretados das três fontes lexicais, o sistema sinalizou 9.494 registros para revisão e identificou 2.003 grupos conflitantes por termo, categoria e alvo. No conjunto de desenvolvimento de 18 frases, o baseline SentiLex V01 pontuou dez frases e o V03 pontuou seis; as correspondências com os rótulos de desenvolvimento foram, respectivamente, oito e seis. Essa diferença é acompanhada de maior abstenção do V03 e não caracteriza superioridade geral ou redução de viés. Nos 36 controles diagnósticos, V01 pontuou 14 frases, enquanto V03 e V04 pontuaram uma cada; V04 modificou dois motivos de abstenção sem ampliar a taxa de pontuação. Os controles já foram utilizados no desenvolvimento e não constituem amostra independente para estimar generalização.

**Próxima atualização:** somente após as fichas R01/R02 serem concluídas e verificadas; conservar métricas de concordância e decisão em seções distintas.
