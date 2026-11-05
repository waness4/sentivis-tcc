# SentiVis — Bloco 5: diagnóstico ortográfico de frases

## Instalação no Windows

Salve `sentivis_bloco5_diagnostico.zip` em `C:\TCC`, abra o PowerShell em `C:\TCC\sentivis_bloco1` e mantenha `.venv` ativado.

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco5_diagnostico.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
```

A instalação **não modifica** `backend/core.py`, `backend/main.py`, arquivos dos léxicos, relatórios ou testes existentes. Adiciona apenas `backend/frase_diagnostico.py` e `backend/tests/test_frase_diagnostico.py`.

## Execução prática

**OpLexicon — frase:**
```powershell
python -m backend.frase_diagnostico --lexico oplexicon --texto "A prova foi fácil."
```

**SentiLex — frase, sem assumir alvo:**
```powershell
python -m backend.frase_diagnostico --lexico sentilex --texto "Ela é intrépida."
```

**Par de frases — somente cobertura lexical:**
```powershell
python -m backend.frase_diagnostico --lexico oplexicon --feminina "A aluna é dedicada." --masculina "O aluno é dedicado."
```

Opcionalmente, grave o JSON com `--saida .\data\piloto\diagnostico_frase.json`.

## O que faz

- Correspondência literal de palavras e expressões compostas, privilegiando a expressão mais longa.
- Aponta tokens encontrados e ausentes sem confundir ausência com neutralidade.
- Propaga alertas de ambiguidade, inconsistências de polaridade e metadados pendentes.
- Preserva candidatos e proveniência do registro.
- Indica existência de marcadores de negação, sem interpretar escopo.
- Compara cobertura de pares, sem afirmar equivalência semântica ou viés.

## Limites e decisões que ainda exigem pesquisa

1. **NÃO é classificador científico**. Não fornece classe/pontuação de sentimento por frase nem mede viés.
2. Correspondência lexical não resolve contexto, polissemia ou categoria gramatical.
3. O SentiLex requer análise sintática do referente de N0/N1; escolher `--alvo N0` ou `--alvo N1` apenas inspeciona possibilidades.
4. Expressões idiomáticas com argumentos, construções descontínuas e flexões irregulares podem exigir regras próprias.
5. Emoticons, hashtags, símbolos e termos com números são intencionalmente não cobertos por este índice inicial e estão contabilizados em `escopo_indexacao`.
6. A cobertura é superficial e deve ser apresentada com escopo; jamais serve como evidência de viés.
7. O OpLexicon utilizado ainda é cópia cuja equivalência à distribuição oficial e condições de uso precisam ser confirmadas.

## Próxima etapa

Especificar e validar um baseline de pontuação com política contextual explícita e dados de avaliação independente. Depois, aplicar aos pares controlados com revisão humana e separação de desenvolvimento e teste.
