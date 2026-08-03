#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
docker run --rm phase1-benchmark:amd64 test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
