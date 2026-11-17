# Bloco 15 — Comparação V01 x V02 (somente desenvolvimento)

Pré-requisitos: Blocos 1–14 instalados, ambiente `.venv` ativado, spaCy e `pt_core_news_sm` disponíveis, OpLexicon original em `data/lexicos/originais` e ficha consolidada `data/piloto/restrito/pares_desenvolvimento_revisados_v02.csv`.

## Instalação

Copie o ZIP para `C:\TCC\` e, dentro de `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco15_comparacao.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

## Testes

```powershell
python -m pytest .\backend\tests -q
```

São 12 testes novos. Se a base mantiver os 196 anteriores, o esperado é 208.

## Executar a comparação

```powershell
python -m backend.comparacao_baselines_v01_v02 `
  --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v02.csv `
  --saida-json .\data\piloto\restrito\comparacao_baselines_desenvolvimento_v01_v02.json `
  --saida-csv .\data\piloto\restrito\comparacao_baselines_desenvolvimento_v01_v02.csv
```

Os relatórios **não sobrescrevem** arquivos existentes; escolha nomes novos se necessário. Eles NÃO usam o SentiLex. Não envie arquivos restritos ao GitHub.

## Conferir o resumo

```powershell
python -c "import json; p=json.load(open('data/piloto/restrito/comparacao_baselines_desenvolvimento_v01_v02.json',encoding='utf-8')); print('Pares:',p['pares_desenvolvimento_aprovados']); print('V01:',p['metricas']['v01']); print('V02:',p['metricas']['v02']); print('Transicoes:',p['transicoes_v01_para_v02']); print('Avaliação processada:',p['pares_avaliacao_classificados'])"
```

## Versionamento da infraestrutura (não dos resultados privados)

```powershell
git add backend/comparacao_baselines_v01_v02.py backend/tests/test_comparacao_baselines_v01_v02.py docs/metodologia/PROTOCOLO_COMPARACAO_BASELINES_V01_V02.md INSTRUCOES_BLOCO15.md
git commit -m "feat: comparar baselines V01 V02 no desenvolvimento"
git push
```

**Interpretação:** se a V02 deixar de atribuir as únicas previsões incorretas da V01, ela terá evitado erros por abstenção. Sem previsões pontuadas na V02, não se calcula sua acurácia seletiva, nem se afirma melhoria geral ou presença/ausência de viés de gênero.
