# Capturas reais da interface

Esta pasta reúne **capturas reais do SentiVis em execução**, enviadas em 17/11/2026. Não são imagens simuladas nem evidência da avaliação científica reservada.

| Arquivo | Conteúdo | Situação |
| :--- | :--- | :--- |
| [02-analise-sentimentos.png](02-analise-sentimentos.png) | OpLexicon e resultado de “O atendimento foi excelente.”: +1 e cobertura superficial 25%. | Captura recebida e publicada |
| [03-comparacao-genero.png](03-comparacao-genero.png) | Comparação demonstrativa “A aluna é dedicada.” / “O aluno é dedicado.”: +1 para ambas, delta descritivo 0. | Captura recebida e publicada |
| [01-pagina-inicial.png](01-pagina-inicial.png) | Página inicial do laboratório SentiVis, com cabeçalho, módulo de exploração lexical, configuração do léxico e campo de análise. | Captura recebida e publicada |

A segunda e a terceira imagens recebidas mostravam a **mesma captura**, portanto foi mantida uma única cópia.

## Página inicial registrada

A captura [01-pagina-inicial.png](01-pagina-inicial.png) foi publicada com o nome padronizado e é exibida na seção **Interface e capturas** do [README principal](../../README.md#interface-e-capturas).

Para futuras atualizações, execute `python -m uvicorn backend.ui_server:app --reload`, abra `http://127.0.0.1:8000/` e registre a interface sem dados privados ou conteúdo reservado. Substitua o arquivo correspondente e atualize a documentação apenas quando a nova imagem refletir a versão efetivamente apresentada.

## Cuidados científicos

As capturas exibem exemplos demonstrativos. A pontuação exploratória não é uma validação da interpretação integral da frase. Uma cobertura de 25% não é confiança, precisão nem percentagem de sentimento. A diferença zero na comparação não prova inexistência de viés.

Nunca exponha os 27 pares reservados, arquivos de anotação ou informações pessoais de participantes. Ver [segurança e dados](../SEGURANCA_E_DADOS.md).
