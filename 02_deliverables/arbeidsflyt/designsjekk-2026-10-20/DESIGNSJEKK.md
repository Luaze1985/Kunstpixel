# Designsjekk: Datafinner
*2026-10-20 · Grunnlag: `index.html` regelversjon 7, designsystemet Arbeidsflyt (`G:\Min disk\Designssystemer\arbeidsflyt`) · Testet i nettleserpanelet på 1100 × 800 (PC) og 375 × 812 (mobil)*

## Kort fortalt
Strukturen følger Arbeidsflyt godt. Rapporten har alle 5 delene, tallene kommer fra databasen, og kontrast og etiketter er i orden.

**Én feil stopper en demo:** brede tabeller kuttes til høyre. På mobil forsvinner fem av ni kolonner, og de kan ikke rulles frem. Feilen ligger i designsystemet selv, ikke i Datafinner.

## Funn, sortert etter alvor

| # | Alvor | Funn | Bevis | Forslag |
|---|---|---|---|---|
| 1 | **Blokkerer demo** | Brede tabeller kuttes til høyre. På mobil vises bare Start, Slutt, Navn og Stilling. På PC (1100 px) får skallet sidelengs rulling (1052 px synlig av 1360). Bryter Datatabell-regelen «Brede tabeller ruller i sin egen ramme» og Trepanel-regelen «ingen sidelengs rulling ved 320 px». | `mobil-tabell-kuttet.jpg`, `pc-tabell-kuttet.jpg`. Målt: `.af-table-wrap` 928 px bred i en 306 px kolonne. | **Rotårsak i `bundle.css`:** `.af-report-block` bruker `grid-template-columns: 110px 1fr` og `1fr` på mobil. `1fr` krymper ikke under tabellens bredde. Rett i designsystemet til `minmax(0, 1fr)` (begge regler), og kopier til `af.css`. |
| 2 | Høy | «Stilling %» viser 1, 0,4 og 0,8. Det er en andel, ikke prosent. | `pc-rapport-arbeidstid.jpg` | Gang med 100 i `db.py`, ikke i HTML (regel: ingen tall regnes ut i HTML), eller endre etiketten til «Stillingsandel». |
| 3 | Høy | Kildemerkene bruker egne ord: «Fra museum.db», «Syntetiske data i museum.db», «Syntetisk regel i museum.db», «Henter» og «Ufullstendig tariff». Arbeidsflyt har fem faste ord: Bekreftet, AI-forslag, Systemforslag, Bør verifiseres og Mangler. | `index.html` (FRA_DB, SYNTETISK, `settRegel`) | Vurdering og forslag fra `rapport_regler` er **Systemforslag** og blir Bekreftet først når en person godtar dem. Fakta fra databasen får Bekreftet eller Bør verifiseres. «Syntetisk» vises én gang som et tydelig varsel øverst (se 5), ikke som kildemerke. |
| 4 | Middels | Rapporten kan bli «Bekreftet» selv om vurderingen er et regelforslag ingen har godtatt. Kontroll-boksene gjelder bare fakta («Tallene stemmer …»). | `oppdaterStatus()` teller ikke `.af-source.system` | Legg til ett kontrollpunkt «Vurdering og forslag er godtatt», og la Systemforslag holde rapporten som Utkast til det er krysset av. |
| 5 | Middels | Det står ingen steder at **alle HR-data er syntetiske**. Ved demo eller hosting kan seere tro at navn, telefonnumre og e-post er ekte personer. | Forside og rapport | Bruk ett `Varsel` (info) øverst på alle sider: «Øvingsdata: alle ansatte, vakter og tall er syntetiske.» |
| 6 | Middels | Forsidekortene viser `/hr` og `/okonomi`. Det er agent-kommandoer som ikke betyr noe for en demo-seer, og det bryter regelen «ingen metatekst». | `pc-forside-1100.jpg` | Vis bare navn, beskrivelse og antall spørsmål. Kommandoen kan stå i høyre panel. |
| 7 | Lav | Tom tabell viser «Ingen rader.» Tomtilstand krever at teksten sier hvorfor og gir én handling. | `index.html` (`Ingen rader.`) | For eksempel «Ingen vakter denne datoen.» med handlingen «Velg en annen dato». |
| 8 | Lav | `lang="no"`. | `<html>` | Bruk `nb`. Skjermlesere velger da riktig uttale. |
| 9 | Lav | Tabellene mangler `scope="col"` og `<caption>`, og tabellrammen kan ikke nås med tastatur når den ruller. | Målt i nettleseren | Legg til `scope`, en skjult `caption` og `tabindex="0"` med `aria-label` på `.af-table-wrap` (etter funn 1). |
| 10 | Lav | Vurdering og forslag fylles inn etter at fokus har flyttet seg til rapporten, og endringen leses ikke opp. | `settRegel` | Legg `aria-live="polite"` på vurderingsblokken, eller flytt fokus etter at regelen er lastet. |

