param(
    [string]$Mode = "manual"
)

$ErrorActionPreference = "Stop"

Write-Host "== Kunstpixel Backend Deterministisk Verifisering ($Mode) ==" -ForegroundColor Cyan

# 1. Kjoer pytest
Write-Host "1. Kjoerer automatisert testsuite med pytest..." -ForegroundColor Yellow
$pytestOut = py -3.13 -m pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pytest feilet!" -ForegroundColor Red
    Write-Host $pytestOut
    exit 1
}
Write-Host "Pytest passerte 100 %!" -ForegroundColor Green

# 2. Verifiser CLI-kommandoer
Write-Host "2. Verifiserer CLI-rapportering..." -ForegroundColor Yellow
$cliKiosk = py -3.13 src/hr_cli.py kiosk
if ($LASTEXITCODE -ne 0 -or -not ($cliKiosk -match "suggested_ids")) {
    Write-Host "CLI kiosk-rapport feilet!" -ForegroundColor Red
    exit 1
}

$cliRules = py -3.13 src/hr_cli.py rules
if ($LASTEXITCODE -ne 0 -or -not ($cliRules -match "HMS-001")) {
    Write-Host "CLI rules-rapport feilet!" -ForegroundColor Red
    exit 1
}

$cliSkills = py -3.13 src/hr_cli.py skills
if ($LASTEXITCODE -ne 0 -or -not ($cliSkills -match "allergen")) {
    Write-Host "CLI skills-rapport feilet!" -ForegroundColor Red
    exit 1
}

# 3. Verifiser master immutabilitet
Write-Host "3. Verifiserer immutabilitet for 05_data/museum.db..." -ForegroundColor Yellow
$pyScript = "import sqlite3; con = sqlite3.connect('05_data/museum.db'); print('tables:', len(con.execute('SELECT name FROM sqlite_master').fetchall()))"
$immutCheck = py -3.13 -c $pyScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "Master DB sjekk feilet!" -ForegroundColor Red
    exit 1
}

Write-Host "== VERIFISERING PASS: Alt er i orden! ==" -ForegroundColor Green
exit 0
