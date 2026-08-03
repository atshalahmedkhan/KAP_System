#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root

$Lock = Join-Path $Root 'benchmark\source.lock'
if (-not (Test-Path -LiteralPath $Lock)) {
    throw "Missing source.lock at $Lock"
}

$Dest = Join-Path $Root 'benchmark\fetched-src'
if (Test-Path -LiteralPath $Dest) {
    Remove-Item -LiteralPath $Dest -Recurse -Force
}

Write-Host "Fetching zstd v1.5.7 into benchmark/fetched-src (temporary; image build also fetches)..."
git clone --branch v1.5.7 --depth 1 https://github.com/facebook/zstd.git $Dest
Push-Location $Dest
try {
    $sha = (git rev-parse HEAD).Trim()
    $expected = 'f8745da6ff1ad1e7bab384bd1f9d742439278e99'
    if ($sha -ne $expected) {
        throw "Commit mismatch: got $sha expected $expected"
    }
    Write-Host "Fetched commit: $sha"
}
finally {
    Pop-Location
}
