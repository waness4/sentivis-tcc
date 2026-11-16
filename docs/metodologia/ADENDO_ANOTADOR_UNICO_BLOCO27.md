# SentiVis — Adendo metodológico: anotação individual (Bloco 27)

**Estado:** adaptação metodológica *após o recebimento da ficha*. Não substituir nem reescrever retrospectivamente o protocolo pré-definido do Bloco 21. Data: 16/11/2026.

## Motivo e alteração

O protocolo original previa duas pessoas (R01 e R02) para os 36 controles. Somente R01 devolveu uma ficha. A pesquisa prosseguirá com **uma fonte humana individual**, usada **apenas para descrição e discussão de casos**, sem proclamar referência consensual. Essa decisão é uma alteração pós-coleta e deve ser registrada nas limitações do TCC.

## Integridade, formato e lacunas

A ficha original é preservada em `data/piloto/restrito/ficha_controles_R01_recebida.csv` (não enviar ao GitHub). A auditoria do Bloco 27 checa correspondência dos 36 IDs, coteja os textos com o conjunto fixado, registra SHA-256 e conta campos vazios. O arquivo recebido usa vírgula em vez do ponto e vírgula definido pelo gerador original; isso não autoriza editar o original.

O avaliador empregou `positivo`, `negativo`, `neutro` em vez de `positiva`, `negativa`, `neutra`, `sem_avaliacao`, `mista`, `indeterminada`. Somente `positivo`→`positiva` e `negativo`→`negativa` têm normalização **morfossintática inequívoca**, caso se opte por alguma análise exploratória; não alterar os valores do arquivo. `neutro` não é automaticamente `neutra` ou `sem_avaliacao`, pois o protocolo diferencia neutralidade afetiva de descrição factual. Campos `referente` são texto livre, não as categorias definidas; `papel_com` não foi preenchido.

## Plano de uso conservador

1. Relatar a distribuição descritiva das marcações individuais e a incompletude da ficha.
2. Analisar qualitativamente erros, casos controversos e abstenções do sistema, separando **anotação original**, **eventual interpretação posterior** e **saída do baseline**. Não modificar o julgamento original com base na saída automática.
3. Se comparar rótulos apenas de `positivo/negativo` com classes dos baselines, identificar explicitamente a análise como *concordância descritiva com um único avaliador* (não acurácia validada), informar denominadores e abstenções. Não apresentar os casos `neutro` como verdade-terreno de classe neutra.
4. Assinalar C001 como potencialmente exposto ao avaliador: verificar se o exemplo chegou a esta pessoa; documentar e avaliar sensibilidade excluindo C001 quando fizer comparações futuras.
5. Revisar manualmente inconsistências textuais e observações possíveis em C003, C013, C030 e C033. Uma segunda resposta humana **não** deve ser fabricada ou inferida.
6. Não calcular kappa, porcentagem de concordância interavaliadores nem adjudicação, pois inexiste R02.
7. **Não acessar nem classificar os 27 pares reservados** durante esta etapa. O pré-registro de avaliação final não está congelado e pode exigir revisão do desenho antes de uso.

## O que pode ser escrito no TCC

> Devido à devolução de apenas uma das fichas previstas, a anotação humana dos controles foi conduzida como análise individual exploratória. O material não permite estimar concordância entre anotadores nem estabelecer referência consensual. As respostas foram preservadas integralmente, auditadas estruturalmente e consideradas com ressalvas, incluindo diferenças em relação ao esquema categórico inicialmente definido. Dessa forma, a comparação com os baselines limita-se à descrição de decisões e casos, sem inferências sobre acurácia validada, generalização ou viés de gênero.

O adendo é público, mas a ficha original e os relatórios de anotação permanecem na pasta privada ignorada pelo Git.
