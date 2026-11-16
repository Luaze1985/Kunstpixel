<#
Start Kunstpixel-demoen: sjekker miljø og database, og åpner Datafinner i nettleseren.

Bruk (fra hvor som helst):
    powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1        # KI på når .env eller Claude er tilgjengelig
    powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1 -UtenKI # bare database og rapporter
    powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1 -Bakgrunn # autostart: ingen nettleser, logg til .scratch

Skriptet leser bare. Det skriver aldri til 05_data/museum.db og installerer ingenting.
Kjører Datafinner fra denne mappen allerede, åpnes bare nettleseren.
Stopp demoen med Ctrl+C (eller avslutt python-prosessen når den kjører i bakgrunnen).
#>
param([switch]$KI, [switch]$UtenKI, [switch]$Bakgrunn)

if ($Bakgrunn) {
    $env:KUNSTPIXEL_DEMO_IKKE_NETTLESER = '1'
    $loggmappe = Join-Path (Split-Path -Parent $PSScriptRoot) '.scratch'
    New-Item -ItemType Directory -Force $loggmappe | Out-Null
    Start-Transcript -Path (Join-Path $loggmappe 'datafinner_bakgrunn.log') -Force | Out-Null
}

# Ikke 'Stop': i PowerShell 5.1 blir stderr fra py til feil som ville skjult STOPP-meldingene. Vi sjekker $LASTEXITCODE selv.
$ErrorActionPreference = 'Continue'
$Port = 8010
$ForventetMcp = '1.29.1'

function Stopp([string]$melding, [string]$rad = '') {
    Write-Host ""
    Write-Host "STOPP: $melding" -ForegroundColor Red
    if ($rad) { Write-Host "Gjør dette: $rad" -ForegroundColor Yellow }
    exit 1
}
function Ok([string]$melding) { Write-Host "[OK] $melding" -ForegroundColor Green }
if ($KI -and $UtenKI) { Stopp "Velg enten -KI eller -UtenKI." }

# 0. Kjør fra repo-roten, uansett hvor mappen ligger (koden importerer src.kunstpixel...).
$Rot = Split-Path -Parent $PSScriptRoot
Set-Location $Rot
Write-Host "Kunstpixel-demo fra $Rot"
$versjon = (git describe --tags --always 2>$null)
if ($versjon) { Write-Host "Versjon: $versjon" }

# 1. Python 3.13
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Stopp "Fant ikke Python-starteren «py»." "Installer Python 3.13 fra python.org."
}
& py -3.13 -c "import sys" 2>$null
if ($LASTEXITCODE -ne 0) { Stopp "Python 3.13 er ikke installert." "Installer Python 3.13 fra python.org." }
Ok "Python 3.13"

# 2. Låst mcp-versjon (2.x brøt Datafinner)
$mcp = (& py -3.13 -c "import importlib.metadata as m; print(m.version('mcp'))" 2>$null)
if ($LASTEXITCODE -ne 0) { Stopp "Pakken mcp mangler." "py -3.13 -m pip install mcp==$ForventetMcp" }
if ($mcp -ne $ForventetMcp) { Stopp "mcp er $mcp, demoen krever $ForventetMcp." "py -3.13 -m pip install mcp==$ForventetMcp" }
Ok "mcp $mcp"

# 2b. Porten må være ledig, ellers åpner nettleseren en annen Datafinner (f.eks. utviklingskopien).
$Server = Join-Path $Rot 'src\kunstpixel\adapters\datafinner.py'
$lytter = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($lytter) {
    $kommando = (Get-CimInstance Win32_Process -Filter "ProcessId=$($lytter.OwningProcess)" -ErrorAction SilentlyContinue).CommandLine
    if ($kommando -and $kommando.ToLower().Contains($Server.ToLower())) {
        Ok "Datafinner fra denne mappen kjører allerede på http://127.0.0.1:$Port"
        if (-not $env:KUNSTPIXEL_DEMO_IKKE_NETTLESER) { Start-Process "http://127.0.0.1:$Port" }
        exit 0
    }
    Stopp "Port $Port er allerede i bruk av en annen prosess (trolig en annen Datafinner-kopi)." "Lukk den, og start på nytt."
}
Ok "Port $Port er ledig"

