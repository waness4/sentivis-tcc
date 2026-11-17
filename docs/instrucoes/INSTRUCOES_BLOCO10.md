# SentiVis — Bloco 10: interface web

Esta etapa instala uma interface responsiva e novas rotas de análise **exploratória**. Não substitui `backend/main.py`, `backend/core.py`, os 130 testes anteriores, os arquivos originais ou as fichas de revisão.

## Instalação (Windows / PowerShell)

A partir de `C:\TCC\sentivis_bloco1`, com `(.venv)` ativado:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco10_interface.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
python -m uvicorn backend.ui_server:app --reload
```

Acesse **http://127.0.0.1:8000/** no navegador. A API continua disponível em **http://127.0.0.1:8000/docs**.

Se um terminal estiver executando `python -m uvicorn backend.main:app --reload`, pare-o com Ctrl+C antes de iniciar `backend.ui_server:app` (a porta 8000 só pode ser ocupada por um servidor). A interface usa o MESMO servidor da API; não precisa instalar Node.js, npm ou bibliotecas de interface.

Ao acessar pela primeira vez um léxico, o backend lê os arquivos originais e verifica SHA-256 contra a curadoria. Os índices são mantidos na memória para consultas seguintes. Reinicie o servidor após alterar os arquivos dos léxicos ou o relatório da curadoria.

## Funcionalidades

- Interface responsiva para análise de frase e comparação feminina/masculina.
- Seleção OpLexicon 3.0 / SentiLex-PT02 e alvo N0/N1 (manual, sem inferência contextual).
- Exibição de abstenções, cobertura, termos pontuados, termos ausentes e polaridades.
- Exportação do resultado **exploratório** em JSON.
- Metodologia e limites visíveis na página; não há métricas finais nem evidência inferida de viés.

A interface não acessa `data/piloto/avaliacao_final`, `data/piloto/restrito` nem altera rótulos de revisores. Nenhum resultado é enviado a serviço externo.

## GitHub

Depois de verificar os testes e inspecionar os arquivos:

```powershell
git add frontend/ backend/ui_server.py backend/tests/test_ui_server.py docs/desenvolvimento/PROTOCOLO_INTERFACE_V01.md INSTRUCOES_BLOCO10.md
git diff --cached --stat
git commit -m "feat: adicionar interface web exploratoria ao SentiVis"
git push
```

Não versionar os léxicos originais nem os arquivos de avaliação reservada.
