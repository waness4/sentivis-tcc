# SentiVis — Bloco 12: métricas exploratórias do piloto de desenvolvimento

## Objetivo

Adicionar **um módulo de métricas**, sem modificar `backend/core.py`, `backend/pares_piloto.py`, `backend/ui_server.py`, interface, léxicos, CSVs originais ou as fichas dos revisores. Foram acrescentados 22 testes sintéticos e um protocolo metodológico.

### Instalação Windows / PowerShell

A partir de `C:\TCC\sentivis_bloco1`, com `.venv` ativado:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco12_metricas.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force

python -m pytest .\backend\tests -q
```

O projeto tinha 156 testes aprovados antes desta etapa; com os **22 novos**, o esperado na máquina de origem é **178 testes**. O pacote foi testado em ambiente de validação com 172 testes (os seis testes originais não estão presentes nessa cópia).

## Primeiro comando a executar (SEM revisores concluídos)

```powershell
python -m backend.metricas_exploratorias verificar
```

Com o arquivo candidato de 36 pares do Bloco 8 ainda não anotado, espera-se:

```text
Verificação de desenvolvimento:
Pares: 9; aprovados: 0; pendentes ou reprovados: 9
Nenhuma avaliação final acessada, nenhuma métrica de sentimentos calculada.
```

Isto é o **comportamento correto**: não há resultados científicos a produzir sem revisões humanas reais.

## Posteriormente, após as duas revisões independentes

**Não execute estes comandos antes que pessoas distintas preencham as duas fichas**. Não modifique rótulos apenas para forçar a aprovação dos testes.

```powershell
python -m backend.revisao_humana consolidar --id-a R01 --id-b R02
```

Confirme no relatório de revisão quais pares obtiveram `APROVADO_DUPLA_REVISAO`. Discordâncias requerem adjudicação humana e devem ser documentadas. Não use os pares ainda pendentes.

```powershell
python -m backend.pares_piloto `
  --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v01.csv `
  --saida .\data\piloto\restrito\resultado_piloto_v01.json `
  --piloto
```

```powershell
python -m backend.metricas_exploratorias calcular
```

Por padrão, serão produzidos, sem sobrescrever arquivos existentes:

```text
data/piloto/restrito/metricas_desenvolvimento_v01.json
data/piloto/restrito/metricas_desenvolvimento_v01.csv
```

As métricas são **exploratórias, somente desenvolvimento**, e não demonstram viés. Não publique esses dados como resultados definitivos do TCC.

## GitHub

Após instalar, conferir os testes e o comando `verificar`:

```powershell
git add backend/metricas_exploratorias.py backend/tests/test_metricas_exploratorias.py docs/metodologia/PROTOCOLO_METRICAS_V01.md INSTRUCOES_BLOCO12.md
git diff --cached --stat
git commit -m "feat: adicionar metricas descritivas do piloto"
git push
```

**Não faça `git add -f` nos dados**. Fichas humanas e saídas de desenvolvimento permanecem em `data/piloto/restrito/` e léxicos originais em `data/lexicos/originais/`, protegidos pelo `.gitignore`.
