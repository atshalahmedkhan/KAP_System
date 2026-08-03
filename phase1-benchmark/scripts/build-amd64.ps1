#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
docker buildx build --platform linux/amd64 --load -t phase1-benchmark:amd64 .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
