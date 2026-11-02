# Testsele for vps_veileder.ps1: kjører trinn 2, 4, 5 og 7 mot falske svar.
# Ingen nettleser, ingen ekte DNS og ingen ssh. Trinn 3 (lage nøkkel) og 6 (ssh) testes ikke her.
#   powershell -ExecutionPolicy Bypass -File scripts	est_vps_veileder.ps1
param([string]$Veileder = (Join-Path $PSScriptRoot 'vps_veileder.ps1'))
$ErrorActionPreference = 'Stop'
$script:svar = New-Object System.Collections.Queue
$script:apnet = @()
function Read-Host { param($Prompt) if ($script:svar.Count -eq 0) { throw "Veilederen spurte mer enn forventet: $Prompt" }; $s = $script:svar.Dequeue(); $script:spurt += ,$Prompt; return $s }
function Clear-Host {}
function Start-Process { param($FilePath) $script:apnet += $FilePath }
function Resolve-DnsName { param($Name, $Type, $Server, [switch]$DnsOnly, $ErrorAction) [pscustomobject]@{ Type = 'A'; IPAddress = '203.0.113.10' } }
function Start-Sleep { param($Seconds) }
$script:spurt = @()
. $Veileder
$feil = 0
function Forvent([string]$navn, $faktisk, $forventet) { if ($faktisk -eq $forventet) { Write-Host "[OK]   $navn" -ForegroundColor Green } else { Write-Host "[FEIL] $navn : fikk '$faktisk', ventet '$forventet'" -ForegroundColor Red; $script:feil++ } }

if (Test-Path $ValgFil) { Remove-Item $ValgFil }
$valg = Les-Valg
# Trinn 2: ja til å åpne Norid, Enter, ugyldig domene, gyldig domene, tomt underdomene (standard demo), Enter
foreach ($s in @('j', '', 'http://feil', 'Mitt-Demo.no', '', '')) { $script:svar.Enqueue($s) }
Trinn2
Forvent 'domene lagret' $valg.domene 'mitt-demo.no'
Forvent 'underdomene standard' $valg.underdomene 'demo'
Forvent 'tre Norid-sider åpnet' $script:apnet.Count 3
Forvent 'valgfil skrevet' (Test-Path $ValgFil) $true

# Trinn 4: Enter, ugyldig IP, gyldig IP, bruker med ugyldig tegn, gyldig bruker, Enter
$script:apnet = @()
foreach ($s in @('n', '', '999.1.1.1', '203.0.113.10', 'a;b', 'deploy', '')) { $script:svar.Enqueue($s) }
Trinn4
Forvent 'ip lagret' $valg.ip '203.0.113.10'
Forvent 'bruker lagret' $valg.bruker 'deploy'

# Trinn 5: Enter -> DNS-sjekken (falsk) skal bekrefte
foreach ($s in @('', '')) { $script:svar.Enqueue($s) }
Trinn5
Forvent 'dns_ok satt' $valg.dns_ok $true

# Valgfilen har ingen hemmeligheter og kan leses tilbake
$les = Get-Content $ValgFil -Raw -Encoding UTF8 | ConvertFrom-Json
Forvent 'valgfil: domene' $les.domene 'mitt-demo.no'
Forvent 'valgfil: ip' $les.ip '203.0.113.10'
Forvent 'valgfil har ingen passord/token-felt' (($les.PSObject.Properties.Name | Where-Object { $_ -match 'pass|token|hemmelig|secret' }).Count) 0

# Trinn 7 skriver sammendrag uten å spørre om noe
Trinn7
Forvent 'ingen ubesvarte spørsmål igjen' $script:svar.Count 0
Remove-Item $ValgFil
if ($feil -eq 0) { Write-Host 'Testselen bestått.' -ForegroundColor Green; exit 0 } else { exit 1 }