## Det som er i orden
- **Rapportstruktur:** alle 5 delene (tittel og formål, maks 4 nøkkeltall, Fakta/Vurdering/Forslag, Kontroll, Grunnlag).
- **Fakta, vurdering og forslag** er skilt, og vurderingen kommer fra faste regler, ikke fra en LLM.
- **Kontrast:** ingen tekst under 4,5:1 (målt på alle synlige tekstelementer).
- **Etiketter:** alle felt har synlig label, og alle knapper har navn.
- **Fokus:** synlig fokusmarkering (skygge i `--blue-shadow`). Rollekort og spørsmål er ekte knapper.
- **Feil:** feilmeldinger sier hva som mangler («Fyll inn dato for å fortsette») og flytter fokus til feltet.
- **Mobil:** ett felt per rad, og menyen blir en nedtrekksliste med «Meny» som label.
- **Titler** er 1–3 ord, og filtrene står i én rad.
- **CSS:** lokal `af.css` er nøyaktig tokens pluss `bundle.css`, uten egne avvik.

## Ikke testet
- Skjermleser (NVDA) og ekte tastaturgjennomgang med Tab og Shift+Tab. Sjekkene over er målt med JavaScript.
- Zoom 200 % på PC. Det gir omtrent mobilbredde, så funn 1 gjelder der også.
- axe, WAVE og Nu HTML Checker. Kjør dem etter at funn 1 er rettet.
- Brukertest med en person som ikke har laget løsningen (Trepanel-sjekklisten punkt 10).

## Anbefalt rekkefølge før demo
1. Funn 1 (rettes i designsystemet, deretter kopi til `af.css`).
2. Funn 5 og 2.
3. Funn 3 og 4 sammen, siden begge gjelder merkingen.
4. Resten.

---

## Status etter retting (2026-10-20)
Funn 1, 2 og 5 er rettet og målt på nytt (1100 px og 375 px). Funn 3, 4 og 6–10 er ikke rettet.

| # | Status | Hva som ble gjort | Bevis |
|---|---|---|---|
| 1 | **Rettet** | `.af-report-block` bruker nå `minmax(0, 1fr)` i `bundle.css` (designsystemet), i `af.css` (kopi i Datafinner) og som en note i `DESIGN.md`. I tillegg brytes lange strenger uten mellomrom (verktøykallet og Grunnlag) med `overflow-wrap: anywhere`. De strakk skallet til 1360 px, og det ble funnet først etter den første rettingen. | PC: skall 1052 av 1052 px og ingen sidelengs rulling, målt på alle fire rapportene (Arbeidstid, Vaktplan, Sykefravær, Vaktkostnad). Mobil: tabellrammen er 304 av 928 px og ruller, alle 9 kolonner nås, og siden er 375 av 375 px. Bilder: `etter-pc-tabell.jpg`, `etter-mobil-tabell-utrullet.jpg`. |
| 2 | **Rettet** | `query_working_hours` i `db.py` gir stillingsprosent som prosent (40) i stedet for andel (0,4). Test lagt til. | `etter-pc-tabell.jpg` viser 100, 40 og 80. |
| 5 | **Rettet** | `Varsel` (info) «Øvingsdata: Alle ansatte, vakter og tall i Datafinner er syntetiske.» øverst i midtfeltet, én gang per side. | `etter-pc-forside.jpg`, `etter-mobil-toppen.jpg` |

**Nytt funn under testingen (lav):** forsiden er tom i et øyeblikk mens rollene hentes fra databasen. Vis «Henter roller …» i den tiden.

**Merk:** `bundle.css` og `DESIGN.md` ligger i `G:\Min disk\Designssystemer\arbeidsflyt`. Det er ikke et git-repo, så endringen er ikke versjonert. Andre prosjekter som kopierer `bundle.css` får rettingen først når de kopierer den på nytt.
