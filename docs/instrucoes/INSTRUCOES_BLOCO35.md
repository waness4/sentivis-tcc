# SentiVis — Instruções do Bloco 35

**Objetivo:** gerar um dossiê **preliminar** para revisão metodológica. O programa não aprova, não congela e não executa a avaliação final. Os dados dos 27 pares reservados não são abertos. Há oito portões a resolver com decisões documentadas.

## Instalação

1. Descompactar `sentivis_bloco35_revisao.zip` na raiz `C:\TCC\sentivis_bloco1` com `Expand-Archive -Force`, sem mover arquivos de dados.
2. Verificar o contrato e o inventário com `python -m backend.revisao_congelamento_bloco35 verificar`. O resultado esperado deve incluir `NAO_CONGELADO_NAO_AUTORIZADO`, `protocolo_congelado=false`, `autorizacao_execucao_final=false` e oito pendências.
3. Executar `python -m pytest .\backend\tests -q -rs` e `git status --short`. As duas exclusões antigas de testes de symlink em Windows podem permanecer, o que exige ressalva técnica.
4. Conferir o parecer `docs/metodologia/PARECER_PENDENCIAS_BLOCO35.md` e o modelo `docs/metodologia/MODELO_ATA_REVISAO_BLOCO35.md` para encaminhar ao responsável acadêmico.
5. Preparar seletivamente para Git os **cinco** arquivos do Bloco 35. Não incluir `docs/instrucoes/INSTRUCOES_REVISAO_V02.md` sem revisão e não usar `git add .`.
6. **Após** publicar o commit do Bloco 35, pode-se registrar o dossiê preliminar com `python -m backend.revisao_congelamento_bloco35 registrar`. Esse modo cria o registro privado uma só vez em `data/piloto/restrito/bloco35_dossie/dossie_preliminar_bloco35.json` e bloqueia sobrescritas; não executar antes de conferir o commit caso seja necessário vinculá-lo à versão publicada.

## Atenção

- Os documentos são **rascunhos para revisão**; campos de aprovação permanecem PENDENTES.
- O bloco não corrige a divergência entre o tratamento de falta de resposta previsto no Bloco 28 e o bloqueio de ficha incompleta do Bloco 34. Essa política requer deliberação antes de qualquer avaliação.
- O script B34 `executar_final` permanece bloqueado; não substituí-lo por uma chamada direta aos modelos nem utilizar os arquivos reservados para validação.
- O `registrar` do Bloco 35 é só um inventário de revisão; não libera execução. Não repetir após seu primeiro uso.
