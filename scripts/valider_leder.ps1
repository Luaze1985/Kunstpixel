$ErrorActionPreference = 'Stop'
$prosjekt = Split-Path -Parent $PSScriptRoot

function Sjekk-Exitkode([string]$steg) {
    if ($LASTEXITCODE -ne 0) {
        throw "$steg feilet med kode $LASTEXITCODE."
    }
}

Push-Location $prosjekt
try {
    Get-Command py -ErrorAction Stop | Out-Null
    & py -3.13 -c 'import playwright.sync_api'
    Sjekk-Exitkode 'Playwright-kontroll'

    & py -3.13 -m pytest tests/test_start_gate.py tests/test_ledervalidering.py -q
    Sjekk-Exitkode 'Lederens tester'

    & py -3.13 scripts/db_status_gate.py --uten-pytest --aktiv-db 05_data/museum.db --kort
    Sjekk-Exitkode 'Statusport for aktiv database'

    Write-Host 'KLAR: lederens valideringssett passerer.'
}
finally {
    Pop-Location
}
