@echo off
chcp 65001 >nul
rem Dobbeltklikk for aa sjekke helsen paa nye data (05_data og 01_inbox), kunnskapsgraf og LLM-tilgjengelighet.
cd /d "%~dp0"
echo ======================================================================
echo  1. SJEKKER ALLE CSV-FILER, KUNNSKAPSGRAF OG LLM-VERKTOYDEKNING
echo ======================================================================
py -3.13 scripts/sjekk_kunnskapsgraf.py
echo.
echo ======================================================================
echo  2. BYGGER MIDLERTIDIG DB FRA NYE DATA OG SJEKKER REGLER (0 tokens)
echo ======================================================================
py -3.13 scripts/db_kvalitet.py --fra-data --rapport lagring
echo.
echo ======================================================================
echo  Rapporter lagret til:
echo    - .scratch\kvalitet\KUNNSKAPSGRAF_FOR_LLM.md  (Tabeller, koblinger og LLM-status)
echo    - .scratch\kvalitet\RAPPORT.md                (Databasehelse og arbeidsmiljoregler)
echo.
echo  Slik ber du LLM (Claude / Codex / Antigravity) fikse og koble paa nye data:
echo    "Les .scratch/kvalitet/KUNNSKAPSGRAF_FOR_LLM.md og .scratch/kvalitet/RAPPORT.md og koble paa / fiks avvikene"
echo ======================================================================
pause
