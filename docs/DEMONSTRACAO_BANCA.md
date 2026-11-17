# Demonstração do SentiVis para a banca — roteiro operacional

**Estado:** material de apoio para apresentação do artefato técnico. Não constitui aprovação científica, protocolo de avaliação final, validação linguística ou registro de execução sobre os dados reservados.

## Objetivo e limite

Mostrar que o software permite localizar registros lexicais, apresentar informações de polaridade/cobertura, distinguir pontuação de abstenção e comparar duas frases de maneira **descritiva**, sem afirmar viés de gênero. Os **27 pares reservados (54 frases)** não entram na demonstração, em testes nem na preparação do ambiente.

## 1. Conferência prévia, antes da sessão

Usar um ambiente local Windows/PowerShell com Python 3.13, Git, acesso à interface e os arquivos lexicais de terceiros **obtidos legitimamente**. Os relatórios locais não acompanham o repositório público. O procedimento completo de instalação está no [guia de execução](GUIA_EXECUCAO.md).

```powershell
git clone https://github.com/waness4/sentivis-tcc.git
cd sentivis-tcc
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt -c backend/constraints-ci.txt
python -m pytest backend/tests -q -rs
```

Para mostrar os métodos contextuais V04, a instalação opcional exige spaCy e `pt_core_news_sm` (ver guia); não prometer sua operação se não estiverem instalados. Para análise real de frases, conferir a existência dos arquivos originais em `data/lexicos/originais/` e de `data/lexicos/relatorio_curadoria.json` **sem exibir conteúdos privados**. Caso os originais estejam disponíveis, gerar/verificar os relatórios apenas conforme o guia e respeitando suas condições de uso. Não inserir conteúdos reservados como exemplos.

Antes de iniciar a apresentação:

