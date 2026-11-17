# Bloco 18 — Controles sintáticos V03

**Dependências:** Blocos anteriores instalados e testados (238 testes), Python 3.13, spaCy + `pt_core_news_sm`, SentiLex preservado na pasta original. Não sobrescrever os resultados anteriores.

## 1. Descompactar

Salve `sentivis_bloco18_controles_sintaticos.zip` em `C:\TCC` e execute, a partir de `C:\TCC\sentivis_bloco1`, com `.venv` ativo:

```powershell
Expand-Archive `
  -Path "C:\TCC\sentivis_bloco18_controles_sintaticos.zip" `
  -DestinationPath "C:\TCC\sentivis_bloco1" `
  -Force
```

## 2. Testes e integridade dos controles

```powershell
python -m pytest .\backend\tests -q
python -m backend.controles_sintaticos_v03 --modo verificar
```

Esperam-se **257 testes** no ambiente completo (238 anteriores + 19 novos), se os arquivos das versões anteriores permanecerem presentes. O segundo comando deve identificar **36 controles** com SHA-256 prefixado `a0272955`.

## 3. Diagnóstico V01 × V03 (SentiLex)

```powershell
python -m backend.controles_sintaticos_v03 `
  --modo executar `
  --alvo N0 --hipotese-modo `
  --saida-json .\data\piloto\restrito\controles_sintaticos_v03_resultado.json `
  --saida-csv .\data\piloto\restrito\controles_sintaticos_v03_resultado.csv
```

O comando NÃO lê o dataset do piloto. As saídas são novas e, por padrão, não podem sobrescrever arquivos existentes. Se forem criadas, utilize outros nomes numa execução posterior.

O relatório apresenta **cobertura de pontuação, motivos de abstenção, transições e dados de auditoria**. Não calcula acurácia nem F1: **não há rótulos humanos**. N0 é hipótese manual, não resolução de referentes.

## 4. Inspecionar o resumo

```powershell
python -c "import json; p=json.load(open('data/piloto/restrito/controles_sintaticos_v03_resultado.json',encoding='utf-8')); print('Controles:',p['n_controles']); print('V01:',p['metricas']['v01']); print('V03:',p['metricas']['v03']); print('Transições:',p['transicoes'])"
```

Envie a saída para interpretarmos os resultados e definirmos a próxima etapa. **Não altere a V03 com base neste conjunto e depois o apresente como avaliação independente**. Os 27 pares reservados continuam fora deste bloco.

## 5. GitHub (somente após confirmar os testes)

```powershell
git add backend/controles_sintaticos_v03.py backend/tests/test_controles_sintaticos_v03.py data/controles/controles_sintaticos_v01.csv docs/metodologia/PROTOCOLO_CONTROLES_SINTATICOS_V03.md INSTRUCOES_BLOCO18.md
git diff --cached --stat
git commit -m "test: adicionar controles sintaticos para V03"
git push
```

Apenas os controles **sintéticos sem anotações humanas** entram no Git. **Não** versionar as saídas do diagnóstico, as fichas dos revisores nem os léxicos originais.

## Nota metodológica

Controles criados por quem conhece as falhas da V03 são uma sonda de robustez, não dados de generalização independente. A avaliação científica final permanece pendente.
