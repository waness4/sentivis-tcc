# SentiVis — Bloco 11: refinamento visual e comparação

## O que muda

- Dá destaque à comparação entre referências femininas e masculinas na área inicial e nas abas.
- Reduz o espaço da apresentação inicial para que a área de exploração seja encontrada mais rapidamente.
- Mostra pontuação e classe explicitamente como **exploratórias**, inclusive nos cartões de comparação.
- Acrescenta barras de **cobertura superficial**, sem apresentá-las como acurácia ou métrica de viés.
- Exibe uma interpretação descritiva do delta, inclusive quando seu valor é zero, sem afirmar ausência de viés.
- Trata casos de abstenção em um ou ambos os textos sem mostrar diferença numérica enganosa.
- Impede que uma requisição antiga sobrescreva o resultado se o usuário mudar de aba ou léxico durante o processamento.
- Ajusta a responsividade para telas menores, mantém o JSON acessível e acrescenta favicon local.

## O que NÃO muda

A implementação **não altera** `backend/core.py`, `backend/baseline_experimental.py`, `backend/ui_server.py`, as rotas da API, os léxicos, a revisão humana ou as partições de dados. Não produz resultados científicos nem valida equivalência semântica.

## Instalação — Windows/PowerShell

No projeto `C:\TCC\sentivis_bloco1`, mantenha o ambiente virtual ativado. Salve o ZIP em `C:\TCC` e execute:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco11_refino_visual.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

Confirme os testes (10 testes novos, 146 testes anteriores):

```powershell
python -m pytest .\backend\tests -q
```

**Esperado no computador com o Bloco 10 completo: 156 testes aprovados.**

Reinicie o servidor, se necessário, com `Ctrl+C` no terminal anterior e:

```powershell
python -m uvicorn backend.ui_server:app --reload --port 8001
```

Acesse `http://127.0.0.1:8001/`. Se o navegador conservar a versão antiga, recarregue com `Ctrl+F5`.

## Teste manual

1. Clique em **Comparar frases femininas e masculinas** no início da página.
2. Clique em **Preencher exemplo** e **Comparar textos**. Confirme pontuações `1` e `1`, cobertura `25%` em cada cartão e delta descritivo `0`, acompanhado do aviso de que isso **não** demonstra ausência de viés.
3. No modo **Analisar frase**, teste `A aluna não é dedicada.`. A resposta deve continuar sendo **abstenção contextual**, com pontuação não atribuída.
4. Verifique a página numa janela estreita: os cartões devem aparecer um abaixo do outro.

## GitHub — depois de verificar

```powershell
git status --short
git add frontend/ backend/tests/test_refino_interface.py docs/desenvolvimento/PROTOCOLO_INTERFACE_V02.md INSTRUCOES_BLOCO11.md
git diff --cached --stat
git commit -m "feat: aprimorar visualizacao exploratoria do SentiVis"
git push
```

Os arquivos em `data/lexicos/originais/` e `data/piloto/restrito/` devem continuar fora do repositório. A revisão humana e a avaliação científica seguem em etapas separadas.

## Validação do pacote

Os 150 testes disponíveis no ambiente de validação passaram. O projeto da usuária possui seis testes iniciais adicionais que não estavam no ambiente de validação; por isso o número completo de **156** deve ser confirmado no Windows. Também foi realizado um teste visual com dados simulados da API; os resultados dessas simulações não são dados científicos.
