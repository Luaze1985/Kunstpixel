' Starter Datafinner skjult (uten vindu) via start_demo.ps1 -Bakgrunn.
' Brukes av autostart (scripts/autostart.ps1). Logg: .scratch\datafinner_bakgrunn.log
Set fso = CreateObject("Scripting.FileSystemObject")
mappe = fso.GetParentFolderName(WScript.ScriptFullName)
skript = mappe & "\start_demo.ps1"
CreateObject("WScript.Shell").Run "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & skript & """ -Bakgrunn", 0, False
