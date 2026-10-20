# Bestilling: Opplæringsarena i VS Code og Colab
*Til: Lars (og agenten du jobber med i VS Code) · Fra: Claude Code · 2026-10-20 · Status: forslag, ikke startet*

## Formål
Én arena der du **bygger** i VS Code og **underviser** i Colab, med casene fra Kunstpixel-dataene. Hver case viser den samme kjeden:

```
data (museum.db)  →  kobling av variabler (Python/SQL)  →  fast rapport + regel (deterministisk)  →  LLM på toppen (forklarer, AI-forslag)  →  menneske vurderer
```
Læringsmålet går igjen i alle casene: **tallene kommer fra data og regler, aldri fra språkmodellen.** Modellen forklarer og drøfter, og et menneske avgjør.

---

## Del A. Vurdering: stemmer det at VS Code kan hjelpe deg?

**Kort svar: ja, til å bygge. Undervisningen bør gå i Colab i nettleseren.** Colab-MCP-en du installerte er ikke en del av VS Code. Den er et verktøy for agenten.

| Del | Hva den faktisk er (sjekket 2026-10-20) | Bruk den til |
|---|---|---|
| **VS Code** | Installert (1.142). Har Claude Code, Python, Pylance, Gemini Code Assist og Cline. **Mangler Jupyter-utvidelsen**, så `.ipynb` kan ikke kjøres der i dag. | Kode, datafiler, tester, git. Verkstedet. |
| **colab-mcp** (`googlecolab/colab-mcp`) | Lagt inn i Antigravity og i Claude Code (brukernivå), men ikke testet i en økt. Kjører lokalt, åpner en Colab-fane i nettleseren din og lar agenten jobbe i den notatboken over en websocket. Koden kjører i Colab, men agenten styres fra din PC. Krever en lokal klient (Claude Code, Gemini CLI m.fl.). | La agenten **bygge og kjøre** en undervisningsnotatbok foran deg i Colab. Fint som live-demo. |
| **Colab-utvidelsen til VS Code** | Finnes (offisiell, ifølge flere kilder). Kjører en lokal notatbok på en Colab-kjøretid (også gratis GPU). Krever Jupyter-utvidelsen. **Ikke installert.** | Trengs ikke nå. Kjøretiden i skyen ser ikke filene på `G:`, så dataene må lastes opp eller ligge på Drive. Det er mer styr enn nytte for dette. |
| **`google.colab.ai`** | LLM direkte i Colab uten egen nøkkel. Offisielt gratis for Pro/Pro+. Kilder er uenige om hva gratisbrukere får (trolig lettere modeller). | KI-laget i undervisningen uten at elevene trenger nøkkel. **Sjekk på en elevkonto før du lover det.** |

**Anbefalt oppsett:**
1. **VS Code = verkstedet.** Lokal Python 3.13, repoet på `G:`. Installer Jupyter-utvidelsen (`ms-toolsai.jupyter`). Bygg case-modulene som vanlig Python med tester.
2. **Colab = klasserommet.** Tynne notatbøker som importerer case-modulene fra repoet på Drive (`/content/drive/MyDrive/Kunstpixel`), slik `notebooks/data_pipeline_colab.ipynb` allerede gjør.
3. **colab-mcp = demo-verktøy.** Agenten bygger eller endrer en notatbok live, mens du forklarer.

---

## Del B. Det du må tenke på når du jobber videre i VS Code

1. **Én sannhet.** Repoet ligger på Google Drive, og VS Code og Colab ser de samme filene. Rediger ikke samme fil to steder samtidig, for Drive synkroniserer med forsinkelse. Lagre undervisningsnotatbøker i repoet, og fjern utdata før commit, så ikke data og støy havner i git.
2. **museum.db bygges, den redigeres ikke.** Du må bygge den på nytt nå (CSV-rettingen fra sist). Følg `docs/DATAPIPELINE.md` for alt du utvider. `tests/test_data_csv.py` fanger komma uten anførselstegn.
3. **🔴 Personverndatabasen må ryddes før bruk (blokkerer case 6).** `05_data/colab_personvern_historikk.db` (AGY) spores i git og har navn, Trondheim-adresser, «syntetiske» fødselsnumre, fagforening og helse (art. 9) og skattetall. Fødselsnumrene følger **ikke** Skatteetatens syntetiske ordning (måned + 80), og **3 av 168 har gyldige kontrollsiffer**. Lag dem på nytt etter den syntetiske ordningen, ikke push grenen før det er gjort, og del aldri filen med elever eller send den til en språkmodell.
4. **Nøkler.** I Colab: bruk Secrets (`from google.colab import userdata`), aldri nøkler i celler. Elever skal ikke få din nøkkel. Bruk `google.colab.ai`, en lokal modell (Ollama, som du allerede har) eller Datafinner-API-et bak innlogging med grense per time.
5. **Agentens tilgang.** Når colab-mcp styrer en Colab-økt med Drive montert, kan agenten lese og endre hele Drive-en din. I agentstyrte økter: ikke monter Drive, last heller opp `museum_demo.db` til kjøretiden.
6. **For mange assistenter i VS Code.** Claude Code, Cline, Gemini Code Assist og Copilot kan endre de samme filene. Bruk én per oppgave. `AGENTS.md` leses av de fleste, og `CLAUDE.md` av Claude.
7. **Versjoner.** `mcp==1.29.1` (2.x virker ikke). Colab har sin egen Python-versjon. Hold case-modulene til standardbibliotek + `pandas` + `sqlite3`.
8. **Kjente feller:** git-låser på Drive, formatterhooker som fjerner importer, BOM i `.ps1`. Se `docs/DATAPIPELINE.md` § Kjente feller.

