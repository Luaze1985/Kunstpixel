# Spesifikasjon: Datafinner som ledelsesside (etappe 2–4)

**Status:** ready-for-agent. Unntak: oppgaver merket 🔒 krever Lars' ja før de starter (datamodell, ny lagring, arkitekturvalg). · **Dato:** 2026-11-16
**Grunnlag:**
- [Ledelsesside-innhold](../research/2026-11-16-ledelsesside-innhold.md) (lov, statistikk, bransje, K01–K15)
- [74 GitHub-repoer](../research/2026-11-16-github-repos-ledelsesside.md)
- Plan `~/.claude/plans/jeg-jeg-er-jeg-keen-tulip.md`
- `docs/DECISIONS.md` E1–E8 (etappe 1 ferdig)

**Låste føringer (gjelder alle oppgaver):**
- `museum.db` er kun-les.
- Bare Lars bygger databasen.
- `af.css` endres ikke.
- `textContent`, aldri `innerHTML`.
- Siden virker uten KI.
- KI-tekst merkes «AI-forslag».
- Hvitelisten av verktøy består. Ingen fri SQL for KI.
- Handlinger lagres bare i nettleseren (Lars 2026-11-16).
- Ingenting sendes automatisk. Bare utkast.
- Alle data er syntetiske.

---

## Problembeskrivelse

Datafinner viser tall og rapporter, men svarer ikke på det en leder spør om hver morgen:
- **Hva skjer i dag?** Er besøket som normalt, hvem er på jobb, har noe gått galt?
- **Hva må jeg gjøre, og innen når?** Loven gir harde frister: oppfølgingsplan etter 4 uker sykefravær, dialogmøte innen 7 uker (AML § 4-6). Avvik må rettes (AML § 3-1, IK-forskriften § 5).
- **Hvordan går det over tid**, i samme form som museet uansett må rapportere til Kulturdirektoratet?

I dag må lederen lete i rapporter, tolke tabeller selv og huske fristene. Tall uten sammenligning («312 besøk») sier ikke om noe er galt. Et tomt svar kan se ut som «alt er fint». KI-svar lenker ikke til rapporten de bygger på. Det finnes heller ikke noe testsett som viser at KI velger riktig verktøy.

Researchen viser at nesten ingen av de 74 åpne systemene har en forside med «det du må gjøre i dag». Det er her Datafinner kan skille seg ut.

## Løsning

Sett fra lederen:

1. **Hjem** har to kort over chatten: **«I dag»** og **«Mine frister»**.
   - Hvert tall vises med «normalt for ukedagen», endring og en status: Normal, Følg med, Over terskel eller **Ukjent**.
   - Øverst står «Tall per 16.11 kl. 08:02».
   - Hvert tall er en lenke til radene bak det.
2. **«Driften denne uka»** er en rapport. Den viser besøk per dag mot forrige uke og samme uke i fjor, hendelser, nye og åpne driftsmeldinger og HMS-avvik, tilfredshet, og kafésalg per besøkende.
3. **«Mine frister»** er gruppert i **Forfalt / I dag / Denne uka / Senere / Fulgt opp**. Kortet viser:
   - sykefraværsfrister (uke 4 og 7)
   - åpne HMS-avvik eldre enn grensen
   - rapporter med frist innen 30 dager
   - tilstandskontroller som forfaller
   - innlån som går ut

   Hver rad har en **handlingslinje** med fire knapper:
   - **Fulgt opp**: huskes i nettleseren.
   - **E-postutkast**: fast mal, fakta fra databasen.
   - **Meld avvik**: utkast.
   - **Spør KI om dette**.
4. **Kontroll-avkrysningene** på rapporter erstattes av samme handlingslinje, pluss **«Godta»**, som gjør et AI-forslag til godkjent.
5. **KI-svar** får en «Åpne rapport»-lenke laget av koden. Ferdige spørsmål per rolle vises når det finnes godkjente svar.
6. **«Museumsstatistikk»** viser en forhåndsvisning av årets tall i samme oppsett som Kulturdirektoratets skjema.

---

## Brukerhistorier

