# Bloco 27 — Uma ficha R01: auditoria e adendo metodológico

## Instalação

A partir de `C:\TCC\sentivis_bloco1`, depois de salvar `sentivis_bloco27_r01_unica.zip` em `C:\TCC`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco27_r01_unica.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

O pacote deposita uma **cópia exata da ficha enviada**, com outro nome, em `data/piloto/restrito/ficha_controles_R01_recebida.csv` para não sobrescrever a ficha-modelo anterior. O conteúdo privado não deve ser enviado ao GitHub. Confira se a cópia recebida está correta antes de executar.

## Executar somente a auditoria individual

```powershell
python .\scripts\auditar_r01_bloco27.py
```

O script lê apenas os 36 controles públicos e a cópia da ficha R01. Não executa os modelos, não calcula acurácia, não lê a avaliação final e não usa a ficha ausente de R02. Cria `data/piloto/restrito/relatorio_r01_unica_bloco27.json` sem sobrescrever arquivos existentes. Se desejar repetir, use `--saida` com um nome novo.

## Conferir versionamento

```powershell
python -m pytest .\backend\tests -q
git status --short
```

Não usar `git add .`. Somente `INSTRUCOES_BLOCO27.md`, o script, o teste e `docs/metodologia/ADENDO_ANOTADOR_UNICO_BLOCO27.md` podem ser candidatos a um commit público; mantenha a ficha, o relatório gerado e a avaliação final fora do Git. O arquivo `INSTRUCOES_REVISAO_V02.md` já existia não versionado e permanece fora do commit.

## Observação científica

A decisão de continuar com uma pessoa é **pós-coleta** e limita o estudo: ausência de concordância entre anotadores, campo de papel sintático ausente, referentes não padronizados e categoria neutra ainda sem distinção entre descrição factual e avaliação neutra. Não chame essa etapa de validação independente.

## Comparação descritiva opcional usando os relatórios locais existentes

Depois de obter a auditoria individual acima, execute:

```powershell
python -m scripts.comparar_r01_bloco27
```

Ele lê exclusivamente as duas tabelas já existentes em `data/piloto/restrito/` (`controles_sintaticos_v03_resultado.csv` e `comparacao_controles_v03_v04.csv`) e compara as classes pontuadas de V01, V03 e V04 com a marcação individual **somente nas 29 respostas `positivo`/`negativo`**. As 7 marcações `neutro` não são classificadas automaticamente como `neutra` ou `sem_avaliacao`. O relatório inclui abstenções e sensibilidade excluindo C001; não é uma avaliação independente nem calcula acurácia. Se algum arquivo local não tiver o nome esperado, confira seu caminho e passe `--v01-v03` e `--v03-v04` explicitamente. Nunca aponte esses parâmetros para arquivos de avaliação final.
