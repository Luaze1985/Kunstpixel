@echo off
rem Dobbeltklikk for aa aapne din egen Claude i Kunstpixel-mappen, med Kunstpixel-verktoyene (MCP, se .mcp.json).
rem Foerste gang spoer Claude om du vil godkjenne serveren "kunstpixel". Svar ja.
rem Statusporten kjoeres foerst. Er den roed, starter ikke Claude (DECISIONS L10). Etter et svar: skriv /sjekk.
cd /d "%~dp0"
where claude >nul 2>nul || (echo Fant ikke kommandoen claude. Installer Claude Code foerst. & pause & exit /b 1)
echo Sjekker museum.db med statusporten ...
py -3.13 scripts/db_status_gate.py --uten-pytest
if errorlevel 1 (echo. & echo STOPP: statusporten fant feil i museum.db. Se rapporten over. & pause & exit /b 1)
claude %*
if errorlevel 1 pause
