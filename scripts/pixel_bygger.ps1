<#
.SYNOPSIS
    pixel_bygger.ps1 - Den helhetlige byggeren og orkestratoren for Kunstpixel (ADR 014).
    Kjører hele den samlede multi-agentflyten fra A til Å uten stopp:
    1. Forgreiningssjekk (arbeidsområde)
    2. Steg 1 (Informasjonsjeger): Gap-analyse (informasjonsjeger_kontroll.py --finn-hull)
    3. Steg 2 (Kontrollport & Databygger): Validerer funn, ruller tilbake ved feil, bygger museum.db, sjekker sha256, kjører statusport og Colab-synk
    4. Steg 3 (Kurator & Motor/Kjernetester): kurator_generator.py + pytest på bemanning, HR-caser, oppslag og MCP
    5. Steg 4 (Systeminspektør / Sentinel): Genererer Mermaid ERD og INSPEKSJON-SISTE.md
#>

param(
    [switch]$UtenTester,
    [string]$Forgreining = ""
)

$ErrorActionPreference = "Continue"
$projectRoot = "C:\Users\larse\Documents\Kunstpixel"

# 1. Sikre at prosjektmappen er tilgjengelig
$maxRetries = 10
$retry = 0
while (-not (Test-Path $projectRoot) -and $retry -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retry++
}

if (-not (Test-Path $projectRoot)) {
    Write-Error "Kunne ikke finne $projectRoot."
    exit 1
}

Set-Location $projectRoot

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$scratchDir = "$projectRoot\.scratch"
if (-not (Test-Path $scratchDir)) {
    New-Item -ItemType Directory -Path $scratchDir -Force | Out-Null
}
if (-not (Test-Path "$scratchDir\db-status")) {
    New-Item -ItemType Directory -Path "$scratchDir\db-status" -Force | Out-Null
}

$logFile = "$scratchDir\pixel_bygger_log.txt"
"============================================================" | Out-File -FilePath $logFile -Encoding utf8
"=== KUNSTPIXEL: SAMLET AUTONOM TOTALKJØRING (ADR 014) ===" | Out-File -FilePath $logFile -Append -Encoding utf8
"Tidspunkt: $timestamp" | Out-File -FilePath $logFile -Append -Encoding utf8
"============================================================" | Out-File -FilePath $logFile -Append -Encoding utf8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "=== KUNSTPIXEL: SAMLET BYGGER STARTER ($timestamp) ===" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# -------------------------------------------------------------------------
# FASE 1: FORGREININGSVALG (Valgfri isolasjon)
# -------------------------------------------------------------------------
if ($Forgreining) {
    Write-Host "`n[FASE 1] Verifiserer agent-forgreining: $Forgreining..." -ForegroundColor Yellow
    $wtPath = "$projectRoot\.worktrees\$Forgreining"
    if (-not (Test-Path $wtPath)) {
        & powershell -File "$projectRoot\scripts\ny_forgreining.ps1" -Navn $Forgreining
    }
} else {
    $currentBranch = (git branch --show-current).Trim()
    Write-Host "`n[FASE 1] Kjører i aktiv forgreining: $currentBranch" -ForegroundColor Gray
}

# -------------------------------------------------------------------------
# FASE 2: INFORMASJONSJEGER GAP-ANALYSE (ADR 014 Steg 1)
# -------------------------------------------------------------------------
Write-Host "`n[FASE 2] Kjører Informasjonsjeger gap-analyse (0 tokens)..." -ForegroundColor Yellow
& py -3.13 scripts/informasjonsjeger_kontroll.py --finn-hull | Tee-Object -FilePath $logFile -Append

# -------------------------------------------------------------------------
# FASE 3: KONTROLLPORT, DATABASEBYGG, STATUSPORT & COLAB-SYNK (ADR 014 Steg 2)
# -------------------------------------------------------------------------
Write-Host "`n[FASE 3] Kjører Kontrollport, bygger museum.db, statusport og Colab-synk..." -ForegroundColor Yellow
& py -3.13 scripts/informasjonsjeger_kontroll.py --kontroller | Tee-Object -FilePath $logFile -Append
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVARSEL: Kontrollporten rapporterte avvik eller feil." -ForegroundColor Red
} else {
    Write-Host "Kontrollport, databasebygg, statusport og Colab-synk bestått!" -ForegroundColor Green
}

Write-Host "`n[FASE 3b] Verifiserer museum.db SHA256-sjekksum..." -ForegroundColor Yellow
& py -3.13 src/kunstpixel/data/build_museum_db.py --check | Tee-Object -FilePath $logFile -Append

# -------------------------------------------------------------------------
# FASE 4: KURATOR-AGENT & KUNSTHISTORISK ARTIFACT
# -------------------------------------------------------------------------
Write-Host "`n[FASE 4] Kaller kurator-agent for utstillings-artefakt..." -ForegroundColor Yellow
& py -3.13 scripts/kurator_generator.py | Tee-Object -FilePath $logFile -Append

# -------------------------------------------------------------------------
# FASE 5: MOTOR- & FUNKSJONSBYGGER / KJERNEVALIDERING (ADR 014 Steg 3)
# -------------------------------------------------------------------------
if (-not $UtenTester) {
    Write-Host "`n[FASE 5] Kjører kjernevalidering og automatiserte tester..." -ForegroundColor Yellow
    & py -3.13 -m pytest tests/test_mvp_bemanning.py tests/test_hr_cases.py tests/test_mcp_server.py tests/test_mvp_oppslag.py tests/test_handbook_compliance.py tests/test_hr_hms_pakke.py tests/test_publikum_data.py tests/test_datakatalog.py tests/test_daglig_driftsinnboks.py | Tee-Object -FilePath $logFile -Append
    $testResult = $LASTEXITCODE
    if ($testResult -eq 0) {
        Write-Host "Alle kjernetester passerte med 100% suksess!" -ForegroundColor Green
    } else {
        Write-Host "Noen tester feilet (exit code: $testResult)." -ForegroundColor Red
    }
} else {
    Write-Host "`n[FASE 5] Hoppet over tester etter parameter." -ForegroundColor Gray
}

# -------------------------------------------------------------------------
# FASE 6: SYSTEMINSPEKTØR, KUNNSKAPSGRAF & SENTINEL (ADR 014 Steg 4)
# -------------------------------------------------------------------------
Write-Host "`n[FASE 6] Kjører Systeminspektør (Mermaid ERD, sjekk_kunnskapsgraf.py & INSPEKSJON-SISTE.md)..." -ForegroundColor Yellow
& py -3.13 "C:\Users\larse\.gemini\config\skills\database-inspektor\scripts\db_inspect.py" --db "05_data/museum.db" --output "$scratchDir\db-status\INSPEKSJON-SISTE.md" | Tee-Object -FilePath $logFile -Append
& py -3.13 scripts/sjekk_kunnskapsgraf.py | Tee-Object -FilePath $logFile -Append

$sluttTid = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"Kjøring fullført kl $sluttTid" | Out-File -FilePath "$scratchDir\oppstart_siste.txt" -Encoding utf8

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "=== PIXEL-BYGGER SAMLET FLYT FULLFØRT ($sluttTid) ===" -ForegroundColor Green
Write-Host "Inspeksjon lagret til: .scratch\db-status\INSPEKSJON-SISTE.md" -ForegroundColor Green
Write-Host "Utstilling lagret til: .scratch\kurator_siste_utstilling.md" -ForegroundColor Green
Write-Host "Logg lagret til:       .scratch\pixel_bygger_log.txt" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
