# SentiVis — Bloco 30: pré-verificação e ensaio controlado da avaliação futura

**Situação em 16/11/2026: IMPLEMENTAÇÃO DE SEGURANÇA SINTÉTICA. PRÉ-REGISTRO NÃO CONGELADO. AVALIAÇÃO FINAL NÃO AUTORIZADA.**

## Objetivo e alcance

Este bloco prepara verificações técnicas exigidas pelos Blocos 26, 28 e 29: estrutura da ficha individual, integridade de documentos públicos, registro parcial do ambiente, segregação dos dados e bloqueio de repetição de um **ensaio sintético**. O projeto trabalha com uma única pessoa avaliadora, R01. O registro de controles existente não demonstra validade de um consenso humano; nenhum dado reservado é usado aqui.

O programa `backend.preflight_avaliacao_bloco30` expõe SOMENTE `verificar-ambiente` e `ensaiar`. Não existe comando para abrir a partição de 27 pares, carregar uma ficha real, ler léxicos originais ou executar o estudo final. Os arquivos reservados permanecem fora desta implementação.

## Validação do formulário (somente em memória no Bloco 30)

O CSV precisa ter estas seis colunas, nesta ordem, separadas por `;`: `id_par;frase_feminina;frase_masculina;equivalencia;rotulo;observacoes`. O validador verifica cabeçalho exato; uma linha por ID; ausência de linhas/colunas extras; textos idênticos à fonte informada; `equivalencia` em `sim`, `nao` ou vazio; rótulos `positiva`, `negativa`, `neutra` ou vazio. Quando `sim`, exige rótulo comum; quando `nao`, exige justificativa e proíbe rótulo. Não resposta é registrada como pendente, não inferida. Valores `neutra` e `sem_avaliacao` **não** são equiparados.

O comando acessível cria **somente quatro pares fictícios de IDs SINT001–SINT004**, fixados pelo Bloco 29. Não há parâmetro para importar pares reais. A ficha de ensaio, sem previsões de baseline, é produzida e validada em memória. As respostas fictícias exercitam elegibilidade, não equivalência e neutralidade; não são resultados científicos.

## Manifesto de pré-verificação

`verificar-ambiente` calcula SHA-256 de uma lista literal de arquivos **públicos** de código e protocolo; não percorre nem abre diretórios de dados. Também informa a versão de Python, versões instaladas de spaCy e `pt_core_news_sm` quando disponíveis e o `git HEAD` observado. Não lê nem calcula SHA-256 dos léxicos originais e dos dados reservados. `git HEAD` observado pode não incluir arquivos ainda não commitados; **não é o commit congelado**.

As chaves `estado=NAO_CONGELADO_NAO_AUTORIZADO`, `autorizacao_execucao_final=false`, `hash_particao_reservada=null` e `hashes_lexicos_originais=null` são deliberadas. O manifesto é incompleto para a avaliação real e não autoriza sua abertura.

## Ensaio com proteção contra repetição

`ensaiar` usa a função de simulação sintética V01/V03/V04 do Bloco 29, valida os formulários fictícios e então cria, de forma exclusiva (`open(..., 'x')`), dois arquivos em `data/piloto/restrito/bloco30_ensaio/`:

1. `marcador_tentativa_bloco30.json`: criado antes do resultado; identifica a tentativa, data UTC e hashes das fichas **fictícias** e do manifesto público.
2. `relatorio_ensaio_bloco30.json`: contém somente estatísticas sintéticas agregadas, manifesto público, status de não execução final e registro da tentativa.

Se o marcador já existir, uma nova tentativa falha; o relatório anterior não é sobrescrito. Se ocorrer erro entre marcador e relatório, o marcador permanece como evidência da tentativa: **não apagar automaticamente, não sobrescrever e documentar a falha**. Nenhum dado individual é publicado; a pasta está sob `/data/piloto/restrito/`, ignorada pelo `.gitignore` do projeto.

A proteção é uma demonstração técnica, não garantia transacional ou trava definitiva para o estudo reservado. Antes de qualquer uso real, a equipe deve revisar riscos de concorrência, falhas de I/O, permissões e o processo de custódia.

## Critérios ainda pendentes

- Aprovação e data formal do adendo de único anotador e do protocolo final.
- Revisão do protocolo de equivalência, casos incompletos e critérios de exclusão, sem olhar os 27 pares.
- Congelamento do código de execução final **ainda não existente**, dos baselines, versões, hashes dos léxicos e do modelo de linguagem, parâmetros, relatórios e tratamento de falhas.
- Implementação e revisão específica de geração cega de ficha reservada e execução real após a aprovação; realizar antes apenas testes fictícios.
- Registro da custódia e autorização de acesso ao conjunto reservado, dos responsáveis e do commit congelado.

**Testes automatizados e ensaio sintético não são validação científica, nem evidência de acurácia ou viés de gênero.**
