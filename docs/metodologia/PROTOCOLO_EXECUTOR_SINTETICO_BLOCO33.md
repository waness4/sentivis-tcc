# SentiVis — Bloco 33: contrato de execução experimental com 27 pares fictícios

**Situação: IMPLEMENTAÇÃO DE ENSAIO EXCLUSIVAMENTE SINTÉTICO. NÃO CONGELADO. NÃO AUTORIZADO.**

## Escopo

O módulo `backend.executor_sintetico_bloco33` verifica a **forma operacional** prevista para a avaliação: 27 pares, 54 frases, nove famílias de três pares e execução separada dos baselines SentiLex V01, V03 e V04. A quantidade é deliberadamente igual à quantidade prevista no protocolo reservado, mas **todas as frases e IDs são inventados**. São repetidos os quatro exemplos de laboratório do Bloco 29, com IDs `SINT001` a `SINT027` e famílias `SINT_FAM01` a `SINT_FAM09`. Essa repetição NÃO constitui nova amostragem, diversidade textual ou qualquer evidência de desempenho.

O programa não acessa nem varre os 27 pares reservados. Não abre CSV de avaliação, não utiliza relatórios de R01, não lê arquivos de léxicos originais e não usa spaCy. A CLI aceita exclusivamente os modos `verificar-contrato` e `ensaiar`; **não aceita arquivos de entrada**, parâmetros de modelos, acesso à partição real ou modo de avaliação final. A função em memória exige igualdade integral com a fixture gerada; uma frase, ID, família ou coluna alterada bloqueia a pontuação. O programa específico da avaliação real permanece **a implementar e aprovar**.

## Separação das etapas de execução

1. Construir a fixture inventada de 27 pares e nove famílias. Criar uma **ficha cega em memória** contendo só seis colunas: `id_par;frase_feminina;frase_masculina;equivalencia;rotulo;observacoes`. A ficha cega não apresenta famílias, rótulos, etiquetas ou previsões.
2. Validar a ficha preenchida artificialmente **antes de qualquer baseline**. A anotação simulada não substitui avaliação humana independente. A correspondência textual e os IDs são obrigatórios; não equivalência recebe observação e não pode ter rótulo.
3. Construir um índice SentiLex **inventado**, com somente `gentileza` (+1) e `grosseria` (−1) como entradas fictícias, e etiquetador `_EtiquetadorFicticio` **não spaCy**. Executar V01 com `alvo=N0`; V03 e V04 com `alvo=N0`, `hipotese_modo=True` e etiquetador artificial. Nenhuma interpretação de alvo real é validada.
4. Validar a saída de cada frase: status pontuado exige classe coerente e pontuação inteira; abstenção exige `pontuacao_exploratoria=null` e `classe_exploratoria=null`. Erro de execução ou contrato gera falha, **não** é mascarado como abstenção.
5. Reutilizar a agregação do Bloco 29, com contagens globais sobre 54 frases, subconjuntos elegíveis/positivos/negativos/neutros, abstenções e deltas calculáveis apenas quando ambos os lados pontuam. As métricas mantêm denominadores explícitos; nenhuma coincidência nominal é chamada de acurácia validada.
6. Conservar no relatório privado apenas IDs sintéticos, resultados normalizados (status, pontuação e classe) e contagens. Não reproduzir frases ou observações. Os campos de validação científica e viés permanecem `null`.

## Proteção do registro

`verificar-contrato` não grava arquivos. `ensaiar` cria uma tentativa única em `data/piloto/restrito/bloco33_ensaio/`, coberta pelo `.gitignore` atual. Primeiro escreve um **marcador exclusivo** (`marcador_tentativa_bloco33.json`); depois de executar todos os baselines, grava `relatorio_sintetico_bloco33.json` também com criação exclusiva. Não permite sobrescrita, alteração do nome ou reexecução. Em caso de erro após o marcador, ele permanece e a execução não deve ser repetida/reciclada como se inédita fosse. A execução do Bloco 30 não precisa nem deve ser repetida.

Dois testes de symlink do Bloco 31 foram ignorados no Windows porque não havia permissão de criar links simbólicos. O Bloco 33 inclui uma verificação direta de componentes de caminho simbólicos, mas a proteção precisa de revisão adicional em plataforma onde links simbólicos sejam suportados. A ausência de falhas no Windows não prova cobertura daquela condição.

## O que este bloco não demonstra

- Não houve medição independente de qualidade de classificação, acurácia, viés ou ausência de viés.
- Os dados artificiais, incluindo seus rótulos, não representam resultados obtidos de R01 ou dos 27 pares reservados.
- O contrato real de entrada (estrutura efetiva dos arquivos reservados), autorização formal, custódia, criação de ficha real sem previsões, recepção de anotação individual e congelamento **continuam pendentes**.
- O relatório do ensaio é somente um ensaio de engenharia. O marco de autorização não pode ser deduzido automaticamente dos resultados de testes.

## Próximo passo, antes de qualquer contato com a partição reservada

Implementar o executor de avaliação real como programa **separado, bloqueado por autorização formal**, revisar seu contrato sem usar dados reservados, exercitá-lo com dados sintéticos, congelar código/versões/hashes, preencher e aprovar o termo do Bloco 32 com responsável habilitado e então preparar a ficha cega privada. Somente depois da anotação individual preservada com hash é que a pontuação real poderá ser realizada uma vez, com relato das limitações.
