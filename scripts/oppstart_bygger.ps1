# Kunstpixel Oppstartsbygger - Kjøres automatisk ved maskinoppstart via Pixel-Bygger
$ErrorActionPreference = "Continue"
$projectRoot = "G:\Min disk\Kunstpixel"

& powershell -NoProfile -ExecutionPolicy Bypass -File "$projectRoot\scripts\pixel_bygger.ps1"
