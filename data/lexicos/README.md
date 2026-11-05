# Léxicos — arquivos ainda não incorporados

Esta pasta está vazia intencionalmente: é necessário confirmar a origem e os termos de redistribuição de cada base antes de incluir dados de terceiros.

No protótipo, importar cópias **normalizadas e auditadas** como `oplexicon_3.csv` e `sentilex_pt02.csv`, no formato CSV UTF-8 com cabeçalho `termo;polaridade`. Esse formato é provisório, pois o SentiLex exige preservar e tratar os campos de categoria e alvo de polaridade e o OpLexicon também contém outras informações. O importador científico final será substituído por importadores específicos que mantenham os metadados.

Fontes para revisão:
- https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/oplexicon/
- https://search.r-project.org/CRAN/refmans/lexiconPT/html/00Index.html
- https://rdrr.io/github/sillasgonzaga/lexiconPT/src/data-raw/setup.R

NÃO copiar pontuações fictícias dos testes para esta pasta. O teste automatizado usa uma fixture artificial isolada.
