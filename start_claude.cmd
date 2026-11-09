@echo off
rem Dobbeltklikk for aa aapne din egen Claude i Kunstpixel-mappen, med Kunstpixel-verktoyene (MCP, se .mcp.json).
rem Foerste gang spoer Claude om du vil godkjenne serveren "kunstpixel". Svar ja.
cd /d "%~dp0"
where claude >nul 2>nul || (echo Fant ikke kommandoen claude. Installer Claude Code foerst. & pause & exit /b 1)
claude %*
if errorlevel 1 pause
