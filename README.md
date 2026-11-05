# Sentivis — início do desenvolvimento

Este é o **bloco 1** do projeto. Contém a definição científica inicial e um protótipo de API com testes de engenharia. **Não contém léxicos originais, experimentos executados ou resultados de pesquisa.**

## Requisitos
Python 3.11+.

## Configuração Windows / PowerShell
```powershell
cd sentivis_bloco1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m pytest backend/tests -q
python -m uvicorn backend.main:app --reload
```
Visite http://127.0.0.1:8000/docs. `GET /api/health` funciona sem dados. As análises exigem importar léxicos verdadeiros em `data/lexicos`.

Se o PowerShell bloquear scripts, rode os comandos com `cmd` e `.venv\Scripts\activate.bat`, ou configure a política de execução conforme as regras do seu computador.

## Observação científica essencial
O motor atual implementa pontuação aditiva **provisória** apenas para testar API, normalização e tratamento da ausência de entradas. Não inclui negação, expressões compostas nem a semântica de alvos N0/N1 do SentiLex. Não utilizar suas saídas como resultados do TCC.

## Estrutura
- `PROTOCOLO_EXPERIMENTAL.md`: desenho inicial de pesquisa e critérios de validade.
- `backend/core.py`: funções determinísticas iniciais com tratamento separado para sem cobertura.
- `backend/main.py`: endpoints FastAPI de saúde, análise e comparação.
- `backend/tests`: verificações automatizadas com vocabulário artificial (somente teste de software).
- `data/piloto/pares_exemplos.csv`: exemplos **não validados** de frases; não são dataset final.
- `data/lexicos/README.md`: preparação de arquivos reais e pendências de licença.

## Próximo passo
Auditar os arquivos **originais** do SentiLex-PT02 e do OpLexicon 3.0, definir regras de consulta correspondentes e congelar o protocolo após um piloto. Depois disso começar os experimentos científicos e a interface React.
