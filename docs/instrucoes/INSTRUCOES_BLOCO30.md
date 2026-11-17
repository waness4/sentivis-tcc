# Bloco 30 — Pré-verificação e bloqueio de ensaio sintético

**Escopo:** preparação da avaliação, sem acesso aos 27 pares reservados.

## 1. Instalação

Salve `sentivis_bloco30_preflight.zip` em `C:\TCC` e, no PowerShell com `.venv` ativo e pasta `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco30_preflight.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

O ZIP contém **somente quatro arquivos novos**: um módulo Python, um conjunto de testes, o protocolo e estas instruções. Não substitui arquivos anteriores, classificadores, fichas humanas ou dados.

## 2. Verificação pública do ambiente (somente leitura)

```powershell
python -m backend.preflight_avaliacao_bloco30 verificar-ambiente
```

Observe `estado=NAO_CONGELADO_NAO_AUTORIZADO` e `autorizacao_execucao_final=false`. O comando consulta apenas arquivos públicos em lista fixada e versões de pacotes; NÃO lê léxicos nem arquivos reservados. O SHA do commit é apenas o HEAD naquele instante, não o registro final congelado.

## 3. Ensaio fictício com bloqueio de repetição

```powershell
python -m backend.preflight_avaliacao_bloco30 ensaiar
```

O esperado é `ENSAIO_SINTETICO_CONCLUIDO` com `P_total_sinteticos=4` e `avaliacao_final_executada=false`. Em `data\piloto\restrito\bloco30_ensaio` serão criados um marcador da tentativa e um relatório sem frases reais. **Não repita o comando**: um segundo ensaio é recusado por `FileExistsError`, sem apagar o anterior. Se ocorrer erro, preserve o marcador e envie a mensagem para análise.

## 4. Testes e status Git

```powershell
python -m pytest .\backend\tests -q
git status --short
```

Esperam-se 387 testes se a versão anterior tinha 370 e não houve mudanças externas. Verifique os quatro arquivos novos. **Não use `git add .`**. O antigo `INSTRUCOES_REVISAO_V02.md` fica fora do commit.

## Restrições

A implementação deste bloco não aceita `--entrada`, `--ficha`, caminhos privados nem comando de execução da avaliação final. O ensaio com dados fictícios não valida cientificamente nenhum baseline. Não publicar fichas humanas nem relatório privado. O checklist de congelamento permanece pendente.
