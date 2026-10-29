# Levering: H5-bestilling og HR-realisme fra Colab (`Untitled22.ipynb`)

**Dato:** 2026-10-29  
**Kilde:** `G:\Min disk\Colab Notebooks\Untitled22.ipynb`  
**Status:** Inntatt i innboks og behandlet.

---

## 1. Hva dette er
Denne mappen inneholder den komplette Google Colab-notatboken der H5-bestillingen (syntetisk fyll for Kunstpixel om myndighetskontakt, rapportering, tidsbruk og 17-årshistorikk 2010–2026) samt en utvidelse av HR- og onboardingdata ble utviklet og testet.

Notatboken inneholder:
1. Skrevne fritekster for `myndighetskontakter.yaml` (Arbeidstilsynet, Mattilsynet, Brann- og redningsetaten, Kommunen, Datatilsynet).
2. Tilsynsbesøksrutiner fordelt på `forberedelse`, `gjennomforing` og `etterarbeid`.
3. 17 års `hendelse`- og `laerdom`-tekster (2010–2026) tilpasset årlige hendelser og pandemi.
4. Et syntetisk datasett `hr_data_realisme.yaml` med onboarding, kompetansematrise og HMS-opplæring for museet.

---

## 2. Inspeksjon og avvik i råkjøringen
En gjennomgang av koden i notatboken avdekket:
- **`FAST_FELT_ENDRET` (celle 20 & 21):** Colab-modellen kjørte `random.choice` som overstyrte de faste avviksfristene (endret fra 14 dager / 24 timer til 21 dager / 12 timer) og overstyrte faste timer per oppgave slik at summen for 2026 ikke lenger ga 287 timer.
- **`KOPIERT_TEKST` (celle 12 & 13):** Enkelte søk-og-erstatt-funksjoner fylte flere felter i rapportmaler og arbeidsoppgaver med identiske standardsetninger.

---

## 3. Behandling og videreforedling
Råleveransen ble ikke forkastet, men videreforedlet:
1. Alle faste felt, summer (287t for 2026) og HMS-frister (14 dager gult / 24 timer rødt) er låst tilbake til autoritativ kilde i `leveranse.py`.
2. Tekstene fra Colab er bevart ordrett der de var unike, og utvidet med unike fagsetninger der Colab hadde brukt duplikater.
3. Dataene skrives ut som autoritative YAML-filer i `05_data/governance/`, som 7 CSV-filer i `05_data/`, og bygges inn i `museum.db` via `build_museum_db.py` (skjemaversjon 5).
