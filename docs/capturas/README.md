# Capturas reais da interface

Ainda não há capturas verificadas da aplicação no repositório. **Não usar imagens geradas, simulações de tela ou montagens como se fossem prints da execução real.**

## Como registrar prints com segurança

1. No seu ambiente local, execute `python -m uvicorn backend.ui_server:app --reload` e abra http://127.0.0.1:8000/.
2. Use apenas **exemplos públicos ou frases inteiramente inventadas**. Nunca use os 27 pares reservados, fichas de pessoas avaliadoras ou anotações privadas.
3. Capture, preferencialmente em resolução desktop, os arquivos `inicio.png` (visão geral), `analise-exploratoria.png` (resultado de demonstração) e `comparacao-exploratoria.png` (exemplo artificial feminino/masculino).
4. Revise cada imagem: ocultar notificações, nomes de pastas privadas, tokens, contas, e-mails, caminhos locais e quaisquer elementos não destinados à publicação.
5. Ao aprovar cada arquivo, adicione-o a `docs/capturas/` e então inclua no README a imagem Markdown, com legenda de que a operação é **exploratória**.

Exemplo de inclusão após verificar que a captura existe:

```markdown
![Interface real do laboratório SentiVis](docs/capturas/inicio.png)
```

Os exemplos para captura devem mostrar a interface e seu estado, **não alegar desempenho científico**. A exibição de uma diferença de pontuação nunca deve ser rotulada como prova de viés.
