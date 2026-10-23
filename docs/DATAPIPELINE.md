# Datadelen: slik virker den, og slik tar du over

For en hvilken som helst språkmodell eller utvikler som kan Python. Du trenger ikke VS Code, Antigravity, Claude Code eller Codex.
Alt er vanlig Python og CSV. Kommandoene under virker i en terminal på Windows, macOS og Linux, og i Google Colab (se `notebooks/data_pipeline_colab.ipynb`).

**Hovedregel:** `05_data/museum.db` skrives aldri for hånd. Den *bygges* av datafiler, og kan alltid bygges opp igjen likt (samme hash).
Du endrer datafilene eller generatoren, ikke databasen.

## Kartet

```
05_data/kilde/museum_base.db  (frosset grunnlag, rør aldri)  ─┐
05_data/*.csv  (syntetiske datafiler)                          ├─ build_museum_db.py ─▶ 05_data/museum.db  (+ museum.db.sha256)
src/kunstpixel/data/archive_generator.py  (lager noen av CSV-ene) ┘                              │
                                                                                                 ├─ build_demo_db.py ─▶ demokopi (hostes)
                                                                                                 └─ Datafinner (kun lesing) ─▶ API ─▶ (valgfritt) KI-forklaring
```

| Del | Fil | Hva den gjør |
|---|---|---|
| Datafiler | `05_data/*.csv` | Det som bygges inn. Alt har kolonnen `datakilde` som starter med «syntetisk» |
| Generator | `src/kunstpixel/data/archive_generator.py` | Lager CSV-ene for vakter, klokkeslett, fravær, overtid, tariff og arrangementer. Egen tilfeldighet per post, så resultatet er det samme hver gang |
| Bygger | `src/kunstpixel/data/build_museum_db.py` | Grunnlaget + CSV-ene → `museum.db`. Ett `bygg_*`-trinn per datasett, og `SKJEMAVERSJON` |
| Demokopi | `src/kunstpixel/data/build_demo_db.py` | Kopi uten e-post, telefon og fødselsår, med bare tabellene Datafinner bruker |
| Spørringer | `src/kunstpixel/core/db.py` | Alle lesende SQL-spørringer. `mode=ro` |
| Verktøy | `src/kunstpixel/core/mcp_server.py` | Spørringene som verktøy (MCP) |
| Nett og API | `src/kunstpixel/adapters/datafinner.py`, `datafinner_api.py` | Hvitelistet HTTP-API, se `docs/DATAFINNER_API.md` |
| Statusport | `scripts/db_status_gate.py` | Sjekker et nytt bygg før noe slås sammen |

Datafilene som bygges inn (se `CSV_FILER` i `tests/test_data_csv.py`):
`arbeidstid_grenser.csv`, `arkiv_hr_fravaer.csv`, `arkiv_hr_vakt_justering.csv`, `arkiv_hr_vakt_klokkeslett.csv`, `hendelser_tillegg_2026.csv`,
`rapport_regler.csv`, `rolle_sporsmal.csv`, `roller.csv`, `virke_tariff_tillegg.csv`. De tre siste i rekken er skrevet for hånd (ingen generator).

Intern organisasjon (generator `src/kunstpixel/data/org_builder.py`, notatbok `notebooks/intern_org_databygger.ipynb`, skjemaversjon 4):
`mock_interne_ferdigheter.csv` → `org_ferdigheter`, `mock_ansatt_kompetanser.csv` → `org_ansatt_kompetanse`,
`mock_interne_henvendelser.csv` → `interne_henvendelser`, `mock_avvik_hms_tekst.csv` → `hms_avvik_tekst`.
Navn og avdeling lagres ikke på nytt, de hentes fra `hr_ansatte`. Verktøyene `get_employee_skills` og `search_internal_requests`
ligger bare i `core/mcp_server.py`, med vilje ikke i Datafinner eller demokopien (personsaker). Varsler (CASE-013) skjermes alltid.
**Generatoren skriver CSV-ene på nytt hver gang pytest kjører** (`tests/test_org_builder.py`), så rett data i `org_builder.py`, ikke i CSV-ene.

## Kommandoer

Bruk `python` på macOS, Linux og Colab, og `py -3.13` på Windows. Kjør fra rotmappen i repoet.

| Hva | Kommando |
|---|---|
| Statusport (anbefalt først og sist) | `python scripts/db_status_gate.py` (`--uten-pytest` for rask kjøring) |
| Alle tester | `python -m pytest -q` |
| Prøvebygg uten å røre noe | `python src/kunstpixel/data/build_museum_db.py --check` |
| Lag en CSV på nytt | `python src/kunstpixel/data/archive_generator.py --bare-fravaer` (også `--bare-klokkeslett`, `--bare-tariff`, `--bare-overtid`, `--bare-hendelser`) |
| Demokopi | `python src/kunstpixel/data/build_demo_db.py` |
| Datafinner lokalt | `python src/kunstpixel/adapters/datafinner.py` (port 8010) |
| Demomodus lokalt | `python scripts/start_demo.py` (port 8011) |

