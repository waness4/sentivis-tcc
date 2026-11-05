# SentiVis — Bloco 9: revisão humana do piloto de desenvolvimento

**Objetivo:** gerar fichas independentes para os 9 pares de desenvolvimento, consolidar avaliações humanas sem decisões automáticas e preservar os 27 pares de avaliação. Nenhum léxico ou classificador é executado neste módulo.

## Instalação (PowerShell)

Estando em `C:\TCC\sentivis_bloco1` com `(.venv)` ativado, salve o arquivo `sentivis_bloco9_revisao.zip` em `C:\TCC` e execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco9_revisao.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
```

A execução local com os módulos disponíveis aprovou 124 testes; o projeto da usuária inclui mais seis testes iniciais, logo **130 aprovados são esperados**, mas precisam ser confirmados no Windows.

## Gerar as fichas do piloto

```powershell
python -m backend.revisao_humana preparar
```

Resultado previsto: 9 pares de desenvolvimento, 0 pares da avaliação exportados. Serão criados:

- `data/piloto/restrito/ficha_revisor_A_desenvolvimento.csv`
- `data/piloto/restrito/ficha_revisor_B_desenvolvimento.csv`

**Os arquivos não são sobrescritos por padrão.** Não executar `--substituir-saida` após os revisores iniciarem a anotação.

## Revisão humana (etapa manual e obrigatória)

1. Entregar a ficha A a um revisor humano e a ficha B a outra pessoa. Os revisores não devem compartilhar suas respostas entre si.
2. Cada pessoa preenche `equivalencia` com `sim` ou `nao`. O rótulo de sentimento (`rotulo`) deve ser `positiva`, `negativa` ou `neutra`, quando houver avaliação comum à dupla.
3. Para `sim`, exigir o rótulo; para `nao`, justificar em `observacoes` (pode deixar `rotulo` vazio). Dúvidas, ambiguidades, ironia ou linguagem pouco natural devem ser registradas em `observacoes`.
4. Não mostrar aos revisores os rótulos planejados, a lista de léxicos, saídas do algoritmo ou respostas do outro revisor.
5. Salvar cada CSV mantendo o cabeçalho, `;` como separador, codificação UTF-8 e as frases originais **inalteradas**.

## Consolidar após receber as duas fichas

Substitua `REV_A` e `REV_B` por identificadores pseudônimos distintos **sem usar nomes pessoais**:

```powershell
python -m backend.revisao_humana consolidar --id-a REV_A --id-b REV_B
```

Saídas locais (ignoradas pelo Git):

- `data/piloto/restrito/pares_desenvolvimento_revisados_v01.csv` — preserva todos os 36 pares, mas preenche revisão **somente dos 9 de desenvolvimento**;
- `data/piloto/restrito/relatorio_revisao_v01.json` — contagem e estado das revisões, IDs e hashes, sem frases de avaliação.

Discordâncias ou equivalência `nao` recebem `PENDENTE_ADJUDICACAO`. **Não há decisão automática**. Somente avaliador humano terceiro poderá adjudicar, conforme protocolo aprovado e com trilha documental própria. A função existente `validar_pares` poderá nomear casos de equivalência `nao` como `REPROVADO_EQUIVALENCIA`; neste Bloco 9, o estado *operacional* é `PENDENTE_ADJUDICACAO` até decisão humana. Não editar os originais para forçar concordância.

Verifique a estrutura do consolidado:

```powershell
python -m backend.pares_piloto --entrada .\data\piloto\restrito\pares_desenvolvimento_revisados_v01.csv --saida .\data\piloto\restrito\relatorio_validacao_pares.json
```

**Não execute `--piloto` até haver revisão real concluída, critérios definidos e decisão sobre os casos discordantes.** Nunca execute ou inspecione análises da partição de avaliação enquanto o método estiver em desenvolvimento.

## Versionar somente o código e protocolo

```powershell
git status --short
git check-ignore data/piloto/restrito/ficha_revisor_A_desenvolvimento.csv
# Deve imprimir o caminho, confirmando exclusão.
git add backend/revisao_humana.py backend/tests/test_revisao_humana.py docs/metodologia/PROTOCOLO_EXECUCAO_REVISAO_DESENVOLVIMENTO.md INSTRUCOES_BLOCO9.md
git diff --cached --stat
git commit -m "feat: preparar dupla revisao humana do piloto"
git push
```

Não versionar as fichas preenchidas, os dados restritos, a partição reservada nem os léxicos de terceiros. Mesmo em repositório privado, proteger o acesso aos dados de avaliação.
