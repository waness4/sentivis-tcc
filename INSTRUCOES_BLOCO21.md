# SentiVis — Bloco 21: fichas cegas e concordância humana dos controles

Esta atualização **não altera** V01, V02, V03, V04, interface, léxicos ou os 27 pares reservados. O pacote instala um módulo, 15 testes novos, este manual e um protocolo. **As fichas preenchidas não estão incluídas**; serão feitas por pessoas.

## Instalação

Salve `sentivis_bloco21_anotacao_controles.zip` na pasta `C:\TCC`, e, com a `.venv` ativa e o PowerShell aberto em `C:\TCC\sentivis_bloco1`, execute:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco21_anotacao_controles.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m pytest .\backend\tests -q
```

Se todos os testes anteriores estiverem presentes, são esperados **301 testes aprovados** (286 anteriores + 15 novos).

## Primeiro uso: criar as fichas vazias

```powershell
python -m backend.anotacao_controles_v01 preparar --pasta-saida .\data\piloto\restrito
```

São criadas, sem sobrescrever arquivos existentes:

- `data\piloto\restrito\ficha_controles_R01_v01.csv`
- `data\piloto\restrito\ficha_controles_R02_v01.csv`

Cada ficha tem **36 frases** em ordem embaralhada diferente. Não contém cenário, predição, escore, rótulo pré-definido ou resposta do outro revisor. Abra no Excel/LibreOffice; mantenha separador `;` e salve em **CSV UTF-8**, com todas as colunas inalteradas.

Entregue separadamente as fichas e **somente as Instruções ao anotador** do protocolo `docs\metodologia\PROTOCOLO_ANOTACAO_CONTROLES_V01.md`. Solicite duas pessoas diferentes, trabalhando de forma independente. Não peça para preencherem o que “o classificador diria”.

## Depois de receber as duas fichas preenchidas

Verifique visualmente que ambas estão completas, preservaram a estrutura, e confirme a independência dos anotadores. Execute:

```powershell
python -m backend.anotacao_controles_v01 consolidar --pasta-saida .\data\piloto\restrito
```

Saídas: `consolidacao_controles_humana_v01.csv` e `relatorio_concordancia_controles_v01.json`, na mesma pasta privada. O relatório mostra concordância entre pessoas e divergências pendentes. Não calcula acurácia do classificador nem infere viés.

**Não execute `consolidar` agora**: primeiro é necessário obter anotações humanas genuínas. O comando rejeitará fichas vazias ou incompletas.

## Versionamento

Após testes e revisão, versionar **somente**:

```powershell
git add backend/anotacao_controles_v01.py backend/tests/test_anotacao_controles_v01.py docs/metodologia/PROTOCOLO_ANOTACAO_CONTROLES_V01.md INSTRUCOES_BLOCO21.md
```

O arquivo `INSTRUCOES_REVISAO_V02.md` é documentação de uma revisão **anterior e distinta**: não pertence às novas fichas. Pode ser revisado e versionado separadamente. Não incluir arquivos da pasta `data\piloto\restrito`.
