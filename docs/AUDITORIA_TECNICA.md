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

## Continuação — métricas, anotação e executor experimental

Inspeção estática dos arquivos `backend/metricas_exploratorias.py`, `backend/anotacao_controles_v01.py`, `backend/revisao_humana.py`, `backend/politica_ausencias_bloco36.py` e `backend/executor_avaliacao_bloco37.py`, acompanhada da identificação dos testes de métricas e do executor do Bloco 37.

**Verificações positivas de código:** o cálculo descritivo separa ausência de pontuação de zero; valida o delta apenas para pares pontuados e registra denominadores. O executor de avaliação possui função `executar_final` que lança `PermissionError`, e seu modo de simulação confere conteúdo contra uma fixture artificial. Os testes contêm cenários para rejeitar dados malformados, impedir a execução final pela CLI e verificar abstenções.

**Correção implementada — pendente de execução dos testes:** `backend/metricas_exploratorias.py` agora serializa JSON e CSV antes de gravar, utiliza arquivos temporários nos diretórios de destino, publica arquivos completos por hard links exclusivos (`os.link`) sem sobrescrever resultados existentes e desfaz a primeira publicação se a segunda falhar. Foram adicionados quatro testes em `backend/tests/test_metricas_exploratorias.py` para sucesso, CSV inválido, falha na segunda publicação e recusa de sobrescrita. **Limite:** os dois links não constituem uma transação atômica conjunta; interrupção abrupta entre as publicações ainda pode deixar um arquivo publicado. O ambiente deve suportar hard links locais. Conferir os dois arquivos antes de usar os resultados e não tratar esta implementação como garantia de recuperação após queda de energia.

**Limite da verificação:** a leitura foi estática e seletiva; não houve execução dos testes nem inspeção integral de todos os ramos de cada módulo. O resultado desta seção não representa autorização acadêmica nem comprovação de segurança em produção. Os procedimentos da avaliação reservada continuam bloqueados.

## Correção de publicação dos resultados — validação pendente

A alteração de gravação do par JSON/CSV foi versionada com testes de regressão, sem modificar a fórmula das métricas, os dados reservados ou os comandos bloqueados do executor final. **Os testes adicionados ainda não foram executados neste ambiente**. Para verificar localmente:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m pytest backend/tests/test_metricas_exploratorias.py -q -rs
python -m pytest backend/tests -q -rs
```

Antes de considerar os resultados publicáveis, confirmar também o comportamento de hard links no sistema de arquivos utilizado. A operação evita sobrescrita e reverte falhas tratadas, mas não garante atomicidade de dois arquivos sob interrupção do processo. Uma futura etapa pode publicar um manifesto de conclusão, com hashes de ambos os relatórios, para distinguir conjuntos completos de artefatos órfãos.

## Integração contínua — testes em dois sistemas

A configuração [`.github/workflows/testes.yml`](../.github/workflows/testes.yml) foi adicionada para executar a suíte completa de testes automatizados em Python 3.13, com matrizes Linux e Windows, nas alterações de `main` e nos pull requests. A configuração inclui apenas dependências de desenvolvimento e não instala léxicos privados ou usa a partição reservada.

O resultado deve ser consultado em [GitHub Actions](https://github.com/waness4/sentivis-tcc/actions/workflows/testes.yml). **A criação do fluxo não equivale à aprovação dos testes:** verificar os resultados de ambos os sistemas e registrar falhas ou testes ignorados antes de declarar a validação concluída.

## Verificação por GitHub Actions — resultados observados

O fluxo automático apontou inicialmente duas classes de falha:

1. **Linux:** `backend/tests/test_interface_bloco24.py` exigia um comentário CSS removido na organização do repositório. O teste foi corrigido para verificar as regras de estilo relevantes e o utilitário `scripts/aplicar_bloco24.py` passou a detectar sua aplicação por seletor funcional, sem depender do comentário histórico.
2. **Windows:** testes de integridade do arquivo `data/controles/controles_sintaticos_v01.csv` falhavam quando o checkout convertia as quebras de linha. O arquivo está protegido por `.gitattributes` com `-text`, preservando seus bytes originais no checkout. **O hash esperado não foi alterado.**

Na execução [44144938794](https://github.com/waness4/sentivis-tcc/actions/runs/44144938794), as matrizes **Linux e Windows foram concluídas com sucesso** em Python 3.13. Esse resultado valida os testes automatizados daquele commit, não a qualidade científica do método. Uma correção posterior no gerador histórico de CSS exige observar também o resultado das execuções subsequentes.

Não houve alteração dos dados de controle, das métricas científicas, das regras de classificação ou dos bloqueios de avaliação reservada.

## Ambiente de referência e rastreabilidade das dependências

A execução [Execução 44145121330](https://github.com/waness4/sentivis-tcc/actions/runs/44145121330), de **17/11/2026**, apresentou **590 testes aprovados no Linux e 590 no Windows**, sem testes ignorados. Houve um aviso de biblioteca em cada sistema; os resultados de execução devem ser interpretados no contexto das versões efetivamente instaladas.

O arquivo [`backend/constraints-ci.txt`](../backend/constraints-ci.txt) fixa somente quatro dependências diretas observadas naquela execução: FastAPI 0.163.1, Uvicorn 0.54.0, pytest 9.2.0 e HTTPX 0.28.1. O GitHub Actions instala com essa restrição, executa `pip check` e registra a saída de `pip freeze --all` como artefato separado por sistema. Essas restrições não congelam todas as dependências transitivas e **não** incluem o modelo `pt_core_news_sm` utilizado opcionalmente no método V04.

Para reprodução científica definitiva, ainda é necessário congelar e conservar um manifesto integral de ambiente e hashes de recursos autorizados na mesma versão da execução aprovada, respeitando as decisões metodológicas e a custódia dos dados.

**Validação do ambiente de referência:** na [execução 44145626554](https://github.com/waness4/sentivis-tcc/actions/runs/44145626554), os dois jobs (Linux e Windows) terminaram com sucesso, inclusive instalação com restrições, `pip check`, execução dos testes e envio dos artefatos `dependencias-ubuntu-latest` e `dependencias-windows-latest`. Os arquivos registram as dependências instaladas naquela execução, mas não incluem os léxicos originais nem o modelo opcional da V04.

## Revisão humana — proteções adicionais de integridade

Foi identificada a possibilidade de `preparar(..., substituir=True)` utilizar como destino da ficha A ou B o próprio caminho do CSV de origem. O código agora rejeita essa colisão **antes da primeira escrita**. As funções de gravação utilizam modo exclusivo (`x`) quando a substituição não é explicitamente solicitada, reduzindo a janela de sobrescrita concorrente. A validação de ficha também rejeita rótulo preenchido para equivalência marcada como `nao`, evitando anotações contraditórias. Três testes de regressão com dados artificiais documentam essas regras.

Esses ajustes se aplicam apenas ao fluxo de revisão de desenvolvimento. Não habilitam avaliação final, não modificam o protocolo científico e exigem confirmação da suíte automatizada no Linux e Windows.
