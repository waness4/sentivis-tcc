# Roteiro de leitura e demonstração — SentiVis

Este documento orienta a consulta ao repositório como **artefato técnico de TCC em desenvolvimento**. Não substitui o manuscrito acadêmico ou a deliberação da banca.

## 1. Objetivo e delimitação

O SentiVis reúne rotinas de auditoria e curadoria de léxicos de sentimentos em português (OpLexicon 3.0 e SentiLex-PT02), além de uma interface de consulta e comparação **exploratórias**. Seu propósito documentado é tornar visíveis cobertura, divergências, abstenções e limitações de métodos lexicais.

**Não são resultados alcançados:** demonstração de viés de gênero, mitigação de viés, acurácia linguística validada ou conclusão da avaliação final reservada.

## 2. Onde verificar cada componente

| Componente | Evidência no repositório |
| :--- | :--- |
| Interface | [frontend/](../frontend/) e [capturas reais](capturas/README.md) |
| API web | [backend/ui_server.py](../backend/ui_server.py) |
| Auditoria dos léxicos | [backend/lexicon_audit.py](../backend/lexicon_audit.py) |
| Curadoria lexical | [backend/lexicon_triage.py](../backend/lexicon_triage.py) |
| Métodos exploratórios | [backend/baseline_experimental.py](../backend/baseline_experimental.py), [V03](../backend/baseline_contextual_v03.py) e [V04](../backend/baseline_contextual_v04.py) |
| Testes automatizados | [backend/tests/](../backend/tests/) |
| Protocolos e decisões pendentes | [metodologia/](metodologia/) e [parecer de pendências](metodologia/PARECER_PENDENCIAS_BLOCO35.md) |
| Execução local | [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md) |
| Proteção de dados | [SEGURANCA_E_DADOS.md](SEGURANCA_E_DADOS.md) |

## 3. Demonstração reprodutível

1. Seguir o [guia de execução](GUIA_EXECUCAO.md), instalar as dependências e executar `python -m pytest backend/tests -q -rs`.
2. Iniciar `python -m uvicorn backend.ui_server:app --reload` e abrir `http://127.0.0.1:8000/`.
3. Mostrar a seleção de léxico, a análise de frase e a comparação descritiva com **exemplos públicos**, nunca com a partição reservada.
4. Explicar que o acesso aos resultados de consulta exige os léxicos originais obtidos separadamente e a curadoria com integridade verificada.

Na [Execução 44146555269](https://github.com/waness4/sentivis-tcc/actions/runs/44146555269), em **17/11/2026**, houve **596 testes aprovados no Linux e 596 no Windows**, com Python 3.13 e um aviso de biblioteca por ambiente. Isso demonstra verificação técnica naquele commit, não validação científica. A reprodução de dependências está documentada no [guia de execução](GUIA_EXECUCAO.md).

## 4. Como interpretar as evidências

- **Auditoria/curadoria:** registros sinalizados são candidatos a revisão, não erros automaticamente confirmados.
- **Pontuação e cobertura:** são medidas exploratórias do método; cobertura não é precisão nem confiança estatística.
- **Comparação:** diferença zero não comprova ausência de viés; diferença diferente de zero não comprova viés.
- **Abstenção:** deve permanecer distinta de pontuação zero e de neutralidade.
- **Avaliação final:** os 27 pares reservados (54 frases) não foram executados; exigem aprovação acadêmica, protocolo definido e controles de custódia.

## 5. Situação documental

O histórico de desenvolvimento está preservado em [instrucoes/](instrucoes/) e [desenvolvimento/](desenvolvimento/). Esses documentos registram etapas passadas e **não são instruções vigentes** para reproduzir o sistema. A pasta [artigo/versoes_anteriores/](artigo/versoes_anteriores/) contém manuscritos históricos e não deve ser interpretada como entrega final aprovada.

A versão do manuscrito acadêmico, a adequação às normas institucionais e as decisões metodológicas ainda precisam ser confirmadas pelos responsáveis acadêmicos.
