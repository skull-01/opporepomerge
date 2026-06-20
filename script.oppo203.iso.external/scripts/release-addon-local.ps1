#Requires -Version 5
<#
.SYNOPSIS
  Build + publish the Kodi add-on GitHub release locally (local-first).

.DESCRIPTION
  Local replacement for the cloud "Package Installable ZIP" release job
  (.github/workflows/package.yml). Builds the runtime installable ZIP + .sha256
  via the POSIX packaging helper (scripts/package_release.sh) under WSL, then
  publishes the GitHub release "v<version>" titled "v<version> Final" with those
  assets. gh runs natively on Windows (already authenticated).

  The configurator -- not the add-on -- holds the repo "Latest" badge, so this
  passes --latest=false (a bare add-on ZIP as "Latest" would misdirect Windows
  users). See [[readme-current-status-per-release]] / the handoff release norm.

.PARAMETER NotesFile
  Release-notes markdown. Default: docs/release-history/RELEASE_NOTES_v<version>.md.
  If absent, falls back to --generate-notes.

.PARAMETER Target
  Commit-ish the tag is cut from if it does not already exist. Default: main.

.PARAMETER DryRun
  Build the artifacts and print the gh command; do not create the release.

.EXAMPLE
  powershell -File scripts/release-addon-local.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [string]$NotesFile,
    [string]$Target = 'main',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot

# 1) Add-on version from the single source of truth (resources/lib/kodi/version.py).
$py = if (Test-Path "$RepoRoot\.venv\Scripts\python.exe") { "$RepoRoot\.venv\Scripts\python.exe" } else { "python" }
$Version = (& $py -c "from resources.lib.kodi.version import ADDON_VERSION; print(ADDON_VERSION)").Trim()
if (-not $Version) { throw "Could not read ADDON_VERSION from resources/lib/kodi/version.py" }
Write-Host "Add-on version: $Version"

# 2) Build the runtime installable ZIP + checksum under WSL. We call the Python
#    packager directly (not scripts/package_release.sh) so we build ONLY the
#    runtime ZIP -- package_release.sh also writes a dev-source ZIP that would
#    walk configurator/node_modules + src-tauri/target in a live checkout.
$Dist = Join-Path $RepoRoot 'dist'
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
Get-ChildItem $Dist -Filter '*.zip' -ErrorAction SilentlyContinue | Remove-Item -Force
# Convert D:\path -> /mnt/d/path in PowerShell (a backslash path mangles through wsl.exe).
$drive = $RepoRoot.Substring(0, 1).ToLower()
$WslRoot = "/mnt/$drive" + ($RepoRoot.Substring(2) -replace '\\', '/')
$zipName = "script.oppo203.iso.external-$Version.zip"
$bash = "cd '$WslRoot' && python3 tools/sync_version.py --check --expected-version '$Version' && python3 tools/package_installable_zip.py --root . --output 'dist/$zipName' && cd dist && sha256sum '$zipName' > 'script.oppo203.iso.external-$Version.sha256'"
& wsl.exe -e bash -lc $bash
if ($LASTEXITCODE -ne 0) { throw "runtime ZIP packaging failed (exit $LASTEXITCODE)" }

$Zip = Join-Path $Dist "script.oppo203.iso.external-$Version.zip"
$Sha = Join-Path $Dist "script.oppo203.iso.external-$Version.sha256"
foreach ($f in @($Zip, $Sha)) { if (-not (Test-Path $f)) { throw "Missing expected artifact: $f" } }
Write-Host "Built: $Zip"
Get-Content $Sha

# 3) Compose the gh release command.
if (-not $NotesFile) { $NotesFile = Join-Path $RepoRoot "docs/release-history/RELEASE_NOTES_v$Version.md" }
$ghArgs = @('release', 'create', "v$Version", '--target', $Target, '--title', "v$Version Final", '--latest=false')
if (Test-Path $NotesFile) {
    $ghArgs += @('--notes-file', $NotesFile)
}
else {
    Write-Warning "Notes file not found ($NotesFile); using --generate-notes"
    $ghArgs += '--generate-notes'
}
$ghArgs += @($Zip, $Sha)

# 4) Publish (or print under -DryRun).
if ($DryRun) {
    Write-Host "[dry-run] gh $($ghArgs -join ' ')"
    return
}
& gh @ghArgs
if ($LASTEXITCODE -ne 0) { throw "gh release create failed (exit $LASTEXITCODE)" }
Write-Host "Published add-on release v$Version Final (latest=false; the configurator holds Latest)."
