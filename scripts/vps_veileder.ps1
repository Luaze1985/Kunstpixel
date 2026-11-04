# vps_veileder.ps1 - Veileder for domene og VPS til Datafinner-demoen
#
# Hva dette er: en trinnvis veileder du kjører i PowerShell på din egen PC. Den åpner riktige sider,
# sier hva du skal klikke og velge, og sjekker underveis at det du har gjort virker.
#
# Hva den ALDRI gjør:
#   - Den ber ikke om passord, kort, BankID eller API-nøkler. Du gjør innlogging og betaling selv, i nettleseren.
#   - Den leser eller viser ikke din private SSH-nøkkel. Bare den offentlige delen vises.
#   - Den bestiller, betaler eller sletter ingenting. Den kobler seg bare til serveren din når du ber om det i trinn 6.
#
# Bruk:
#   powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1            # fra trinn 1
#   powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1 -Fra 5     # fortsett fra trinn 5
#   powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1 -SelfTest  # sjekk at veilederen selv virker
#
# Valgene dine (domene, IP-adresse, brukernavn, sti til nøkkel) lagres i .scratch\demo\vps-valg.json.
# Det er ikke hemmeligheter, så du kan gi filen til Claude når du er ferdig.

param(
    [int]$Fra = 1,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
$TotalSteg = 7
$Rot = Split-Path -Parent $PSScriptRoot
$ValgFil = Join-Path $Rot '.scratch\demo\vps-valg.json'
$NokkelSti = Join-Path $env:USERPROFILE '.ssh\kunstpixel_demo'

# ---------- hjelpefunksjoner ----------

function Test-Domene([string]$d) {
    return ($d -match '^(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$')
}

function Test-Ipv4([string]$ip) {
    if ($ip -match '^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$') {
        foreach ($del in $Matches[1..4]) { if ([int]$del -gt 255) { return $false } }
        return $true
    }
    return $false
}

function Test-Brukernavn([string]$b) {
    return ($b -match '^[a-z_][a-z0-9_-]{0,31}$')
}

function Les-Valg {
    if (Test-Path $ValgFil) { return (Get-Content $ValgFil -Raw -Encoding UTF8 | ConvertFrom-Json) }
    return [pscustomobject]@{ domene = ''; underdomene = ''; ip = ''; bruker = 'root'; nokkel = ''; dns_ok = $false; ssh_ok = $false }
}

function Lagre-Valg($valg) {
    $mappe = Split-Path -Parent $ValgFil
    if (-not (Test-Path $mappe)) { New-Item -ItemType Directory -Force -Path $mappe | Out-Null }
    ($valg | ConvertTo-Json) | Set-Content -Path $ValgFil -Encoding UTF8
}

function Steg([int]$n, [string]$tittel) {
    Clear-Host
    Write-Host ''
    Write-Host ("=== Trinn {0} av {1}: {2} ===" -f $n, $TotalSteg, $tittel) -ForegroundColor Cyan
    Write-Host ''
}

function Skriv([string]$tekst) { Write-Host $tekst }
function Viktig([string]$tekst) { Write-Host $tekst -ForegroundColor Yellow }
function Bra([string]$tekst) { Write-Host $tekst -ForegroundColor Green }
function Feil([string]$tekst) { Write-Host $tekst -ForegroundColor Red }

function Apne([string]$url) {
    Skriv ("Åpner: " + $url)
    try { Start-Process $url } catch { Viktig ("Fikk ikke åpnet nettleseren. Åpne denne selv: " + $url) }
}

function Ja-Nei([string]$sporsmal) {
    while ($true) {
        $svar = (Read-Host ($sporsmal + ' [j/n]')).Trim().ToLower()
        if ($svar -eq 'j' -or $svar -eq 'ja') { return $true }
        if ($svar -eq 'n' -or $svar -eq 'nei') { return $false }
    }
}

function Vent([string]$tekst = 'Trykk Enter når du er klar') { [void](Read-Host $tekst) }

function Spor-Etter([string]$ledetekst, [scriptblock]$gyldig, [string]$feilmelding, [string]$standard = '') {
    while ($true) {
        $visning = $ledetekst
        if ($standard) { $visning = $ledetekst + ' [' + $standard + ']' }
        $svar = (Read-Host $visning).Trim().ToLower()
        if (-not $svar -and $standard) { $svar = $standard }
        if (& $gyldig $svar) { return $svar }
        Feil $feilmelding
    }
}

# ---------- selvtest (ingen input, ingen nettleser) ----------

if ($SelfTest) {
    $feil = 0
    function Sjekk([string]$navn, [bool]$ok) {
        if ($ok) { Bra ("[OK]   " + $navn) } else { Feil ("[FEIL] " + $navn); $script:feil++ }
    }
    Sjekk 'Test-Domene godtar kunstpixel-demo.no' (Test-Domene 'kunstpixel-demo.no')
    Sjekk 'Test-Domene godtar underdomene' (Test-Domene 'demo.eksempel.no')
    Sjekk 'Test-Domene avviser mellomrom' (-not (Test-Domene 'min side.no'))
    Sjekk 'Test-Domene avviser uten toppdomene' (-not (Test-Domene 'bare-et-navn'))
    Sjekk 'Test-Domene avviser http://-adresse' (-not (Test-Domene 'http://a.no'))
    Sjekk 'Test-Ipv4 godtar 203.0.113.10' (Test-Ipv4 '203.0.113.10')
    Sjekk 'Test-Ipv4 avviser 256.1.1.1' (-not (Test-Ipv4 '256.1.1.1'))
    Sjekk 'Test-Ipv4 avviser 1.2.3' (-not (Test-Ipv4 '1.2.3'))
    Sjekk 'Test-Ipv4 avviser tekst' (-not (Test-Ipv4 'abc'))
    Sjekk 'Test-Brukernavn godtar root og deploy' ((Test-Brukernavn 'root') -and (Test-Brukernavn 'deploy'))
    Sjekk 'Test-Brukernavn avviser ; og mellomrom' ((-not (Test-Brukernavn 'a;b')) -and (-not (Test-Brukernavn 'a b')))
    Sjekk 'ssh finnes' ($null -ne (Get-Command ssh -ErrorAction SilentlyContinue))
    Sjekk 'ssh-keygen finnes' ($null -ne (Get-Command ssh-keygen -ErrorAction SilentlyContinue))
    Sjekk 'Resolve-DnsName finnes' ($null -ne (Get-Command Resolve-DnsName -ErrorAction SilentlyContinue))
    $dns = $false
    try { $dns = [bool](Resolve-DnsName -Name 'norid.no' -Type A -Server 1.1.1.1 -DnsOnly -ErrorAction Stop) } catch { $dns = $false }
    Sjekk 'DNS-oppslag virker (norid.no via 1.1.1.1)' $dns
    Skriv ''
    if ($feil -eq 0) { Bra 'Selvtest bestått. Interaktive trinn er ikke kjørt: de krever deg.'; exit 0 }
    Feil ("Selvtest feilet: {0} feil." -f $feil); exit 1
}

# ---------- trinnene ----------

$valg = Les-Valg

function Trinn1 {
    Steg 1 'Før du starter'
    Skriv 'Dette trenger du, og det tar ca. 30-60 minutter (pluss litt venting på DNS):'
    Skriv '  - Et betalingskort (til VPS-en).'
    Skriv '  - BankID eller annen innlogging hos domeneforhandleren.'
    Skriv '  - Et domenenavn du kan eie. Du trenger bare ett. Demoen legges på et underdomene.'
    Skriv ''
    Viktig 'Denne veilederen ber ikke om passord, kortnummer, BankID eller nøkler. Hvis noe ber deg lime dem inn her, avbryt.'
    Skriv ''
    Skriv 'Sjekker verktøyene på PC-en din:'
    $mangler = @()
    foreach ($v in @('ssh', 'ssh-keygen')) {
        if (Get-Command $v -ErrorAction SilentlyContinue) { Bra ('  [OK]   ' + $v) }
        else { Feil ('  [FEIL] ' + $v + ' finnes ikke'); $mangler += $v }
    }
    if ($mangler.Count -gt 0) {
        Skriv ''
        Viktig 'OpenSSH-klienten mangler. Slå den på i Windows: Innstillinger > System > Valgfrie funksjoner > Legg til > OpenSSH-klient.'
        Skriv 'Kjør veilederen på nytt når det er gjort.'
        exit 1
    }
    Skriv ''
    Vent
}

function Trinn2 {
    Steg 2 'Domene'
    Skriv 'Hvorfor: nettleseren viser hengelåsen (HTTPS) bare for et domenenavn. Med bare en IP-adresse får du en advarsel.'
    Skriv ''
    Skriv 'Hvem kan få et .no-domene (Norid, norid.no):'
    Skriv '  - Organisasjoner med organisasjonsnummer i Enhetsregisteret.'
    Skriv '  - Privatpersoner over 18 år som er registrert i Folkeregisteret.'
    Skriv '  - Alle trenger en norsk postadresse.'
    Skriv 'Norid sier ikke eksplisitt om enkeltpersonforetak (ENK) teller. Det står i vedlegg E til regelverket (lenken åpnes under).'
    Skriv 'Vil du heller ha .com eller annet, hopper du over Norid og bruker en vanlig domeneforhandler.'
    Skriv ''
    Skriv 'Slik gjør du det:'
    Skriv '  1. Finn et ledig navn (første side).'
    Skriv '  2. Velg en domeneforhandler fra Noids liste (andre side) og bestill der. Du betaler og logger inn selv.'
    Skriv '  3. Priser varierer. Sammenlign selv, og se etter hva fornyelsen koster, ikke bare første året.'
    Skriv ''
    if (Ja-Nei 'Åpne Noids sider nå?') {
        Apne 'https://www.norid.no/en/nytt-domenenavn/finn-ledig-domenenavn/'
        Apne 'https://www.norid.no/en/nytt-domenenavn/forhandlerliste/'
        Apne 'https://www.norid.no/en/om-domenenavn/regelverk-for-no/vedlegg-e/'
    }
    Skriv ''
    Vent 'Trykk Enter når domenet er bestilt og du har bekreftelse fra forhandleren'
    $d = Spor-Etter 'Hva er domenet ditt? (f.eks. mittnavn.no)' { param($x) Test-Domene $x } 'Skriv bare domenet, uten http:// og uten mellomrom.' $valg.domene
    $valg.domene = $d
    $u = Spor-Etter 'Hvilket underdomene skal demoen ha?' { param($x) ($x -match '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$') } 'Bare ett ord, små bokstaver, tall og bindestrek.' $(if ($valg.underdomene) { $valg.underdomene } else { 'demo' })
    $valg.underdomene = $u
    Lagre-Valg $valg
    Bra ("Demoen får adressen: https://{0}.{1}" -f $u, $d)
    Skriv ''
    Vent
}

function Trinn3 {
    Steg 3 'SSH-nøkkel (lås og nøkkel til serveren)'
    Skriv 'Hvorfor: du logger inn på serveren med en nøkkel i stedet for passord. Passord kan gjettes, nøkler kan ikke.'
    Skriv 'Nøkkelen har to deler: en privat (blir på PC-en din, deles aldri) og en offentlig (legges på serveren).'
    Skriv ''
    $pub = $NokkelSti + '.pub'
    if (Test-Path $NokkelSti) {
        Bra ('Du har allerede en nøkkel: ' + $NokkelSti)
        Skriv 'Den lages ikke på nytt, så ingenting overskrives.'
    } else {
        Skriv ('Jeg lager nøkkelen her: ' + $NokkelSti)
        Viktig 'Du blir bedt om en passordfrase av programmet ssh-keygen. Velg en lang en og skriv den inn der. Den går ikke gjennom denne veilederen.'
        if (-not (Ja-Nei 'Lage nøkkelen nå?')) { Skriv 'Hoppet over. Kjør trinnet på nytt når du vil.'; return }
        $mappe = Split-Path -Parent $NokkelSti
        if (-not (Test-Path $mappe)) { New-Item -ItemType Directory -Force -Path $mappe | Out-Null }
        & ssh-keygen -t ed25519 -C 'kunstpixel-demo' -f $NokkelSti
        if (-not (Test-Path $pub)) { Feil 'Nøkkelen ble ikke laget.'; exit 1 }
    }
    $valg.nokkel = $NokkelSti
    Lagre-Valg $valg
    Skriv ''
    Skriv 'Dette er den OFFENTLIGE nøkkelen. Den skal du lime inn hos VPS-leverandøren i neste trinn:'
    Skriv ''
    Write-Host (Get-Content $pub -Raw) -ForegroundColor White
    try { Get-Content $pub -Raw | Set-Clipboard; Bra 'Den er kopiert til utklippstavlen.' } catch { Viktig 'Fikk ikke kopiert. Merk teksten over og kopier selv.' }
    Viktig 'Filen uten .pub er den private nøkkelen. Den skal aldri sendes til noen, heller ikke til Claude.'
    Skriv ''
    Vent
}

function Trinn4 {
    Steg 4 'VPS (serveren)'
    Skriv 'Slik maskin trenger Datafinner (målt: selve programmet bruker ca. 88 MB minne):'
    Skriv '  - Operativsystem: Ubuntu 24.04 LTS (eller nyeste LTS).'
    Skriv '  - Størrelse: 1 vCPU og 2 GB minne er mer enn nok. 1 GB kan gå, men er trangt med Docker.'
    Skriv '  - Disk: 20 GB eller mer.'
    Skriv '  - Sted: i Europa (nærmest Norge, og data holdes innenfor EØS).'
    Skriv '  - Må ha en offentlig IPv4-adresse.'
    Skriv '  - SSH-nøkkel: lim inn den offentlige nøkkelen fra trinn 3.'
    Viktig '  - Velg IKKE passord-innlogging, og ikke la leverandøren sende deg et rotpassord på e-post.'
    Skriv '  - Brannmur hos leverandøren (hvis den finnes): åpne bare port 22 (SSH), 80 og 443. Alt annet stengt.'
    Skriv '  - Sikkerhetskopi trenger du ikke. Alt på serveren kan bygges opp igjen fra git.'
    Skriv ''
    Skriv 'Leverandør er ditt valg. Hetzner Cloud er ett eksempel i Europa. Prisene jeg fant var motstridende, så sjekk selv og se på prisen per måned.'
    Skriv ''
    if (Ja-Nei 'Åpne Hetzner Cloud som eksempel?') { Apne 'https://www.hetzner.com/cloud' }
    Skriv ''
    Vent 'Trykk Enter når serveren er opprettet og du ser en IP-adresse'
    $ip = Spor-Etter 'Hva er serverens IPv4-adresse? (fire tall med punktum, f.eks. 203.0.113.10)' { param($x) Test-Ipv4 $x } 'Det ser ikke ut som en IPv4-adresse.' $valg.ip
    $valg.ip = $ip
    $b = Spor-Etter 'Brukernavn for innlogging' { param($x) Test-Brukernavn $x } 'Bruk små bokstaver, tall, understrek eller bindestrek.' $(if ($valg.bruker) { $valg.bruker } else { 'root' })
    $valg.bruker = $b
    Lagre-Valg $valg
    Bra ('Lagret: {0}@{1}' -f $b, $ip)
    Skriv ''
    Vent
}

function Trinn5 {
    Steg 5 'Pek domenet til serveren (DNS)'
    if (-not $valg.domene -or -not $valg.ip) { Feil 'Mangler domene eller IP. Kjør trinn 2 og 4 først.'; exit 1 }
    $navn = '{0}.{1}' -f $valg.underdomene, $valg.domene
    Skriv 'Hvorfor: DNS er telefonkatalogen som sier hvilken server et navn hører til.'
    Skriv ''
    Skriv 'Gjør dette hos domeneforhandleren (finn "DNS", "DNS-innstillinger" eller "navnetjener"):'
    Skriv ('  Legg til en post av typen A:')
    Skriv ('    Navn/vert:  {0}' -f $valg.underdomene)
    Skriv ('    Verdi:      {0}' -f $valg.ip)
    Skriv ('    TTL:        lav verdi, f.eks. 300 (hvis du får velge)')
    Skriv ''
    Skriv ('Hvis forhandleren ber om "hele navnet", er det: ' + $navn)
    Skriv ''
    Vent 'Trykk Enter når posten er lagret, så begynner jeg å sjekke'
    Skriv ''
    Skriv ('Sjekker {0} mot {1} (opptil 10 minutter) ...' -f $navn, $valg.ip)
    $ok = $false
    for ($i = 1; $i -le 40; $i++) {
        try {
            $svar = Resolve-DnsName -Name $navn -Type A -Server 1.1.1.1 -DnsOnly -ErrorAction Stop | Where-Object { $_.Type -eq 'A' }
            $funnet = @($svar | ForEach-Object { $_.IPAddress })
            if ($funnet -contains $valg.ip) { $ok = $true; break }
            Write-Host ('  forsøk {0}: navnet peker på {1}, ikke ennå på {2}' -f $i, ($funnet -join ', '), $valg.ip)
        } catch {
            Write-Host ('  forsøk {0}: ingen svar ennå' -f $i)
        }
        Start-Sleep -Seconds 15
    }
    if ($ok) {
        $valg.dns_ok = $true; Lagre-Valg $valg
        Bra ('{0} peker nå på {1}.' -f $navn, $valg.ip)
    } else {
        Viktig 'Ikke på plass ennå. Det kan ta opptil en time, sjelden mer. Sjekk at posten er av typen A og har riktig IP.'
        Skriv 'Kjør veilederen på nytt med -Fra 5 senere.'
        exit 1
    }
    Skriv ''
    Vent
}

function Trinn6 {
    Steg 6 'Test innlogging på serveren'
    if (-not $valg.ip -or -not $valg.nokkel) { Feil 'Mangler IP eller nøkkel. Kjør trinn 3 og 4 først.'; exit 1 }
    Skriv 'Nå kobler jeg meg til serveren din én gang og kjører bare kommandoen "echo". Ingenting endres på serveren.'
    Skriv 'Første gang spør SSH om du stoler på serveren. Veilederen godtar den nye serveren automatisk (accept-new).'
    Skriv 'Har nøkkelen din en passordfrase, skriver du den inn i SSH-spørsmålet. Den går ikke gjennom veilederen.'
    Skriv ''
    if (-not (Ja-Nei ('Koble til {0}@{1} nå?' -f $valg.bruker, $valg.ip))) { Skriv 'Hoppet over.'; return }
    & ssh -i $valg.nokkel -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new ('{0}@{1}' -f $valg.bruker, $valg.ip) 'echo kunstpixel-ok'
    if ($LASTEXITCODE -eq 0) {
        $valg.ssh_ok = $true; Lagre-Valg $valg
        Bra 'Innlogging virker.'
    } else {
        Feil 'Innlogging feilet.'
        Skriv 'Vanlige årsaker: feil brukernavn (prøv root, ubuntu eller debian), brannmuren har ikke port 22 åpen,'
        Skriv 'eller den offentlige nøkkelen ble ikke lagt inn da serveren ble laget. Det siste krever ny server eller leverandørens konsoll.'
        exit 1
    }
    Skriv ''
    Vent
}

function Trinn7 {
    Steg 7 'Ferdig'
    Bra 'Alt du trenger fra deg er på plass:'
    Skriv ('  Domene:       https://{0}.{1}' -f $valg.underdomene, $valg.domene)
    Skriv ('  Server:       {0}@{1}' -f $valg.bruker, $valg.ip)
    Skriv ('  DNS:          {0}' -f $(if ($valg.dns_ok) { 'peker riktig' } else { 'ikke bekreftet' }))
    Skriv ('  Innlogging:   {0}' -f $(if ($valg.ssh_ok) { 'testet' } else { 'ikke testet' }))
    Skriv ''
    Skriv ('Valgene er lagret i: ' + $ValgFil)
    Skriv 'Filen inneholder ingen hemmeligheter. Neste steg: si til Claude "VPS og domene er klare" og pek på filen.'
    Viktig 'Husk: private nøkkelen (filen uten .pub) og passordfrasen deler du ikke, heller ikke med Claude.'
    Skriv ''
}

# ---------- kjør ----------

# Hoppes over når filen leses inn med punktum (.) av testselen.
if ($MyInvocation.InvocationName -ne '.') {
    if ($Fra -lt 1 -or $Fra -gt $TotalSteg) { Feil ("-Fra må være mellom 1 og {0}" -f $TotalSteg); exit 1 }
    $trinn = @(${function:Trinn1}, ${function:Trinn2}, ${function:Trinn3}, ${function:Trinn4}, ${function:Trinn5}, ${function:Trinn6}, ${function:Trinn7})
    for ($n = $Fra; $n -le $TotalSteg; $n++) {
        & $trinn[$n - 1]
    }
}
