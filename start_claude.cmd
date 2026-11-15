@echo off
setlocal
rem Dobbeltklikk for aa aapne din egen Claude i Kunstpixel-mappen, med Kunstpixel-verktoyene (MCP, se .mcp.json).
rem Foerste gang spoer Claude om du vil godkjenne serveren "kunstpixel". Svar ja.
rem Statusporten kjoeres foerst. Er den roed, starter ikke Claude (DECISIONS L10). Etter et svar: skriv /sjekk.
cd /d "%~dp0"
if errorlevel 1 (echo STOPP: Fant ikke prosjektmappen. & pause & exit /b 1)
where claude >nul 2>nul || (echo Fant ikke kommandoen claude. Installer Claude Code foerst. & pause & exit /b 1)
py -3.13 -c "import sys" >nul 2>nul
if errorlevel 1 (echo STOPP: Python 3.13 er ikke tilgjengelig. Installer eller reparer Python 3.13. & pause & exit /b 1)
set "KUNSTPIXEL_DB_PATH=%CD%\05_data\museum.db"
echo Sjekker databasen Claude skal lese ...
py -3.13 scripts/db_status_gate.py --uten-pytest --aktiv-db "%KUNSTPIXEL_DB_PATH%" --kort
if errorlevel 1 (echo. & echo STOPP: statusporten fant feil i museum.db. Se rapporten over. & pause & exit /b 1)
call claude %*
set "KODE=%ERRORLEVEL%"
if not "%KODE%"=="0" (echo STOPP: Claude avsluttet med kode %KODE%. & pause)
exit /b %KODE%
