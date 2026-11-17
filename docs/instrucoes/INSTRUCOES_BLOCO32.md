# Bloco 32 — Verificação documental antes do congelamento

**Esta etapa NÃO congela o protocolo e NÃO acessa a avaliação reservada.**

## Instalar

Salve `sentivis_bloco32_precongelamento.zip` em `C:\TCC` e extraia para a raiz do projeto:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco32_precongelamento.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

## Verificação somente leitura

```powershell
python -m backend.precongelamento_bloco32 verificar
```

A ferramenta reaproveita o inventário de integridade do Bloco 31, que lê apenas os léxicos e arquivos de código/protocolo explicitamente permitidos. Não recebe arquivos do usuário na linha de comando, não grava relatório e não importa dados da partição final. O resultado correto mantém `NAO_CONGELADO_NAO_AUTORIZADO`, lista decisões pendentes e marca autorização `false`.

## Testes e Git

```powershell
python -m pytest .\backend\tests -q -rs
git status --short
```

Depois de verificação e revisão, adicione **somente os cinco arquivos** entregues neste pacote. Não utilize `git add .`; não inclua dados da pasta `data/piloto/restrito`, léxicos originais ou `INSTRUCOES_REVISAO_V02.md`.

## Continuidade

O próximo requisito concreto é desenvolver **um executor real ainda bloqueado**, com contrato definitivo e testes exclusivamente artificiais, e obter a revisão/aprovação acadêmica. Não existem atalhos legítimos de `verificar` para `executar-final` neste Bloco 32.
