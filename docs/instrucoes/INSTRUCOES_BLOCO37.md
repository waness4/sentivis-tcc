# Instruções — SentiVis Bloco 37

## Instalar no Windows PowerShell

Na raiz `C:\TCC\sentivis_bloco1`, com `.venv` ativado, depois de salvar o ZIP na pasta `C:\TCC`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco37_nucleo_executor.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

## Verificar

```powershell
python -m backend.executor_avaliacao_bloco37 verificar-contrato
python -m backend.executor_avaliacao_bloco37 simular
python -m pytest .\backend\tests -q -rs
git status --short
```

**Não execute `executar-final`: continuará bloqueado. Não forneça, cole ou mova dados da avaliação real para a simulação.** O comando `simular` não grava resultados e utiliza apenas 27 pares inventados e recursos fictícios.

A validação isolada executada antes da entrega foi de 59 testes novos aprovados; existem ainda **dois testes de integração** que necessitam do repositório completo: equivalência com o Bloco 29 e execução dos três baselines reais usando apenas os recursos artificiais do Bloco 33. Resultado estimado, se o Bloco 36 tiver 523 testes passando: **584 passed, 2 skipped**. Divergências exigem investigação antes do commit.

## Git

Adicione **somente** os cinco novos arquivos deste pacote e mantenha `INSTRUCOES_REVISAO_V02.md` fora do commit, caso ainda esteja não versionado:

```powershell
git add backend/executor_avaliacao_bloco37.py backend/tests/test_executor_avaliacao_bloco37.py docs/instrucoes/INSTRUCOES_BLOCO37.md docs/metodologia/PROTOCOLO_NUCLEO_EXECUTOR_BLOCO37.md docs/metodologia/ENCAMINHAMENTO_ORIENTADOR_BLOCO37.md
git diff --cached --stat
git commit -m "feat: preparar nucleo executor experimental bloqueado"
git push origin main
git status --short
```

Se os Blocos 35 ou 36 ainda estiverem sem commit, verifique `git status --short` primeiro e informe os arquivos pendentes; não presuma que o `git push` já foi realizado.

## Limites

Este bloco não autoriza, não congela, não abre e não executa a partição final. O núcleo genérico é preparação de código em memória. Faltam custódia privada, hash dos bytes originais, execução única real, revisão metodológica e aprovação acadêmica comprovável. Não transforme resultados fictícios em evidência científica.
