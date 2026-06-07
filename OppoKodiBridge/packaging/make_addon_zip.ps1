# Build dist/service.oppokodibridge-<version>.zip for Kodi install.
# The zip must contain the add-on inside a top-level folder named exactly the add-on id.
param([string]$Version)
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "service.oppokodibridge"
if (-not (Test-Path $src)) { throw "add-on folder not found: $src" }

if (-not $Version) {
    [xml]$x = Get-Content (Join-Path $src "addon.xml")
    $Version = $x.addon.version
}

$dist = Join-Path $root "dist"
$staging = Join-Path $dist "_staging"
New-Item -ItemType Directory -Force -Path $dist | Out-Null
if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Force -Path $staging | Out-Null

$stagedAddon = Join-Path $staging "service.oppokodibridge"
Copy-Item -Recurse $src $stagedAddon
Get-ChildItem -Recurse -Force -Path $stagedAddon -Include "__pycache__" -Directory |
    Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Force -Path $stagedAddon -Include "*.pyc" -File |
    Remove-Item -Force

$zip = Join-Path $dist "service.oppokodibridge-$Version.zip"
if (Test-Path $zip) { Remove-Item -Force $zip }
Compress-Archive -Path $stagedAddon -DestinationPath $zip
Remove-Item -Recurse -Force $staging
Write-Host "Built $zip"
