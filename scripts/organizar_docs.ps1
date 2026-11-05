# Pré-visualização por padrão. Execute com -Aplicar para efetivar as movimentações.
param([switch]$Aplicar)
$Raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Categorias = @(
    @{ Filtro='INSTRUCOES_BLOCO*.md'; Pasta='docs/desenvolvimento' },
    @{ Filtro='INSTRUCOES_CORRECAO*.md'; Pasta='docs/desenvolvimento' },
    @{ Filtro='PROTOCOLO_BLOCO*.md'; Pasta='docs/metodologia' },
    @{ Filtro='POLITICA_METODOLOGICA_BLOCO*.md'; Pasta='docs/metodologia' },
    @{ Filtro='PROTOCOLO_PILOTO_V*.md'; Pasta='docs/metodologia' }
)
foreach ($Grupo in $Categorias) {
    $Originais = Get-ChildItem -LiteralPath $Raiz -File -Filter $Grupo.Filtro
    foreach ($Arquivo in $Originais) {
        $DestinoDir = Join-Path $Raiz $Grupo.Pasta
        $Destino = Join-Path $DestinoDir $Arquivo.Name
        if (Test-Path -LiteralPath $Destino) {
            Write-Warning "Já existe no destino: $Destino. Arquivo NÃO movido."
            continue
        }
        if ($Aplicar) {
            New-Item -ItemType Directory -Force -Path $DestinoDir | Out-Null
            Move-Item -LiteralPath $Arquivo.FullName -Destination $Destino
            Write-Output "Movido: $($Arquivo.Name) -> $($Grupo.Pasta)"
        } else {
            Write-Output "PREVIA: $($Arquivo.Name) -> $($Grupo.Pasta)"
        }
    }
}
if (-not $Aplicar) { Write-Output 'Nenhum arquivo alterado. Use -Aplicar para executar.' }