- Executar `python -m uvicorn backend.ui_server:app --reload` e abrir `http://127.0.0.1:8000/`.
- Acessar `http://127.0.0.1:8000/api/ui/info` para confirmar o estado da interface; uma tela carregada **não comprova** que os léxicos estejam prontos.
- Conferir previamente as frases públicas abaixo no ambiente efetivo. Resultados registrados em capturas anteriores não garantem saídas idênticas caso mudem os arquivos, configurações ou versões.
- Deixar uma aba com o [README](../README.md) e outra com o [histórico de testes](https://github.com/waness4/sentivis-tcc/actions/workflows/testes.yml). Não abrir o diretório `data/piloto/restrito/`, nem navegar em caminhos da partição final.
- Desativar notificações pessoais e revisar a tela compartilhada para evitar exposição de arquivos, identificadores, credenciais e conteúdo de anotações.

## 2. Sequência sugerida para uma demonstração de 7 a 9 minutos

| Duração aproximada | Etapa | Demonstração e mensagem |
| --- | --- | --- |
| 0:00–1:00 | Problema e contribuição | Mostrar a tela inicial. Explicar que a auditoria e a curadoria localizam *candidatos à revisão*, não erros confirmados |
| 1:00–2:00 | Arquitetura | Mostrar o diagrama público do [README](../README.md); relacionar arquivos lexicais, auditoria, curadoria e interface |
| 2:00–3:30 | Consulta exploratória | Selecionar **OpLexicon 3.0** e método **Aditivo V01**; inserir `O atendimento foi excelente.` e explicar a diferença entre pontuação, classe e cobertura |
| 3:30–4:30 | Limitação/abstenção | Usar o exemplo público da interface **“Com negação”**; discutir a possibilidade de abstenção sem tratar ausência de pontuação como neutralidade. Descrever o resultado *efetivamente exibido* |
| 4:30–6:00 | Comparação descritiva | Na aba de comparação, inserir `A aluna é dedicada.` e `O aluno é dedicado.`. Explicar que `delta = pontuação feminina − pontuação masculina` apenas quando ambas forem pontuadas. Delta zero **não prova ausência de viés** |
| 6:00–7:15 | Evidência de engenharia | Mostrar a execução automatizada de testes e os documentos de rastreabilidade dos relatórios; a suíte testa código, não acurácia linguística |
| 7:15–9:00 | Limites e conclusão | Informar que V03 existe no backend, mas não é selecionável na interface; V04 é opcional e depende do modelo. Explicar que a avaliação de 27 pares permanece não executada e exige aprovação acadêmica |

**Registros visuais de referência:** [capturas da interface](capturas/README.md). As capturas públicas documentam OpLexicon com pontuação exploratória +1 e cobertura superficial de 25% para `O atendimento foi excelente.`, e uma comparação demonstrativa com delta zero entre as duas frases da aluna e do aluno. São **observações da execução registrada**, não garantias para qualquer ambiente nem resultados científicos de viés.

## 3. Contingência

**Se não houver originais lexicais ou se o serviço retornar HTTP 503:** mostrar a interface, o endpoint informativo, as capturas públicas e os relatórios de conferência numérica. Explicar que o erro decorre da indisponibilidade dos recursos de terceiros/curadoria, não substituir dados por arquivos improvisados e não prometer uma execução real.

**Se a versão contextual V04 estiver indisponível:** permanecer no fluxo V01 com OpLexicon, demonstrar a interface e explicar que o modelo morfossintático é opcional, externo e sujeito a configuração. Não afirmar que V03 está disponível no menu.

**Se a saída de uma frase diferir da captura:** apresentar o status real, conferir configuração e proveniência após a sessão, sem ajustar exemplos para obter uma pontuação desejada e sem alterar os originais.

**Se os testes não puderem ser executados ao vivo:** apresentar a [execução verificada 44150590578](https://github.com/waness4/sentivis-tcc/actions/runs/44150590578) — commit `606abd7687f02756b88684c7211a12e7a9dbe9d8`, **599 testes aprovados em cada sistema** (Linux e Windows), com um aviso de biblioteca em cada um. Trata-se de evidência técnica histórica daquele commit.

## 4. Perguntas prováveis e respostas sustentáveis

**Os 9.494 registros sinalizados são erros?** Não. São candidatos à revisão conforme critérios declarados; várias sinalizações podem ocorrer em um mesmo registro.

**O SentiVis detectou viés de gênero?** Não há evidência da avaliação final reservada. As diferenças exibidas na interface são comparações exploratórias, insuficientes para uma conclusão de viés.

**Por que há abstenção?** Para representar explicitamente situações sem evidência lexical ou com limitações do método, evitando converter casos incertos em classe neutra.

**Os 599 testes demonstram acurácia?** Não. Demonstram que casos de teste automatizados do software passaram no ambiente da execução citada.

**O que permanece para encerrar cientificamente a etapa reservada?** Decisões acadêmicas G01–G08, protocolo congelado, executor e custódia autorizados; nenhuma aprovação pode ser substituída por uma opção de código ou por uma demonstração pública.

## 5. Checklist de entrega à banca

- Conferir que o artigo final e o roteiro de apresentação usam o mesmo título, autoria, escopo e números documentados.
- Confirmar com o curso o formato exigido para apresentação e os artefatos a entregar; este roteiro **não presume** que GitHub ou vídeo sejam obrigatórios.
- Preservar versões e hashes dos arquivos técnicos publicados. Não adicionar os relatórios privados nem os originais dos léxicos sem autorização.
- Revisar `git status --short` e `git diff --cached --name-only` antes de publicar qualquer mudança.
- Confirmar previamente a disponibilidade da rede e preparar capturas públicas como contingência.

**Referências técnicas:** [guia de execução](GUIA_EXECUCAO.md), [roteiro de leitura para a banca](ROTEIRO_BANCA.md), [proteção de dados](SEGURANCA_E_DADOS.md), [conferência dos relatórios](resultados/CONFERENCIA_RELATORIOS_AUDITORIA_CURADORIA.md), [pendências metodológicas](metodologia/PARECER_PENDENCIAS_BLOCO35.md).
