# Dados, privacidade e publicação

O SentiVis é um protótipo acadêmico. Este repositório guarda **código, documentação, controles públicos de desenvolvimento e testes sintéticos**, não o conjunto reservado da avaliação final.

## Materiais que não devem ser publicados

- `data/lexicos/originais/`, cópias redistribuíveis somente após conferir as licenças específicas.
- `data/lexicos/relatorio_*.json` e `data/lexicos/pendencias_*.csv`: saídas locais de auditoria/curadoria, cuja publicação exige revisão.
- `data/piloto/restrito/` e `data/piloto/avaliacao_final/`.
- Fichas humanas, respostas privadas, versões de controle sob reserva, arquivos `.env`, chaves, credenciais e dados pessoais.

As regras de `.gitignore` ajudam a evitar inclusão acidental, mas **não protegem arquivos que já tenham sido commitados nem substituem revisão humana**.

## Conferir antes de cada publicação

```powershell
git status --short
git diff --cached --name-only
git diff --cached --stat
git check-ignore data/lexicos/originais/lexico_v3.0.txt
git check-ignore data/piloto/restrito/arquivo-privado.csv
```

O último comando apenas demonstra se o caminho fictício está ignorado; não crie esse arquivo para testá-lo.

## Estado da avaliação final

O protocolo de 27 pares e 54 frases permanece sob restrição. A avaliação real **não foi executada**. Faltam decisões metodológicas G01–G08, política de respostas ausentes, custódia privada, executor final e congelamento técnico. A execução exige autorização acadêmica verificável anterior a qualquer leitura, inspeção ou hash da partição reservada.

Os dados fictícios dos testes não são evidência de desempenho ou de viés. Resultados de auditoria lexical também não comprovam erro linguístico, discriminação ou mitigação.

## Capturas e vídeos

Não publique exemplos da partição reservada como demonstração. Antes de enviar prints, verifique termos, endereços, e-mails, notificações e dados que possam identificar participantes. Veja [instruções de captura](capturas/README.md).

## Licenças

O código ainda não possui `LICENSE` definida. OpLexicon e SentiLex são recursos de terceiros com condições próprias. A eventual abertura pública do repositório não deverá ser realizada sem conferir dados, licenças, arquivos previamente versionados e critérios institucionais.
