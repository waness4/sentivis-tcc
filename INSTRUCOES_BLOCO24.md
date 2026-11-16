# SentiVis — Bloco 24: ajustes finais de legibilidade

Escopo exclusivamente visual: não altera `frontend/app.js`, APIs, classificadores, critérios de pontuação, dados reservados ou fichas humanas.

## Instalar no Windows / PowerShell

1. Salve `sentivis_bloco24_ajuste_tabelas.zip` em `C:\TCC`.
2. Na raiz do projeto (`C:\TCC\sentivis_bloco1`) e com `.venv` ativo, execute:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco24_ajuste_tabelas.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" -Force

python .\scripts\aplicar_bloco24.py
python -m pytest .\backend\tests -q
```

O instalador verifica os textos esperados antes de modificar os arquivos e pode ser executado novamente sem duplicar alterações.

## Verificação visual

Reinicie ou atualize o servidor e, se necessário, use `Ctrl+F5` no navegador. Selecione SentiLex-PT02, V04, N0, hipótese sintática ativada. Em **Comparar referências de gênero**, teste:

- A atendente tratou o cliente com gentileza.
- O atendente tratou o cliente com gentileza.

As palavras “Termo” e “gentileza” não devem partir no meio. Se a tabela contextual ficar larga demais no cartão, a rolagem é **dentro da tabela**, sem distorcer o restante da página.

No topo, o cartão informativo exibirá `Interface experimental · baselines V01 e V04`, sem usar `v0.1` como se fosse a versão atual de todos os recursos.

## Git (somente após verificar)

```powershell
git status --short
git add frontend/index.html frontend/styles.css scripts/aplicar_bloco24.py backend/tests/test_interface_bloco24.py INSTRUCOES_BLOCO24.md docs/desenvolvimento/PROTOCOLO_AJUSTE_VISUAL_BLOCO24.md
git diff --cached --stat
git commit -m "style: corrigir legibilidade das tabelas e identificar baselines"
git push origin main
```

Não incluir `INSTRUCOES_REVISAO_V02.md` nem qualquer conteúdo de `data/piloto/restrito`.

## Limites

Ajuste visual não constitui validação científica. Nenhum dado da avaliação final deve ser aberto ou alterado. Este pacote não inclui léxicos ou relatórios privados.
