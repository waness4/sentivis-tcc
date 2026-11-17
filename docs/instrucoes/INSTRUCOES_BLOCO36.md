# SentiVis — instruções do Bloco 36

Este bloco compara **duas propostas** de tratamento de não respostas humanas exclusivamente em dados artificiais. Não concede permissão para abrir os 27 pares reservados.

1. Extraia `sentivis_bloco36_politica_g03.zip` em `C:\TCC\sentivis_bloco1`, sem alterar os arquivos já presentes.
2. Ative o `.venv` e confirme o diretório do projeto.
3. Verifique: `python -m backend.politica_ausencias_bloco36 verificar-contrato`.
4. Compare as opções em memória: `python -m backend.politica_ausencias_bloco36 comparar-opcoes` (sem gravação; pode ser repetido).
5. Teste: `python -m pytest .\backend\tests -q -rs`.
6. Confirme os arquivos não rastreados: `git status --short`.
7. Publique SOMENTE os arquivos do Bloco 35 e deste Bloco 36 depois da verificação. Não inclua `INSTRUCOES_REVISAO_V02.md` ou arquivos da pasta `data`.

Saída esperada com uma resposta **fictícia** ausente: a política estrita bloqueia, enquanto a alternativa de contabilização informa 27 pares globais, 20 elegíveis e uma não resposta. A **escolha real ainda é PENDENTE** e requer aprovação acadêmica e alteração prospectiva do executor real.

Documentos de decisão e protocolo: `docs/metodologia/DECISAO_G03_NAO_RESPOSTA_BLOCO36.md` e `docs/metodologia/PROTOCOLO_ENSAIO_G03_BLOCO36.md`.

Não execute `executar-final`: ele foi deliberadamente implementado para recusar a operação. Não execute novamente os ensaios com marcador único dos Blocos 30, 33 e 34.
