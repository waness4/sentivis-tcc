# SentiVis — Bloco 29: ensaio sintético da avaliação final

**Status:** mecanismo de ensaio técnico, NÃO avaliação final, NÃO protocolo congelado.

## Instalar

A partir de `C:\TCC\sentivis_bloco1`, depois de salvar `sentivis_bloco29_ensaio_sintetico.zip` em `C:\TCC`:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco29_ensaio_sintetico.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

## Executar o ensaio fictício

```powershell
python -m backend.avaliacao_final_preparacao_bloco29 simular
```

O comando usa quatro pares **inventados**, um índice lexical fictício e um etiquetador gramatical **simulado**. Os algoritmos de classificação V01, V03 e V04 reais são chamados somente com esse material fictício. Não há opção `--entrada` nem carregamento de CSV da pesquisa; qualquer tentativa de passar arquivo é rejeitada pelo argumento da CLI.

**Resultado esperado do ensaio:** `P_total=4`, `P_equivalentes_R01=3`, `F_total=8`, `F_elegiveis=6`. Comportamento numérico da simulação depende dos contratos V01–V04 atuais; se houver erro, enviar a saída para revisão, sem adaptar as regras olhando dados reservados.

## Verificar testes

```powershell
python -m pytest .\backend\tests -q
git status --short
```

O pacote adiciona **14 testes sintéticos** aos 356 aprovados anteriormente; o total esperado passa a **370**, se o restante do projeto não tiver sido modificado. Os testes foram executados isoladamente durante a preparação; a suíte completa deve ser executada no projeto local.

## Arquivos do pacote

- `backend/avaliacao_final_preparacao_bloco29.py`: simulação e funções de agregação com validações estritas.
- `backend/tests/test_avaliacao_final_preparacao_bloco29.py`: 14 testes sem dados reais.
- `docs/metodologia/PROTOCOLO_ENSAIO_SINTETICO_BLOCO29.md`: escopo, verificações, bloqueios.
- `INSTRUCOES_BLOCO29.md`: este documento.

Não executar `git add .`. Não versionar ficha real, relatórios individuais ou nenhum arquivo `data/piloto/restrito/`. O arquivo `INSTRUCOES_REVISAO_V02.md` deve continuar fora do commit.

## Próxima fase — ainda pendente

Este ensaio **não implementa a extração nem o processamento de 27 pares reservados**. Uma operação real exigirá um adaptador de acesso específico com validação do corpus, hashes, autorização formal prévia, registro imutável de execução e testes de falha antes do congelamento. Nenhuma saída da simulação pode ser apresentada como resultado empírico do TCC.
