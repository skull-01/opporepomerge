#Requires -Version 5
<#
.SYNOPSIS
  Build + publish the configurator GitHub release locally (local-first).

.DESCRIPTION
  Local replacement for the cloud Configurator CI release job
  (.github/workflows/configurator-ci.yml). Builds the Windows MSI + NSIS
  installers natively (npm run dist), collects them with SHA-256 sums, and
  publishes the GitHub release "configurator-v<version>" as Latest (the
  configurator holds the repo Latest badge). gh runs natively on Windows.

  Tauri's installer build needs MSVC + WebView2, so this is Windows-native and
  cannot run under WSL (unlike the add-on packaging in release-addon-local.ps1).

.PARAMETER SkipBuild
  Skip `npm ci` + `npm run dist`; collect + publish whatever installers already
  exist under src-tauri/target/release/bundle. For logic checks / re-publishing.

.PARAMETER DryRun
  Build + collect + checksum, then print the gh command; do not create the release.

.EXAMPLE
  powershell -File scripts/release-configurator-local.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Cfg = Join-Path $RepoRoot 'configurator'
Set-Location $Cfg

# 1) Configurator version (pinned across package.json / tauri.conf.json / Cargo.toml by version.test.ts).
$Version = (Get-Content (Join-Path $Cfg 'package.json') -Raw | ConvertFrom-Json).version
if (-not $Version) { throw "Could not read configurator version from package.json" }
Write-Host "Configurator version: $Version"

# 2) Build the installers natively (Tauri needs MSVC + WebView2 - Windows only).
if (-not $SkipBuild) {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed (exit $LASTEXITCODE)" }
    npm run dist
    if ($LASTEXITCODE -ne 0) { throw "npm run dist failed (exit $LASTEXITCODE)" }
}
else {
    Write-Warning "SkipBuild: collecting existing installers under src-tauri/target/release/bundle"
}

# 3) Collect MSI + NSIS + SHA256SUMS (mirrors the cloud release job's PowerShell).
$Bundle = Join-Path $Cfg 'src-tauri/target/release/bundle'
$Out = Join-Path $env:TEMP "configurator-release-$Version"
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Out | Out-Null
# Filter to the CURRENT version: a local bundle dir accumulates installers from
# prior builds (the cloud runner is always fresh), so collect only *_<version>_*.
$installers = Get-ChildItem -Path (Join-Path $Bundle 'msi'), (Join-Path $Bundle 'nsis') `
    -Recurse -Include *.msi, *-setup.exe -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*_${Version}_*" }
foreach ($i in $installers) { Copy-Item $i.FullName -Destination $Out }
$sumsFile = Join-Path $Out 'SHA256SUMS.txt'
Get-ChildItem $Out -File | ForEach-Object {
    $h = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    "$h  $($_.Name)" | Out-File -Append -Encoding ascii $sumsFile
}
if (Test-Path $sumsFile) { Get-Content $sumsFile }

$files = @(Get-ChildItem "$Out\*" -File | ForEach-Object { $_.FullName })
if (-not $files) {
    if ($DryRun) { Write-Warning "No installers collected (expected with -SkipBuild and no prior build)." }
    else { throw "No installers found under $Bundle - did npm run dist succeed?" }
}

# 4) Publish (configurator holds Latest), or print under -DryRun.
$tag = "configurator-v$Version"
$ghArgs = @('release', 'create', $tag, '--latest', '--title', "Kodi Oppo External Player Configurator $Version", '--generate-notes') + $files
if ($DryRun) {
    Write-Host "[dry-run] gh $($ghArgs -join ' ')"
    return
}
& gh @ghArgs
if ($LASTEXITCODE -ne 0) { throw "gh release create failed (exit $LASTEXITCODE)" }
Write-Host "Published $tag as Latest."
