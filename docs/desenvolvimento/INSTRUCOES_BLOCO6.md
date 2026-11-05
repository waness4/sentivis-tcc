# SentiVis — Bloco 6: baseline aditivo exploratório, com abstenções

## O que foi implementado

Um **baseline de engenharia** para testar se o sistema consegue calcular pontuações reprodutíveis em textos de baixo risco interpretativo. A pontuação é uma soma de polaridades das expressões lexicais reconhecidas, com a regra de selecionar a expressão mais longa já implementada no Bloco 5. **Não é classificador científico validado** e **não é evidência de viés**.

- `SEM_COBERTURA`: nenhuma expressão lexical encontrada. Não equivale a sentimento neutro.
- `ABSTENCAO_ALVO`: SentiLex consultado sem escolha explícita de N0/N1.
- `ABSTENCAO_LEXICAL`: algum termo encontrado tem conflito, polaridade inválida, categoria ou lema ambíguo, alvo inconsistente ou metadado pendente.
- `ABSTENCAO_CONTEXTO`: negador ou modificador reconhecido sem regra contextual validada.
- `PONTUACAO_EXPLORATORIA_NAO_VALIDADA`: soma de polaridades -1/0/+1 apenas para os candidatos lexicalmente consistentes, sem marcador contextual reconhecido.

**Importante:** uma frase aparentemente simples ainda pode conter ironia, polissemia, modificadores não listados e diferenças de alvo não capturadas. Se N0/N1 for especificado, o programa **não verifica** se o referente informado é o correto; essa escolha é uma hipótese manual, não inferência sintática.

## Instalar (PowerShell Windows)

Salve `sentivis_bloco6_baseline.zip` em `C:\TCC`. Mantenha o terminal na pasta `C:\TCC\sentivis_bloco1` com o ambiente virtual ativado.

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco6_baseline.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
python -m pytest .\backend\tests -q
```

Esta atualização **não substitui** `core.py`, `main.py`, nem modifica léxicos, relatórios ou testes anteriores. Só adiciona `backend/baseline_experimental.py`, seus testes e documentação.

## Exemplos para verificação

```powershell
# Par com dois adjetivos positivos no OpLexicon:
python -m backend.baseline_experimental --lexico oplexicon --feminina "A aluna é dedicada." --masculina "O aluno é dedicado."

# Palavra com divergência lexical: deve abster-se.
python -m backend.baseline_experimental --lexico oplexicon --texto "A prova foi fácil."

# Negação: deve abster-se, NÃO inverter polaridade.
python -m backend.baseline_experimental --lexico oplexicon --texto "A aluna não é dedicada."

# Alvo não escolhido no SentiLex: deve abster-se.
python -m backend.baseline_experimental --lexico sentilex --texto "Ela é intrépida."

# Consulte também o modo detalhado, se necessário:
python -m backend.baseline_experimental --lexico oplexicon --texto "A aluna é dedicada." --detalhado
```

Opcional: `--saida .\data\piloto\saida_baseline.json` salva o JSON com o manifesto SHA-256 das fontes. Não use resultados desta etapa como métricas finais do TCC.

## Próximas exigências científicas

1. Especificar regras linguísticas para N0/N1, negação, modificadores, polissemia, composição e categoria gramatical. Documentar decisões e versões de ferramentas.
2. Preparar pares contrafactuais de gênero, com equivalência semântica revisada por pessoas independentes e rótulos de sentimento revisados. Não usar os pares finais para ajustar regras.
3. Separar famílias de sentenças entre desenvolvimento e avaliação; congelar protocolo antes de testar a hipótese principal.
4. Calcular cobertura e taxas de abstenção, acurácia e F1-macro com política clara para abstenções; comparar cada léxico separadamente e reportar intervalos por reamostragem de famílias.
5. Auditar termos/licenças de redistribuição dos léxicos; a versão OpLexicon ainda é cópia GitHub não verificada com o original oficial.

## Atenção ao resultado de `intrépida` / `intrépido`

No léxico importado, `intrépida` tem entrada +1, enquanto `intrépido` tem polaridade inválida. Isso é uma **assimetria de qualidade dos dados**, não prova de viés social. Documente, considere tratamento conservador e evite corrigir as polaridades sem evidência externa.
