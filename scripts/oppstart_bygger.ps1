# Kunstpixel Oppstartsbygger - Kjøres automatisk ved maskinoppstart via Pixel-Bygger
$ErrorActionPreference = "Continue"
$projectRoot = "C:\Users\larse\Documents\Kunstpixel"

& powershell -NoProfile -ExecutionPolicy Bypass -File "$projectRoot\scripts\pixel_bygger.ps1"