---

## Del C. Casene

Alle casene bygger på kolonner som finnes i `museum.db` i dag (sjekket). Nivå 1 er nybegynner, og nivå 3 er drøfting og etikk.

| # | Spørsmål (slik elevene møter det) | Koblinger (tabell.kolonne) | Deterministisk del | LLM på toppen | Læringsmål | Nivå |
|---|---|---|---|---|---|---|
| 1 | **Er vi riktig bemannet når publikum kommer?** | `dagsbesok.besok_totalt`, `er_aapent` × `hr_vakter.dato`, `timer` | Besøk per vakttime per dag, uke og måned. Regel: terskel → Systemforslag | Forklarer mønsteret og foreslår spørsmål til lederen | Koble på dato. Stengte dager (`er_aapent`) må tas ut | 1 |
| 2 | **Hva koster en utstilling egentlig?** | `utstilling_okonomi.*` + `hr_vakter.utstilling_id` × `hr_ansatte.lonnstrinn_virke` × `virke_tariff.timesats_*` (+ `hr_innleie.totalbelop_nok`) | Lønnskost og innleie per utstilling, kostnad per besøkende (`besokstall_total`) | Sammenligner to utstillinger i klarspråk | Flere ledd i en kobling. Kontroller mot `netto_resultat_nok` | 2 |
| 3 | **Hva driver vaktkostnaden?** | `hr_vakter` × `norske_helligdager.tillegg_faktor` × `virke_tariff` × `arbeidstid_grenser` | Kostnaden delt i ordinær, kveld, helg og helligdag | Forklarer fordelingen og tallkontrollen | Å dele et tall i deler. Avrunding (jf. G11) | 2 |
| 4 | **Henger arrangementer og overtid sammen?** | `hendelser.dato`, `klokkeslett_slutt` × `hr_vakter.slutt`, `timer` × `arbeidstid_grenser` | Overtid på dager med og uten arrangement | Lager hypoteser, merket AI-forslag | **Dataene er laget med en regel (T5). Elevene «oppdager» generatoren.** Hva kan syntetiske data bevise? | 2 |
| 5 | **Henger fravær og belastning sammen?** | `hr_fravaer` × `hr_vakter` (ukesum før fravær) × `hms_ergonomi_rotasjon.maks_sammenhengende_timer`, med `ssb_sykefraver_kultur` som referanse | Fravær etter belastningsnivå, og museet mot SSB | Drøfter årsak eller sammenfall | Korrelasjon er ikke årsak. Et sammenligningsgrunnlag | 3 |
| 6 | **Mosaikkeffekten: når ufarlige data blir sensitive** | AGYs personverndatabase: `vakt_time_for_time` × `kollektiv_avvik_trondheim` × profiler | Hvor få koblinger skal til før en person kan identifiseres | Får bare dataminimert grunnlag (`llm.forenkle_for_llm`), og elevene ser hva som strippes | Dataminimering, art. 9, kobling som risiko. **Blokkert til fødselsnumrene er rettet** | 3 |
| 7 | **Kan vi stole på KI-forklaringen?** | Hvilken som helst rapport fra 1–5 | `llm.tallkontroll` sjekker hvert tall | To modeller forklarer samme rapport, og én får beskjed om å «runde av fritt» | Verifisering. Elevene ser tallkontrollen fange funnet-på-tall | 2 |
| 8 | **Lag din egen regel** | En rad i en regeltabell (felt, operator, terskel, vurdering, forslag, fallback) | Regelen vurderes deterministisk mot en case | Kritiserer formuleringen, men endrer ikke terskelen | Regler som data, versjonering, «samme input gir samme svar» | 1 |

**Gode diskusjonsspørsmål til alle casene:** Hva er fakta, hva er regel, og hva er KI? Hvem har ansvaret for vurderingen? Hva ville vært annerledes med ekte data?

---

## Del D. Små utvidelser av datasettet («utvide litt»)
Følg oppskriften i `docs/DATAPIPELINE.md`. Én commit per punkt, `datakilde` som starter med «syntetisk», og statusporten skal gi KLAR.

