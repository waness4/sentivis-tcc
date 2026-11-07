# SentiVis — Bloco 20: Comparação V03 × V04 (36 controles)

Este pacote **não altera** V03, V04, a interface, os léxicos nem os 27 pares reservados de avaliação final.

## 1. Instalação

Salve o pacote `sentivis_bloco20_comparacao_v03_v04.zip` em `C:\TCC`, abra o PowerShell com o ambiente virtual do projeto ativado na pasta `C:\TCC\sentivis_bloco1` e execute:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco20_comparacao_v03_v04.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

## 2. Testes de regressão

```powershell
python -m pytest .\backend\tests -q
```

Expectativa de **286 testes** (271 previamente confirmados e 15 novos). No ambiente de validação, 260 testes de backend passaram; 26 de interface dependem de arquivos do `frontend` não presentes naquele ambiente. Se falhar, interrompa a publicação e encaminhe a saída.

## 3. Comparar os controles pré-fixados

```powershell
python -m backend.comparacao_controles_v03_v04 `
  --alvo N0 --hipotese-modo `
  --saida-json .\data\piloto\restrito\comparacao_controles_v03_v04.json `
  --saida-csv .\data\piloto\restrito\comparacao_controles_v03_v04.csv
```

O programa só aceita o conjunto fixado de 36 controles mediante SHA-256. Não reescreve arquivos existentes. Se o arquivo de saída já existir, use um nome novo, sem `-Force`.

Esperado: uma linha resumo com a quantidade de frases pontuadas em cada versão, o número de frases onde o filtro foi aplicado e a quantidade de status alterados. **Não presumir** que V04 pontuará mais frases: C005 e C006 permanecem em abstenção por ligação sintática ambígua, embora o status mude.

Os relatórios contêm apenas métricas descritivas. Não calculam acurácia, F1 ou evidência de viés, porque os controles não têm rótulos humanos independentes.

## 4. Versão de código

Depois que os testes e a execução local forem confirmados, conferir `git status --short` e registrar somente os arquivos novos:

```powershell
git add backend/comparacao_controles_v03_v04.py backend/tests/test_comparacao_controles_v03_v04.py docs/metodologia/PROTOCOLO_COMPARACAO_CONTROLES_V03_V04.md INSTRUCOES_BLOCO20.md
git diff --cached --stat
git commit -m "test: comparar controles sintaticos V03 e V04"
git push
```

Não executar `git add .` nem publicar `data/piloto/restrito/`. Fichas de revisores e relatórios de desenvolvimento devem permanecer privados.
