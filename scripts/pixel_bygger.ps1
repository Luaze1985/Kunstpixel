<#
.SYNOPSIS
    pixel_bygger.ps1 - Den helhetlige byggeren og orkestratoren for Kunstpixel.
    Kjører hele multi-agentflyten fra A til Å:
    1. Sjekker arbeidsområde og Google Drive
    2. Deterministisk statusport (db_status_gate.py)
    3. Toveis Colab MCP-synk & bestillinger (colab_sync.py)
    4. Kurator-agent (kurator_generator.py -> utstillings-artefakt)
    5. Kjernevalidering & tester (pytest)
    6. Oppdaterer bygger-fremdrift.md og logg
#>

param(
    [switch]$UtenTester,
    [string]$Forgreining = ""
)

$ErrorActionPreference = "Continue"
$projectRoot = "G:\Min disk\Kunstpixel"

# 1. Sikre at Google Drive og prosjektmappen er tilgjengelig
$maxRetries = 10
$retry = 0
while (-not (Test-Path $projectRoot) -and $retry -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retry++
}

if (-not (Test-Path $projectRoot)) {
    Write-Error "Kunne ikke finne $projectRoot. Er Google Drive montert?"
    exit 1
}

Set-Location $projectRoot

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$scratchDir = "$projectRoot\.scratch"
if (-not (Test-Path $scratchDir)) {
    New-Item -ItemType Directory -Path $scratchDir -Force | Out-Null
}

$logFile = "$scratchDir\pixel_bygger_log.txt"
"============================================================" | Out-File -FilePath $logFile -Encoding utf8
"=== KUNSTPIXEL: PIXEL-BYGGER TOTALKJØRING ===" | Out-File -FilePath $logFile -Append -Encoding utf8
"Tidspunkt: $timestamp" | Out-File -FilePath $logFile -Append -Encoding utf8
"============================================================" | Out-File -FilePath $logFile -Append -Encoding utf8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "=== KUNSTPIXEL: PIXEL-BYGGER STARTER ($timestamp) ===" -ForegroundColor Cyan
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
# FASE 2: DETERMINISTISK GRUNNKAM (0 TOKENS)
# -------------------------------------------------------------------------
Write-Host "`n[FASE 2] Kjører deterministisk statusport (0 tokens)..." -ForegroundColor Yellow
& py -3.13 scripts/db_status_gate.py --uten-pytest | Tee-Object -FilePath $logFile -Append
if ($LASTEXITCODE -ne 0) {
    Write-Host "ADVARSEL: Statusporten ga avvik eller feil." -ForegroundColor Red
} else {
    Write-Host "Statusport bestått med 0 feil og 0 fremmednøkkelbrudd!" -ForegroundColor Green
}

# -------------------------------------------------------------------------
# FASE 3: TOVEIS COLAB MCP-BRO & DATAFANGST
# -------------------------------------------------------------------------
Write-Host "`n[FASE 3] Synkroniserer Google Colab via FastMCP..." -ForegroundColor Yellow
& py -3.13 scripts/colab_sync.py | Tee-Object -FilePath $logFile -Append

# -------------------------------------------------------------------------
# FASE 4: KURATOR-AGENT & KUNSTHISTORISK ARTIFACT
# -------------------------------------------------------------------------
Write-Host "`n[FASE 4] Kaller kurator-agent for utstillings-artefakt..." -ForegroundColor Yellow
& py -3.13 scripts/kurator_generator.py | Tee-Object -FilePath $logFile -Append

# -------------------------------------------------------------------------
# FASE 5: KJERNEVALIDERING & TESTER
# -------------------------------------------------------------------------
if (-not $UtenTester) {
    Write-Host "`n[FASE 5] Kjører kjernevalidering og automatiserte tester..." -ForegroundColor Yellow
    & py -3.13 -m pytest tests/test_mvp_bemanning.py tests/test_hr_cases.py tests/test_mcp_server.py tests/test_mvp_oppslag.py | Tee-Object -FilePath $logFile -Append
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
# FASE 6: OPPDATER MERMAID ERD & FREMDRIFTSSTATUS
# -------------------------------------------------------------------------
Write-Host "`n[FASE 6] Oppdaterer Mermaid ERD og bygger-fremdrift..." -ForegroundColor Yellow
& py -3.13 "C:\Users\larse\.gemini\config\skills\database-inspektor\scripts\db_inspect.py" --db "05_data/museum.db" --output "$scratchDir\db-status\INSPEKSJON-SISTE.md" | Out-Null

$sluttTid = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"Kjøring fullført kl $sluttTid" | Out-File -FilePath "$scratchDir\oppstart_siste.txt" -Encoding utf8

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "=== PIXEL-BYGGER FULLFØRT MED SUKSESS ($sluttTid) ===" -ForegroundColor Green
Write-Host "Utstilling lagret til: .scratch\kurator_siste_utstilling.md" -ForegroundColor Green
Write-Host "Logg lagret til:      .scratch\pixel_bygger_log.txt" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
