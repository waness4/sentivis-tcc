# Bloco 31 — Inventário de integridade dos léxicos e do ambiente

## Instalar

Salve `sentivis_bloco31_manifesto.zip` em `C:\TCC` e execute na raiz `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco31_manifesto.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
```

O pacote adiciona somente quatro arquivos: módulo, testes, protocolo e estas instruções. Não substitui originais lexicais, ficha humana, pré-registro antigo ou avaliadores.

## Conferir integridade (somente leitura)

```powershell
python -m backend.manifesto_lexicos_bloco31 verificar
```

Esperado: `integridade_lexicos=CONFERIDA_COM_RELATORIOS_LOCAIS`, `estado=NAO_CONGELADO_NAO_AUTORIZADO`, quatro artefatos lexicais com hashes conferidos. O programa **não lê** dados da avaliação final.

## Registrar manifesto preliminar (uma única vez, depois de verificar)

```powershell
python -m backend.manifesto_lexicos_bloco31 registrar
```

O comando cria `data\piloto\restrito\bloco31_manifesto\manifesto_preliminar_bloco31.json`, excluído do Git. Uma segunda execução é bloqueada; **não apague nem sobrescreva** o arquivo para contornar esse bloqueio. Se a verificação falhar, não execute `registrar`: guarde e envie o erro.

## Testes e inspeção

```powershell
python -m pytest .\backend\tests -q
git status --short
```

Se os 387 testes anteriores permanecerem válidos, o total esperado é **403 testes** (16 novos). Não execute a avaliação final. A versão e o SHA de código definitivos ainda precisarão ser congelados e aprovados academicamente.

## O que enviar ao ChatGPT

Informe apenas o resultado dos comandos (o manifesto pode conter hashes, não frases nem rótulos reservados). **Não** compartilhe ou abra os 27 pares nem a ficha final antes de autorização.
