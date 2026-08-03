#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root

$Image = if ($env:PHASE1_IMAGE) { $env:PHASE1_IMAGE } else { 'phase1-benchmark:amd64' }
$PlatformArgs = @()
if ($Image -match 'arm64') {
    $PlatformArgs = @('--platform', 'linux/arm64')
}

docker run --rm @PlatformArgs $Image verify
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
