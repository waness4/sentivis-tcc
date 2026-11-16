# Bloco 21 — Protocolo pré-definido de anotação humana dos 36 controles

**Natureza:** diagnóstico de desenvolvimento. **Não é avaliação final independente**, nem estudo confirmatório de viés de gênero. Os controles foram escritos para diagnosticar a V03 e examinados durante o aperfeiçoamento da V04.

## Base e blindagem

- Fonte fixa: `data/controles/controles_sintaticos_v01.csv`, SHA-256 `a027295544514c7e3db70abc99e92ab799015ee1f7416157748951b5a896b9bc`; 36 frases únicas.
- Duas fichas diferentes, embaralhadas deterministicamente, com apenas `id_controle`, `texto`, `polaridade`, `referente`, `papel_com`, `observacoes`. O tipo de cenário e as predições dos baselines **não são mostrados**.
- Entregar a cada anotador apenas sua ficha e a seção **Instruções ao anotador** abaixo. Cada pessoa trabalha sozinha, sem consultar os baselines, léxicos, relatórios, os outros controles ou respostas do outro anotador.
- Identificar as pessoas como `R01` e `R02`. O software não consegue confirmar a independência de fato; a equipe deve confirmá-la documentalmente.
- Não usar os 27 pares reservados da avaliação final, nem as fichas de 9 pares do desenvolvimento como substitutos desta anotação.

## Instruções ao anotador

Analise **o sentido expresso na frase**, não a polaridade isolada de uma palavra. **Não associe automaticamente o gênero gramatical da pessoa à polaridade**. Não consulte classificadores, léxicos ou respostas de outras pessoas.

Preencha as seguintes categorias exatamente, sem acentos adicionais, em minúsculas:

**`polaridade`:**
- `positiva`: avaliação predominantemente favorável expressa.
- `negativa`: avaliação predominantemente desfavorável expressa.
- `neutra`: avaliação efetivamente neutra ou sem orientação positiva/negativa dominante, quando ainda existe conteúdo avaliativo.
- `sem_avaliacao`: descrição factual sem opinião/avaliação identificável. Não confundir com ausência de entrada no léxico.
- `mista`: avaliações positivas e negativas distintas na mesma frase, sem predomínio seguro.
- `indeterminada`: contexto insuficiente, ironia possível, referência ambígua ou sentido não decidível.

**`referente`:** o principal alvo interpretado da avaliação: `agente` (quem realiza a ação), `acao` (modo/qualidade do ato), `objeto` (entidade mencionada), `terceiro` (outra pessoa), `multiplos`, `nenhum` (frase sem avaliação), `indeterminado`.

**`papel_com`:** classifique o papel da construção com a preposição **com**, quando houver: `modo` (maneira), `instrumento` (meio material), `companhia` (acompanhante), `outro`, `ambiguo` (duas leituras sustentáveis) ou `nao_aplicavel` (frase sem a preposição *com*). Quando há mais de uma ocorrência de *com*, marque a mais relevante para a avaliação e explique em `observacoes`.

**`observacoes`:** campo livre, sem dados pessoais. É obrigatório para `mista`, `indeterminada`, referente `indeterminado` ou papel `ambiguo`; nos demais casos, opcional. Não deixar os outros três campos vazios. **Não alterar os valores de `id_controle` ou `texto`.**

Exemplos ilustrativos **que não pertencem aos controles**:
- “Ela atendeu com gentileza.” → `positiva`; `acao`; `modo`.
- “Ele abriu o cadeado com uma chave.” → `sem_avaliacao`; `nenhum`; `instrumento`.
- “Ela encontrou os colegas com o professor.” → `sem_avaliacao`; `nenhum`; `companhia` **ou** `ambiguo`, conforme a interpretação e observação explicitadas.

## Consolidação e conflitos

- A consolidação **não cria rótulos**, não altera os julgamentos, não desempata, não faz maioria e não lê resultados da V01–V04.
- O relatório informa contagens e percentuais de concordância por coluna, a proporção de concordância total e o kappa de Cohen para `polaridade` (descritivo, pode ser indefinido). Concordância entre avaliadores **não é** acurácia do modelo.
- Qualquer discrepância em `polaridade`, `referente` ou `papel_com` recebe `DIVERGENCIA_PENDENTE`. Para uma referência adjudicada posterior é preciso protocolo adicional, registro de motivos e intervenção humana separada. Não substituir desacordo por um rótulo do sistema.
- Somente depois de decidir um procedimento de adjudicação poderão ser calculadas estatísticas **diagnósticas** de acerto/erro nos exemplos avaliáveis, acompanhadas da taxa de abstenção. Os casos com `mista`, `sem_avaliacao` e `indeterminada` não devem ser mapeados automaticamente a classes do classificador sem justificação prévia.
- O alvo `N0` ou `N1` dos baselines é manual, não validado: a anotação de `referente` não resolve sozinha o alinhamento da pessoa-alvo com as entradas lexicais.

## Restrições e rastreabilidade

- Congelar fontes e versões do classificador ao relatar resultados. Registrar hash de cada ficha antes da análise. O script faz os hashes.
- Não publicar respostas individuais, as fichas preenchidas ou o CSV de consolidação na versão pública do repositório. Preferir `data/piloto/restrito` (já usado no projeto); conferir `.gitignore` antes de qualquer `git add`.
- O conjunto é pequeno, autoral, selecionado de forma intencional e utilizado no desenvolvimento; logo, **não extrapolar** a população de textos em português. Não calcular métrica de viés de gênero a partir desses controles.
- Os **27 pares reservados** permanecem sem leitura, sem rótulo e sem classificação nesta etapa.
