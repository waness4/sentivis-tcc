# Capturas reais da interface

Esta pasta reúne **capturas reais do SentiVis em execução**, enviadas em 17/11/2026. Não são imagens simuladas nem evidência da avaliação científica reservada.

| Arquivo | Conteúdo | Situação |
| :--- | :--- | :--- |
| [02-analise-sentimentos.png](02-analise-sentimentos.png) | OpLexicon e resultado de “O atendimento foi excelente.”: +1 e cobertura superficial 25%. | Captura recebida e publicada |
| [03-comparacao-genero.png](03-comparacao-genero.png) | Comparação demonstrativa “A aluna é dedicada.” / “O aluno é dedicado.”: +1 para ambas, delta descritivo 0. | Captura recebida e publicada |
| `01-pagina-inicial.png` | Visão geral da interface com título, seletor de léxico e campo de análise. | Pendente — não inventar nem reutilizar outro print |

A segunda e a terceira imagens recebidas mostravam a **mesma captura**, portanto foi mantida uma única cópia.

## Registrar a página inicial pendente

1. Execute `python -m uvicorn backend.ui_server:app --reload` no diretório do projeto.
2. Acesse `http://127.0.0.1:8000/` e deixe a aba **Analisar frase** vazia.
3. Com o navegador maximizado, capture o título, a configuração lateral e a área do laboratório.
4. Confirme que não aparecem dados privados, notificações ou informações reservadas.
5. Salve em PNG com o nome `01-pagina-inicial.png` e atualize a galeria do README.

## Cuidados científicos

As capturas exibem exemplos demonstrativos. A pontuação exploratória não é uma validação da interpretação integral da frase. Uma cobertura de 25% não é confiança, precisão nem percentagem de sentimento. A diferença zero na comparação não prova inexistência de viés.

Nunca exponha os 27 pares reservados, arquivos de anotação ou informações pessoais de participantes. Ver [segurança e dados](../SEGURANCA_E_DADOS.md).
