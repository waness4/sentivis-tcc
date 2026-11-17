# Dados lexicais — orientação de instalação

Os arquivos originais de **OpLexicon 3.0** e **SentiLex-PT02** não estão incluídos neste repositório devido à necessidade de verificar as condições de uso e redistribuição. Não confundir ausência no Git com ausência no ambiente local dos pesquisadores.

O fluxo atual **não se limita** ao CSV provisório do primeiro protótipo. A auditoria utiliza arquivos originais e preserva informações de categoria gramatical, flexão, alvo de polaridade e metadados.

## Originais esperados

```text
data/lexicos/originais/
├── lexico_v3.0.txt
├── SentiLex-lem-PT02.txt
├── SentiLex-flex-PT02.txt
└── SentiLex-PT02.zip
```

- OpLexicon: https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/oplexicon/
- Registro de dados SentiLex-PT02: https://b2share.eudat.eu/records/cbyr7-dkf18

É necessário conferir integridade, proveniência e licença de cada fonte; não publicar os arquivos automaticamente.

## Auditoria e curadoria

Depois de obter os arquivos de fontes autorizadas:

```powershell
python -m backend.lexicon_audit
python -m backend.lexicon_triage
```

Isso gera relatórios locais ignorados pelo Git:

- `relatorio_auditoria.json`;
- `relatorio_curadoria.json`;
- `pendencias_curadoria.csv`.

A consulta `backend.lexicon_consulta` verifica SHA-256 contra a curadoria antes de usar originais. Não alterar os arquivos originais para eliminar conflitos ou forçar polaridades. Uma sinalização de curadoria não significa erro confirmado.

Para instalar e executar a interface, consulte [o guia principal](../../docs/GUIA_EXECUCAO.md).

### API histórica

A API inicial em `backend.main` ainda aceita CSVs normalizados provisórios (`oplexicon_3.csv` e `sentilex_pt02.csv`). Esse contrato **não** substitui a auditoria baseada em arquivos originais nem a interface experimental em `backend.ui_server`.
