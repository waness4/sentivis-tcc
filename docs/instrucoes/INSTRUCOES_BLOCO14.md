# SentiVis — Bloco 14: filtro gramatical experimental V02

Esta atualização adiciona `backend/baseline_gramatical_v02.py`, testes e protocolo. **Não sobrescreve** `backend/baseline_experimental.py`, léxicos, API, frontend, pares ou métricas do experimento atual.

## 1. Instalação

Salve `sentivis_bloco14_filtro_gramatical_v02.zip` em `C:\TCC`, na pasta do projeto com venv ativo:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco14_filtro_gramatical_v02.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

Os testes do filtro não precisam do spaCy (utilizam etiquetas simuladas). Para executar o **modelo real** no Windows com Python 3.13, instale:

```powershell
python -m pip install "spacy>=3.8.7,<3.9"
python -m spacy download pt_core_news_sm
python -m spacy validate
```

O modelo é um pacote adicional e precisa ser instalado antes da CLI. Se houver erro de instalação, não altere o ambiente global: envie a saída do erro.

## 2. Testes de engenharia

```powershell
python -m pytest .\backend\tests -q
```

São 14 testes novos. Com os 182 testes anteriormente aprovados, o total esperado é de **196**, se todo o seu conjunto continuar disponível. Isso **não valida** as etiquetas reais do spaCy nem o mérito científico.

## 3. Verificar P006 com o modelo treinado

```powershell
python -m backend.baseline_gramatical_v02 `
  --texto "A atendente registrou o pedido." `
  --detalhado `
  --saida .\data\piloto\restrito\diagnostico_p006_v02.json

Get-Content .\data\piloto\restrito\diagnostico_p006_v02.json -Raw -Encoding UTF8
```

**Saída esperada, condicionada ao etiquetador atribuir `NOUN` a `pedido`:** status `ABSTENCAO_CATEGORIA_GRAMATICAL`, motivo `categoria_gramatical_incompativel`, `pontuacao_exploratoria: null` e `classe_exploratoria: null`. Se retornar `ADJ`, o baseline V02 manterá o +1 e a inspeção revelará erro provável do etiquetador; não force o resultado.

## 4. Verificar o par feminino/masculino

```powershell
python -m backend.baseline_gramatical_v02 `
  --feminina "A atendente registrou o pedido." `
  --masculina "O atendente registrou o pedido." `
  --saida .\data\piloto\restrito\comparacao_p006_v02.json
```

## 5. Versionamento

Depois de verificar a execução e os testes, publique **somente código, documentação e testes**:

```powershell
git add backend/baseline_gramatical_v02.py backend/tests/test_baseline_gramatical_v02.py docs/metodologia/PROTOCOLO_BASELINE_POS_V02.md INSTRUCOES_BLOCO14.md
git diff --cached --stat
git commit -m "feat: adicionar filtro POS experimental ao baseline V02"
git push
```

Nunca publique `data/piloto/restrito` ou dados humanos brutos no GitHub. Os resultados do piloto V01 permanecem intactos. O cálculo atual de métricas continuará usando V01; não afirmar melhoria de desempenho com base nos testes de engenharia.
