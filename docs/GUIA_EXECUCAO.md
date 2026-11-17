# Guia de execução — SentiVis

Este guia descreve os procedimentos de **desenvolvimento e uso exploratório**. Não acessa nem autoriza a avaliação reservada.

## 1. Pré-requisitos

- Windows e PowerShell (ambiente local documentado).
- **Python 3.13** como referência de desenvolvimento, `git` e conexão para instalar dependências.
- Acesso autorizado às fontes lexicais de terceiros, se quiser executar análises.
- Node.js **não** é necessário para a interface atual.

## 2. Preparar o ambiente

```powershell
git clone https://github.com/waness4/sentivis-tcc.git
cd sentivis-tcc

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r backend/requirements-dev.txt -c backend/constraints-ci.txt
```

O arquivo `backend/constraints-ci.txt` fixa as **dependências diretas** usadas na verificação automática; as dependências transitivas e o ambiente instalado são registrados por execução no GitHub Actions. Isso não constitui, isoladamente, um lockfile integral nem congela o modelo spaCy. Para instalação sem as restrições de referência, omita `-c backend/constraints-ci.txt`.

O código e a documentação deste repositório estão disponíveis publicamente. Os léxicos de terceiros e os dados reservados da avaliação não são distribuídos.

Para utilizar o método contextual V04, instale também:

```powershell
python -m pip install "spacy>=3.8.7,<3.9"
python -m spacy download pt_core_news_sm
```

O modelo treinado não deve ser substituído por um pipeline vazio. Registre a versão efetiva de `spacy` e `pt_core_news_sm` quando produzir relatórios técnicos.

## 3. Testes automatizados

```powershell
python -m pytest backend/tests -q -rs
```

O registro verificado de **17/11/2026** ([Execução 44145121330](https://github.com/waness4/sentivis-tcc/actions/runs/44145121330)) aponta **590 testes aprovados no Linux e 590 no Windows**, com um aviso de biblioteca em cada ambiente. Consulte as execuções atuais e seus artefatos de dependências no [GitHub Actions](https://github.com/waness4/sentivis-tcc/actions/workflows/testes.yml). Esses resultados não garantem aprovação em versões futuras nem validam cientificamente o método. Os testes não utilizam o conjunto reservado.

## 4. Abrir a interface

```powershell
python -m uvicorn backend.ui_server:app --reload
```

- Página inicial: http://127.0.0.1:8000/
- Documentação das rotas: http://127.0.0.1:8000/docs
- Estado informativo da interface: http://127.0.0.1:8000/api/ui/info

A página pode ser acessada sem léxicos instalados, mas tentativas de analisar textos dependem da instalação e verificação dos arquivos originais; na falta deles, a API retorna erro de indisponibilidade.

Há uma API anterior de protótipo em `backend.main:app`. Ela não serve a interface. Para demonstração visual, use `backend.ui_server:app`.

## 5. Instalar os recursos lexicais

**Não publique nem envie para GitHub os originais.** Os arquivos são obtidos e mantidos localmente e precisam respeitar as licenças pertinentes.

Estrutura esperada para as funções de auditoria e curadoria:

```text
data/lexicos/originais/
├── lexico_v3.0.txt
├── SentiLex-lem-PT02.txt
├── SentiLex-flex-PT02.txt
└── SentiLex-PT02.zip
```

Fontes documentadas: [OpLexicon na PUCRS](https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/oplexicon/) e [SentiLex-PT02 no B2SHARE](https://b2share.eudat.eu/records/cbyr7-dkf18). A cópia de OpLexicon usada na auditoria também está identificada pelo projeto, mas sua correspondência com a distribuição institucional precisa ser conferida.

Depois de posicionar **somente** os arquivos lexicais originais:

```powershell
python -m backend.lexicon_audit
python -m backend.lexicon_triage
```

A primeira etapa gera `data/lexicos/relatorio_auditoria.json`. A segunda gera `relatorio_curadoria.json` e `pendencias_curadoria.csv`. A consulta compara o SHA-256 dos originais com o registrado na curadoria e falha se detectar incompatibilidade.

## 6. Consultar um termo

Após instalar os léxicos e concluir a triagem:

```powershell
python -m backend.lexicon_consulta --termo "fácil" --lexico oplexicon
python -m backend.lexicon_consulta --termo "alegre" --lexico sentilex --alvo N0
```

Os resultados descrevem candidatos lexicais e podem solicitar revisão; não são classificação validada de frases.

## 7. Modos da interface

- **OpLexicon:** análise aditiva exploratória.
- **SentiLex / V01:** pontuação lexical condicionada à escolha manual de alvo quando necessário.
- **SentiLex / V04:** exige alvo N0 ou N1 informado manualmente, ativação explícita da hipótese de modo e spaCy com `pt_core_news_sm`.
- **Comparação:** recebe duas frases; diferenças de pontuação não comprovam viés.
- **V03:** implementada no backend, mas não selecionável na interface atual.

Abstenção não é classe neutra. Um zero de pontuação não significa, por si, ausência de sentimento.

## 8. Diagnóstico de problemas

| Sintoma | Verificação |
| :--- | :--- |
| `ModuleNotFoundError` | Ative `.venv` e instale os requirements. |
| A interface abre, mas a análise retorna `503` | Instale os originais e gere a curadoria. Confira os hashes. |
| V04 retorna indisponibilidade do modelo | Instale spaCy e execute `python -m spacy download pt_core_news_sm`. |
| Porta 8000 ocupada | Pare a instância antiga do Uvicorn antes de iniciar outra. |
| PowerShell bloqueia a ativação | Utilize um terminal compatível, respeitando a política de segurança local. |
| `git clone` retorna erro de acesso | Confira a URL, a conexão e a disponibilidade do GitHub; a clonagem pública não exige autenticação. |

## 9. O que nunca executar sem aprovação

A interface e os comandos descritos aqui **não** abrem `data/piloto/restrito/` nem `data/piloto/avaliacao_final/`. Não execute caminhos de avaliação final, não faça hash e não inspecione esses dados sem aprovação acadêmica e protocolo congelado. O comando `executar-final` do núcleo do Bloco 37 permanece intencionalmente bloqueado.

Consulte [dados e segurança](SEGURANCA_E_DADOS.md).
