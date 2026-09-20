Param(
  [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

New-Item -ItemType Directory -Force -Path "..\build" | Out-Null

if ($Clean) {
  latexmk -C -xelatex resum.tex
  exit 0
}

$env:MIKTEX_AUTOINSTALL = "1"

& latexmk -xelatex resum.tex
if ($LASTEXITCODE -ne 0) {
  throw "latexmk failed with exit code $LASTEXITCODE"
}

$dest = Join-Path (Resolve-Path "..\build") "Resum-TFG-TFM-Hao-Yang.pdf"
$src = Join-Path (Resolve-Path "..\build") "resum.pdf"
try {
  Copy-Item -Force $src $dest
} catch {
  $alt = Join-Path (Resolve-Path "..\build") "Resum-TFG-TFM-Hao-Yang-nou.pdf"
  Copy-Item -Force $src $alt
  Write-Host "El PDF de diposit estava obert; copia a: $alt"
  exit 0
}
Write-Host ""
Write-Host "PDF generat: $dest"