| # | Utvidelse | Hvorfor | Ferdig når |
|---|---|---|---|
| D1 | `05_data/undervisning_regler.csv` → tabell `undervisning_regler` (samme kolonner som `rapport_regler`) | Egne regler for case 1–5 og 8, uten å endre Datafinners seks spørsmål (en test vokter dem) | Hver case har minst én regel og en fallback. Samme verdier gir samme regel (test) |
| D2 | `besoksundersokelse` (dag, tilfredshet 1–5, ventetid i minutter), generert med egen `Random` og avhengig av bemanning per besøkende | Gir case 1 et utfall å se etter («påvirker bemanning opplevelsen?») | Finnes for alle åpne dager i `dagsbesok`. Sammenhengen er dokumentert som laget, ikke funnet |
| D3 | Lag fødselsnumrene i personverndatabasen på nytt etter Skatteetatens syntetiske ordning (måned + 80, gyldige kontrollsiffer) | Fjerner risikoen for ekte numre. Låser opp case 6 | 0 av 168 med vanlig måned. Test som sjekker ordningen. **Krever ditt ja, siden det er AGYs data** |
| D4 | (Valgfritt) Dagsbesøk per time på åpne dager | Kobling mot `vakt_time_for_time` på timenivå | Summen per dag er lik `dagsbesok.besok_totalt` (test) |

---

## Del E. Slik bygges det (teknisk ramme)
- **Case-moduler:** `src/kunstpixel/undervisning/case_<navn>.py` med én funksjon `lag_case(con) -> dict` som gir `{fakta, nokkeltall, regelverdier}` (samme form som `datafinner_api.lag_rapport`). Bare `sqlite3` med `mode=ro`, og ingen skriving.
- **Vurdering:** én felles `vurder(case_id, regelverdier)` mot `undervisning_regler` (gjenbruk logikken i `query_report_assessment`).
- **KI:** gjenbruk `src/kunstpixel/core/llm.py` (`forenkle_for_llm`, `tallkontroll`, `forklar`). Legg til et tredje grensesnitt, `colab`, som bruker `google.colab.ai` når det finnes. Alt annet er likt.
- **Notatbøker:** `notebooks/undervisning/NN_<case>.ipynb`. Tynne: importer, kjør, vis og drøft. Ingen logikk som ikke er testet. Utdata fjernes før commit.
- **Tester:** `tests/test_undervisning_<case>.py` mot en temp-bygget database (`bygget_db`). Én test per case som låser nøkkeltallene, og én som viser at samme input gir samme svar.

## Del F. Rekkefølge og leveranser

| Fase | Innhold | Ferdig når |
|---|---|---|
| 0 Oppsett | Bygg museum.db på nytt. Installer Jupyter-utvidelsen i VS Code. Test colab-mcp i en ny Claude Code-økt (`open_colab_browser_connection`). Sjekk `google.colab.ai` på en elevkonto | `--check` gir LIK. En notatbok kjører i VS Code. Agenten kan legge til en celle i Colab. Du vet hva elevene får av KI |
| 1 To caser | Case 1 og 8 med D1. Modul, test og notatbok | Statusporten er KLAR, og begge notatbøkene kjører i Colab |
| 2 KI på toppen | Case 7 + `colab`-grensesnitt i `llm.py` | Tallkontrollen fanger et funnet-på-tall foran klassen |
| 3 Utvide | D2 + case 2–5 | Hver case har test og notatbok |
| 4 Personvern | D3 (etter ditt ja) + case 6 | 0 vanlige fødselsnumre. Ingen art. 9-felt sendes til en modell (test) |
| 5 Undervisningspakke | Oppgaveark, fasit og diskusjonsspørsmål per case | En kollega kan kjøre en case uten deg |

## Del G. Ikke med nå
Ekte persondata · elevkontoer eller innlogging i selve arenaen · finjustering av modeller · Colab-utvidelsen i VS Code · å endre Datafinners seks spørsmål.

## Åpne beslutninger (dine)
1. Skal D3 (rette fødselsnumrene i AGYs personverndatabase) gjøres nå, før noe annet?
2. Hvilken KI skal elevene bruke: `google.colab.ai`, en lokal modell, eller Datafinner-API-et bak innlogging?
3. Hvem er elevene (nivå), og hvor mye tid har dere per case?

*Kilder til Del A:* [googlecolab/colab-mcp](https://github.com/googlecolab/colab-mcp) (README og `session.py`) · [i-programmer: Colab-utvidelse for VS Code](https://www.i-programmer.info/news/90-tools/18498-google-launches-colab-extension-for-visual-studio.html) · [Medium (Google Colab): google.colab.ai](https://medium.com/google-colab/introducing-google-colab-ai-the-easiest-way-to-use-generative-ai-in-colab-no-setup-required-eee01230e0cf)
