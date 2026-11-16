# Bloco 25 — Registro parcial científico (documentação apenas)

Este pacote adiciona `docs/metodologia/RELATORIO_PARCIAL_BLOCO25.md` ao projeto SentiVis.

**Não modifica código, testes, léxicos ou arquivos privados.** Os números são descritos como observações previamente registradas e devem ser reconferidos nos relatórios locais antes do TCC final.

## Instalar no PowerShell

Salve o ZIP na pasta `C:\TCC` e, com o projeto aberto, execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco25_relatorio_parcial.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
Get-Content .\docs\metodologia\RELATORIO_PARCIAL_BLOCO25.md -TotalCount 22 -Encoding UTF8
git status --short
```

Quando revisar o conteúdo, registre **somente** a documentação:

```powershell
git add docs/metodologia/RELATORIO_PARCIAL_BLOCO25.md INSTRUCOES_BLOCO25.md
git diff --cached --stat
git commit -m "docs: consolidar resultados parciais e limites metodologicos"
git push origin main
```

Não use `git add .` nem inclua fichas/relatórios em `data/piloto/restrito`. O `INSTRUCOES_REVISAO_V02.md` anterior pode permanecer separado.

## Próximo trabalho

Aguardar as duas fichas dos 36 controles e confirmar a independência real do preenchimento. A consolidação humana existente só deve rodar depois de ambas estarem completas. Não executar avaliação nos 27 pares reservados ainda.
