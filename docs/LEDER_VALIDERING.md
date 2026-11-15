# Validering av lederens Datafinner

Målet er at en museumsleder skal åpne Datafinner, stille et spørsmål med vanlige ord og finne kilden til svaret. Rapporter og råtabeller skal være tilgjengelige uten å fylle startsiden. Testene bruker den syntetiske databasen og skriver ikke til den.

## Metode

- [SQLite](https://www.sqlite.org/pragma.html) krever en egen `foreign_key_check`; `integrity_check` finner ikke fremmednøkkelbrudd. Begge kjøres mot aktiv database i lesemodus.
- [dbt sine generiske datatester](https://docs.getdbt.com/docs/build/data-tests) gir mønsteret for unik nøkkel, ikke-tom nøkkel, tillatte verdier og relasjoner. Testene her er direkte SQLite-spørringer i pytest, uten en dbt-installasjon.
- [Playwrights nettlesertester](https://playwright.dev/python/docs/writing-tests) kontrollerer det brukeren ser og kan gjøre: spørsmål først, lite menystøy, rapporter, tabeller, mobilvisning og et simulert KI-svar. Den simuleringen tester flyten uten å sende data til en ekstern modell.

## Kjør valideringssettet

```powershell
py -3.13 -m pip install -e ".[ui-test]"
py -3.13 -m playwright install chromium
.\scripts\valider_leder.ps1
.\start_claude.cmd --version
```

Valideringsskriptet stopper hvis Playwright mangler, en test feiler eller aktiv database ikke samsvarer med validert bygg. Hele prosjektets testport er `py -3.13 -m pytest -q`. Nettlesertestene starter sin egen server på en tilfeldig lokal port og trenger ingen kjørende demo. `start_demo.cmd` åpner lederen rett i «Spør om data» med Claude hvis tilgjengelig; `start_demo.cmd -UtenKI` viser samme data uten KI.

## Siste manuelle prøverunde

1. Start `start_demo.cmd` og kontroller at «KI konfigurert» vises. Spør: «Hva er nettoresultatet for utstillingen KP-EXH-2026-FOKUS-2? Oppgi kilde.» Fasit i aktiv database er 657 556 kr i `utstilling_okonomi`. Etter et vellykket svar skal siden vise «KI tilkoblet». Kontroller svaret og kilden i siden.
2. Åpne «Tabeller», velg `utstilling_okonomi` og finn raden. Gå tilbake til «Spør om data».
3. Start `start_claude.cmd`, spør om Stine Haugen (`KP-ANS-155`, ingen personalmappe) og Anja Eriksen (to ansatte: `KP-ANS-047` og `KP-ANS-115`). Kjør `/sjekk` etter hvert svar.

En grønn status fra `/api/status` viser at en modell er konfigurert; den beviser ikke at modellen svarte på et spørsmål. Trinn 1 og 3 er derfor egne live-kontroller. Statusporten slipper gjennom de kjente syntetiske varslene og stopper ved nye feil.

## Gjennomført kontroll 15.11.2026

- `scripts/valider_leder.ps1`: 18 tester bestått. Aktiv `museum.db` hadde samme SHA-256 som validert bygg; 0 feil og 2 kjente syntetiske varsler.
- Hele `pytest`-pakken: exitkode 0, med 9 tidligere hoppede tester og 2 forventede feil (`xfail`).
- Datafinner med ekte Claude: spørsmål om `KP-EXH-2026-FOKUS-2` ga 657 556 NOK og kilde `get_exhibition_economy`. Nettlesertestene kontrollerte i tillegg startvisning, svar, kildepanel, tabeller og mobil.
- Datafinner med `-UtenKI`: `/api/status` viste `llm: false`; katalogen var fortsatt tilgjengelig med 61 tabeller.
- `start_claude.cmd` i en ny sesjon: Stine `KP-ANS-155` fikk riktig svar om manglende personalmappe; `/sjekk` bekreftet 4 av 4 påstander. Anja Eriksen fikk begge ID-ene `KP-ANS-047` og `KP-ANS-115`; `/sjekk` bekreftet 2 av 2 påstander.

Nettlesertestene simulerer KI-svar for å være raske og stabile. De tre konkrete live-spørsmålene over kontrollerer den faktiske Claude-koblingen; nye spørsmål kan fortsatt gi andre svar og bør vurderes med `/sjekk`.
