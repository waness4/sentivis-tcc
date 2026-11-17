# SentiVis — Ajuste de integração do piloto e das métricas

Este ajuste não modifica as fichas, o baseline ou os léxicos. Corrige uma incompatibilidade entre o formato gerado por `backend.pares_piloto` (`{"auditoria": ..., "piloto": ...}`) e a leitura em `backend.metricas_exploratorias`.

## Instalação

No PowerShell, em `C:\TCC\sentivis_bloco1`, após salvar o ZIP em `C:\TCC`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_ajuste_integracao_piloto.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
```

## Execução do piloto de desenvolvimento

**A execução é exploratória. Confirme e registre se os dois revisores trabalharam separadamente antes de relatar a anotação como independente no TCC.**

```powershell
python -m backend.pares_piloto `
  --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v02.csv `
  --saida .\data\piloto\restrito\resultado_piloto_v02.json `
  --piloto
```

O arquivo `resultado_piloto_v02.json` contém um objeto `auditoria` e um objeto `piloto`.

```powershell
python -m backend.metricas_exploratorias calcular `
  --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v02.csv `
  --piloto .\data\piloto\restrito\resultado_piloto_v02.json `
  --saida-json .\data\piloto\restrito\metricas_desenvolvimento_v02.json `
  --saida-csv .\data\piloto\restrito\metricas_desenvolvimento_v02.csv
```

## Git (somente código e testes)

```powershell
git add backend/metricas_exploratorias.py backend/tests/test_integracao_piloto_metricas.py INSTRUCOES_AJUSTE_INTEGRACAO.md
git commit -m "fix: integrar relatorio do piloto ao calculo de metricas"
git push
```

Os resultados e fichas em `data/piloto/restrito/` **não devem ser publicados**. Os resultados são exploratórios e não demonstram viés ou ausência de viés.
