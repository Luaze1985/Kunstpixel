@echo off
rem Dobbeltklikk for aa starte Kunstpixel-demoen (Datafinner) med KI hvis tilgjengelig. Legg til -UtenKI for bare data.
rem Virker fra hvilken som helst mappe: %~dp0 er mappen denne filen ligger i.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_demo.ps1" %*
if errorlevel 1 pause
