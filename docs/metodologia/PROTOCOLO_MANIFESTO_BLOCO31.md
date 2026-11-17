# SentiVis — Bloco 31: inventário de integridade e decisões pendentes

**Estado: PREPARAÇÃO, NÃO CONGELADO, SEM AUTORIZAÇÃO PARA AVALIAÇÃO FINAL.**

## Objetivo

Conferir localmente, em modo somente leitura, se os três arquivos textuais dos léxicos e o ZIP SentiLex-PT02 correspondem às referências de auditoria/curadoria já produzidas. Registrar hashes dos módulos relevantes e do protocolo, ambiente e configuração **proposta** para a avaliação final, sem consultar os 27 pares reservados.

## Entradas de leitura autorizadas

O módulo `backend.manifesto_lexicos_bloco31` lê exclusivamente:

- `data/lexicos/relatorio_curadoria.json` (zero falhas de leitura e SHA-256 por fonte);
- `data/lexicos/relatorio_auditoria.json` (SHA-256 das fontes originais, SHA-256 e MD5 do ZIP);
- Em `data/lexicos/originais/`, exatamente uma ocorrência de `lexico_v3.0.txt`, `SentiLex-lem-PT02.txt`, `SentiLex-flex-PT02.txt` e `SentiLex-PT02.zip` (eventualmente em subpastas de extração);
- Arquivos de código e metodologia da lista constante `CODIGO_E_PROTOCOLOS`, declarada no próprio módulo.

O ZIP é conferido contra o MD5 publicado para o SentiLex-PT02: `026e1dceeaa506cc048d6ce7e0174cd0`, além da auditoria local. Arquivos ausentes, duplicados ou com divergência de checksum geram erro e impedem registrar um manifesto consistente. As verificações não alteram as fontes. **Integridade de arquivo não demonstra adequação linguística, validade científica, qualidade das anotações ou ausência de vieses.**

Os caminhos são fixos. O utilitário não aceita caminho de entrada pelo CLI, não varre a pasta de avaliação e não lê arquivos da pasta `data/piloto`. Não realiza classificação, treinamento nem inferência.

## Configuração registrada, ainda sujeita à aprovação

- Análise primária proposta: SentiLex-PT02 e baselines V01/V03/V04.
- Alvo lexical `N0` **informado manualmente**, não resolvido pela frase.
- `hipotese_modo=True` em V03 e V04; V01 sem essa hipótese contextual.
- Uma pessoa anotadora na avaliação final; sem concordância interavaliadores.
- Recorte primário de coincidência descritiva somente para marcações positivas/negativas e frases pontuadas; neutros humanos em estrato próprio; abstenção não é zero.
- Diferença feminina−masculina somente quando ambas as frases elegíveis são pontuadas no mesmo baseline.

Este registro descreve a configuração **proposta**, não a congela nem comprova sua aplicação. OpLexicon não está incluído na análise primária; sua integridade é inventariada para a rastreabilidade dos léxicos de origem.

## Saídas e controles

- `verificar`: imprime JSON de integridade e ambiente, sem gravar arquivo.
- `registrar`: calcula novamente e cria **uma única vez** `data/piloto/restrito/bloco31_manifesto/manifesto_preliminar_bloco31.json`. O modo de escrita exclusivo não sobrescreve registro anterior.
- O manifesto registra SHA-256 dos arquivos de código e relatórios, commit **observado**, Python e versões instaladas de spaCy e `pt_core_news_sm`. Não registra rótulos, frases da partição reservada nem inferências de desempenho.
- O registro privado está coberto pelo `.gitignore`. Não publicar ou mover as fontes lexicais para GitHub; adicionar seletivamente apenas código, testes e documentação.
- Uma execução futura após novo commit pode produzir hashes distintos. O arquivo anterior permanece como evidência de estado, **não** como congelamento definitivo.

## Itens pendentes antes de liberar a avaliação final

1. Responsáveis pelo TCC revisarem e aprovarem por escrito os critérios e o uso de um único anotador; registrar data, identidade/função e versão do protocolo.
2. Finalizar e testar em dados sintéticos o procedimento específico de autorização, extração da ficha reservada, preservação de seu hash e processamento único da avaliação final.
3. Formalizar versões/código final (SHA do commit), recursos, modo de execução e tratamento de exceções, abstenções e exclusões **antes** de acessar os 27 pares.
4. Aprovar o checklist do Bloco 28, sem marcar etapas não concluídas como concluídas.
5. Somente após o congelamento e a autorização formal, colher a anotação individual sem mostrar previsões, preservar a ficha e então executar a comparação final.

**Nenhum passo deste Bloco 31 abre, classifica ou autoriza os 27 pares reservados.**
