# SentiVis — Relatório parcial de resultados e limitações metodológicas

**Bloco 25 | Situação em 16/11/2026 | Documento de desenvolvimento, não resultado final de TCC**

> **Regra de uso:** este texto consolida informações de execuções já relatadas e protocolos versionados. Antes de incorporar números ao manuscrito definitivo, conferir os JSON/CSV originais na máquina do projeto, seus manifestos, hashes e parâmetros. Nenhum arquivo de avaliação final foi consultado para a elaboração deste relatório.

## 1. Escopo da pesquisa implementada

O SentiVis é um protótipo de auditoria, curadoria e exploração rastreável de léxicos de sentimentos em português, apoiado em OpLexicon 3.0 e SentiLex-PT02. A aplicação possui interface web com análise de frases, comparação exploratória de referências de gênero, apresentação da cobertura lexical e explicação explícita das abstenções. Os baselines contextuais SentiLex V03 e V04 são **hipóteses** dependentes de etiquetas sintáticas do spaCy, não classificadores de sentimento validados ou instrumentos que, isoladamente, demonstram viés de gênero.

As três camadas devem ser tratadas separadamente: (a) auditoria das entradas dos léxicos; (b) análise exploratória de frases com abstenção; (c) avaliação empírica com referência humana. Sucesso técnico da camada (a) ou (b) não valida automaticamente a camada (c).

## 2. Rastreabilidade dos conjuntos

| Conjunto | Tamanho | Uso permitido nesta etapa | Estado |
|---|---:|---|---|
| Pares do piloto de desenvolvimento | 9 pares / 18 frases | Desenvolvimento, análises descritivas, inspeção de erros | Revisão prévia registrada; confirmar independência e documentação das fichas |
| Controles sintáticos (`data/controles/controles_sintaticos_v01.csv`) | 36 frases | Diagnóstico de robustez e abstenções | Predições inspecionadas; fichas de dois avaliadores preparadas; rótulos humanos ainda não consolidados |
| Pares reservados para avaliação final | 27 pares | Somente após protocolo, versões e critérios congelados | **Não abrir, não pontuar, não ajustar regras com base nesses dados** |

Os 36 controles são autorais e já foram examinados durante o refinamento V04. Mesmo com anotação humana posterior, **não constituem teste independente de generalização**. O arquivo dos controles possui SHA-256 `a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc`, conforme o protocolo versionado do Bloco 20.

## 3. Auditoria e curadoria lexical — números registrados anteriormente

Conforme os relatórios das execuções de auditoria e curadoria relatados durante o desenvolvimento (a conferir nos respectivos arquivos locais):

- OpLexicon: **32.191** registros interpretados.
- SentiLex-lem: **7.014** registros interpretados.
- SentiLex-flex: **82.347** registros interpretados.
- Total processado entre as três fontes: **121.552** registros.
- **9.494** registros sinalizados para revisão e **2.003** conflitos termo/categoria/alvo registrados na triagem.

Essas contagens representam processamento e **sinalizações para inspeção**; não demonstram correção efetiva de todas as entradas, prevalência de viés de gênero ou acerto de classificação de frases. Os léxicos originais devem permanecer íntegros, com manifestos e SHA-256 preservados.

## 4. Resultados exploratórios já obtidos

### 4.1 SentiLex nos 9 pares de desenvolvimento (18 frases)

Comparação registrada entre V01 aditivo e V03 contextual, ambas com **N0 fornecido manualmente**, V03 com hipótese de modo ativada:

| Indicador | SentiLex V01 com N0 manual | SentiLex V03 com N0 manual e hipótese |
|---|---:|---:|
| Frases examinadas | 18 | 18 |
| Frases com pontuação | 10 | 6 |
| Acertos entre frases pontuadas, conforme referência do desenvolvimento | 8 | 6 |
| Erros entre frases pontuadas | 2 | 0 |
| Frases sem pontuação | 8 | 12 |
| Cobertura de pontuação | 55,6% | 33,3% |
| Acurácia **seletiva** (apenas sobre pontuadas) | 80,0% | 100,0% |

**Interpretação:** a V03 produziu menos classificações e, nessa pequena amostra usada no desenvolvimento, não errou entre aquelas que decidiu classificar. O resultado de 100% é **condicional à abstenção**, não mede acurácia sobre todas as frases, não garante generalização e não demonstra redução de viés. A referência humana e sua independência devem ser documentadas.

**Não confundir:** o comportamento do OpLexicon em uma comparação separada V01/V02 não é diretamente intercambiável com os números da tabela SentiLex; são léxicos e critérios diferentes.

### 4.2 Controles sintáticos sem rótulos (36 frases)

| Indicador | SentiLex V01 | SentiLex V03 | SentiLex V04 |
|---|---:|---:|---:|
| Frases com pontuação | 14 | 1 | 1 |
| Frases sem pontuação | 22 | 35 | 35 |
| Taxa de pontuação | 38,9% | 2,8% | 2,8% |