**I dag og denne uka**
1. Som museumsdirektør ønsker jeg å se dagens og gårsdagens besøk mot normalt for ukedagen, slik at jeg straks ser om noe avviker.
2. Som leder ønsker jeg at «0» og «mangler data» vises ulikt, slik at et tomt svar aldri ser ut som «alt i orden».
3. Som leder ønsker jeg å se når tallene ble hentet, slik at jeg vet hvor ferske de er.
4. Som driftsansvarlig ønsker jeg å se hvem som er på jobb per stasjon i dag, slik at jeg oppdager hull og feilplasseringer (som kafévaktene).
5. Som driftsansvarlig ønsker jeg å se nye og åpne driftsmeldinger med de som haster først, slik at jeg vet hva som har gått galt.
6. Som leder ønsker jeg å klikke på et tall og få radene bak det med samme filter, slik at jeg kan sjekke tallet selv.
7. Som direktør ønsker jeg å se besøk denne uka mot forrige uke og samme uke i fjor, slik at jeg ser trend og ikke bare dagsform.
8. Som kafeansvarlig ønsker jeg å se kafésalg per besøkende, slik at jeg ser om salget følger besøket.
9. Som leder ønsker jeg at avvik og hendelser vises med «lavere er bedre», slik at fargen betyr det samme overalt.

**Mine frister og handlinger**

10. Som HR-leder ønsker jeg å se hvem som nærmer seg uke 4 og uke 7 i sykefravær, slik at oppfølgingsplan og dialogmøte skjer innen fristen i AML § 4-6.
11. Som leder ønsker jeg at fristlisten **aldri viser årsak eller diagnose**, bare fristtype og dato, slik at personvernet holdes.
12. Som driftsansvarlig ønsker jeg å se HMS-avvik som har stått åpne for lenge, slik at de blir lukket.
13. Som direktør ønsker jeg å se rapporter med frist de neste 30 dagene, slik at ingen rapport kommer for sent.
14. Som samlingsansvarlig ønsker jeg å se tilstandskontroller og innlån som forfaller, slik at verk og avtaler følges opp.
15. Som leder ønsker jeg å merke en frist «fulgt opp», slik at den flyttes til Fulgt opp og ikke vises som åpen igjen.
16. Som leder ønsker jeg et e-postutkast der fakta allerede står riktig, slik at jeg bare trenger å lese over og sende fra eget e-postprogram.
17. Som leder ønsker jeg å melde et avvik fra en rad, slik at jeg har et utkast å sende videre.
18. Som leder ønsker jeg å ta med en rad eller rapport til KI og få forklaring og forslag, slik at jeg forstår hva jeg ser.
19. Som leder ønsker jeg å godta et AI-forslag eksplisitt, slik at det er klart hva en person har godkjent.

**KI og kvalitet**

20. Som leder ønsker jeg at hvert KI-svar har en lenke til rapporten eller tabellen det bygger på, slik at jeg kan sjekke kilden med ett klikk.
21. Som leder ønsker jeg ferdige spørsmål for min rolle, slik at jeg kommer raskt i gang.
22. Som Lars ønsker jeg et fasitsett per rolle som sjekker at KI velger riktig verktøy og argumenter, slik at jeg kan vise at KI-laget er etterprøvbart.
23. Som Lars ønsker jeg at bare godkjente svar blir eksempler, slik at feil ikke læres inn.
24. Som Lars ønsker jeg en ordliste med begrepene (besøk, betalende, avvik, årsverk) med Kulturdirektoratets definisjoner, slik at KI og rapporter bruker samme ord.

**Statistikk og opprydding**

25. Som direktør ønsker jeg en forhåndsvisning av årets museumsstatistikk, slik at årsrapporteringen blir et biprodukt.
26. Som leder ønsker jeg at feltnavn vises med riktige bokstaver (Måned, Formål), slik at tabellene ser ferdige ut.
27. Som Lars ønsker jeg at Claude i terminalen (MCP) ser de samme tabellene som Datafinner, slik at `/sjekk` og demo gir samme svar.

---

## Oppgaveliste

ID-format: **B** = backend, **F** = frontend, **K** = KI, **D** = data. 🔒 = Lars må si ja først. «Avh.» = avhengighet.

