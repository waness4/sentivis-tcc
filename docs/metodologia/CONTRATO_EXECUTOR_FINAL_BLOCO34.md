# SentiVis — Bloco 34: contrato de entrada da avaliação final, ainda bloqueada

**Estado: NÃO CONGELADO — NÃO AUTORIZADO — NÃO EXECUTADO.** Este bloco introduz um adaptador e um portão de execução **somente sintéticos**. Não abre, lê, gera ficha, anota nem classifica qualquer dos 27 pares reservados. `executar-final` falha sempre com erro de permissão, independentemente dos parâmetros.

## 1. Escopo e relação com os blocos anteriores

O Bloco 33 já exercitou V01/V03/V04 e métricas descritivas em 27 pares **repetidos e fictícios** de nove famílias inventadas, com índice lexical e etiquetador artificiais. O Bloco 34 acrescenta o contrato da fonte original com **14 campos**, uma projeção cega de **6 campos**, validação do retorno da ficha antes de pontuar e preservação de ensaio único. O contrato real permanece **sem habilitação**; um futuro release deve ser submetido a nova revisão.

O esquema de origem reproduz o cabeçalho do formato `backend.pares_piloto`:

`id_par;familia;particao;frase_feminina;frase_masculina;rotulo_revisor1;rotulo_revisor2;equivalencia_revisor1;equivalencia_revisor2;id_revisor1;id_revisor2;alvo_sentilex_feminina;alvo_sentilex_masculina;observacoes`

A ficha cega terá **apenas**:

`id_par;frase_feminina;frase_masculina;equivalencia;rotulo;observacoes`

Campos de família, partição, rótulos dos revisores anteriores, alvos existentes no CSV, identificadores e observações internas **não são exportados à ficha cega**. A existência de colunas `rotulo_revisor1/2` no arquivo original não substitui a nova anotação independente de R01 para a avaliação final. A presença de `alvo_sentilex_feminina/masculina` na fonte original não altera o `N0` **manual proposto** nos baselines V01/V03/V04; esse `N0` não é uma identificação semântica validada.

## 2. Tratamento de entrada e validação

No bloco atual, a origem de 14 colunas é construída **dentro do próprio programa**, com exatamente as fixtures inventadas do Bloco 33 e metadados inventados. O importador funciona somente sobre *strings em memória*, não recebe caminhos. A verificação compara a fonte integral aos bytes textuais da fixture interna antes de qualquer cálculo; mudança de ID, texto, partição, revisão, alvo ou observação interna bloqueia. Portanto, **não** é um importador utilizável para a partição reservada.

A ficha cega é gerada com campos humanos vazios, sem qualquer classe automática. Para ensaiar a devolução, uma ficha completamente **fictícia** é preenchida em memória; a validação exige uma linha por ID, textos idênticos e códigos `sim`/`nao`, rótulos admissíveis para equivalentes e justificativa para `nao`. Respostas sem equivalência decidida são bloqueadas *neste ensaio*. A política efetiva de não resposta/ambiguidade exige decisão e aprovação antes da anotação real.

Apenas depois dessas validações o Bloco 34 chama a lógica sintética do Bloco 33, que usa índice e etiquetador artificiais, passa `alvo="N0"` e `hipotese_modo=True` em V03/V04, e calcula contagens de 27 pares/54 frases. Abstenções conservam `None`, não são convertidas em zero; delta feminino − masculino só é calculável quando as duas frases do par elegível foram pontuadas. Coincidência nominal com uma **anotação artificial** não é acurácia científica. `neutra` permanece separada do estrato positivo/negativo.

## 3. Operações permitidas

- `python -m backend.executor_final_bloqueado_bloco34 verificar-contrato`: descreve portas, formato e estado. Não lê arquivos.
- `python -m backend.executor_final_bloqueado_bloco34 ensaiar`: utiliza unicamente a origem e ficha artificiais internas, cria marcador e relatório de ensaio em `data/piloto/restrito/bloco34_ensaio/`, com criação exclusiva. **Executar uma única vez**. Em falha após marcador, a tentativa continua registrada e um rerun automático é proibido.
- `python -m backend.executor_final_bloqueado_bloco34 executar-final`: sempre retorna `BLOQUEADO`, sem acesso aos dados.
- `--entrada`, `--saida`, `--raiz` e outros parâmetros de caminhos não são aceitos pela CLI.

O ensaio registra hashes **das fixtures inventadas**, métricas agregadas sem frases individuais e aviso de ausência de validade científica. O caminho privado está coberto pelo `.gitignore`; nunca publicar relatórios privados nem os recursos originais.

## 4. Portões obrigatórios para o estudo futuro

1. Revisar formalmente adendo de anotador único, critérios de equivalência/ambiguidade/neutralidade, não resposta, exclusão, denominadores, C001 e limitações da revisão humana.
2. Implementar e revisar a habilitação de uma execução real, *ainda ausente*: cadeia de custódia da partição, isolamento do CSV original, ficha cega após autorização, comprovação de anotação independente anterior às pontuações, arquivo original e hash imutáveis, registro de parâmetros e falha parcial.
3. Exercitar em **novos dados fictícios** o contrato completo de entrada final e as tentativas de ataques por caminho/symlink; dois testes de symlink anteriores ficaram ignorados no Windows e exigem avaliação de risco ou ambiente compatível.
4. Fixar commit completo do código aprovado, versões de Python/spaCy/`pt_core_news_sm`, hashes dos léxicos, condições operacionais e versão assinada do protocolo.
5. Obter a aprovação real, datada e rastreável de responsável habilitado, **antes** de abrir, gerar ficha ou processar os 27 pares reservados. Qualquer alteração ou reexecução posterior deve ser declarada pós-hoc.

A consulta a dados reservados não é condição para testar o código. **O sucesso de testes sintéticos não é prova de acurácia, concordância interavaliadores, presença ou ausência de viés**. O objetivo ainda é uma avaliação descritiva exploratória com um anotador.
