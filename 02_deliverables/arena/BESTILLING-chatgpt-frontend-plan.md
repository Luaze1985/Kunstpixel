# Bestilling til ChatGPT: frontend-plan for hele Kunstpixel-appen

*Fra: Lars (Kunstpixel) · Dato: 2026-10-31 · Leveranse: én plan i Markdown, ingen kode*

## 1. Oppdraget
Lag en plan for frontend til hele appen. Hver rolle i museet åpner appen, trykker på knapper og får svar.
Designet er allerede bestemt, og mange sider finnes. Jobben er å samle dem til én app, fylle hullene og
bestemme hvor LLM skal brukes.

Hovedeksempel: ledelsen trykker «Hvem har hatt vakt?», ser hvem som har jobbet helger, finner kvalifisert
kompetanse blant egne ansatte og innleide, vurderer kandidatene og tar kontakt.

## 2. Ikke design på nytt
- **Designsystemet er Arbeidsflyt** (`af.css`). Stegmeny til venstre, hovedfelt i midten, hjelpepanel
  til høyre. Komponenter som Oppgavekort, Datatabell, Nøkkeltall, Filterrad, Rapportseksjon, Utfall,
  Kildemerke og Statusmerke finnes allerede. Bruk dem. Ikke lag nye farger, fonter eller komponenter.
- **Sidene som finnes på Datafinner (port 8010):** `index.html` (start), `sok.html` (søk og rapporter
  med valgfri KI-forklaring) og `arena.html` (19 øvelsescaser). Planen skal si hva som beholdes, hva som
  flyttes og hva som er nytt. Ikke foreslå å skrive dem om fra bunnen.
- **API-et finnes:** `/api/verktoyskjema`, `/api/verktoy`, `/api/rapport`, `/api/forklar`, `/api/arena/*`.

## 3. Hovedregelen: to lag i hvert svar
Hver knapp hører til ett av to lag. Planen skal merke hver eneste knapp med laget sitt.

| Lag | Hva det gjør | Hvordan det vises |
|---|---|---|
| **Rapport (deterministisk)** | Henter tall og lister fra verktøyene. Samme input gir alltid samme svar. | Fakta, regel, vurdering. Merket «Bør verifiseres» eller «Systemforslag». |
| **Handling (LLM på toppen)** | Bruker rapporten til å gjøre noe: forklare, sammenligne kandidater, skrive utkast til e-post eller SMS, foreslå bemanning. | Alltid merket «AI-forslag». Står ved siden av rapporten, aldri i stedet for den. |

Regler for LLM-laget, som allerede gjelder i koden:
- LLM-en får bare den ferdige rapporten, aldri databasen.
- Navn, e-post, telefon og fødselsår fjernes før noe sendes til en ekstern modell.
- Tallkontroll: et tall i LLM-teksten som ikke finnes i rapporten, gir en synlig advarsel.
- Ingenting sendes, lagres eller blir «Bekreftet» før et menneske har trykket på det.
- Umerket data regnes som ekte og får aldri ekstern KI (fail-closed). Da vises bare rapporten.
- LLM er av som standard. Appen må virke fullt ut uten den.

## 4. Roller
Museumsdirektør, driftsansvarlig, avdelingsleder, HR/HMS, kafeansvarlig, kommunikasjon og museumsvert.
Hver rolle ser bare knappene den har lov til. Museumsverten ser for eksempel aldri personalmapper.

## 5. Verktøy appen kan bygge på
Vakter per dato, kompetansetelling, kioskforslag, evaluering av forslag mot KI-feller, hviletidsrevisjon
(AML § 10-8), skiftkostnad (Virke), CV-oppslag, aktive innleide med firma, timepris og kontaktinfo,
personalmappe med rollesperre, økonomi og bunnlinje (D1–D5), sykefravær mot SSB, rapportfrister,
HMS-veiledning og håndbøker. Hele listen ligger i `/api/verktoyskjema`.

## 6. Flyten vi vil se planlagt først (ledelsen, helgebemanning)
1. **Rapport:** velg helg, se hvem som har hatt vakt der før, summert per stasjon.
2. **Rapport:** se hva stasjonen krever, for eksempel vekter og førstehjelp.
3. **Rapport:** kandidater med gyldig kurs på datoen, først egne ansatte, så innleide. Fravær vises bare
   som «utilgjengelig», aldri årsak.
4. **Rapport:** kontrollen kjører på utvalget (hviletid, overlapp, kompetanse) og viser feil.
5. **Handling:** LLM sammenligner de godkjente kandidatene og forklarer valget.
6. **Handling:** LLM skriver utkast til henvendelse. Lars redigerer og sender selv.

## 7. Grensemodus (test av det som ikke er lov i dag)
- Egen fane med fast tekst: «Ulovlig i dag. Kun syntetiske data. Ingenting lagres.»
- Hver test viser side om side: hva brukeren ba om, hva LLM-en ville gjort uten sperre, og regelen som
  stopper det (GDPR art. 9, AML kap. 2 A, CASE-008/012/013/016).
- Eksempler: rangere vakter på sykefravær, vise personalmappe til feil rolle, måle enkeltansatte på besøk
  per time, sende umerket data til ekstern KI.
- Planen skal si hvordan grensemodus aldri kan slås på mot ekte data.

## 8. Kjent svakhet du må ta stilling til
Personalmappe-endepunktet leser rollen fra en HTTP-header, og den kan forfalskes. Planen må si hvor
rollen skal komme fra (innlogging foran serveren) før appen deles med andre.

## 9. Hva planen skal inneholde
1. Skjermkart for hele appen per rolle, med eksisterende sider markert.
2. Knappeliste: hver knapp med rolle, lag (Rapport eller Handling) og API-kall.
3. Én skisse per ny skjerm, i tekst eller ASCII, med Arbeidsflyt-komponentene navngitt.
4. Tilgangsmatrise: rolle mot knapp.
5. Nye lesende endepunkter som trengs, og hvorfor de eksisterende ikke holder.
6. Byggerekkefølge i små oppgaver som kan testes hver for seg.
7. Åpne spørsmål til Lars, hvert med ditt anbefalte svar.

## 10. Rammer
- Ren HTML, CSS og JavaScript på Datafinner. Ingen React, ingen sky, ingen ny database.
- Innhold settes inn med `textContent`, aldri `innerHTML`.
- Norsk bokmål og klarspråk. Ikke dikt opp ansatte, kurs eller priser.