### Etappe 2: «I dag» og «Driften denne uka»

| ID | Oppgave | Avh. | Ferdig når |
|---|---|---|---|
| **B1** | **Ren beregningsmodul for ledelsestall** (ny modul i `core/`). Funksjonene tar rader og en `idag`-dato inn og returnerer tall, og leser selv ingenting fra databasen. Den skal kunne: (1) fylle inn dager uten rader, (2) regne «normalt» som snitt for samme ukedag de siste 4 åpne ukene, (3) regne endring og prosent, (4) sette status Normal / Følg med / Over terskel / Ukjent ut fra terskler og `lavere_er_bra`. | – | Enhetstester grønne. Se teststrategi. |
| **B2** | **Terskler som data i koden** (Python-konstant eller liten YAML i `05_data/governance/`, ikke i `museum.db`): måltall → `lavere_er_bra`, grense for Følg med og grense for Over terskel. | B1 | Ett sted å endre. Testet via B1. |
| **B3** | **Verktøyet `get_today_overview(dato)`** (hvitelistet). Henter besøk, vakter per stasjon, arrangementer, driftsmeldinger og HMS-avvik for dagen og dagen før, og kjører B1. Svaret har `hentet_kl`, og hvert tall har `status`, `normalt`, `endring` og en `lenke` (rapportadresse med filter). Skriver aldri tall etter `dato`. | B1, B2 | Hvitelistetesten (E7) er grønn. Svaret er stabilt for en fast dato. |
| **B4** | **Verktøyet `get_week_overview(dato)`**: besøk per dag i uka mot forrige uke og samme ISO-uke i fjor, tilfredshet, lave anmeldelser, kafésalg per besøkende, og hendelser og avvik åpnet mot lukket. | B1 | Som B3. |
| **B5** | **Ny rapport «Driften denne uka»** på de fire stedene (`SPORSMAL`, `rolle_sporsmal.csv`, `rapport_regler.csv`, forsiden) for Museumsdirektør, Driftsansvarlig og Kafeansvarlig. 🔒 CSV-endringen krever at Lars bygger `museum.db`. | B4 | Spørsmålstesten (fire steder like) er grønn etter bygging. |
| **F1** | **Kortet «I dag» på Hjem**, over chatten. Viser tall, normalt, endring, statusmerke og «Tall per …». «Ukjent» er grått med teksten «Mangler data», aldri grønt. Hvert tall lenker til radene bak. | B3 | Se teststrategi. |
| **F2** | **Ren JS-fil `ledelse.js`** (lastes som `vaktrom.js`), uten DOM. Funksjonene lager statustekst og fargeklasse fra status, formaterer «normalt / endring», og formaterer «Tall per». | – | Node-tester grønne. |
| **F3** | **Statusmerker med eksisterende `af-source`/`af-badge`-klasser** (ingen ny CSS). Hvis en klasse mangler: spør Lars før `af.css` røres. | F2 | Ingen endring i `af.css`. |
| **F4** | **Etiketter med æøå** (Maned→Måned, Formal→Formål, Ar→År osv.) via en ordtabell i `ledelse.js`. | F2 | Node-test for kjente felt. |
| **D1** | **Datahull i fremtiden:** tall etter dagens dato (syntetiske fram til 2026-12-31) skal aldri vises som faktiske. Håndteres i B1 og B3 ved å kutte på `idag`. | B1 | Enhetstest med rader etter `idag`. |

### Etappe 3: «Mine frister» og handlinger

