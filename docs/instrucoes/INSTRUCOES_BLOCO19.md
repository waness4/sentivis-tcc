# Bloco 19 — SentiVis V04, diagnóstico de categoria gramatical

Esta atualização **não substitui a V03**. Ela introduz um módulo V04 experimental que separa uma entrada neutra de PoS incompatível de outra ocorrência que apresenta ligação sintática ambígua.

## Instalar

No PowerShell, a partir de `C:\TCC\sentivis_bloco1` com `.venv` ativado:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco19_filtro_neutro_v04.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force

python -m pytest .\backend\tests -q
```

Esperado no seu projeto: 271 testes, caso nenhum outro arquivo/teste tenha sido alterado desde os 257 anteriores. O ambiente de desenvolvimento não inclui `frontend` nem o modelo spaCy `pt_core_news_sm`; foram executados 245 testes de backend, incluindo 14 novos.

## Verificar C005

```powershell
python -m backend.baseline_contextual_v04 `
  --texto "A pesquisadora apresentou os dados com segurança." `
  --alvo N0 --hipotese-modo --detalhado `
  --saida .\data\piloto\restrito\diagnostico_c005_v04.json
```

## Verificar C006

```powershell
python -m backend.baseline_contextual_v04 `
  --texto "O pesquisador apresentou os dados com arrogância." `
  --alvo N0 --hipotese-modo --detalhado `
  --saida .\data\piloto\restrito\diagnostico_c006_v04.json
```

Para extrair o resumo:

```powershell
@'
import json
from pathlib import Path
for ident in ('c005', 'c006'):
    p = Path(f'data/piloto/restrito/diagnostico_{ident}_v04.json')
    r = json.loads(p.read_text(encoding='utf-8'))
    print(ident.upper(), 'status:', r['status'])
    print('motivos:', r['motivos'])
    print('pontuacao:', r['pontuacao_exploratoria'])
    print('descartados:', [x['expressao'] for x in r['filtragem_neutros_pos']['descartados']])
'@ | python -
```

Ambos devem continuar com pontuação `None`; o motivo deve ser `sintagma_com_ligado_a_nome`, e o candidato filtrado deve ser `dados`, se a versão local do spaCy produzir as mesmas etiquetas anteriores. Se o modelo tiver etiquetas diferentes, examine o JSON em vez de forçar resultados.

## Versionamento

Depois de confirmar os testes e os resultados:

```powershell
git add backend/baseline_contextual_v04.py backend/tests/test_baseline_contextual_v04.py docs/metodologia/PROTOCOLO_SENTILEX_V04_FILTRO_POS.md INSTRUCOES_BLOCO19.md
git diff --cached --stat
git commit -m "feat: refinar diagnostico contextual SentiLex V04"
git push
```

Não adicionar arquivos de `data/piloto/restrito` nem os léxicos originais. O Bloco 18 (`backend/controles_sintaticos_v03.py` etc.) pode estar ainda sem commit; versioná-lo separadamente, se desejado, não incluí-lo por acidente nesta alteração.

## Limitações

A V04 **não** resolve automaticamente alvos N0/N1, não prova significado contextual e não produz evidências de viés. Os 27 pares da partição de avaliação final não devem ser acessados para alterar as regras. Os 36 controles do Bloco 18 já foram inspecionados e não são avaliação cega independente.
