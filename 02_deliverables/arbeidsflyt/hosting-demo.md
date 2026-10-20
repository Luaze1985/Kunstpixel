# Datafinner som hostet demo: status og kjørebok
*2026-10-20 · Plan: VPS med container og innlogging foran. Ingenting er hostet ennå.*

## Hva som er gjort

| Del | Fil | Status |
|---|---|---|
| Demomodus i serveren | `src/kunstpixel/adapters/datafinner.py` | Ferdig og testet. `DATAFINNER_DEMO=1` fjerner `grep_mappe`, `les_fil` og `/sok.html`. |
| Sikkerhetshoder og generelle feilmeldinger | samme | Ferdig og testet. Siden fungerer med den strenge innholdspolicyen (ingen brudd målt i nettleseren). |
| Demokopi av databasen | `src/kunstpixel/data/build_demo_db.py` | Ferdig og testet. 20 av 35 tabeller beholdes. Fødselsår, e-post og telefon er tatt ut. |
| Lokal start i demomodus | `scripts/start_demo.py` | Ferdig. Porten er 8011. |
| Veileder for domene og VPS | `scripts/vps_veileder.ps1` | Selvtest og testsele består. Trinn 3 (lage nøkkel) og 6 (ekte SSH) er ikke kjørt: de krever deg. |
| Docker, Caddy med innlogging, brukerskript, serveroppsett, kjørebok | `deploy/demo/` | Ferdig. Testet i Docker lokalt (24 sjekker, `scripts/test_demo_container.ps1`). `server-oppsett.sh` og `bruker.sh` er ikke kjørt på en ekte server. |
| Åpent API og valgfritt KI-lag | `src/kunstpixel/adapters/datafinner_api.py`, `src/kunstpixel/core/llm.py`, `docs/DATAFINNER_API.md` | Ferdig. Faste rapporter og verktøyskjema testet i Docker. KI-laget er av som standard og testet mot en falsk KI-server (OpenAI- og Claude-format), **ikke mot en ekte leverandør**. |
| Datadel for annen Python-modell og Colab | `docs/DATAPIPELINE.md`, `notebooks/data_pipeline_colab.ipynb` | Ferdig. Cellene er kjørt lokalt, ikke i selve Colab. |
| Utrulling til VPS | `deploy/demo/README.md` | Gjenstår, og må gjøres av deg etter veilederen. |

## Slik bruker du det

Se demoen lokalt, slik den vil se ut hostet:
```powershell
py -3.13 scripts/start_demo.py
```
Åpne http://127.0.0.1:8011. Du skal ikke se kolonnene Telefon og E-post, og `/sok.html` gir «Finnes ikke».

Skaff domene og VPS (du gjør innlogging og betaling selv):
```powershell
powershell -ExecutionPolicy Bypass -File scripts\vps_veileder.ps1
```
Du kan stoppe når du vil og fortsette med `-Fra <trinn>`. Valgene lagres i `.scratch/demo/vps-valg.json` uten hemmeligheter.

Gå gjennom navnene i demokopien: `.scratch/demo/navneliste.md` (lages av `build_demo_db.py --navneliste <fil>`).

## Det som må avgjøres av deg før noe går ut på nett

1. **Navnene.** Programmet kan ikke vite om et oppdiktet navn tilhører en ekte person. Gå gjennom listen.
2. **Regeltekstene** i `05_data/rapport_regler.csv`. De er skrevet av Antigravity, og kildene de viser til (for eksempel «Bemanningsplan 2026») finnes ikke i repoet.
3. **Datoene.** Vaktdata slutter 2026-12-31, og mandager viser bare 2 vakter. Det ser ut som en feil i en demo.
4. **Hvem får logge inn.** Planen er ett brukernavn per person i Caddy.

## Det demokopien ikke dekker
- Telefon og e-post er fjernet, men navn, kjønn, avdeling, lønnstrinn og vakter ligger der. Alt er syntetisk.
- Kunstnernavn og verk (Munch m.fl.) er ekte, offentlig informasjon.
- Demokopien er ikke i git. Den bygges fra `museum.db` og ligger i `05_data/demo/` (ignorert).

## Kjente begrensninger
- Serveren har ingen innlogging selv. Den skal alltid ligge bak noe som krever det.
- Serveren har ingen grense for antall forespørsler. Det bør settes i Caddy.
- Grenene fra spesifikasjonen (én verktøyliste, delt `db.py`) er ikke slått sammen. Demomodus er lagt til i dagens `datafinner.py`, og må flettes med punkt 1 senere (ventet liten konflikt rundt `VERKTOY`).