| ID | Oppgave | Avh. | Ferdig når |
|---|---|---|---|
| **B6** | **Ren fristmodul** (i samme modul som B1 eller egen). `beregn_frister(rader, regler, idag)` returnerer `{type, ref, frist_dato, dager_til, gruppe}`. Gruppene er Forfalt, I dag, Denne uka og Senere. Regelformen er `{type, dato_felt, dager_etter_start, start_teller_med}`. | – | Enhetstester, også grensetester. |
| **B7** | **Fristregler** (konstant eller YAML, ikke DB):<br>• sykefravær uke 4 (oppfølgingsplan) og uke 7 (dialogmøte, bare ved fullt fravær hvis dataene skiller)<br>• HMS-avvik åpent lenger enn N dager<br>• rapportfrist (måned i kalenderen → første dag i neste måned? se åpent spørsmål Å2)<br>• tilstandskontroll (`neste_kontroll`, ellers siste + intervall)<br>• innlån (sluttdato for utstillingen)<br>🔒 Hvilke regler og tall Lars godkjenner. | B6 | Reglene er skrevet i `DECISIONS.md`. |
| **B8** | **Verktøyet `get_my_deadlines(rolle, dato)`** (hvitelistet). Henter fravær, avvik, kalender, tilstandsrapporter og innlån, og kjører B6. **Gir aldri fraværstype eller årsak ut**, bare `ansatt_id`, navn, fristtype og dato. Rollefilter: HR ser sykefravær, Drift ser avvik og så videre. | B6, B7 | Personverntest: ingen felt fra `hr_fravaer.type` i svaret. |
| **B9** | **E-postmaler som data** med plassholdere (`{navn}`, `{frist_dato}`, `{dager_over}`, `{kilde}`). Ren funksjon `fyll_mal(mal, verdier)` som feiler hvis en plassholder mangler. Malene skal ikke ha felt for diagnose eller årsak. | – | Enhetstester. |
| **B10** | **`get_tilstandsrapporter` og `get_innlan` på hvitelisten** (lesende). Dekker også oppgave 09 (`get_condition_report`, `search_loans`). 🔒 Ny hvitelisting er en endring i verktøylaget, så Lars må godkjenne den. | – | Hvitelistetesten er grønn. |
| **F5** | **Kortet «Mine frister» på Hjem** og egen visning `#frister`, gruppert, med tellemerke i menyen («Følg opp»). Farget prikk etter gruppe. | B8, F2 | Se teststrategi. |
| **F6** | **Lagring i nettleseren**, nøkkel `kunstpixel.oppfolging.v1`. Ren JS-funksjoner i `ledelse.js`: `lesOppfolging`, `merkFulgtOpp(id)`, `erFulgtOpp(id)`, `grupper(frister, oppfolging)`. Lagringen pakkes inn i try/catch, og siden virker uten lagring. | F2 | Node-tester med falsk lagring. |
| **F7** | **Handlingslinje** (én komponent) på fristrad, raddetalj, rapportkort og KI-svar. Knappene er Fulgt opp, E-postutkast (`mailto:` fra B9-teksten via API), Meld avvik (utkast i oppfølgingslisten med type «avvik») og Spør KI om dette (bruker `CHAT.utkast` fra etappe 1). | F6, B9 | Se teststrategi. |
| **F8** | **Erstatt Kontroll-avkrysningene** med handlingslinjen pluss **«Godta»**. Godta setter Vurdering og Forslag til «Bekreftet» og lagres i oppfølgingslisten. Merkene (Bekreftet, Systemforslag, Bør verifiseres, Mangler) beholdes. | F7 | Etappe 1-testene oppdatert med vilje. |
| **F9** | **Visningen «Mine oppfølginger»** (`#oppfolging`): åpne og lukkede, «Last ned» som .csv, og lenke tilbake til kildeadressen (rapport/rad). De tre nyeste åpne vises i huskelappen til høyre. | F6 | Node-test for CSV-bygger. |

### Etappe 4: KI og kvalitet, statistikk, opprydding

