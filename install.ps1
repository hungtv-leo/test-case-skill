#Requires -Version 5.1
<#
.SYNOPSIS
  Install self-test-cases skill into the current project's .cursor/skills/ folder.
  Copies ONLY runtime files listed in install.manifest (no scripts/tests, no .git).

.EXAMPLE
  # From target project root (download from GitHub):
  irm https://raw.githubusercontent.com/hungtv-leo/test-case-skill/main/install.ps1 | iex

.EXAMPLE
  # From a local clone of this skill repo:
  .\install.ps1 -ProjectRoot C:\path\to\your-app

.EXAMPLE
  # Install into current directory using local skill source:
  .\install.ps1 -Source .
#>
param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$Source = "",
    [string]$Repo = "hungtv-leo/test-case-skill",
    [string]$Branch = "main",
    [string]$SkillName = "self-test-cases"
)

$ErrorActionPreference = "Stop"

function Read-Manifest([string]$ManifestPath) {
    Get-Content -LiteralPath $ManifestPath -Encoding UTF8 |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith("#") }
}

function Copy-RuntimeFiles([string]$FromRoot, [string]$ToRoot, [string[]]$RelPaths) {
    New-Item -ItemType Directory -Force -Path $ToRoot | Out-Null
    foreach ($rel in $RelPaths) {
        $src = Join-Path $FromRoot ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path -LiteralPath $src)) {
            Write-Warning "Skip missing file in source: $rel"
            continue
        }
        $dst = Join-Path $ToRoot ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)
        $dstDir = Split-Path -Parent $dst
        if ($dstDir) {
            New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
        }
        Copy-Item -LiteralPath $src -Destination $dst -Force
    }
}

$dest = Join-Path $ProjectRoot (Join-Path ".cursor\skills" $SkillName)
$tempRoot = $null

try {
    if ($Source) {
        $from = (Resolve-Path -LiteralPath $Source).Path
        $manifestPath = Join-Path $from "install.manifest"
        if (-not (Test-Path -LiteralPath $manifestPath)) {
            throw "install.manifest not found in Source: $from"
        }
        Write-Host "Installing from local source: $from"
    }
    else {
        $zipUrl = "https://github.com/$Repo/archive/refs/heads/$Branch.zip"
        $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("self-test-cases-install-" + [guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
        $zipPath = Join-Path $tempRoot "skill.zip"
        Write-Host "Downloading $zipUrl ..."
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        Expand-Archive -LiteralPath $zipPath -DestinationPath $tempRoot -Force
        $extracted = Get-ChildItem -LiteralPath $tempRoot -Directory | Select-Object -First 1
        if (-not $extracted) {
            throw "Could not find extracted folder from zip."
        }
        $from = $extracted.FullName
        $manifestPath = Join-Path $from "install.manifest"
        if (-not (Test-Path -LiteralPath $manifestPath)) {
            throw "install.manifest missing in downloaded archive. Is Branch='$Branch' correct?"
        }
        Write-Host "Installing from GitHub: $Repo@$Branch"
    }

    $files = @(Read-Manifest $manifestPath)
    if ($files.Count -eq 0) {
        throw "install.manifest is empty."
    }

    if (Test-Path -LiteralPath $dest) {
        Write-Host "Replacing existing install: $dest"
        Remove-Item -LiteralPath $dest -Recurse -Force
    }

    Copy-RuntimeFiles -FromRoot $from -ToRoot $dest -RelPaths $files

    # Ensure sandbox folder exists for generated artifacts
    $workdir = Join-Path $dest "workdir"
    New-Item -ItemType Directory -Force -Path $workdir | Out-Null

    $skillOk = Test-Path -LiteralPath (Join-Path $dest "SKILL.md")
    $testsPresent = Test-Path -LiteralPath (Join-Path $dest "scripts\tests")
    if (-not $skillOk) {
        throw "Install failed: SKILL.md missing at $dest"
    }
    if ($testsPresent) {
        throw "Install polluted: scripts/tests should not be copied."
    }

    Write-Host ""
    Write-Host "[OK] Installed runtime skill -> $dest"
    Write-Host "     Files: $($files.Count) (maintainer tests NOT included)"
    Write-Host ""
    Write-Host "Next:"
    Write-Host "  pip install --user -r `"$dest\scripts\requirements.txt`""
    Write-Host "  Restart Cursor, then run: /self-test-cases"
}
finally {
    if ($tempRoot -and (Test-Path -LiteralPath $tempRoot)) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
