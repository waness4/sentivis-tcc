# SentiVis — Bloco 22: integração da V04 à interface web

## Objetivo

Permitir escolher, na interface, entre o baseline aditivo V01 (padrão) e o contextual SentiLex V04 (hipótese não validada). Não altera as funções V01/V03/V04 de classificação, os léxicos, os controles ou quaisquer dados de avaliação humana.

## Arquivos deste pacote

- `backend/ui_server.py`: validação HTTP de método e hipótese, execução da V04 apenas para SentiLex e carregamento tardio do modelo spaCy.
- `frontend/index.html`: seletor de método, escolha de N0/N1 manual e confirmação da hipótese.
- `frontend/app.js`: chamadas dos métodos e detalhamento de abstenções e filtros.
- `frontend/styles.css`: apresentação adicional dos controles e da tabela contextual.
- `backend/tests/test_integracao_ui_v04.py`: testes sintéticos de API, proteção e renderização.
- `docs/desenvolvimento/PROTOCOLO_INTERFACE_V04_BLOCO22.md`: protocolo da demonstração.

## 1. Instalar no PowerShell

Na pasta `C:\TCC\sentivis_bloco1`, com a venv ativada, e após salvar o ZIP em `C:\TCC`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco22_interface_v04.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
```

Esperado: **317 testes aprovados**, desde que os arquivos locais correspondam ao histórico do projeto. O ambiente de preparação executou 317 testes em arquivos reconstruídos dos pacotes anteriores; **não** executou os léxicos completos reais nem o navegador do computador do usuário.

## 2. Executar a interface

```powershell
python -m uvicorn backend.ui_server:app --reload --port 8001
```

Abra `http://127.0.0.1:8001`.

Para usar V04: escolha **SentiLex-PT02**, depois **Contextual V04**, informe **N0** ou **N1** manualmente e assinale **Ativar hipótese sintática de modo**. A seleção manual não valida o alvo semântico.

Experimente, por exemplo, as frases já estudadas:

- `A pesquisadora apresentou os dados com segurança.`
- `O pesquisador apresentou os dados com arrogância.`

Com o etiquetador e os léxicos usados anteriormente, o esperado é `ABSTENCAO_ANEXACAO_AMBIGUA`, com indicação de que `dados` foi descartado da pontuação por incompatibilidade gramatical. Se o ambiente ou as versões mudarem, o comportamento pode variar.

V01 permanece o método padrão. Para OpLexicon, a escolha V04 não aparece. A API também rejeita V04 sem SentiLex, sem alvo manual ou sem autorização da hipótese (422).

## 3. Versionar somente após conferir

```powershell
git status --short
```

Estes arquivos devem estar modificados ou novos: `backend/ui_server.py`, `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`, `backend/tests/test_integracao_ui_v04.py`, `docs/desenvolvimento/PROTOCOLO_INTERFACE_V04_BLOCO22.md`, `INSTRUCOES_BLOCO22.md`. Não use `git add .`: fichas humanas e JSONs restritos não devem ser publicados.

## Limites

A V04 pode se abster em grande parte das frases. Sua escolha na UI não demonstra ganho de acurácia, cobertura ou evidência de viés de gênero. As frases de controle já usadas para diagnóstico não são validação independente; os 27 pares finais continuam isolados. A interface não lê fichas de revisores nem resultados finais restritos.
