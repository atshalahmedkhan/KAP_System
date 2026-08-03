#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
docker run --rm --platform linux/arm64 phase1-benchmark:arm64 test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