| ID | Oppgave | Avh. | Ferdig når |
|---|---|---|---|
| **K1** | **Lenke fra KI-svar til rapport.** Ren funksjon `lenke_for_kall(verktoy, args)` på serveren. Den slår opp i `SPORSMAL` og gir rapportadresse eller `null`. `/api/chat` legger `lenker` i svaret. Frontend viser «Åpne rapport». KI lager aldri lenken. | – | Enhetstest for alle `SPORSMAL`-verktøy. |
| **K2** | **Fasitsett per rolle** (YAML i `tests/`): spørsmål → forventet verktøy, forventede argumenter (delmengde) og forventet tall. Utfallene er pass, fail, review og error. Kjøres mot **opptak** av KI-svar (eksisterende kassettmønster), ikke live. | – | Minst 3 spørsmål per rolle med rapporter. |
| **K3** | **Godkjente svar som eksempler.** «Godta» på et KI-svar lagrer spørsmål, verktøy og argumenter lokalt. Ferdige spørsmål per rolle vises fra godkjente svar når det finnes minst 3. Ellers vises dagens faste forslag. | F8 | Node-test for utvalget. |
| **K4** | **Ordliste** (`05_data/governance/ordliste.yaml`) med Kulturdirektoratets definisjoner av besøk, betalende, barn og unge, årsverk og avvik. Den sendes med i systemprompten og vises i huskelappen når et begrep brukes. 🔒 Nytt datagrunnlag. | – | Test: systemprompten inneholder ordlisten. |
| **K5** | **Valgfri «streng modus»**: KI får bare kolonner og antall rader, ikke tallene. Den beskriver hva svaret viser, mens tallene vises fra verktøyet. Bryter i huskelappen. 🔒 Arkitekturvalg. | K1 | Test: meldingen til KI inneholder ingen tall fra resultatet. |
| **B11** | **Verktøyet `get_museum_statistics_preview(aar)`**: besøk (totalt, betalende, voksne, barn og unge), utstillinger (faste, midlertidige) og økonomi, i skjemaets rekkefølge. Felt uten data (årsverk, samlinger etter type) vises som «Mangler data». | B1 | Enhetstest mot fast år. |
| **F10** | **Rapport «Museumsstatistikk (forhåndsvisning)»** for direktøren, på de fire stedene. 🔒 DB-bygging. | B11 | Spørsmålstesten er grønn. |
| **D2** | **Datagenerator:** vakter fordeles etter stilling, ikke avdeling (`archive_generator.py`). Håndbokens målgruppe settes per avsnitt (`seed_handbooks.py`). 🔒 Datamodell og Lars bygger. | – | Test: ingen ikke-kaféstilling på kafévakt. |
| **D3** | **MCP-dekning (K2 fra PLAN):** lesende MCP-verktøy for `dagsbesok`, `hr_medarbeidersamtaler` og `hr_innleide_kompetanse`, pluss B3/B4/B8 når de finnes. 🔒 | B3 | `sjekk_kunnskapsgraf.py` melder 61/61. |
| **F11** | **Arena og personvern:** Arena blir under «Mer». Personvern-casene (G1–G5) skrives om til spørsmål en leder faktisk har, eller fjernes. 🔒 Lars avgjør innholdet. | – | – |

---

## Beslutninger om implementasjon

- **Logikk i rene funksjoner, I/O i tynne verktøy.** Beregninger (normalt, status, frister, maler, lenker) ligger i rene Python-funksjoner som tar rader og dato inn. Verktøyene i hvitelisten henter rader og kaller dem. På klientsiden ligger tilsvarende rene funksjoner i `ledelse.js`, uten DOM og lagring, og `ett-vindu.html` står for visningen.
- **Frister og status regnes ut når siden lastes, og lagres aldri.** Ingen planlagte jobber og ingen utsending.
- **Ingen ny database eller skrivbar tabell.** Regler, terskler, maler og ordliste ligger som konstanter eller YAML i repoet. Oppfølging ligger i nettleserens `localStorage`.
- **Personvern:** fristverktøyet sender aldri fraværsårsak ut. E-postmalene har ikke felt for den.
- **Lenker lages av koden** fra verktøy og argumenter, aldri av KI.
- **Ny hvitelisting** (B3, B4, B8, B10, B11) følger hvitelistetesten fra etappe 1. Argumentnavnene må stemme med funksjonen.
- **Status har fire nivåer**, og «Ukjent» er alltid eget. Tomt eller manglende resultat blir aldri Normal.
- **Rekkefølge:** etappe 2 → 3 → 4. Innen hver etappe: B (backend) og F2 først, deretter visningen.

## Teststrategi og testgrenser

**Valgt testgrense (Lars 2026-11-16): dypere tester på enkeltfunksjoner.** Logikken testes direkte på de rene funksjonene. Konsekvensen er at feil fanges raskt og presist, men testene må skrives om hvis funksjonene endres. Nettlesertestene fra etappe 1 beholdes som en tynn sikkerhetsline for flyten.

