$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    & py -3.13 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Kunne ikke opprette .venv med Python 3.13.' }
}
$demoPython = Join-Path $PWD '.venv\Scripts\python.exe'
& $demoPython -c 'import sys; assert sys.version_info[:2] == (3, 13), "Demoen krever Python 3.13 i .venv"'
if ($LASTEXITCODE -ne 0) { throw 'Kontroller Python-versjonen i .venv.' }
& $demoPython -m pip install --disable-pip-version-check --no-input -r requirements-demo.txt
if ($LASTEXITCODE -ne 0) { throw 'Installasjonen av demoavhengigheter feilet.' }
& $demoPython -m src.kunstpixel.hr_simulator web
if ($LASTEXITCODE -ne 0) { throw 'Demoserveren stoppet med feil.' }
