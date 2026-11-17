# SentiVis — Instruções do Bloco 34

**Estágio:** executor final ainda BLOQUEADO. Os testes e o ensaio usam **somente 27 pares fictícios**, nenhum dado reservado.

## Instalação — PowerShell na pasta `C:\TCC\sentivis_bloco1`

O ZIP deve ser descompactado preservando `backend/`, `backend/tests/`, `docs/instrucoes/` e `docs/metodologia/`.

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco34_contrato_bloqueado.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

## 1. Inspeção sem escrever

```powershell
python -m backend.executor_final_bloqueado_bloco34 verificar-contrato
```

**Esperado:** `NAO_CONGELADO_NAO_AUTORIZADO`, `origem_campos: 14`, `ficha_campos: 6`, `executor_real_liberado: false`.

## 2. Ensaio único — somente se ainda não executado

```powershell
python -m backend.executor_final_bloqueado_bloco34 ensaiar
```

**Esperado:** `ENSAIO_SINTETICO_CONCLUIDO`, `pares_ficticios: 27`, `avaliacao_final_executada: false`. O programa grava um marcador e um relatório privado em `data/piloto/restrito/bloco34_ensaio/`. Não executar de novo nem apagar o marcador. Se ocorrer erro, preservar o marcador para auditoria.

## 3. Testes e verificação de arquivos

```powershell
python -m pytest .\backend\tests -q -rs
git status --short
```

**Referência:** Bloco 33 registrou 437 testes aprovados e 2 ignorados por impossibilidade de symlink no Windows. Bloco 34 acrescenta **32 testes**; espera-se **469 aprovados e 2 ignorados**, se nenhum outro arquivo/ambiente tiver mudado. Não tratar *skipped* como teste aprovado.

## 4. Publicação após verificar as saídas

Adicionar **somente** estes quatro arquivos:

```powershell
git add docs/instrucoes/INSTRUCOES_BLOCO34.md backend/executor_final_bloqueado_bloco34.py backend/tests/test_executor_final_bloqueado_bloco34.py docs/metodologia/CONTRATO_EXECUTOR_FINAL_BLOCO34.md
git diff --cached --stat
git commit -m "test: preparar contrato bloqueado da avaliacao final"
git push origin main
git status --short
```

O arquivo ainda não revisado `docs/instrucoes/INSTRUCOES_REVISAO_V02.md` deve continuar sem publicação. Não usar `git add .`.

**Não executar** `executar-final`, não preparar ficha dos 27 pares reservados e não marcar congelamento como aprovado. A aprovação humana e o release real estão pendentes.
