# Conferência independente das tabelas de auditoria e curadoria — 17/11/2026

**Objeto da conferência:** cruzamento das contagens publicadas no artigo científico de revisão com dois arquivos JSON locais preservados na biblioteca de trabalho: `relatorio_auditoria.json` e `relatorio_curadoria.json`, ambos datados de 05/11/2026. Esses relatórios **não são redistribuídos pelo repositório**.

## Identificação dos arquivos conferidos

| Relatório | SHA-256 do arquivo JSON examinado |
| --- | --- |
| `relatorio_auditoria.json` | `95acd8e4486a636e82f13f471b997554998618b43c7d7be01c8d1eb67f41c133` |
| `relatorio_curadoria.json` | `486cc007619df76944d92f04dfbff90d8aa15d2030eb77ba2a89a29bf2f7f131` |

Os três hashes SHA-256 das **fontes lexicais**, registrados independentemente nos dois relatórios, são idênticos entre eles:

| Fonte | SHA-256 declarado nos dois relatórios |
| --- | --- |
| OpLexicon 3.0 (`lexico_v3.0.txt`) | `bbc69030343384b3abf3aae0707920fc556af0f6c84f6ed27dfbc66668049b08` |
| SentiLex-PT02 (`SentiLex-lem-PT02.txt`) | `6aa86fd1598336ed2ab9a0d34f2d6b51e0537d0a892e630ad43f289acdfd29a5` |
| SentiLex-PT02 (`SentiLex-flex-PT02.txt`) | `88ab7389bfe6f4a2b489a4a53c42306691796bc2fef9d4c2a26790dd927ba85c` |

**Escopo da evidência:** verificar a igualdade entre valores declarados nos dois relatórios não prova que os bytes das três fontes lexicais ainda estejam disponíveis ou que uma nova execução produza resultados idênticos. A correspondência do MD5 da distribuição compactada SentiLex com o valor reportado pela B2SHARE está **declarada** no arquivo de auditoria; não foi reobtida aqui a partir da fonte remota.

## Reconciliação das tabelas do artigo

| Indicador | Valor no JSON |
| --- | ---: |
| OpLexicon: registros / não interpretáveis | 32.191 / 0 |
| SentiLex lemas: registros / não interpretáveis | 7.014 / 0 |
| SentiLex flexões: registros / não interpretáveis | 82.347 / 0 |
| Total de registros interpretados | 121.552 |
| Registros sinalizados / sem sinalização | 9.494 / 112.058 |
| Sinalizados: OpLexicon / lemas / flexões | 34 / 4 / 9.456 |
| Grupos conflitantes por termo, categoria e alvo | 2.003 |
| Grupos de forma/categoria com lemas distintos | 2.234 |

Os motivos de sinalização foram `atributo_sem_chave=4568`, `mesma_forma_categorias_e_lemas_diferentes=4529`, `polaridade_divergente_mesmo_alvo=3949` e `polaridade_fora_do_padrao=13`. Somam **13.059 ocorrências de motivo**, não 13.059 registros distintos, pois os motivos podem coexistir.

Verificações aritméticas: `32191 + 7014 + 82347 = 121552`; `9494 + 112058 = 121552`; `34 + 4 + 9456 = 9494`; `4 + 9 = 13`.

Os indicadores adicionais citados no corpo do artigo também coincidem com os campos de auditoria: OpLexicon com 32.112 formas normalizadas, 443 entradas multi-palavras e 15 chaves divergentes; SentiLex lemas com 7.010 formas e 757 multi-palavras; SentiLex flexões com 79.189 formas, 34.918 multi-palavras, 2.354 chaves divergentes, 4.568 registros com atributos sem chave e 9 registros com polaridade fora do padrão.

**Resultado:** não foi identificada divergência entre as contagens do artigo e esses dois relatórios JSON. Trata-se de conferência documental e aritmética, **não de nova auditoria dos léxicos originais**, validação linguística dos registros, avaliação de vieses ou reexecução experimental. Para reprodução independente, os originais licenciados devem ser obtidos de fontes autorizadas e conferidos com os hashes acima, utilizando versão de código e ambiente documentados.

Os 27 pares reservados e as anotações humanas privadas não foram consultados nesta conferência.

## Exemplos documentados e interpretação controlada

A versão de revisão do artigo científico passou a incluir três exemplos retirados dos campos de exemplos dos relatórios originais, **sem consultar ou publicar os arquivos lexicais completos**:

| Origem e referência | Exemplo confirmado | Motivo de sinalização | Limite de interpretação |
| --- | --- | --- | --- |
| Curadoria OpLexicon, chave `fácil`, categoria `adj`, alvo `GLOBAL` | Polaridades `0` e `1` | Valores divergentes para a mesma chave normalizada | Não comprova erro lexical nem explica o contexto de cada valor |
| Auditoria SentiLex lematizado, linha `4320` | `intrépido`, `POL:N0=7` | Polaridade fora do conjunto `{-1,0,1}` | Exige revisão da fonte; não corrigir automaticamente o valor |
| Auditoria SentiLex flexionado, linha `1107` | `acha piada a`, `P2s\|P4s\|P3s\|Y2s` | Atributo sem chave explícita para o esquema de leitura | Não determina erro linguístico; pode refletir convenção do recurso |

Esses exemplos sustentam **somente** a descrição dos comportamentos de auditoria e triagem, não uma conclusão sobre qualidade comparativa dos léxicos ou viés de gênero. Os relatórios locais originais permanecem fora do repositório; os pares reservados não foram consultados.
