# SentiVis — Bloco 7: protocolo de pares e piloto de desenvolvimento

**Objetivo:** organizar um conjunto de pares femininos/masculinos para revisão humana, detectar vazamento entre partições e permitir um piloto **exclusivamente na partição de desenvolvimento**. Esta etapa **não comprova viés** e **não executa a avaliação final**.

## Instalação no Windows

1. Salve `sentivis_bloco7_piloto.zip` em `C:\TCC`.
2. No PowerShell, esteja em `C:\TCC\sentivis_bloco1` com `(.venv)` ativado.
3. Execute:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco7_piloto.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
python -m pytest .\backend\tests -q
```

Esta atualização **adiciona** `backend/pares_piloto.py`, os testes correspondentes, documentação e um modelo CSV. **Não substitui** os demais módulos; **não** altera os arquivos de léxicos nem os relatórios existentes. São 23 novos testes; se os 91 anteriores continuarem no diretório, o esperado é **114 testes aprovados**.

## Inspecione o modelo do conjunto de pares

Abra o arquivo em um editor com suporte UTF-8, por exemplo VS Code:

`data\piloto\modelo_pares_para_revisao.csv`

O arquivo tem **quatro pares didáticos**. São rascunhos, **não** frases revisadas. Não use esse arquivo como evidência do TCC. Para criar a versão de trabalho sem modificar o exemplo:

```powershell
Copy-Item .\data\piloto\modelo_pares_para_revisao.csv .\data\piloto\pares_em_revisao.csv
```

As colunas seguem a ordem fixa: `id_par;familia;particao;frase_feminina;frase_masculina;rotulo_revisor1;rotulo_revisor2;equivalencia_revisor1;equivalencia_revisor2;id_revisor1;id_revisor2;alvo_sentilex_feminina;alvo_sentilex_masculina;observacoes`.

- `particao`: `desenvolvimento` ou `avaliacao`. Nunca misture a mesma **família** de moldes entre partições. A avaliação final está sempre bloqueada neste módulo.
- `rotulo_revisor1` e `rotulo_revisor2`: `positiva`, `negativa`, `neutra` ou vazio enquanto aguardam revisão. São rótulos **de referência definidos por pessoas**, nunca valores produzidos pelo baseline.
- `equivalencia_revisor1` e `equivalencia_revisor2`: `sim`, `nao` ou vazio. Só use `sim` quando o revisor considerar que a substituição de gênero preserva sentido, contexto e avaliação.
- `id_revisor1` e `id_revisor2`: dois identificadores **diferentes**, atribuídos a pessoas reais que revisaram **independentemente**; identificadores distintos **não provam** independência. Não invente identificadores para liberar a classificação.
- `alvo_sentilex_feminina` e `alvo_sentilex_masculina`: opcionalmente `N0` ou `N1` como **hipótese manual** por frase. Isso NÃO constitui análise sintática e precisará de validação antes dos resultados finais.
- `familia`: nome de um mesmo molde/contexto; famílias inteiras ficam em uma só partição.
- `observacoes`: contexto, transformação realizada, dificuldades de equivalência e motivo de exclusão.

Mantenha CSV UTF-8, separado por `;`. Textos não podem conter quebras de linha arbitrárias nem ultrapassar 5.000 caracteres. Não modifique o cabeçalho.

## Conferir o conjunto — sem calcular polaridades

```powershell
python -m backend.pares_piloto `
  --entrada .\data\piloto\modelo_pares_para_revisao.csv `
  --saida .\data\piloto\relatorio_pares.json
```

O resultado esperado no exemplo é `Pares: 4; erros estruturais: 0; revisões: {'PENDENTE_REVISAO': 4}`. **Todos são pendentes de revisão.** O arquivo `relatorio_pares.json` contém a auditoria, partições, duplicações e conflitos encontrados. IDs repetidos, frases idênticas no par e famílias em ambas as partições são erros impeditivos.

## Piloto somente após a revisão humana

**Não rode o piloto como se fosse um resultado da pesquisa enquanto não houver pares com revisão dupla concluída.** Após revisar os pares e preencher o CSV de trabalho:

```powershell
python -m backend.pares_piloto `
  --entrada .\data\piloto\pares_em_revisao.csv `
  --saida .\data\piloto\relatorio_piloto.json `
  --piloto
```

O relatório preserva o SHA-256 do dataset e dos léxicos, status de pontuação e abstenção por frase, cobertura lexical e diferença numérica exploratória nos pares aprovados **de desenvolvimento**. Nenhum par da partição `avaliacao` é pontuado. Com zero pares aprovados, a lista de resultados será vazia — comportamento esperado.

## Limitações e próximos passos

1. A concordância dos dois revisores é requisito operacional, não demonstra por si só equivalência semântica, concordância interavaliador ou correção dos rótulos. Revisões discordantes devem ser resolvidas com um protocolo humano pré-definido e documentadas.
2. Não usar o baseline para criar rótulos de referência; não mostrar resultados da partição final enquanto as regras do sistema ainda estiverem em desenvolvimento.
3. O baseline aditivo ainda não interpreta negação, ironia, modificadores, alvos sintáticos ou polissemia; os cálculos desta etapa são apenas testes exploratórios.
4. Antes de análise confirmatória, fixar versão do software, políticas lexicais, protocolo, famílias, dados e separações; documentar revisores e decisões.
5. O número de 240 pares do protocolo é **meta logística**, não garantia de poder estatístico. A qualidade das famílias e a revisão são requisitos fundamentais.
6. O OpLexicon ainda necessita confirmar a correspondência da cópia utilizada com a distribuição oficial e as condições de redistribuição.
