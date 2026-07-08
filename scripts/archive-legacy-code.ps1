$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$legacyRoot = Join-Path $repoRoot "legacy_code"

if (-not (Test-Path $legacyRoot)) {
    New-Item -ItemType Directory -Path $legacyRoot | Out-Null
}

$targets = @(
    "backend",
    "backend_v2",
    "backend_v3",
    "backend_v4",
    "frontend"
)

foreach ($name in $targets) {
    $source = Join-Path $repoRoot $name
    $destination = Join-Path $legacyRoot $name

    if (-not (Test-Path $source)) {
        Write-Host "[skip] Missing source: $name"
        continue
    }

    if (Test-Path $destination) {
        Write-Host "[skip] Destination already exists: legacy_code/$name"
        continue
    }

    Move-Item -Path $source -Destination $destination
    Write-Host "[ok] Moved $name -> legacy_code/$name"
}

Write-Host ""
Write-Host "Archive routine completed."
Write-Host "Review changes with: git status"

