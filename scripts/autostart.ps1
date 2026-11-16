<#
Slår autostart av Datafinner på eller av for din Windows-bruker.

    powershell -ExecutionPolicy Bypass -File scripts/autostart.ps1          # på: starter skjult ved pålogging
    powershell -ExecutionPolicy Bypass -File scripts/autostart.ps1 -Fjern   # av

"På" lager to snarveier:
  - Oppstart-mappen: «Kunstpixel Datafinner.lnk» -> scripts\start_bakgrunn.vbs
  - Skrivebordet:    «Kunstpixel Datafinner.url» -> http://127.0.0.1:8010
Ingen administratorrettigheter, ingen tjeneste, ingen registerendring.
#>
param([switch]$Fjern)

$Navn = 'Kunstpixel Datafinner'
$Oppstart = Join-Path ([Environment]::GetFolderPath('Startup')) "$Navn.lnk"
$Skrivebord = Join-Path ([Environment]::GetFolderPath('Desktop')) "$Navn.url"
$Vbs = Join-Path $PSScriptRoot 'start_bakgrunn.vbs'

if ($Fjern) {
    foreach ($f in $Oppstart, $Skrivebord) {
        if (Test-Path $f) { Remove-Item $f; Write-Host "Fjernet $f" }
    }
    Write-Host "Autostart er av. En Datafinner som kjører nå, stopper ved neste omstart (eller avslutt python-prosessen)."
    exit 0
}

$skall = New-Object -ComObject WScript.Shell
$lnk = $skall.CreateShortcut($Oppstart)
$lnk.TargetPath = "$env:WINDIR\System32\wscript.exe"
$lnk.Arguments = "`"$Vbs`""
$lnk.WorkingDirectory = Split-Path -Parent $PSScriptRoot
$lnk.Description = 'Starter Kunstpixel Datafinner skjult på http://127.0.0.1:8010'
$lnk.Save()
Write-Host "Laget $Oppstart"

Set-Content -Path $Skrivebord -Encoding ASCII -Value "[InternetShortcut]`r`nURL=http://127.0.0.1:8010/`r`n"
Write-Host "Laget $Skrivebord"
Write-Host "Autostart er på. Datafinner starter skjult ved neste pålogging. Logg: .scratch\datafinner_bakgrunn.log"
