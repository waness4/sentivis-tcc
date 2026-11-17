# Instalação — Bloco 17 SentiVis (baseline contextual V03)

Esta atualização NÃO substitui o baseline V01/V02 nem altera interface, léxicos ou dados do piloto. Copia apenas dois módulos Python, dois arquivos de testes e um protocolo metodológico.

## 1. Copiar a atualização

Salve `sentivis_bloco17_contextual_v03.zip` em `C:\TCC` e execute no PowerShell com `.venv` ativo, em `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco17_contextual_v03.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

Os arquivos novos estão em:

- `backend/baseline_contextual_v03.py`
- `backend/comparacao_sentilex_v01_v03.py`
- `backend/tests/test_baseline_contextual_v03.py`
- `backend/tests/test_comparacao_sentilex_v01_v03.py`
- `docs/metodologia/PROTOCOLO_CONTEXTUAL_SENTILEX_V03.md`
- `INSTRUCOES_BLOCO17.md`

## 2. Testar

```powershell
python -m pytest .\backend\tests -q
```

Com 208 testes anteriores + 30 adicionados, a expectativa é **238 testes** em seu computador, desde que os arquivos da interface e as dependências estejam presentes. O pacote de código enviado para construção não continha os arquivos frontend, portanto os testes de interface não puderam ser reexecutados integralmente no ambiente de construção.

O spaCy e `pt_core_news_sm` já haviam sido instalados no seu computador no Bloco 14. Sem essas dependências, a linha de comando informará como obtê-las.

## 3. Teste diagnóstico em P004 com N0 manual

```powershell
python -m backend.baseline_contextual_v03 `
  --texto "A atendente tratou o cliente com gentileza." `
  --alvo N0 --hipotese-modo --detalhado `
  --saida .\data\piloto\restrito\teste_v03_p004.json
```

**N0 e a interpretação de `com` são hipóteses manuais, não foram validados pelo classificador.** A heurística pode produzir uma classificação positiva, dependendo da PoS e da anexação sintática calculada pelo seu spaCy.

## 4. Inspecionar P007 para verificar abstenção em anexação ambígua

```powershell
python -m backend.baseline_contextual_v03 `
  --texto "A programadora resolveu o problema com habilidade." `
  --alvo N0 --hipotese-modo `
  --saida .\data\piloto\restrito\teste_v03_p007.json
```

A análise sintática que você mostrou anteriormente atribuiu `nmod` a `habilidade`. Nesta situação esperamos `ABSTENCAO_ANEXACAO_AMBIGUA`, não uma classificação positiva artificial. A saída real depende do modelo instalado.

Verifique as duas saídas compactamente:

```powershell
@'
import json
from pathlib import Path
for nome in ("teste_v03_p004.json", "teste_v03_p007.json"):
    p = Path("data/piloto/restrito") / nome
    d = json.loads(p.read_text(encoding="utf-8"))
    print(nome, "status:", d["status"], "classe:", d["classe_exploratoria"],
          "pontuacao:", d["pontuacao_exploratoria"])
'@ | python -
```

## 5. Comparar V01 x V03 nos pares aprovados de desenvolvimento

Somente após verificar os testes e as saídas dos passos anteriores:

```powershell
python -m backend.comparacao_sentilex_v01_v03 `
  --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v02.csv `
  --alvo N0 --hipotese-modo `
  --saida-json .\data\piloto\restrito\comparacao_sentilex_v01_v03.json `
  --saida-csv .\data\piloto\restrito\comparacao_sentilex_v01_v03.csv
```

Importante: a V01 é executada **com N0 manual**, diferentemente do piloto SentiLex original sem N0, que se abstinha de todas as frases. Não compare os números sem essa distinção. Não existe inferência de viés. A comparação filtra somente desenvolvimento aprovado, antes de classificar. Os 27 pares reservados não são usados para pontuação.

Os relatórios não serão sobrescritos. Se já existirem, escolha nomes de arquivo novos.

## 6. GitHub (somente depois de verificar os comandos)

```powershell
git add backend/baseline_contextual_v03.py backend/comparacao_sentilex_v01_v03.py backend/tests/test_baseline_contextual_v03.py backend/tests/test_comparacao_sentilex_v01_v03.py docs/metodologia/PROTOCOLO_CONTEXTUAL_SENTILEX_V03.md INSTRUCOES_BLOCO17.md
git diff --cached --stat
git commit -m "feat: adicionar hipotese contextual SentiLex V03"
git push
```

**Não adicione** o diretório `data/piloto/restrito`, fichas humanas, JSON/CSV privados ou os léxicos originais ao GitHub. Não integre V03 ao frontend enquanto as limitações e o comportamento real não estiverem revisados.
