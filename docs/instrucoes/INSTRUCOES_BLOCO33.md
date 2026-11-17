# SentiVis — Bloco 33

**Executor de ensaio: 27 pares inteiramente fictícios e nove famílias artificiais. O protocolo permanece NÃO CONGELADO.**

## Instalação (PowerShell com `.venv` ativado)

Salve `sentivis_bloco33_executor_sintetico.zip` em `C:\TCC`, sem alterar a estrutura interna do ZIP. Na pasta `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco33_executor_sintetico.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

## Etapa 1 — verificar contrato sem gravar

```powershell
python -m backend.executor_sintetico_bloco33 verificar-contrato
```

Deve mostrar `NAO_CONGELADO_NAO_AUTORIZADO`, `n_pares_sinteticos=27`, `n_familias_sinteticas=9`, `programa_real_implementado=false` e `autorizacao_execucao_final=false`.

## Etapa 2 — registrar o ensaio sintético apenas UMA vez

```powershell
python -m backend.executor_sintetico_bloco33 ensaiar
```

Deve criar `data\piloto\restrito\bloco33_ensaio\marcador_tentativa_bloco33.json` e `relatorio_sintetico_bloco33.json`. **Não execute o mesmo comando pela segunda vez.** Não apague/edite os arquivos criados. Não são arquivos para o GitHub.

## Etapa 3 — executar testes e verificar o Git

```powershell
python -m pytest .\backend\tests -q -rs
git status --short
```

Os **23 novos testes** passaram isoladamente na preparação deste pacote. Somados aos 414 testes aprovados na última execução informada, espera-se **437 aprovados e 2 ignorados**, desde que o restante do ambiente permaneça igual. A execução completa deve confirmar isso; não tratar a expectativa como garantia.

**Arquivos novos (somente estes devem ser versionados):**

- `INSTRUCOES_BLOCO33.md`
- `backend/executor_sintetico_bloco33.py`
- `backend/tests/test_executor_sintetico_bloco33.py`
- `docs/metodologia/PROTOCOLO_EXECUTOR_SINTETICO_BLOCO33.md`

`INSTRUCOES_REVISAO_V02.md` continua fora do commit, assim como toda a pasta `data/piloto/restrito/`.

**Importante:** os 27 pares reservados não foram abertos, a avaliação final não aconteceu e o protocolo não foi aprovado. Não há comando para executar a avaliação real neste pacote.
