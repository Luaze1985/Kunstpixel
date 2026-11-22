# Design: chat i «Kunstpixel i dag» (2026-11-19)

Status: utkast til Lars. Bygger på `docs/specs/2026-11-19-storskjerm-dashbord.md` (D1–D8).

## Hvorfor

Lars vil åpne «Kunstpixel i dag» og føle at han kommer på jobb som museumsdirektør: se dagen og spørre om det han lurer på, i samme app. I dag ligger tallene i appen og chatten i prosjektet Kunstpixel. To faner er «ikke godt nok».

## Mål

- Lars kan spørre i vanlig språk inne i appen og få svar hentet fra hele `museum.db` med SQL.
- Samme regler som skillen `kunstpixel-demo`: svar først, `Kilde:` til slutt, finn ID selv, spør ved flere treff, vis begge når kilder er uenige, ingen gjetting.
- Svar med flere sammenlignbare tall får et enkelt stolpediagram.

## Ikke-mål (nå)

- «sjekk»-knapp, rollesperrer, lagring av samtaler, flere brukere.
- Automatisk «god morgen»-melding ved åpning (hver melding bruker Lars' kvote).
- Endring av dashbordets innhold eller tall. D1–D6 og D8 står. D7 (ingen navn) gjelder fortsatt dashbordet, men ikke chatten; se «Persondata».

## Anti-mål (feil selv om det virker)

- Claude svarer med tall den ikke har hentet med SQL.
- «I dag» blir nettleserens dato i stedet for dagen tallene gjelder (bildet av databasen er fra byggedagen).
- Data fra databasen tegnes som HTML (XSS).
- Storskjermen ser annerledes ut når chatten er lukket.

## Tilnærminger (valgt av Lars 2026-11-19)

- **Plassering:** skuff fra høyre (valgt). Alternativer: fast kolonne (gjør tallene mindre på storskjerm), to faner (ser ikke tallene mens man spør).
- **Data:** A, hele databasen med SQL i siden (valgt). B, ferdige oppslag: kan ikke koble tabeller, Claude finner ikke hullene selv. C, bare dashbord-tallene: kan ikke svare på det meste.

## Slik virker det

**Siden** (samme artifact, samme lenke):
- Knappen **KI-chat** øverst ved Fullskjerm åpner en skuff fra høyre (ca. 40 % bredde, hele bredden under 900 px). ✕ og Esc lukker. Dashbordet under endres ikke. KI-chat-knappen har egen farge (Arbeidsflyt-blå med hvit tekst), så den skiller seg fra Fullskjerm og er lett å finne. Lars ba om god oversikt og at chatten er lett å finne (2026-11-20), og valgte derfor skuff (A) framfor fast kolonne, faner eller linje nederst.
- Når Claude spør hvilken av flere ting Lars mener, vises valgene som knapper han kan trykke på (som i skissen).
- Øverst i skuffen: 4 forslag-knapper (Hva krever oppmerksomhet i dag? / Hvordan går utstillingene i år? / Hvordan var besøket forrige uke? / Hvordan gikk Fokusrommet i år?). Ingen HR-spørsmål blant forslagene, siden de kan vises på storskjerm. Under: samtalen, et tekstfelt og Send. Mens Claude jobber: «Tenker …» og en Stopp-knapp.
- All tekst tegnes med `textContent`, linjeskift bevares. Ingen markdown-tolking.
- Samtalen ligger bare i minnet. Lukker man siden, er den borte.

**Claude** (`sample`-kapabiliteten):
- Hvert spørsmål sendes som en liste med meldinger: først én fast instruks, så samtalen så langt (de eldste droppes når den blir lang).
- Instruksen bygges av byggeskriptet og inneholder: reglene fra `deploy/claude-app/SKILL.md` (definisjoner, rolle og fallgruver, svarstil), `references/metrics.md` og `entities.md`, `kjente-hull.md`, alle tabeller med kolonner (ca. 8 KB), og **dagens dato fra `data.json`**.
- **Datoregel:** byggeskriptet skriver om definisjonene slik at de bruker den faste datoen (for eksempel `'2026-11-19'`) i stedet for `date('now','localtime')`. Instruksen skal ikke inneholde `date('now'` noe sted (test).
- Ett verktøy i siden: `sql({sporring})`. Det tar én `SELECT` eller `WITH` (samme regel som `sql.py`), gir maks 200 rader og svar på maks ca. 30 KB. Det returnerer kolonner, rader, antall og om svaret ble kuttet. Feil sendes tilbake som feil, så Claude kan prøve en annen spørring. Databasen åpnes i tillegg med `PRAGMA query_only=ON`.
- Instruksen ber Claude sende uavhengige SQL-spørringer i samme runde (de kjøres samtidig), fordi antall runder er begrenset.
- **Diagram uten egen runde:** vil Claude vise et diagram, avslutter den svaret med én linje `DIAGRAM: {"tittel": …, "etiketter": […], "verdier": […], "enhet": …}`. Siden fjerner linjen fra teksten og tegner stolper (maks 12). Ugyldig linje vises ikke og gir ingen feil.
- Modell: standardnivået (`default`). Ingen bufring av svar (`cache` brukes ikke med verktøy).
- Feil vises som én kort norsk linje (ikke tillatt, for mange spørsmål, avbrutt, ukjent feil). Nekter Lars tilgang, skjules KI-chat-knappen resten av økten. Finnes ikke `sample`, eller sier `sample.limits()` at verktøy ikke kan brukes her, skjules KI-chat-knappen med en kort forklaring.

**Data i siden:**
- `museum.db.gz.txt`: databasen pakket med gzip og skrevet som base64-tekst (ca. 4 MB), publisert ved siden av `data.json`. Artifacter tar ikke imot `.gz`, men `.txt` går (funnet 2026-11-19). Pakkes ut i nettleseren (`atob` + `DecompressionStream`) og åpnes med sql.js første gang skuffen åpnes, ikke ved lasting av siden.
- sql.js 1.12.0 fra cdnjs (finnes der med både `sql-wasm.js`/`sql-wasm.wasm` og ren JavaScript-utgave `sql-asm.js`). Databasen ligger i minnet, så ingenting kan skrives tilbake.
- **Risiko:** claude.ai kan stoppe WebAssembly, enten nedlastingen av `.wasm` fra cdnjs eller selve kjøringen. Da brukes `sql-asm.js` (samme versjon, ingen `.wasm`, tregere men samme SQL).
- **Første steg er en prøveside:** en egen privat artifact som laster sql.js og en liten testdatabase og stiller Claude ett spørsmål med `sql`-verktøyet. Den viser om wasm, asm-reserven, gzip-utpakkingen og verktøyene virker i claude.ai, før noe annet bygges. Virker ikke verktøyene, stopper jeg og kommer tilbake til Lars.

**Bygging:** `scripts/lag_storskjerm.py` skriver i tillegg `museum.db.gz` og `chat-instruks.md`. «oppdater dashbordet» publiserer alle fire filene.

## Persondata (Lars avgjør)

Dashbordet er bygget slik at ingen navn, fraværsårsaker eller e-posttekster når skjermen (D7). Chatten endrer det:
- Hele `museum.db` ligger som fil i artifacten, med personalmapper, fravær (3 456 rader) og medarbeidersamtaler. Den som får lenken via **Del**, kan laste ned fila.
- Svar om navngitte ansatte kan stå på storskjermen mens skuffen er åpen.

Valg: (1) ta med alt, fordi dataene er syntetiske (som C5 for skillen), eller (2) publisere en kopi uten personalmapper, fravær og medarbeidersamtaler.

**Lars valgte (1), ta med alt (2026-11-19).** Lenken deles ikke med andre. Med ekte persondata må dette vurderes på nytt.

## Begrensninger

- Hver melding bruker Lars' egen Claude-kvote. Første gang spør claude.ai om tillatelse.
- Et SQL-spørsmål tar ofte 30–90 s. Claude får bare noen få verktøyrunder per spørsmål, så svært sammensatte spørsmål kan komme halvferdige.
- Databasen (syntetisk) ligger i en privat artifact hos Anthropic, som skillen allerede gjør.

## Tester (skrives først)

- Python: byggeskriptet lager `museum.db.gz` som pakkes ut til nøyaktig samme bytes som databasen som skal publiseres; `chat-instruks.md` inneholder datoen, «aldri med ID», «to kilder er uenige», `Kilde:` og alle tabellnavn, og **ikke** `date('now'`.
- Nettleser (Playwright, med en falsk `claude.use("sample")` som kaller verktøyet): skuffen åpnes og lukkes, storskjermen er lik når den er lukket, `sql` avviser `DELETE`/`DROP`/flere setninger og kutter ved 200 rader, `DIAGRAM:`-linjen tegnes som stolper, fjernes fra teksten og tåler stygg tekst (XSS), KI-chat-knappen skjules når `sample` mangler, nektes eller ikke har verktøy, ingen sidelengs rulling på mobil.
- Nettlesertestene som trenger sql.js fra cdnjs hoppes over uten nett.

## Ikke testet før Lars prøver

- Ekte svar fra Claude i claude.ai, tillatelsesdialogen, tid per svar og kvalitet sammenlignet med prosjekt-chatten.
- Mobilappen.

## Overlatt til den som bygger

- Nøyaktig ordlyd i instruksen utover reglene over, farger og avstander innen Arbeidsflyt-paletten, antall meldinger som beholdes (forslag: siste 20).
