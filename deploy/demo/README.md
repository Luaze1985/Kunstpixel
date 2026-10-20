# Datafinner-demo på en VPS: kjørebok

Slik legger du Datafinner ut som demo med innlogging per person. Du gjør hvert steg selv. Ingenting her går gjennom Claude, og ingen hemmeligheter ligger i git.

```
Nettleser ──HTTPS──▶ Caddy (hengelås + innlogging) ──▶ Datafinner (demomodus, demokopi av databasen)
                     åpen: port 80 og 443               ingen åpen port, nås bare fra Caddy
```

## Før du starter
- Du har kjørt `scripts\vps_veileder.ps1`, og `.scratch\demo\vps-valg.json` viser domene, IP, brukernavn og at DNS peker riktig.
- Du har gått gjennom `.scratch\demo\navneliste.md` og regeltekstene i `05_data\rapport_regler.csv`.
- Docker Desktop kjører på PC-en.

Under: `<bruker>`, `<ip>` og `<nokkel>` er verdiene fra `vps-valg.json`. `<nokkel>` er stien til din private nøkkel, vanligvis `C:\Users\larse\.ssh\kunstpixel_demo`.

## 1. På PC-en: bygg bildet og test det
```powershell
docker build -f deploy/demo/Dockerfile -t kunstpixel-datafinner:demo .
powershell -ExecutionPolicy Bypass -File scripts\test_demo_container.ps1
```
Testen starter alt lokalt (bare på din PC), sjekker innlogging og at filverktøyene er stengt, og rydder etterpå.

## 2. Send filene til serveren
```powershell
ssh -i <nokkel> <bruker>@<ip> "mkdir -p kunstpixel-demo"
scp -i <nokkel> deploy/demo/compose.yaml deploy/demo/Caddyfile deploy/demo/bruker.sh deploy/demo/server-oppsett.sh deploy/demo/.env.example <bruker>@<ip>:kunstpixel-demo/
```

## 3. På serveren: førstegangs oppsett (én gang)
```powershell
ssh -i <nokkel> <bruker>@<ip>
```
Da er du inne på serveren. Kommandoene under skrives der:
```bash
cd kunstpixel-demo
sudo bash server-oppsett.sh
```
Skriptet oppdaterer systemet, installerer Docker og brannmur (bare SSH, 80 og 443). Det spør før det slår av passord-innlogging. Svarer du ja, test i et nytt vindu at nøkkelen fungerer før du lukker det første.

## 4. Send bildet til serveren
Tilbake på PC-en:
```powershell
cmd /c "docker save kunstpixel-datafinner:demo | ssh -C -i <nokkel> <bruker>@<ip> docker load"
```
(`cmd /c` må brukes: PowerShells egen rør ødelegger binære data.) Bildet inneholder demokopien av databasen, ikke museum.db.

## 5. På serveren: sett opp og start
```bash
cd kunstpixel-demo
cp .env.example .env
nano .env                 # sett DEMO_DOMAIN til f.eks. demo.mittnavn.no, lagre med Ctrl+O, Enter, Ctrl+X
chmod +x bruker.sh
./bruker.sh ola           # lag en bruker. Du skriver passordet to ganger (vises ikke).
docker compose up -d --no-build
docker compose ps         # begge skal stå som "running" / "healthy"
docker compose logs caddy # se at Caddy har hentet sertifikat
```
Åpne `https://<underdomene>.<domene>`. Du skal få et påloggingsvindu, og så Datafinner.

## Brukere
```bash
./bruker.sh ola            # legg til
./bruker.sh --fjern ola    # fjern, gjelder med en gang
./bruker.sh --liste        # hvem har tilgang
```
Gi passordet til personen direkte, ikke i chat. Passord kan ikke hentes frem igjen. Glemt passord: fjern og legg til på nytt.

## Oppdatere demoen
Gjenta steg 1 (bygg og test), steg 4 (send bildet), og kjør så på serveren:
```bash
docker compose up -d --no-build
```

## Stoppe og rydde
```bash
docker compose down        # stopper, beholder sertifikatene
docker compose down -v     # stopper og sletter også sertifikatene
```
Slett VPS-en hos leverandøren når du er ferdig, ellers fortsetter regningen.

## Når noe feiler
| Symptom | Mulig årsak | Gjør dette |
|---|---|---|
| Nettleseren sier «ikke sikker» eller ingen kontakt | DNS peker ikke riktig, eller port 80/443 er stengt hos leverandørens brannmur | `nslookup <domene>` skal gi serverens IP. Åpne 80 og 443 i leverandørens brannmur. `docker compose logs caddy` |
| 502 Bad Gateway | Datafinner er ikke frisk | `docker compose ps`, `docker compose logs datafinner` |
| Caddy starter ikke | Ingen brukere i `brukere.caddy` | `./bruker.sh <navn>` |
| `docker load` feiler eller henger | Brukte PowerShell-rør i stedet for `cmd /c` | Bruk kommandoen i steg 4 slik den står |
| Låst ute av SSH | Passord slått av uten at nøkkelen virket | Bruk leverandørens nettkonsoll |

## Hva som er testet og ikke
- **Testet (Docker Desktop på Windows, 24 sjekker i `scripts\test_demo_container.ps1`):**
  - Bildet bygger, og containerne starter slik de gjør på serveren: bare compose-filene ligger der, og bildet er lastet inn på forhånd (`--no-build`).
  - Innlogging: 401 uten, 401 med feil passord, 200 med riktig. Gjelder også API-et.
  - `les_fil` og `grep_mappe` gir 400, og `/sok.html` gir 404.
  - Sikkerhetshodene er på plass, og Server-hodet er fjernet.
  - Datafinner har ingen åpen port, kjører ikke som root og har skrivebeskyttet filsystem. `/app` inneholder bare `src` og `data`.
  - Demobasen har ingen e-post, telefon eller fødselsår.
- **Fanget av testen:** `mcp` 2.x brøt demoen. Versjonene er nå låst i `requirements.txt`. Ikke oppgrader uten å kjøre testen.
- **Ikke testet (krever en ekte server):** `server-oppsett.sh`, `bruker.sh`, sertifikat fra Let's Encrypt, `docker save`-overføring over SSH og oppdatering. Syntaksen er sjekket, men skriptene er ikke kjørt på Ubuntu.
- **Merk om testmiljøet:** Docker Desktop kan ikke montere enkeltfiler fra Google Drive (`G:`). Testen kopierer derfor compose-filene til en vanlig mappe. På serveren er det ikke noe problem.
- **Mangler:** grense for antall innloggingsforsøk. Vanlig Caddy har ingen. Legg til fail2ban hvis demoen blir stående lenge.
