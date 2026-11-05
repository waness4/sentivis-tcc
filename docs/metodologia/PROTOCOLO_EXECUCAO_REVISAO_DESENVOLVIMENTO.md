# SentiVis — Operação da revisão humana independente (desenvolvimento)

**Versão:** 0.1 — procedimento de piloto, sujeito à aprovação dos responsáveis pela pesquisa.

## Escopo e princípios

- O piloto só permite anotação e processamento dos **9 pares de desenvolvimento** previamente definidos em três famílias. Os **27 pares de avaliação** continuam reservados, sem acesso ao classificador nesta etapa.
- Cada revisor humano recebe uma ficha sem classe planejada e sem respostas de outros revisores. ID de revisor é pseudônimo distinto; IDs diferentes não comprovam por si mesmos independência efetiva.
- As duas frases devem diferir somente na referência de gênero e nas concordâncias necessárias, sem mudança de sentido avaliativo. O rótulo é uma avaliação humana, não derivada do léxico.
- Valores possíveis: `equivalencia`: `sim` ou `nao`; `rotulo`: `positiva`, `negativa` ou `neutra`. Em caso de `nao`, justificativa obrigatória, e o rótulo pode ficar em branco.
- Pares com discordâncias ou não equivalência exigem adjudicação humana independente, com decisão e justificativa registradas separadamente. Ausência de adjudicação impede aprovação do par para estudos que exigem equivalência comprovada.
- O sistema não altera frases fornecidas, não consulta o classificador, não resolve automaticamente discordâncias e não altera a partição de avaliação.

## Auditoria e proteção de dados

- Guardar as fichas originais separadas, com data de preenchimento, sem acrescentar nomes ou outras informações pessoais.
- Registrar SHA-256 do conjunto candidato e de cada ficha, além do consolidado. Manter arquivos imutáveis após cada etapa; revisões posteriores devem gerar nova versão.
- Os dados de avaliação e as anotações humanas ficam na pasta `data/piloto/restrito/`, excluída do Git por `.gitignore`. Conferir o resultado de `git status` antes de cada `push`.
- A análise exploratória de desenvolvimento é insuficiente para concluir viés de gênero, qualidade do classificador ou significância estatística. A independência semântica, o método lexical e o tratamento da abstenção requerem validação adicional.

## Critério de passagem

1. Dois revisores humanos distintos enviaram as fichas.
2. Validação estrutural das fichas sem erros; originais preservados.
3. Todos os casos `PENDENTE_ADJUDICACAO` foram analisados por terceiro avaliador ou explicitamente excluídos segundo decisão pré-especificada.
4. Apenas pares elegíveis são analisados, e somente dentro da partição de desenvolvimento.
5. As decisões e limitações são documentadas antes da avaliação final.
