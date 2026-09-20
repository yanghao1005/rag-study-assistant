Param(
  [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

New-Item -ItemType Directory -Force -Path "build" | Out-Null

if ($Clean) {
  latexmk -C -outdir=build main.tex
  exit 0
}

function Convert-PortadaOficial {
  $odt = Join-Path $PSScriptRoot "front\portada-oficial.odt"
  $pdf = Join-Path $PSScriptRoot "front\portada-oficial.pdf"
  if (-not (Test-Path $odt)) {
    throw "Falta la plantilla de portada: $odt"
  }

  $soffice = "C:\Program Files\LibreOffice\program\soffice.exe"
  if (-not (Test-Path $soffice)) {
    if (Test-Path $pdf) {
      Write-Host "LibreOffice no trobat; s'usa la portada PDF existent."
      return
    }
    throw "Cal LibreOffice per convertir la portada ODT."
  }

  $profile = Join-Path $PSScriptRoot "build\lo-profile"
  New-Item -ItemType Directory -Force -Path $profile | Out-Null
  $fileUri = "file:///" + ($profile -replace "\\", "/")
  $outDir = Join-Path $PSScriptRoot "front"

  & $soffice --headless --norestore --nolockcheck --nodefault `
    "-env:UserInstallation=$fileUri" `
    --convert-to "pdf:writer_pdf_Export" --outdir $outDir $odt | Out-Null

  if (-not (Test-Path $pdf)) {
    throw "LibreOffice no ha generat front\portada-oficial.pdf"
  }
}

Convert-PortadaOficial

# MiKTeX: instal·la paquets que faltin sense preguntar en aquesta sessió.
$env:MIKTEX_AUTOINSTALL = "1"

& latexmk -pdf -outdir=build main.tex
if ($LASTEXITCODE -ne 0) {
  throw "latexmk failed with exit code $LASTEXITCODE"
}

$src = Join-Path $PSScriptRoot "build\main.pdf"
$dest = Join-Path $PSScriptRoot "build\memoria.pdf"
try {
  Copy-Item -Force $src $dest
  Write-Host ""
  Write-Host "PDF generat: $dest"
} catch {
  Write-Host ""
  Write-Host "memoria.pdf esta obert. El PDF nou es: $src"
}
