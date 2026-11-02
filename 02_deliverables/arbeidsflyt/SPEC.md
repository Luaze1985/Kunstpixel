# Datafinner v1 — spec

Internt verktøy til eget bruk for HR, HRM og ERP. Ikke publikumsrettet. Design først: ingen kobling til databasen ennå.

**Flyttype:** Innsikt i trepanel. Venstre: områder og faste spørsmål. Midten: spørsmål, kort svar, rapport. Høyre: verktøykall og kilde.

## Regler
- Ingenting vises før et spørsmål er stilt. Spørsmålet avgjør hva som vises (A1).
- Faste spørsmål, maks 2 lukkede filtre, ett verktøykall per spørsmål. Ingen fritekst velger gren.
- Kort svar er én setning eller ett tall. «Lag rapport» gir full rapport med fem deler. Alle detaljer, også navn og kontaktinfo, står i rapporten (A9, A10).
- Rapporten står som «Utkast» til kontrollpunktene er bekreftet.
- Ingen oppdiktede tall i mockupen. Tomtilstand der data skal komme.

## Forside og roller (versjon 3)
Forsiden er en oppgaveliste med ett kort per rolle. Kortet viser rollenavn, merknad, antall spørsmål og «X av Y verktøy finnes». Ingen data vises på forsiden. Inne i en rolle ligger spørsmålene som oppgavekort, og venstre meny bytter fra roller til rollens spørsmål.

| Rolle | Trigger | Spørsmål |
|---|---|---|
| HR og bemanning | /hr | Hvem er på jobb nå? · Vaktplan for en dag · Overtidsbruk i perioden · Sykefravær per kvartal |
| Økonomi og innkjøp | /okonomi | Økonomi per utstilling · Kostnad for vakter |

**Avklart:** HR og bemanning og Økonomi og innkjøp er ført inn som roller K og L i `03_team/team_roster.md`. Triggerne `/hr` og `/okonomi` er foreslått og kan endres. Driftsansvarlig og Museumsdirektør har ingen spørsmål i v1 og vises ikke.

## Spørsmålskatalog (versjon 5, koblet til museum.db)

Regel: alle svar kommer fra museum.db. Det databasen ikke har, vises som «Mangler», aldri utledet.

| Rolle | Spørsmål | Filter | Verktøy | Mangler i databasen |
|---|---|---|---|---|
| HR og bemanning | Hvem har vakt i dag? | ingen | `get_staff_on_shift` | klokkeslett for vakter |
| HR og bemanning | Vaktplan for en dag | dato | `get_shifts_for_date` | klokkeslett for vakter |
| HR og bemanning | Arbeidstid i perioden | måned | `get_working_hours_report` | overtidsgrense som tall |
| HR og bemanning | Sykefravær i kultursektoren | år, kvartal | `get_sickness_absence_statistics` | museets eget sykefravær (bare SSB-tall finnes) |
| Økonomi og innkjøp | Økonomi per utstilling | utstilling, lukket liste | `get_exhibition_economy`, `list_exhibitions_with_economy` | – |
| Økonomi og innkjøp | Kostnad for vakter | måned | `get_shift_cost_for_period` | tariff for lønnstrinn over 65, kveldssats |

Vurdering vises bare når databasen har tekst (utstillingens avviksforklaring). Forslag står som «Mangler». Rapporten er derfor «Utkast» til databasen er utvidet.

**Neste: utvid databasen** (byggeskriptet, kjøres av Lars): klokkeslett for vakter, overtidsgrenser som tall, roller, og museets eget fravær.

## Rapportens fem deler
1. Tittel og formål, én setning.
2. Nøkkeltall, maks 4. Utelates når tall mangler.
3. Fakta, Vurdering og Forslag, hver med kildemerke.
4. Kontroll: punkter som må bekreftes.
5. Grunnlag: kilde, periode og regelversjon (`SPORSMAL.versjon`).

## Åpent
- Personvern: A9 viser personopplysninger med en gang. Greit på syntetiske data. Må revurderes før ekte data.
- Beslutningsrad DEC-005 i `decision_log.md` legges inn når HR-arbeidet i hovedmappen er committet.
