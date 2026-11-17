# SentiVis — Bloco 37: núcleo do executor final, preparado e bloqueado

**Situação: CÓDIGO EM REVISÃO — NÃO CONGELADO — NÃO AUTORIZADO — NENHUMA AVALIAÇÃO FINAL EXECUTADA.**

## Objetivo

Concentrar em um único módulo a validação estrutural, a ficha cega, a política de anotações e as métricas descritivas dos baselines V01, V03 e V04. O núcleo é genérico e em memória, mas **a CLI não aceita CSV/caminho externo e `executar-final` sempre lança `PermissionError`**. A simulação exige a fixture literal produzida no próprio módulo. Este código não deve ser usado para contornar a aprovação acadêmica; funções Python importáveis não são barreira de segurança contra um operador com acesso ao código.

A infraestrutura testada neste bloco não lê, inspeciona, classifica, calcula hash, abre, cria ficha nem inventaria o conjunto reservado de 27 pares.

## Contratos técnicos preparados

1. **Origem em memória:** CSV com 14 colunas exatamente na ordem definida em `backend/executor_avaliacao_bloco37.py`; 27 IDs únicos, 9 famílias, partição única, frases não vazias e não idênticas e pares não duplicados. Não pressupõe 3 pares por família, pois 27 pares / 9 famílias não implica distribuição uniforme. Não usa campos históricos de revisão/`N1` para classificar.
2. **Ficha cega:** CSV com somente `id_par;frase_feminina;frase_masculina;equivalencia;rotulo;observacoes`. Nunca repassa `familia`, revisores históricos, `alvo_sentilex_*`, observações de origem ou predições. A exportação falha se campo potencialmente interpretável como fórmula for detectado; não altera frases silenciosamente.
3. **Anotação:** exige todos os 27 IDs e os textos literais originais. `sim` requer `positiva`, `negativa` ou `neutra`; `nao` exige justificativa e rótulo vazio. Uma equivalência vazia requer rótulo vazio e pode ter observação sem imputar julgamento. IDs repetidos, campos inesperados e textos alterados bloqueiam.
4. **G03 pendente:** a opção `bloquear_ficha_pendente` ou `contabilizar_pendente_nao_elegivel` pode ser simulada, mas **nenhuma está aprovada para uso real** (`POLITICA_APROVADA = None`). A política estrita impede processamento na presença de lacunas; a outra mantém 27 pares no total e conta faltantes fora do conjunto elegível. Esta última depende de aceitação acadêmica e pode exigir adendo ao Bloco 34.
5. **Baselines:** SentiLex, V01, V03, V04; `alvo="N0"` manual, `hipotese_modo=True` somente V03/V04, `incluir_diagnostico=False`. A função responsável pela classificação recebe explicitamente índice e etiquetador, sem carregar arquivos por conta própria.
6. **Resultados:** cobertura/abstenção global sobre 54 frases, cobertura elegível sobre duas vezes os pares equivalentes, coincidência seletiva apenas para rótulos humanos `positiva`/`negativa` em frases pontuadas, neutralidade humana isolada e delta feminino–masculino apenas quando os dois lados do par elegível foram pontuados. Uma taxa com denominador zero é `null`, jamais zero. A distribuição dos deltas por ID e família seria um produto **privado**, não publicável automaticamente.
7. **Falhas:** saídas inconsistentes de qualquer baseline e exceções interrompem o fluxo; nenhuma saída parcial é rotulada como concluída. A CLI `simular` não cria marcador nem grava resultados e pode ser repetida com **dados inventados**.

## Limites desta versão

- Falta escolher e registrar a política G03 (e revisar o adendo de critérios), esclarecer G01/G02/C001, revisar as exceções e obter aprovação acadêmica formal.
- A custódia de dados reais, hash dos **bytes** originais, armazenamento privado da ficha recebida, registro datado da cadeia de custódia, autorização verificável anterior à leitura e marcador transacional de **execução única real** ainda não estão integrados. Esses componentes não devem ser substituídos por uma opção `--autorizado` ou pela simples edição de um booleano.
- O código não acessa os pares reservados, mesmo para calcular hash. Esse hash deve ser calculado apenas após a autorização e sob custódia definida.
- O ensaio de integração da CLI usa o léxico **artificial** e o etiquetador **fictício** do Bloco 33. Não é aferição de desempenho nem comprovação de viés.
- O teste cruzado com `backend.avaliacao_final_preparacao_bloco29.resumir` procura divergências de métricas com a implementação anterior. Os baselines continuam exploratórios e sem validação externa.
- Permanecem dois testes de symlink anteriores ignorados no Windows; uma revisão de segurança/custódia não pode tratá-los como executados.

## Condição para uma futura versão autorizada

Revisar este código e suas diferenças em relação ao B29, obter decisão formal de G03, registrar as demais decisões G01–G08, completar e testar em dados **inventados** a custódia com proteção de links/reexecução e os registros de falha, fixar versão/commit/hashes/dependências, receber aprovação verificável e **somente depois** disponibilizar a operação reservada. Alterações posteriores à abertura deverão ser classificadas como pós-hoc.

**Não usar métricas simuladas deste bloco como resultados empíricos no TCC.**
