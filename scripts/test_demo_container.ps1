# test_demo_container.ps1 - Bygger og starter demo-oppsettet lokalt i Docker og sjekker det.
#
# Hva den gjør: bygger bildet, starter datafinner + Caddy på 127.0.0.1:18080 (bare din PC), tester
# innlogging, verktøy, sikkerhetshoder og at den fulle databasen er i bildet. Rydder etterpå.
# Den rører ikke andre containere eller bilder. Alt den lager heter kpdemo-test.
#
#   powershell -ExecutionPolicy Bypass -File scripts\test_demo_container.ps1
#   ... -Behold        # ikke rydd opp etterpå (for å se på containerne selv)
#
# Testpassordet under brukes bare mot denne lokale testen og er ikke en ekte hemmelighet.

param([switch]$Behold)

$ErrorActionPreference = 'Stop'
$Rot = Split-Path -Parent $PSScriptRoot
$Demo = Join-Path $Rot 'deploy\demo'
$Prosjekt = 'kpdemo-test'
$Bilde = 'kpdemo-test:latest'
$Port = 18080
$Bruker = 'tester'
$Passord = 'lokal-test-1234567890'
$Url = "http://127.0.0.1:$Port"
$Midl = Join-Path ([IO.Path]::GetTempPath()) ('kpdemo-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$ComposeFil = Join-Path $Midl 'server\compose.yaml'
$feil = 0

function Sjekk([string]$navn, [bool]$ok, [string]$detalj = '') {
    if ($ok) { Write-Host "[OK]   $navn" -ForegroundColor Green }
    else { Write-Host ("[FEIL] $navn " + $detalj) -ForegroundColor Red; $script:feil++ }
}

# Obs: ikke gi en funksjon navnet Docker. PowerShell skiller ikke på store og små bokstaver, så den ville kalt seg selv.
function Compose { & docker compose -p $Prosjekt -f $ComposeFil @args; if ($LASTEXITCODE -ne 0) { throw ("compose feilet: " + ($args -join ' ')) } }

# curl.exe følger med Windows 10 og nyere. Returnerer statuskode og hoder.
function Hent([string]$sti, [string]$bruker = '', [string]$passord = '', [string]$kropp = '') {
    $a = @('-s', '-i', '--max-time', '20')
    if ($bruker) { $a += @('-u', ($bruker + ':' + $passord)) }
    if ($kropp) { $a += @('-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', $kropp) }
    $ut = & curl.exe @a ($Url + $sti) | Out-String
    $status = 0
    if ($ut -match '^HTTP/[\d.]+ (\d{3})') { $status = [int]$Matches[1] }
    return [pscustomobject]@{ Status = $status; Tekst = $ut }
}

try {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker finnes ikke.' }
    & docker info *> $null
    if ($LASTEXITCODE -ne 0) { throw 'Docker kjører ikke. Start Docker Desktop.' }
    if (& docker image ls -q $Bilde) { throw "Bildet $Bilde finnes fra før. Fjern det selv hvis det er et gammelt testbilde: docker image rm $Bilde" }

    New-Item -ItemType Directory -Path $Midl | Out-Null
    Write-Host '== Lager testbruker (hash lages av Caddy)'
    $hash = (& docker run --rm caddy:2 caddy hash-password --plaintext $Passord).Trim()
    if ($hash -notmatch '^\$2[aby]\$') { throw 'Fikk ikke en gyldig hash fra Caddy.' }
    $brukereFil = Join-Path $Midl 'brukere.caddy'
    [IO.File]::WriteAllText($brukereFil, "$Bruker $hash`n", (New-Object Text.UTF8Encoding($false)))

    $env:DATAFINNER_IMAGE = $Bilde
    $env:DEMO_DOMAIN = ':80'
    $env:BIND_ADRESSE = '127.0.0.1'
    $env:HTTP_PORT = "$Port"
    $env:HTTPS_PORT = '18443'
    $env:BRUKERE_FIL = $brukereFil

    Write-Host '== Bygger bildet (første gang tar det noen minutter)'
    & docker build -f (Join-Path $Demo 'Dockerfile') -t $Bilde $Rot
    if ($LASTEXITCODE -ne 0) { throw 'docker build feilet.' }

    # Slik serveren bruker det: bare compose-filene ligger der, og bildet er lastet inn på forhånd (--no-build).
    # Filene kopieres til en vanlig mappe, fordi Docker ikke kan montere enkeltfiler fra Google Drive (G:).
    $serverMappe = Join-Path $Midl 'server'
    New-Item -ItemType Directory -Path $serverMappe | Out-Null
    Copy-Item (Join-Path $Demo 'compose.yaml'), (Join-Path $Demo 'Caddyfile') $serverMappe
    Write-Host '== Starter (uten kildekoden ved siden av, som på serveren)'
    Compose up -d --no-build --wait
    Start-Sleep -Seconds 3

    Write-Host '== Innlogging'
    $uten = Hent '/'
    Sjekk 'uten innlogging gir 401' ($uten.Status -eq 401) ("fikk " + $uten.Status)
    Sjekk '401 ber om innlogging (WWW-Authenticate)' ($uten.Tekst -match '(?i)www-authenticate:\s*basic')
    $feilPassord = Hent '/' $Bruker 'feil-passord'
    Sjekk 'feil passord gir 401' ($feilPassord.Status -eq 401) ("fikk " + $feilPassord.Status)
    $ok = Hent '/' $Bruker $Passord
    Sjekk 'riktig passord gir 200 og forsiden' (($ok.Status -eq 200) -and ($ok.Tekst -match 'Datafinner')) ("fikk " + $ok.Status)
    $apiUten = Hent '/api/verktoy?navn=list_roles&args=%7B%7D'
    Sjekk 'API uten innlogging gir 401' ($apiUten.Status -eq 401)

    Write-Host '== Verktøy og sider'
    $roller = Hent '/api/verktoy?navn=list_roles&args=%7B%7D' $Bruker $Passord
    Sjekk 'list_roles gir 200' ($roller.Status -eq 200)
    $les = Hent '/api/verktoy?navn=les_fil&args=%7B%22sti%22%3A%2200_felles%2FFORMAAL.md%22%7D' $Bruker $Passord
    Sjekk 'les_fil finner ikke mapper som ikke er kopiert inn (400)' ($les.Status -eq 400) ("fikk " + $les.Status)
    $grep = Hent '/api/verktoy?navn=grep_mappe&args=%7B%22query%22%3A%22x%22%7D' $Bruker $Passord
    Sjekk 'grep_mappe svarer uten interne mapper (200)' (($grep.Status -eq 200) -and ($grep.Tekst -match '\[\]')) ("fikk " + $grep.Status)
    $sok = Hent '/sok.html' $Bruker $Passord
    Sjekk '/sok.html finnes (200)' ($sok.Status -eq 200) ("fikk " + $sok.Status)
    $vakter = Hent '/api/verktoy?navn=get_shifts_for_date&args=%7B%22dato%22%3A%222026-10-20%22%7D' $Bruker $Passord
    Sjekk 'vaktplan gir 200' ($vakter.Status -eq 200)
    Sjekk 'vaktplanen har ingen e-postadresser' ($vakter.Tekst -notmatch '@')
    Sjekk 'vaktplanen har ingen telefonnummer' ($vakter.Tekst -notmatch '\+47')

    Write-Host '== Åpent API (faste rapporter, KI-laget er av)'
    $status = Hent '/api/status' $Bruker $Passord
    Sjekk '/api/status sier at KI-laget er av' (($status.Status -eq 200) -and ($status.Tekst -match '"llm":\s*false'))
    $skjema = Hent '/api/verktoyskjema' $Bruker $Passord
    Sjekk '/api/verktoyskjema gir verktøylisten' (($skjema.Status -eq 200) -and ($skjema.Tekst -match '"get_absence_report"'))
    Sjekk 'verktøylisten har filverktøyene' (($skjema.Tekst -match 'les_fil') -and ($skjema.Tekst -match 'grep_mappe'))
    $rap1 = Hent '/api/rapport?sporsmal=vaktplan&args=%7B%22dato%22%3A%222026-10-20%22%7D' $Bruker $Passord
    $rap2 = Hent '/api/rapport?sporsmal=vaktplan&args=%7B%22dato%22%3A%222026-10-20%22%7D' $Bruker $Passord
    Sjekk '/api/rapport gir en rapport med regel og merker' (($rap1.Status -eq 200) -and ($rap1.Tekst -match 'R-PLAN-') -and ($rap1.Tekst -match 'Systemforslag'))
    # Sammenligner bare selve rapporten (etter hodene), for hodene har et Date som endrer seg.
    $kropp1 = [regex]::Split($rap1.Tekst, '\r?\n\r?\n', 2)[1]
    $kropp2 = [regex]::Split($rap2.Tekst, '\r?\n\r?\n', 2)[1]
    Sjekk 'samme rapport to ganger gir samme svar' (($kropp1.Length -gt 100) -and ($kropp1 -ceq $kropp2))
    Sjekk 'rapporten har ingen e-postadresser' ($rap1.Tekst -notmatch '@')
    $forklar = Hent '/api/forklar' $Bruker $Passord '{"sporsmal":"vaktplan","args":{"dato":"2026-10-20"}}'
    Sjekk '/api/forklar gir 503 når KI-laget er av' ($forklar.Status -eq 503) ("fikk " + $forklar.Status)
    $forklarUten = Hent '/api/forklar' '' '' '{"sporsmal":"vaktplan"}'
    Sjekk '/api/forklar uten innlogging gir 401' ($forklarUten.Status -eq 401) ("fikk " + $forklarUten.Status)

    Write-Host '== Hoder'
    Sjekk 'X-Frame-Options er DENY' ($ok.Tekst -match '(?i)x-frame-options:\s*DENY')
    Sjekk 'innholdspolicy (CSP) er satt' ($ok.Tekst -match '(?i)content-security-policy:')
    Sjekk 'HSTS er satt av Caddy' ($ok.Tekst -match '(?i)strict-transport-security:')
    Sjekk 'Server-hodet er fjernet' ($ok.Tekst -notmatch '(?im)^server:')

    Write-Host '== Containeren'
    $direkte = (& curl.exe -s -o NUL -w '%{http_code}' --max-time 5 'http://127.0.0.1:8010/' 2>$null)
    Sjekk 'datafinner er ikke åpen direkte på port 8010' (($direkte -eq '000') -or (-not $direkte))
    $uid = (& docker compose -p $Prosjekt -f $ComposeFil exec -T datafinner id -u).Trim()
    Sjekk 'datafinner kjører ikke som root' ($uid -eq '10001') ("uid=" + $uid)
    # Feilmeldingen fra touch skal ikke krasje skriptet, så returkoden skrives ut i stedet.
    $skriv = (& docker compose -p $Prosjekt -f $ComposeFil exec -T datafinner sh -c 'touch /app/x 2>/dev/null; echo $?') -join ''
    Sjekk 'filsystemet er skrivebeskyttet (kan ikke skrive til /app)' ($skriv.Trim() -ne '0') ("touch ga returkode " + $skriv)
    $tmp = (& docker compose -p $Prosjekt -f $ComposeFil exec -T datafinner sh -c 'touch /tmp/x 2>/dev/null; echo $?') -join ''
    Sjekk '/tmp kan skrives til (så programmet fungerer)' ($tmp.Trim() -eq '0')
    $innhold = (& docker compose -p $Prosjekt -f $ComposeFil exec -T datafinner ls /app) -join ','
    Sjekk '/app har bare src og data (ingen interne mapper)' ($innhold -eq 'data,src') ("fikk " + $innhold)
    $py = @'
import sqlite3
c = sqlite3.connect("file:/app/data/museum.db?mode=ro", uri=True)
print(c.execute("select count(*) from hr_ansatte").fetchone()[0])
print(c.execute("pragma user_version").fetchone()[0])
print(c.execute("select count(*) from sqlite_master where type='table' and name='hr_people'").fetchone()[0])
'@
    # Koden sendes via stdin (python -). Som argument ville linjeskiftene gått tapt.
    $tall = ($py | & docker compose -p $Prosjekt -f $ComposeFil exec -T datafinner python -) -join ','
    Sjekk 'bildet har full museum.db med HR-tabeller' ($tall -eq '168,4,1') ("fikk " + $tall)
}
catch {
    Write-Host ("[FEIL] " + $_.Exception.Message) -ForegroundColor Red
    if (Test-Path $ComposeFil) {
        & docker compose -p $Prosjekt -f $ComposeFil logs --no-color --tail 30 datafinner 2>&1 | Out-Host
    }
    $feil++
}
finally {
    if ($Behold) {
        Write-Host "`nBeholdt. Rydd selv med: docker compose -p $Prosjekt -f $ComposeFil down -v ; docker image rm $Bilde" -ForegroundColor Yellow
    } else {
        Write-Host "`n== Rydder opp (bare kpdemo-test)"
        if (Test-Path $ComposeFil) { try { & docker compose -p $Prosjekt -f $ComposeFil down -v 2>&1 | Out-Null } catch { } }
        try { & docker image rm $Bilde 2>&1 | Out-Null } catch { }
        if (Test-Path $Midl) { Remove-Item -Recurse -Force $Midl }
    }
    foreach ($v in 'DATAFINNER_IMAGE', 'DEMO_DOMAIN', 'BIND_ADRESSE', 'HTTP_PORT', 'HTTPS_PORT', 'BRUKERE_FIL') { Remove-Item "Env:$v" -ErrorAction SilentlyContinue }
}

if ($feil -eq 0) { Write-Host "`nAlt bestått." -ForegroundColor Green; exit 0 }
Write-Host ("`n{0} feil." -f $feil) -ForegroundColor Red
exit 1
