# SentiVis — Bloco 28: preparação da avaliação final com um anotador

**Estado: documentação proposta, NÃO congelada, SEM execução da avaliação final.** Elaborado em 16/11/2026.

## Instalação

Salve `sentivis_bloco28_protocolo_anotador_unico.zip` em `C:\TCC` e, no PowerShell, no projeto `C:\TCC\sentivis_bloco1`, execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco28_protocolo_anotador_unico.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
Get-ChildItem .\docs\metodologia\*BLOCO28* | Select-Object Name
Get-Content .\docs\metodologia\CHECKLIST_CONGELAMENTO_BLOCO28.md
```

Não há instalação de dependências, execução de classificador nem testes novos. O pacote contém apenas arquivos de texto e um modelo CSV **com cabeçalho, sem dados reservados**.

## O que o bloco define

- Adendo ao pré-registro do Bloco 26: somente um anotador humano para a partição final, distinguindo resultado exploratório de validação independente.
- Procedimento de anotação *antes* de apresentar previsões de qualquer baseline; elegibilidade dos pares e impossibilidade de adjudicação por um segundo avaliador.
- Métricas descritivas com denominadores claros, abstenções explícitas e comparação positiva/negativa distinta de marcações neutras.
- Checklist de congelamento obrigatório, ainda PENDENTE.
- Ficha-modelo vazia com cabeçalho `id_par;frase_feminina;frase_masculina;equivalencia;rotulo;observacoes`, **não gerada a partir do dataset real**.

## Restrições e próximos passos

1. **Não abrir nem classificar os 27 pares reservados neste bloco.** Não executar `backend.revisao_humana preparar` para eles: o comando existente foi desenvolvido somente para os 9 pares de desenvolvimento.
2. Revisar o plano junto aos responsáveis acadêmicos, definir formalmente os itens marcados como pendentes, e criar futuramente um programa final separado, ensaiado somente com pares fictícios.
3. Antes de usar a partição reservada, registrar data, commit, hashes e dependências, critérios, procedimento de custódia e versão do programa; revisar e aprovar o congelamento formalmente.
4. Preservar as respostas humanas e os resultados individuais em `data/piloto/restrito/`, excluído pelo `.gitignore`. Não utilizar `git add .`.

## Arquivos de documentação pública

- `docs/metodologia/ADENDO_AVALIADOR_UNICO_FINAL_BLOCO28.md`
- `docs/metodologia/PLANO_ANALISE_FINAL_BLOCO28.md`
- `docs/metodologia/CHECKLIST_CONGELAMENTO_BLOCO28.md`
- `docs/metodologia/MODELO_FICHA_FINAL_BLOCO28.csv` — **somente cabeçalho**

A presente documentação não congela o protocolo automaticamente e não altera o arquivo `PLANO_PRE_REGISTRO_AVALIACAO_FINAL_BLOCO26.md`: a diferença deve permanecer visível no histórico científico.
