# SentiVis — Bloco 8: amostra candidata para anotação humana

Versão: v0.1 (provisória). Este pacote contém **exemplos sintéticos** construídos para preparar um piloto; não contém avaliação humana, resultados de um classificador ou evidência sobre viés.

## Conteúdo

- `data/piloto/pares_candidatos_v01.csv`: 36 pares no mesmo esquema de 14 colunas do Bloco 7. Todos os campos de revisão e alvos N0/N1 estão intencionalmente vazios.
- `data/piloto/ficha_revisor_A.csv` e `ficha_revisor_B.csv`: formulários separados para revisão independente, sem rótulos planejados.
- `data/piloto/plano_amostragem_pesquisador_v01.csv`: polaridade **pretendida na construção**, não é rótulo verdadeiro; não compartilhar com revisores, não usar para avaliar o classificador.
- `PROTOCOLO_PILOTO_V01.md`: regras operacionais de revisão e prevenção de vazamento.
- `SHA256SUMS.txt`: checksums dos arquivos preparados.

## Instalação sem sobrescrever os arquivos existentes

Com o ZIP em `C:\TCC\sentivis_bloco8_piloto_humano.zip`, e o terminal em `C:\TCC\sentivis_bloco1`:

```powershell
Expand-Archive -Path "C:\TCC\sentivis_bloco8_piloto_humano.zip" -DestinationPath "C:\TCC\sentivis_bloco1" -Force
python -m backend.pares_piloto --entrada .\data\piloto\pares_candidatos_v01.csv --saida .\data\piloto\relatorio_pares_candidatos_v01.json
python -m pytest .\backend\tests -q
```

Resultado pretendido do verificador: 36 pares, 0 erros estruturais, 36 pendentes de revisão. **Os testes do Bloco 7 podem conter verificações adicionais; se houver divergência, não use o arquivo sem investigar.** A suíte existente tem 114 testes no computador da usuária; este pacote não adiciona código nem testes.

## Cuidados

- Não modificar a amostra após inspecionar resultados do classificador; para mudanças, gerar uma nova versão e novo hash.
- Esta alocação usa 3 das 12 famílias para desenvolvimento (9 pares) e 9 para avaliação **reservada** (27 pares). As famílias são exclusivas por partição; a meta 25%/75% refere-se às famílias, não prova suficiência estatística.
- Não executar testes do classificador sobre a partição `avaliacao` nesta etapa.
- O piloto de desenvolvimento contém apenas 9 pares, insuficientes para estimar métricas com precisão ou ajustar modelos complexos.
- Depois de revisão independente, resolver discordâncias conforme o protocolo. Não atribuir os rótulos planejados aos campos de revisão.
