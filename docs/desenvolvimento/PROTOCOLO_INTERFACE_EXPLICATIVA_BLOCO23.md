# Bloco 23 — protocolo de apresentação e transparência

## Objetivo

Tornar os resultados do laboratório SentiVis legíveis para usuários sem formação
em PLN, preservando integralmente os dados e decisões dos baselines V01/V04.

## Restrições técnicas

1. Somente `frontend/app.js` e `frontend/styles.css` podem alterar a experiência.
   Os endpoints e algoritmos permanecem iguais aos do Bloco 22.
2. O estado de abstenção é representado como ausência de pontuação, nunca como
   classe neutra nem como zero numérico.
3. A origem dos termos, versões, códigos, motivos, filtragem e manifesto lexical
   permanecem acessíveis na seção de detalhes técnicos e no JSON exportado.
4. Códigos conhecidos recebem descrições em português; códigos desconhecidos
   mantêm identidade explícita de motivo técnico sem tradução inventada.
5. Conteúdo dinâmico recebido do backend é escapado antes de entrar no HTML.
6. A interface não lê arquivos da pasta de dados reservados nem apresenta
   respostas, métricas ou exemplos baseados no conjunto final.

## Cobertura lexical superficial

A cobertura informa a fração de tokens com correspondência superficial em uma
entrada do léxico. Ela **não** representa acurácia, confiança, intensidade do
sentimento ou qualidade de classificação. Candidatos identificados mas depois
bloqueados por categoria gramatical podem continuar contando na cobertura.

## Abstenções contextuais

Para `ABSTENCAO_ANEXACAO_AMBIGUA`, apresentar a expressão reconhecida sem
atribuir sentimento global. Exemplo diagnóstico C005: `segurança` tem entrada
lexical, mas a ligação sintática a um substantivo foi considerada incerta. A
entrada neutra `dados`, incompatível gramaticalmente, pode ser ignorada na
decisão V04 sem solucionar a anexação de `segurança`.

## Comparação entre referências de gênero

O campo delta só é exibido numericamente quando o backend informa que ambas
as análises foram pontuáveis. A diferença descritiva não constitui demonstração
de viés. O sistema não resolve automaticamente equivalência semântica nem alvo
`N0/N1`.

## Validação do Bloco 23

- Suíte de backend de referência: 317 testes.
- Testes novos de contrato de interface: 19 testes.
- Total observado no ambiente de montagem: **336 testes aprovados**.
- JavaScript: `node --check frontend/app.js` validado.
- Verificação dinâmica adicional: abstenção C005, pontuação zero, escape HTML e
  comparação com delta não calculável; sem necessidade de Node no computador
  do usuário para executar a aplicação.
- Validação visual final no Windows com os léxicos locais ainda é necessária.
