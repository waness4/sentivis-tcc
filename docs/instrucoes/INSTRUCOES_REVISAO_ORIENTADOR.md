# Instruções — encaminhamento ao orientador (sem novo ensaio)

1. Consulte `docs/metodologia/SOLICITACAO_REVISAO_ORIENTADOR.md` e `docs/metodologia/REGISTRO_DECISOES_PRELIMINARES.md`.
2. Envie ao orientador o pedido **preliminar** de revisão das decisões G01–G04/G06, citando os documentos de apoio. Não peça liberação final ainda.
3. Registre apenas decisões efetivamente recebidas em canal acadêmico verificável; não preencha o modelo como se houvesse aprovação anterior.
4. Preserve todo conteúdo reservado e anotações reais fora do Git, anexos públicos e conversas de revisão.
5. Após a resposta, atualizar prospectivamente o protocolo/contrato, implementar e testar em material artificial a custódia G05; depois preparar G07 e solicitar a aprovação final G08.

Para adicionar os três arquivos públicos deste pacote ao Git, a partir da raiz do projeto:

```powershell
git add docs/metodologia/SOLICITACAO_REVISAO_ORIENTADOR.md docs/metodologia/REGISTRO_DECISOES_PRELIMINARES.md docs/instrucoes/INSTRUCOES_REVISAO_ORIENTADOR.md
git diff --cached --stat
git commit -m "docs: preparar encaminhamento de revisao academica"
git push origin main
git status --short
```

Deixe `docs/instrucoes/INSTRUCOES_REVISAO_V02.md` não versionado até revisão separada. O pacote não modifica código nem habilita avaliação final.
