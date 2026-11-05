# Instalação do Bloco 4 — consulta lexical segura

Descompacte o ZIP **na raiz do projeto** `C:\TCC\sentivis_bloco1`, sobrescrevendo apenas se solicitado. Os arquivos incluídos são novos e não substituem `backend/core.py`, `backend/main.py`, os léxicos, nem relatórios anteriores.

Com `(.venv)` ativado, execute:

```powershell
python -m pytest .\backend\tests -q
python -m backend.lexicon_consulta --lexico sentilex --termo "aborreça" --alvo N0
python -m backend.lexicon_consulta --lexico oplexicon --termo "fácil"
python -m backend.lexicon_consulta --lexico sentilex --termo "intrépido" --alvo N0
```

Resultados esperados: os testes adicionais são **14** (somando aos 36 anteriormente aprovados, espera-se 50). Para `aborreça`, deve retornar `revisao_necessaria` por conflitos/lematização; para `intrépido`, `revisao_necessaria` por polaridade fora do padrão.

A consulta valida que os SHA-256 dos léxicos originais correspondem aos SHA-256 de `relatorio_curadoria.json`. Se não corresponderem, a execução será bloqueada.

**Não use as saídas para resultados científicos de sentimentos ou gênero.** A implementação é exclusivamente uma ferramenta de auditoria lexical.
