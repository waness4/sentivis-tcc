# SentiVis — Bloco 23: clareza dos diagnósticos na interface

## Escopo

Mudança **somente na apresentação** dos resultados já devolvidos por `backend.ui_server`.
Não modifica a API, os léxicos originais, as regras de V01–V04 nem os critérios da avaliação.
Não carrega nem inclui os 27 pares finais ou as fichas dos revisores.

### Arquivos incluídos

- `frontend/app.js`: traduções legíveis dos códigos de motivo e interpretação da abstenção;
  explicação de cobertura superficial (não é acurácia); detalhe de entradas neutras
  descartadas; apresentação responsável da comparação de gênero.
- `frontend/styles.css`: apresentação responsiva das explicações.
- `backend/tests/test_explicacoes_ui_bloco23.py`: testes da camada explicativa.
- `docs/desenvolvimento/PROTOCOLO_INTERFACE_EXPLICATIVA_BLOCO23.md`: protocolo.
- `INSTRUCOES_BLOCO23.md`: este guia.

## 1. Instalar no Windows

Salve o arquivo `sentivis_bloco23_clareza_interface.zip` em `C:\TCC`.

No PowerShell, com o ambiente virtual ativo e dentro de `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco23_clareza_interface.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force

python -m pytest .\backend\tests -q
```

Na montagem testada: **336 testes passaram** (317 anteriores + 19 novos).
Se houver divergência, não publicar o bloco antes de analisar a falha.

## 2. Verificar visualmente

```powershell
python -m uvicorn backend.ui_server:app --reload --port 8001
```

Acesse `http://127.0.0.1:8001` e escolha:

- SentiLex-PT02;
- método contextual V04;
- alvo manual N0;
- hipótese sintática ativada.

Frase de teste: `A pesquisadora apresentou os dados com segurança.`

Verifique:
- Abstenção por ligação sintática ambígua; pontuação não atribuída;
- explicação legível com `segurança` e indicação de ambiguidade;
- `dados` explicado como entrada neutra descartada por classe gramatical;
- cobertura superficial de 28,6% explicada como correspondência lexical, **não acurácia**;
- tabela de classes gramaticais e papéis com descrições legíveis;
- detalhes técnicos (códigos e proveniência) ainda acessíveis.

Também teste a aba de comparação com o par feminino/masculino e confirme que, se
uma análise se abstiver, a diferença numérica continua **não calculável**.

## 3. Versionar somente após conferência

```powershell
git status --short

git add frontend/app.js frontend/styles.css backend/tests/test_explicacoes_ui_bloco23.py docs/desenvolvimento/PROTOCOLO_INTERFACE_EXPLICATIVA_BLOCO23.md INSTRUCOES_BLOCO23.md

git diff --cached --stat

git commit -m "feat: explicar resultados contextuais na interface"

git push origin main
```

**Não use `git add .`:** `INSTRUCOES_REVISAO_V02.md` permanece pendente e deve
ser tratado separadamente. Não incluir dados de `data/piloto/restrito` em commits.

## Limites científicos

- As classificações disponíveis continuam exploratórias e não validadas.
- `N0/N1` continua sendo escolhido manualmente, sem resolução do referente.
- Uma entrada lexical pode ser descartada da decisão e ainda contar na
  cobertura superficial; isso não é erro de cálculo da cobertura.
- O papel de expressões com `com`, incluindo `nmod`, continua incerto.
- A interface não afirma a existência nem ausência de viés de gênero.
- O conjunto de 36 controles já foi usado no desenvolvimento e não é teste
  final independente de generalização.