Avhengigheter: `pip install -r deploy/demo/requirements.txt pytest`. Bruk `mcp==1.29.1`: versjon 2.x virker ikke.

## Reglene

1. **Skriv aldri til `05_data/museum.db` eller `05_data/kilde/museum_base.db`.** Bygget til `museum.db` kjøres bare av Lars (uten `--check`). Du bruker statusporten, som bygger til en midlertidig fil.
2. Alle nye data får en `datakilde`-kolonne som starter med «syntetisk». Ingen ekte personopplysninger.
3. Ingen tall og ingen tekst regnes ut i HTML eller av en språkmodell. Alt kommer fra tabeller og faste regler.
4. Én commit per datasett. Skriv hva som er målt, ikke hva du tror.
5. Ikke si at noe er testet uten at kommandoen er kjørt og viste det. Er den ikke kjørt: skriv `UNTESTED`.
6. Ikke endre designsystemet (`G:\Min disk\Designssystemer\arbeidsflyt`) uten å spørre Lars.

## Oppskrift: legg til eller endre et datasett

1. **Lag dataene.** Ny funksjon i `archive_generator.py` med eget flagg (`--bare-<navn>`), og egen `random.Random("<stabil streng>")`, aldri den globale `random`. Skriv til en CSV i `05_data/` med `datakilde = "syntetisk (archive_generator)"`. For håndskrevne data: rediger CSV-en direkte.
2. **Sjekk CSV-en.** Komma i en tekst må stå i anførselstegn. `python -m pytest tests/test_data_csv.py -q` fanger feil antall felt.
3. **Les den inn.** Ny `bygg_<navn>`-funksjon i `build_museum_db.py`, kalt i `bygg()`, og øk `SKJEMAVERSJON`. Bygget skal feile høyt hvis filen mangler eller har brutte referanser.
4. **Gi tilgang.** Spørring i `core/db.py`, verktøy i `core/mcp_server.py`, og hvitelist i `adapters/datafinner.py`. Verktøyet skal si `mangler` når tabellen ikke finnes. Skal det i demoen: legg tabellen til i `BEHOLD` i `build_demo_db.py`.
5. **Test** mot en temp-bygget database (se `bygget_db` i `tests/test_vakter_tools.py`). Nye verktøy må få eksempelargumenter i `tests/test_build_demo_db.py` (`EKSEMPLER`), ellers feiler testen med vilje.
6. **Bevis.** `python scripts/db_status_gate.py` skal gi KLAR. Be Lars bygge `museum.db` og lag deretter demokopien.

Skal en regel for vurdering og forslag endres: rediger `05_data/rapport_regler.csv` (én rad per regel, `fallback` per spørsmål), bygg på nytt.

## Google Colab

`notebooks/data_pipeline_colab.ipynb` monterer Google Drive, finner repoet, installerer avhengighetene, viser tabellene (kun lesing), gjør et prøvebygg og kjører statusporten.
Notatboken bygger aldri `museum.db` på Drive. Husk: Drive-mappen «Min disk» heter `/content/drive/MyDrive` i Colab.
Status: celleinnholdet er kjørt lokalt, men notatboken er **ikke kjørt i selve Colab**.

## Kjente feller

- **Komma i CSV uten anførselstegn** forskyver eller kutter kolonner stille. Byggeskriptet avviser det ikke. `tests/test_data_csv.py` fanger det.
- **museum.db er en binærfil og kan ikke flettes.** Får to grener ulik museum.db: flett CSV-ene og tekstfilene, bygg på nytt, og ta den nye filen. Aldri velg en av dem på skjønn.
- **DuckDB** blokkeres av Windows (Smart App Control). Den importeres bare inne i `export_all`. Ikke flytt importen til toppen av filen.
- **Google Drive** kan henge `.git/index.lock` og `packed-refs.lock`. Henger `index.lock` i ditt eget arbeidstre og ingen git-prosess kjører, kan den fjernes. Rør aldri låser i en annens mappe.
- **Enkeltfiler kan ikke monteres fra Drive inn i Docker** (`G:`). Test Docker fra en vanlig mappe (testskriptet gjør det).
- **Formatterhooker** kan fjerne en `import` som ikke er brukt ennå. Legg til import og bruk i samme redigering, og kjør testene.
- Skriv filer med et filverktøy, ikke via `\n` i shell. PowerShell 5.1 trenger BOM i `.ps1`-filer med norske tegn.

## Åpne punkter i dataene
- G7: lav bemanning per dag (snitt 8,9 vakter). Foreslått, ikke gjort. Krever Lars' valg.
- Regeltekstene i `rapport_regler.csv` er skrevet av Antigravity, og kildene de viser til («Bemanningsplan 2026», «Driftsplan 2026», «Økonomireglement») finnes ikke i repoet. Må godkjennes eller skrives om.
- `museum.db` må bygges på nytt etter at `datakilde` i `rapport_regler.csv` ble rettet (se `HANDOFF`).