# 3. Databasen er den som er committet (sjekksum) og har ingen kvalitetsfeil.
$db = Join-Path $Rot '05_data\museum.db'
$sumfil = Join-Path $Rot '05_data\museum.db.sha256'
if (-not (Test-Path $db)) { Stopp "Fant ikke 05_data\museum.db." "Sjekk at du står i riktig demomappe." }
$env:KUNSTPIXEL_DB_PATH = $db
if (Test-Path $sumfil) {
    $forventet = ((Get-Content $sumfil -Raw).Trim() -split '\s+')[0].ToLower()
    $faktisk = (Get-FileHash $db -Algorithm SHA256).Hash.ToLower()
    if ($forventet -ne $faktisk) {
        Stopp "museum.db stemmer ikke med sjekksummen. Filen er endret." "git checkout -- 05_data/museum.db"
    }
    Ok "museum.db stemmer med sjekksummen"
}
& py -3.13 scripts/db_kvalitet.py --uten-bygg *> $null
if ($LASTEXITCODE -ne 0) { Stopp "Kvalitetssjekken fant feil i databasen." "py -3.13 scripts/db_kvalitet.py --uten-bygg" }
Ok "Kvalitetssjekk uten feil"

# 4. Selvtest: faste tall fra databasen (bare lesing).
$selvtest = @'
import sqlite3
c = sqlite3.connect("file:05_data/museum.db?mode=ro", uri=True)
print(",".join(str(c.execute(f"select count(*) from {t}").fetchone()[0]) for t in ("verk", "kunstnere", "saler")))
'@
$tall = ($selvtest | & py -3.13 -)
if ($tall -ne '16,12,6') { Stopp "Selvtesten fikk verk,kunstnere,saler = $tall, forventet 16,12,6." }
Ok "Selvtest: 16 verk, 12 kunstnere, 6 saler"

# 5. KI: på når den er tilgjengelig. -UtenKI gir en ren, deterministisk datavisning.
if (-not $UtenKI) {
    $env:LLM_PROVIDER = $null
    $envfil = Join-Path $Rot '.env'
    $navn = @()
    if (Test-Path $envfil) {
        $navn = Get-Content $envfil | Where-Object { $_ -match '^\s*([A-Z_]+)\s*=\s*\S' } | ForEach-Object { ($_ -split '=')[0].Trim() }
    }
    $mangler = @('LLM_PROVIDER', 'LLM_MODEL', 'LLM_API_KEY') | Where-Object { $_ -notin $navn }
    if ($mangler -and (Get-Command claude -ErrorAction SilentlyContinue)) {
        # Ingen API-nøkkel: bruk din egen Claude (Claude Code på abonnementet). Se src/kunstpixel/core/claude_cli.py.
        $env:LLM_PROVIDER = 'claude-cli'
        Ok "KI på via din egen Claude (claude-kommandoen, ingen API-nøkkel)"
    } elseif ($mangler) {
        Write-Host "[!!] KI er ikke satt opp (mangler i .env: $($mangler -join ', '), og claude-kommandoen finnes ikke). Fortsetter uten KI." -ForegroundColor Yellow
        $env:LLM_PROVIDER = ' '
    } else {
        Ok "KI på (fra .env)"
    }
} else {
    $env:LLM_PROVIDER = ' '
    Ok "KI av (-UtenKI)"
}

# 6. Start Datafinner, vent til den svarer, åpne nettleseren.
$url = "http://127.0.0.1:$Port"
Write-Host ""
Write-Host "Starter Datafinner på $url ... (Ctrl+C for å stoppe)"
# Start python.exe direkte (ikke py-starteren), så prosessen vi stopper er selve serveren og porten frigjøres.
$python = (& py -3.13 -c "import sys; print(sys.executable)")
$proc = Start-Process -FilePath $python -ArgumentList "`"$Server`"" -WorkingDirectory $Rot -WindowStyle Hidden -PassThru
$klar = $false
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Milliseconds 500
    if ($proc.HasExited) { Stopp "Datafinner stoppet ved oppstart (kode $($proc.ExitCode))." "Se feilmeldingen over." }
    try { Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 | Out-Null; $klar = $true; break } catch { }
}
if (-not $klar) { Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue; Stopp "Datafinner svarte ikke innen 30 sekunder." }
Ok "Datafinner svarer"
if (-not $env:KUNSTPIXEL_DEMO_IKKE_NETTLESER) { Start-Process $url }
try { Wait-Process -Id $proc.Id } finally { if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue } }
