<#
.SYNOPSIS
    ny_forgreining.ps1 - Behandler git worktrees og forgreininger for Kunstpixel-agenter.

.EXAMPLE
    .\scripts\ny_forgreining.ps1 -Navn "feat-kurator-host"
    .\scripts\ny_forgreining.ps1 -Flett "feat-kurator-host"
    .\scripts\ny_forgreining.ps1 -Liste
#>

param(
    [string]$Navn = "",
    [string]$Flett = "",
    [string]$Fjern = "",
    [switch]$Liste
)

$ErrorActionPreference = "Stop"
$projectRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $projectRoot

if ($Liste) {
    Write-Host "=== Aktive forgreininger (worktrees) i Kunstpixel ===" -ForegroundColor Cyan
    git worktree list
    exit 0
}

# 1. Opprett ny forgreining
if ($Navn) {
    $worktreePath = "$projectRoot\.worktrees\$Navn"
    if (Test-Path $worktreePath) {
        Write-Host "Forgreining finnes allerede på: $worktreePath" -ForegroundColor Yellow
        exit 0
    }

    Write-Host "Oppretter isolert forgreining for agent: $Navn" -ForegroundColor Green
    git worktree add $worktreePath -b $Navn
    Write-Host "Ferdig! Agenten kan nå operere risikofritt i: $worktreePath" -ForegroundColor Green
    exit 0
}

# 2. Flett forgreining tilbake til hovedgrenen
if ($Flett) {
    $worktreePath = "$projectRoot\.worktrees\$Flett"
    if (-not (Test-Path $worktreePath)) {
        Write-Error "Fant ikke forgreiningen: $worktreePath"
    }

    Write-Host "Kjører forhåndsvalidering inne i forgreiningen: $Flett..." -ForegroundColor Cyan
    Set-Location $worktreePath

    # Sjekk statusporten
    py -3.13 scripts/db_status_gate.py --uten-pytest
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Fletting avbrutt! db_status_gate feilet i forgreiningen."
    }

    Write-Host "Statusport bestått! Fletter tilbake til hovedgren..." -ForegroundColor Green
    Set-Location $projectRoot
    git merge $Flett --no-ff -m "Flettet agent-forgreining: $Flett (Statusport validert)"

    Write-Host "Fletting fullført med 0 feil!" -ForegroundColor Green
    exit 0
}

# 3. Fjern forgreining
if ($Fjern) {
    $worktreePath = "$projectRoot\.worktrees\$Fjern"
    Write-Host "Fjerner forgreining: $worktreePath" -ForegroundColor Yellow
    git worktree remove $worktreePath --force
    git branch -d $Fjern
    Write-Host "Ryddet opp forgreining $Fjern." -ForegroundColor Green
    exit 0
}

Write-Host "Bruk: .\scripts\ny_forgreining.ps1 -Navn <navn> | -Flett <navn> | -Liste" -ForegroundColor Yellow
