# Protocolo de interface v0.2 — apresentação exploratória

## Escopo

Esta versão facilita a demonstração de correspondência lexical e comparação descritiva de frases femininas e masculinas. Mantém o baseline aditivo v0.1, o mesmo backend e os mesmos contratos HTTP. Não produz métricas científicas validadas.

## Linguagem visual e interpretação

- Pontuação e classe devem ser identificadas como **exploratórias** em todos os cartões.
- A cobertura exibida é **cobertura superficial de tokens ortográficos**, não acurácia nem representatividade estatística.
- Um delta `0` significa apenas igualdade das somas exploratórias naquele par, não ausência de viés.
- Delta diferente de zero exige investigação, mas não é prova de viés de gênero.
- Um delta não deve ser exibido numericamente quando uma das frases se abstém.
- A equivalência semântica depende de revisão humana independente, não é inferida pela interface.
- A partição de avaliação reservada não é consultada ou exibida.

## Testes de manutenção

`backend/tests/test_refino_interface.py` verifica contratos estáticos essenciais; os testes existentes de `test_ui_server.py` seguem responsáveis pelas rotas e respostas da API. Um teste exploratório de navegador utilizou respostas simuladas e confirmou visualização, comparação, comportamento móvel e ausência de exceções JS. Simulações não substituem testes integrados com os léxicos reais.

## Decisões técnicas

- Somente arquivos em `frontend/` foram alterados na interface.
- O favicon é local e não adiciona dependências externas.
- As respostas são renderizadas com escape de HTML nos dados variáveis.
- Uma sequência de requisições invalida respostas obsoletas depois da troca de aba, léxico ou alvo.
- As análises continuam sem integração com os arquivos dos revisores e com a avaliação reservada.
