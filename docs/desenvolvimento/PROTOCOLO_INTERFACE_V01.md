# Interface de exploração SentiVis — versão 0.1

**Status:** demonstração técnica; nenhum resultado da interface constitui resultado científico validado.

**Serviço:** `backend/ui_server.py`, que importa e estende `backend.main.app`, sem sobrescrever os endpoints existentes.

**Fontes:** `lexicon_consulta.carregar_para_consulta`, com verificação SHA-256 a partir do relatório de curadoria. Ausência/inconsistência de dados implica HTTP 503, não resultado inventado. O cache de índice exige reinício do servidor após a atualização das fontes.

**Análise:** `baseline_experimental.classificar_exploratoriamente`; os códigos de abstenção e as polaridades são os mesmos do baseline. A interface não converte abstenção em zero, não resolve N0/N1 sem seleção manual, não corrige polaridades conflitantes e não considera falta de cobertura como neutralidade.

**Comparação:** `baseline_experimental.comparar_exploratoriamente`, com duas frases digitadas livremente. O delta é descritivo e somente computado quando ambos os resultados forem pontuáveis. A interface não valida equivalência semântica e não fornece inferências de viés.

**Proteção experimental:** nenhum endpoint acessa ou lista pares reservados, respostas de revisores ou validação final; nenhum formulário capta identidades pessoais. Exemplo de comparação no navegador serve apenas à demonstração do sistema.

**Dependências:** HTML, CSS e JavaScript nativos, servidos pelo FastAPI. Nenhum serviço de fontes, analytics, CDN ou API de terceiros é utilizado.

**Aceitação:** aprovação dos testes HTTP e dos 130 testes existentes no projeto; teste manual em navegador em desktop e celular, incluindo erros HTTP 503 e textos vazios. Interface em execução não significa método cientificamente validado.