Na comparação V03→V04, a filtragem de correspondências neutras com categoria gramatical incompatível foi aplicada em **2 frases**, C005 e C006. Nesses dois casos, o status principal mudou de `ABSTENCAO_CATEGORIA_GRAMATICAL` para `ABSTENCAO_ANEXACAO_AMBIGUA`, sem produzir pontuação. Exemplo: `dados`, encontrado como adjetivo neutro no SentiLex, é etiquetado como substantivo no contexto; `segurança` / `arrogância` permanecem ligadas nominalmente segundo a análise sintática.

**Interpretação:** a V04 melhorou o diagnóstico dos dois casos analisados, mas **não ampliou a taxa de pontuação** no conjunto de controles. Sem rótulos humanos nesses controles, não são calculáveis acurácia, F1 ou taxa de erro; a mudança do motivo de abstenção não é um acerto comprovado.

## 5. Estado técnico

- API FastAPI, interface web e seleção explícita entre V01 e V04, com avisos de limitação e exportação exploratória de JSON.
- Melhorias visuais até o Bloco 24, commit registrado `dc08f10` em `main`.
- **345 testes automatizados aprovados** na execução informada no PowerShell em 16/11/2026. Isso verifica comportamento do software nos casos testados, não validade científica.
- A interface não deve acessar as fichas humanas, relatórios privados ou os 27 pares reservados.

## 6. Ameaças à validade que devem aparecer no TCC

1. **Amostra e seleção:** 9 pares de desenvolvimento e 36 controles autorais são pequenos e foram usados para diagnosticar/refinar regras. Estatísticas não representam a população de textos PT-BR.
2. **Abstenção:** reportar sempre cobertura de pontuação, acertos, erros e não pontuadas em conjunto. Não apresentar somente a acurácia seletiva de 100%.
3. **Alvo manual N0/N1:** selecionar N0 não demonstra que a polaridade lexical foi corretamente associada ao referente na frase.
4. **Sintaxe imperfeita:** o etiquetador spaCy pode errar PoS e anexação `nmod`/`obl`; a preposição `com` pode indicar modo, instrumento ou companhia.
5. **Viés de gênero:** diferença descritiva entre duas frases, inclusive zero, **não** confirma ou descarta viés. Para alegação causal ou estatística seriam necessários desenho, referência, métricas e amostra adequados.
6. **Exposição do controle C001:** uma mensagem de orientação elaborada anteriormente usou como exemplo a frase “A fisioterapeuta explicou a tarefa com clareza.”, que pertence aos controles. **Confirmar se ela foi enviada aos anotadores**; se sim, registrar a exposição, assinalar C001 como potencialmente contaminado e fazer uma análise de sensibilidade sem esse item, sem apagar a ocorrência do conjunto.
7. **Independência dos avaliadores:** duas fichas com códigos diferentes não comprovam revisão independente; confirmar procedimento e registrar o histórico sem expor nomes.
8. **Categorias de referência:** `sem_avaliacao`, `neutra`, `mista` e `indeterminada` são distintas no protocolo dos controles e não devem ser convertidas automaticamente às três classes do baseline.

## 7. Critérios de passagem para o próximo estágio

- Receber as duas fichas completas dos 36 controles; preservar os arquivos originais sem editar ou divulgar.
- Validar preenchimento e integridade com o comando existente `python -m backend.anotacao_controles_v01 consolidar --pasta-saida .\data\piloto\restrito` **somente após** receber as duas fichas. O processo calcula concordância descritiva, kappa e divergências, mas não adjudica.
- Resolver ou documentar divergências humanas segundo protocolo adicional antes de calcular métricas de concordância com o classificador.
- Fixar por escrito versão de cada baseline, critério de abstenção, procedimento de comparação, unidade de análise (frase/par), regras para classes não comparáveis e modelo de apresentação das métricas.
- Somente depois definir e executar, uma única vez, a avaliação independente dos 27 pares reservados. **Não consultar esse conjunto para escolher regras, limiares ou exemplos demonstrativos.**

## 8. Texto-base para a seção Resultados parciais do TCC

> A implementação do SentiVis permitiu auditar léxicos de sentimentos em português e desenvolver baselines lexicais exploratórios com abstenção explícita em situações não resolvidas. Nos nove pares de desenvolvimento previamente revisados, a versão contextual do SentiLex atribuiu pontuação a seis de 18 frases, todas coincidentes com a referência utilizada nessa etapa, enquanto a versão aditiva com alvo manual pontuou dez de 18 frases, com oito coincidências. Tal diferença deve ser lida juntamente com a redução da cobertura de pontuação, pois a melhora da acurácia seletiva não equivale a ganho geral de desempenho. Nos 36 controles sintáticos sem rótulos humanos consolidados, as versões V03 e V04 pontuaram uma frase cada, e a V04 alterou os motivos de abstenção em dois casos sem produzir novas pontuações. Esses resultados descrevem comportamentos de desenvolvimento e diagnóstico; não sustentam, por si sós, inferências de viés de gênero ou de generalização a textos não observados.

**Status deste relatório:** preliminar; sujeito à verificação dos relatórios locais e à consolidação das anotações humanas. Não substituir com números de avaliação final antes da execução formal do protocolo.
