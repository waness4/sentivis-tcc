# Auditoria técnica inicial — SentiVis

**Data da revisão:** 17/11/2026  
**Escopo:** inspeção estática do repositório remoto. Esta revisão não é certificação de segurança, validação científica ou execução da suíte de testes.

## Verificações realizadas

Foram conferidos a árvore do repositório, a API principal (`backend/main.py`), o servidor da interface (`backend/ui_server.py`), o motor técnico original (`backend/core.py`), o carregamento e a consulta lexical (`backend/lexicon_consulta.py`), as rotinas de auditoria e curadoria (`backend/lexicon_audit.py` e `backend/lexicon_triage.py`), os arquivos de dependências e testes selecionados (`test_core.py` e `test_ui_server.py`). Os arquivos da interface foram examinados anteriormente para fins de apresentação e documentação, sem auditoria funcional completa.

## Ajustes desta revisão

| Área | Constatação | Tratamento |
| :--- | :--- | :--- |
| Dependências | `pytest` aparecia também em `requirements.txt`, que é usado na instalação da aplicação. | Removido das dependências de execução; permanece em `requirements-dev.txt`. |
| Mensagem de falha | A ausência de `frontend/index.html` referia-se ao antigo “Bloco 10”. | Substituída por orientação genérica para verificar a pasta `frontend`. |
| Documentação | Não havia um registro específico das verificações estáticas e de seu alcance. | Este registro distingue observações, mudanças e validações ainda pendentes. |

## Observações que exigem avaliação posterior

- `backend/core.py` e `backend/main.py` preservam um protótipo técnico anterior. O teste `test_aviso_negacao` mostra que a expressão “não bom” pode resultar em pontuação positiva nesse protótipo. Ele **não deve ser utilizado como evidência científica**. O comportamento da interface experimental é implementado por outros módulos e precisa ser avaliado separadamente.
- Os intervalos de versões em `requirements.txt` e `requirements-dev.txt` não equivalem a um ambiente congelado. Para reprodução científica, registrar versões efetivas do Python, das bibliotecas e do modelo linguístico, além dos hashes dos arquivos de entrada autorizados.
- A leitura e a integridade dos léxicos são verificadas no carregamento. O índice é mantido em cache durante a execução; ao substituir recursos lexicais locais, é necessário reiniciar o servidor antes de uma nova demonstração.
- A interface e os endpoints retornam resultados **exploratórios**, sem validação científica. Os dados reservados e a execução final não foram acessados.

## Verificações ainda não concluídas

1. Executar `python -m pytest backend/tests -q -rs` em instalação limpa e registrar versão, data, resultado e testes ignorados.
2. Realizar inspeção linha a linha dos módulos restantes, com foco nas rotinas de anotação, métricas, caminhos locais e executores bloqueados.
3. Revisar as respostas HTTP e comportamentos de erro com testes de integração, sem léxicos privados.
4. Verificar as dependências efetivamente instaladas, compatibilidade com Python 3.13 e ausência de credenciais ou dados pessoais no histórico Git.
5. Validar visualmente a aplicação em diferentes tamanhos de tela e conferir acessibilidade e comportamento em navegadores.

**Limite desta etapa:** não foi possível executar o projeto localmente a partir do repositório remoto no ambiente desta revisão. Portanto, a contagem de testes registrada anteriormente não foi revalidada aqui.
