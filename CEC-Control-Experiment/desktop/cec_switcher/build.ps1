# Build CEC-Switcher.exe -- a single-file, no-console Windows app from app.py.
# Requires: pip install pyinstaller
param([switch]$Clean)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($Clean) {
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
    Remove-Item -Force *.spec -ErrorAction SilentlyContinue
}

pyinstaller --onefile --noconsole --name CEC-Switcher app.py

Write-Host "Built: $(Join-Path $PSScriptRoot 'dist\CEC-Switcher.exe')"
