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

## Spørsmålskatalog (versjon 3)

| Rolle | Spørsmål | Filter | Verktøy | Status | Rapporten dekker |
|---|---|---|---|---|---|
| HR og bemanning | Hvem er på jobb nå? | ingen | mangler: oppslag på pågående vakter | mangler | navn, rolle, stasjon, avdeling, telefon, e-post, kontor |
| HR og bemanning | Overtidsbruk i perioden | måned | mangler: overtid per ansatt i periode (`audit_shift_compliance` gjelder ett skift) | mangler | ansatt, avdeling, timer over normal, antall vakter, AML-avvik |
| HR og bemanning | Vaktplan for en dag | dato | mangler: vakter per dato | mangler | navn, rolle, stasjon, avdeling, timer |
| HR og bemanning | Sykefravær per kvartal | år, kvartal | `get_sickness_absence_statistics` | finnes | sykefravær, egenmeldt, legemeldt, vikarbuffer, SSB-sammenligning |
| Økonomi og innkjøp | Økonomi per utstilling | utstilling | `get_exhibition_economy` | finnes | budsjett, innleie, totalkostnad, billettinntekter, katalogsalg, sponsorstøtte, netto, avvik |
| Økonomi og innkjøp | Kostnad for vakter | måned | mangler: kostnad per periode (`calculate_shift_cost` gjelder ett skift) | mangler | avdeling, timer, kostnad etter Virke-tariff |

Verktøynavn er hentet fra `src/kunstpixel/core/mcp_server.py` i hovedmappen (ADR 008, ucommittet). Fire av seks spørsmål har ikke et ferdig verktøy; de må lages før kobling.

## Rapportens fem deler
1. Tittel og formål, én setning.
2. Nøkkeltall, maks 4. Utelates når tall mangler.
3. Fakta, Vurdering og Forslag, hver med kildemerke.
4. Kontroll: punkter som må bekreftes.
5. Grunnlag: kilde, periode og regelversjon (`SPORSMAL.versjon`).

## Åpent
- Personvern: A9 viser personopplysninger med en gang. Greit på syntetiske data. Må revurderes før ekte data.
- Beslutningsrad DEC-005 i `decision_log.md` legges inn når HR-arbeidet i hovedmappen er committet.
