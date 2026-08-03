#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
docker buildx build --platform linux/arm64 --load -t phase1-benchmark:arm64 .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
