# SentiVis — Protocolo V03: hipótese contextual sintática do SentiLex

## Estado e escopo

**Versão de engenharia exploratória**. Nenhuma inferência sobre viés de gênero, capacidade de generalização, causalidade, discriminação ou validade do alvo lexical foi realizada. O baseline V01 (`backend.baseline_experimental`) e o filtro OpLexicon V02 (`backend.baseline_gramatical_v02`) permanecem intactos. V03 não substitui V01/V02 na interface, API ou piloto existente.

O objetivo é **testar uma hipótese estrutural explícita**, em vez de somar indiscriminadamente todas as ocorrências lexicais de uma frase. O sistema **não interpreta automaticamente N0/N1**: somente produz pontuações quando `--alvo N0` ou `--alvo N1` é selecionado pelo operador e `--hipotese-modo` é ativado. O alvo informado constitui **hipótese manual não validada**, não uma análise da dependência semântica de uma pessoa.

## Entradas e pré-condições

1. Entradas SentiLex verificadas pelo mecanismo `carregar_para_consulta`, incluindo conferência de SHA-256 frente ao manifesto da curadoria. Não modificar léxicos originais.
2. Frase única ou par de frases passado explicitamente na linha de comando. **Não existe varredura automática de pares reservados à avaliação final** no módulo de classificação.
3. Modelo spaCy `pt_core_news_sm` treinado com análise morfossintática; versão registrada no JSON.
4. Alvo N0/N1 manual obrigatório para pontuar. Sem alvo, a decisão permanece uma abstenção; sem `--hipotese-modo`, um candidato sintático permanece uma abstenção por hipótese não autorizada.
5. O mesmo controle conservador de V01 prevalece: ausência de cobertura, conflitos/entradas suspeitas, negações e modificadores conhecidos continuam bloqueando pontuações. A falta de detecção não implica ausência desses fenômenos.

## Heurística hipotética (não é desambiguação semântica)

1. A V01 detecta as palavras SentiLex e determina quais valores do alvo **manual** são consistentes no registro lexical.
2. Para cada ocorrência, alinhar offsets com **um único token spaCy** e conferir categoria SentiLex contra PoS estimada. Falha, categoria desconhecida, expressão composta não suportada ou divergência de PoS => abstenção.
3. Procurar substantivo com um filho gramatical `case` de texto `com`, cuja etiqueta sintática seja `obl` e cuja cabeça seja um token verbal (`VERB`). Isso constitui uma **pista estrutural** de possível qualificação do ato; **não comprova** que se trate de modo, em vez de instrumento ou companhia.
4. Qualquer candidato com `com` e `nmod` é considerado **anexação ambígua** e leva à abstenção da frase inteira. Demais ligações não suportadas não são promovidas a qualificação.
5. Somente se houver **exatamente um** candidato com a pista sintática admitida e nenhuma anexação `nmod` ambígua, e `--hipotese-modo` tiver sido explicitamente ativado, retornar sua polaridade lexical. Ocorrências em argumentos como `obj` são registradas mas **não somadas automaticamente**. Se houver zero ou mais de um candidato, abster-se.
6. Exibir token, PoS, dependência, cabeça, fonte, polaridade da entrada e decisão. Os valores de `classe_exploratoria`, se presentes, permanecem **hipóteses não validadas**.

### Exemplos exploratórios de desenvolvimento

- P004 (`...tratou ... com gentileza`): quando `gentileza` recebe `obl` ligado ao verbo, a hipótese seleciona `+1` **somente com N0 manual e hipótese ativada**.
- P005 (`...tratou ... com grosseria`): analogamente, pode selecionar `-1`.
- P007 (`...resolveu o problema com habilidade`): quando `habilidade` recebe `nmod` de `problema`, **abster-se**; não ignorar a anexação ambígua para forçar um acerto.
- P008 (`...resolveu o problema com descuido`): quando `descuido` recebe `obl` de `resolveu`, a hipótese pode selecionar `-1`, sem somar o `-1` lexical de `problema` que atua como objeto.

Esses exemplos serviram para **desenvolver** a heurística. **Não são uma avaliação independente** nem evidência de generalização. O modelo spaCy pode prever etiquetas diferentes em outras instalações/versões. Uma hipótese sintática positiva/negativa pode estar semanticamente incorreta mesmo com todas as verificações satisfeitas.

## Comparador de desenvolvimento V01 x V03

`backend.comparacao_sentilex_v01_v03` lê o CSV consolidado, usa as verificações estruturais de `backend.pares_piloto`, filtra **antes de classificar** somente pares `particao=desenvolvimento` e `status_revisao=APROVADO_DUPLA_REVISAO`, e calcula estatísticas descritivas condicionadas às frases pontuadas. Frases de `particao=avaliacao` **não são submetidas a classificadores**. O programa salva estatísticas resumidas JSON e linhas descritivas CSV em caminhos escolhidos pelo operador e **recusa sobrescrever arquivos**.

Para comparação homogênea, tanto V01 como V03 recebem a **mesma hipótese de alvo manual global** (`--alvo N0` ou N1). Isso difere do baseline V01 original **sem alvo**, que necessariamente se abstinha no SentiLex. Essa comparação mostra as consequências da hipótese manual e da seleção sintática, **não** o efeito isolado de uma resolução de N0/N1 automaticamente aprendida. Devem ser relatadas juntas a fração pontuada, a acurácia seletiva (quando definida), o número de previsões corretas/incorretas e a quantidade de abstenções. Não comparar acurácias condicionadas omitindo as abstenções.

## Limitações e próximos passos

- `com` pode introduzir modo, instrumento, acompanhamento ou outra relação. Etiquetas `obl`/`nmod` são estimativas do parser, não provas semânticas.
- Alvos `HUM:N0/N1` do SentiLex não foram associados a referentes concretos. Seleção manual não é validação do alvo.
- Não há tratamento completo de negação, ironia, intensificadores, contexto discursivo, foco ou polissemia.
- Apenas sintagmas estreitos de `com + substantivo` estão no escopo; substantivos de avaliação que funcionem como objetos (p.ex., `demonstrou dedicação`) não recebem classificação contextual por esta regra.
- Casos sintéticos cobrem a engenharia, não validam o spaCy ou a eficácia científica do classificador.
- A V03 usa exemplos de desenvolvimento; melhorar o desempenho neles pode ser **sobreajuste**. Não escolher regras adicionais mirando os 27 pares reservados e não liberar a avaliação final antes de congelar método, critérios e versões.
- A revisão humana exige registro separado da independência dos revisores e do procedimento de reavaliação.
- Antes de integrar V03 à interface, avaliar erros em frases externas ao piloto e realizar revisão metodológica dos alvos N0/N1 e do protocolo.

## Reprodutibilidade

Preservar: arquivos originais com hashes conferidos; CSV de desenvolvimento aprovado em pasta restrita; JSON/CSV gerados em pasta restrita; nome e versão do spaCy e do `pt_core_news_sm`; código Git commit; comandos e opções de alvo/hypótese. Não publicar fichas humanas, resultados privados, nem dados originais sem verificar licenças. A análise final continua isolada.
