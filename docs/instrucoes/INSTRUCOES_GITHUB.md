# Integração do SentiVis ao GitHub (PowerShell)

**Contexto:** o projeto já existe em `C:\TCC\sentivis_bloco1`; não o substitua pelo ZIP. Extraia este pacote dentro dessa pasta.

```powershell
cd C:\TCC\sentivis_bloco1
# O pacote já deve ter sido extraído aqui.
python -m pytest .\backend\tests -q
# Prévia das mudanças dos documentos de implementação
.\scripts\organizar_docs.ps1
# Se concordar, aplicar a organização
.\scripts\organizar_docs.ps1 -Aplicar
# Conferir o que será excluído do Git
git init -b main
git status --short
# O --ignored abaixo mostra arquivos ignorados, sem adicioná-los
git status --short --ignored
# Testar a regra para o léxico original
git check-ignore data/lexicos/originais/lexico_v3.0.txt
# Preparar o primeiro commit (ainda sem enviar ao GitHub)
git add .
git diff --cached --stat
# ATENÇÃO: revisar cuidadosamente o resultado antes de executar git commit!
```

Depois de revisar, quando tudo estiver correto:

```powershell
git commit -m "chore: estruturar repositorio e documentacao do TCC"
```

Crie no GitHub um repositório **privado** chamado `sentivis-tcc` **sem** adicionar README ou `.gitignore` na interface. Copie a URL HTTPS exibida pelo GitHub e execute (substitua pela URL real):

```powershell
git remote add origin https://github.com/SEU_USUARIO/sentivis-tcc.git
git push -u origin main
```

Se `git commit` pedir identidade, configure nome e e-mail do autor de acordo com suas preferências. Antes de publicar, verifique se o índice Git NÃO contém `data/lexicos/originais/`, dados humanos privados, segredos ou arquivos internos do ambiente `.venv`.

Para conferir os caminhos que serão commitados:

```powershell
git diff --cached --name-only
```

**Importante:** a pasta `data/piloto/pares_candidatos_v01.csv` foi excluída por conter exemplos reservados para avaliação. Também não publicar resultados e rótulos humanos confidenciais.