**Hva som testes automatisk:**
- **Python, rene funksjoner** (pytest, fast `idag`):
  - Normalt for ukedag: 4 åpne uker, stengte dager hoppes over, for lite historikk gir «Ukjent».
  - Utfylling av tomme dager. Kutt etter `idag` (D1).
  - Status: alle fire nivåer, `lavere_er_bra` snur retningen, tomt gir Ukjent, og 0 er ikke Ukjent.
  - Frister:
    - uke 4 og 7 med `start_teller_med` sann og usann
    - fravær som ender før fristen gir ingen frist
    - grupper rundt midnatt og helg
    - forfalt i går
    - i dag
    - om 6 og 8 dager
  - Maler: alle plassholdere fylt, en manglende plassholder gir feil, og ingen årsak eller diagnose finnes i noen mal.
  - `lenke_for_kall`: alle `SPORSMAL`-verktøy gir adresse, og ukjent verktøy gir `null`.
  - Statistikk-forhåndsvisning: summer mot direkte SQL for et fast år.
- **Python, verktøy** (tynne): hvitelistetest, personverntest (B8 gir ikke `type`), og at svaret er stabilt for en fast dato.
- **JavaScript, rene funksjoner** (`ledelse.js`, kjøres med `node` fra pytest og hoppes over uten node, samme mønster som `test_intern_page.py`): status → tekst/klasse, formatering, æøå-etiketter, `grupper`, `merkFulgtOpp` med falsk lagring, CSV-bygger og utvalg av ferdige spørsmål.
- **KI** (K2): fasitsettet kjøres mot opptak. Utfall pass/fail/review/error. Ingen live-kall i testsuiten.
- **Nettleser** (Playwright, tynt): én test per etappe for hovedflyten:
  - Hjem viser «I dag» og «Mine frister».
  - Klikk på et tall gir rader.
  - Fulgt opp overlever omlasting.
  - E-postutkastets `mailto:` har riktig emne.
- **Kontrakter som allerede finnes:** hvitelistetesten, spørsmålstesten (fire steder), `textContent`/ingen `innerHTML`, og at siden virker uten KI.

**Hva som ikke testes automatisk (manuell sjekk ved hver etappe):**
- Utseende, farger og plass på mobil (390 px). Lars ser på det i nettleseren.
- Ekte e-postprogram som åpner `mailto:`.
- Kvaliteten på formuleringene fra live Claude (dekkes av `/sjekk` og fasitsettet med opptak).
- Juridisk riktighet av fristreglene. Lars eller en fagperson bekrefter Å1 og Å2.

## Åpne spørsmål (avklares før oppgaven starter)

- **Å1 (B7):** Telles første fraværsdag med når uke 4 og uke 7 regnes ut? Gjelder dialogmøtet bare ved fullt fravær, og skiller dataene (`hr_fravaer`) mellom fullt og delvis?
- **Å2 (B7):** Hva er fristdatoen for en rapport som bare har måned i kalenderen? Siste dag i måneden eller første dag i neste?
- **Å3 (B2):** Tersklene for Følg med og Over terskel per måltall. Forslag: ±15 % og ±30 % mot normalt.
- **Å4 (F11):** Hva skal skje med personvern-casene?

## Avgrensning (lages IKKE nå)

- Automatisk utsending av e-post eller varsler, planlagte jobber og bakgrunnsprosesser.
- Lagring på server eller i database for oppfølging og avvik (valgt: bare nettleser).
- Full avviksflyt med faser og godkjenning. Bare «utkast» og «fulgt opp».
- Innlogging, tilgangsstyring per rolle i verktøylaget og flere brukere.
- Fri SQL eller nye skrivende verktøy for KI.
- Grafer og diagrambibliotek. Tall, endring og tabeller holder.
- Ekte data eller kobling til eksterne systemer (Altinn, NAV, billettsystem).
- Grensemodus, Søk og Arbeidsflyter (fjernet i etappe 1).
- Automatisk læring av KI-svar uten at en person har godtatt dem.
