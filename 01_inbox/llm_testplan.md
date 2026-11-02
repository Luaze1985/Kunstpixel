# Testplan v2: LLM over HR og intern data

## TLDR

- **Nytt fokus:** En intern assistent for ansatte og ledelse. Den svarer på HMS, arbeidsmiljø, IK-Mat, brann, tilsynskalender, roller og personalrutiner. Kunstgalleriet og publikumsvisningene fryses som de er.
- **To trinn for modell:** Ekstern modell (Anthropic) brukes til trening og demo, bare på syntetiske data. Lokal modell (LM Studio eller Ollama) er målet for ekte HR-data. Ekte data skal aldri kunne nå en ekstern modell. **Lokal modell er satt på vent (2026-10-27).** Inntil videre får derfor ingen modell se ekte data, og H6 og H7 venter.
- **Grunnregel:** Verktøyene eier fakta, og LLM-en formulerer. Hvert svar viser kilde (fil og avsnitt). Står svaret ikke i dataene, sier assistenten at den ikke vet.
- **Gjenbruk:** LLM-laget, faktakontrollen og web-chatten fra fase 0 til 3 beholdes. De 216 testene blir stående som sikkerhetsnett.
- **Datakilder:** Governance-filene i repoet nå, ekte HR-data senere. Mangler vi data, lager vi syntetisk påfyll som er tydelig merket, og du godkjenner det.

## Hva er suksess

Alle krav må holde:

1. **Ingen oppdiktede fakta.** Tall med enhet, frister, myndigheter, roller og lovhenvisninger i svaret finnes i dataene.
2. **Ingen lekkasje.** Ekte data sendes aldri til ekstern modell. Dette sikres i kode og testes med fiendtlige skript.
3. **Kilde på alt.** Hvert LLM-svar peker på minst én kilde som finnes i verktøyresultatet.
4. **Ærlig «vet ikke».** På spørsmål som dataene ikke dekker, avslår assistenten i stedet for å gjette.
5. **Rett person får rett data.** En rolle ser bare det den har lov til å se.
6. **Det tåler svikt.** Er modellen nede, treg eller gir den feil, vises det regelbaserte svaret.

| Mål | Krav |
|---|---|
| Svar med feil fakta | 0 % |
| Ekte data til ekstern modell | 0 tilfeller, håndhevet i kode |
| Svar med kildehenvisning | 100 % |
| Riktig avslag på spørsmål uten dekning | 100 % på prøvesettet |
| Fallback til regelbasert svar | under 20 % ekstern modell, under 30 % lokal modell |

## Hva som finnes i dag

Intern data i repoet er syntetisk og strukturert:

| Kilde | Innhold |
|---|---|
| `05_data/governance/hms_arbeidsmiljo.yaml` | Ergonomi, løft, alenearbeid, varsling, vernerunder, avviksfrister |
| `05_data/governance/ik_mat_kafe.yaml` | Temperaturkrav, hygiene, sykdom og karantene, renhold |
| `05_data/governance/brann_sikring_kapasitet.yaml` | Brann, sikring, kapasitet |
| `05_data/governance/tilsynskalender.json` | Tilsyn per måned, myndighet og ansvarlig rolle |
| `05_data/governance/noexcuse_*.json/yaml` | Diagnostikk og prioriterte tiltak |
| `03_team/team_roster.md` og `04_knowledge/04_domain/roles/*.md` | Roller, ansvar og verktøytilgang |
| `04_knowledge/04_domain/operations/tool_access.md` | Minste privilegium per rolle |

Det finnes ingen personalhåndbok, vaktplaner, kontrakter eller personopplysninger. Slikt må lages som syntetisk påfyll, eller hentes fra ekte kilde senere.

Gjenbrukes fra forrige runde: `core/llm.py`, `core/fact_check.py`, kassett-avspilling, fallback-logikk og web-chatten med LLM-bryter.

## Datapolicy (bygges først)

Hver kilde får en klassifisering, og hver modell får en plassering:

| Klassifisering | Betydning | Tillatt modell |
|---|---|---|
| `syntetisk` | Laget for trening og demo. Ingen ekte personer. | Ekstern eller lokal |
| `ekte` | Ekte HR-data eller personopplysninger. | Bare lokal |

- Hver `LLMClient` har `locality: "local" | "external"`.
- En port i agenten stopper LLM-kallet hvis noe verktøyresultat har klassifisering `ekte` og modellen er ekstern. Brukeren får det regelbaserte svaret, og årsaken logges som `policy`.
- Det logges aldri persondata. Logger har bare spørsmålskategori, verktøy, modell og utfall.

## Testbare grep

1. **Ny intern agent** `InternAgent` ved siden av `MuseumsvertAgent`, med egne skrivebeskyttede verktøy: `search_hms`, `get_tilsyn`, `get_rolle`, `search_ik_mat`, `search_personalrutine`. Ingen fri SQL eller fri filsti fra modellen.
2. **Kildehenvisning som del av verktøyresultatet.** Hvert funn har `kilde` (fil) og `sti` (avsnitt i filen). Kontrollen krever at hvert LLM-svar sitter igjen med minst én gyldig kilde.
3. **Faktakontroll v2** (utvider `verify_facts`): alle tall med enhet (90 minutter, 15 kg, 14 dager, +4 °C, kl. 20:00), måneder, myndigheter, roller og lovnavn i svaret må finnes i verktøyresultatet. Ingen juridiske råd utover det dataene sier.
4. **Rollestyring.** Spørsmålet følger med en rolle. Verktøyene filtrerer etter `tool_access.md`. En rolle uten tilgang får avslag, ikke LLM-svar.
5. **Fast dato** gjennom `AURA_TODAY`, slik at «hva er neste tilsyn?» gir samme svar i testene hver dag.

## Faseplan

### H0: Baseline (ferdig)
216 tester er grønne, 4 hoppes over bevisst. LLM-lag, faktakontroll og web-chat er på plass. Museumsvertens svar henter fakta fra verktøy.

### H1: Datapolicy og klassifisering (1 økt)
- Legg til `klassifisering` på alle kilder og `locality` på alle modeller.
- Port i agenten som stopper ekte data mot ekstern modell.
- Tester: ekte testdata + ekstern FakeLLM gir `fallback_reason` som starter med `policy`. Syntetiske data + ekstern modell slipper gjennom. Lokal modell slipper alltid gjennom. Ingen logglinje inneholder spørsmålstekst fra ekte kilde.

### H2: Datalag og verktøy (1–2 økter)
- Lesere for YAML, JSON og markdown som gir små, adresserbare funn med kilde og sti.
- Verktøyene fra «Testbare grep», med tester for tom treff, ukjente nøkler og feilformat.
- Prøvesett på 40 spørsmål: 30 som dataene dekker (frister, grenser, ansvarlig rolle, rutiner) og 10 som dataene ikke dekker (feriedager, lønn, enkeltpersoner).
- Gyldne svar fra regelbasert søk for de 30 første. De 10 skal gi et ærlig «ikke i dataene».
- Port: nye tester grønne og alle 216 grønne.

### H3: Intern visning (1 økt)
- Egen intern side i web-chatten (eget endepunkt og egen port eller sti), tydelig merket som intern. Museumsvert-siden beholdes uendret.
- Viser modellnavn, kilder og eventuell fallback-grunn.
- Tester som for den offentlige chatten: tom, ugyldig og for stor melding, krasj i agenten gir 500 uten feilspor, rolle mangler gir avslag.
- Manuell port: du stiller de 40 spørsmålene og leser svarene.

### H4: Ekstern modell på syntetiske data (2 økter)
- Faktakontroll v2 og kildekrav kobles til.
- Fiendtlige skript: oppdiktet frist (30 dager i stedet for 14), feil myndighet, feil rolle, svar uten kilde, juridisk råd utover dataene, og forsøk på å få ut data fra en rolle uten tilgang. Alle skal avvises.
- Mutasjonstest: endre en verdi i en kopi av YAML-filen (alenearbeid etter kl. 21 i stedet for 20). Et innspilt svar med kl. 20 må avvises, og brukeren får 21.
- 40 svar tas opp fra ekte modell én gang og lagres som kassetter. Koster tokens, så kostnadstak settes først.
- Port: 0 feil fakta på prøvesettet, 100 % kilde, 100 % riktig avslag.

### H5: Syntetisk påfyll (etter behov)
Hvis prøvesettet viser hull, lager vi nye syntetiske filer. Hver fil merkes `klassifisering: syntetisk` og `syntetisk: true`. Du godkjenner dem før de brukes. Forslag til filer:
1. Personalhåndbok: arbeidstid, ferie, sykefravær, permisjon og overtid i generelle ordelag.
2. Anonymisert turnus-eksempel med roller i stedet for navn.
3. Onboarding-sjekkliste for nye ansatte.
4. Opplæringskrav per rolle: brannvern, HLR, IK-Mat, løft.
5. Stillingsbeskrivelser for rollene i teamoversikten.
6. Varslingsrutine og avvikshåndtering utover det HMS-filen sier.

For hver ny fil utvides prøvesettet med spørsmål og forventede kilder.

### H6: Lokal modell (2–3 økter)
- Ny `LocalLLM` mot et lokalt, OpenAI-kompatibelt endepunkt (LM Studio eller Ollama). `locality: "local"`.
- Forutsetning: avklar modellvalg og om PC-en har kraft nok. Måles først med ti spørsmål: svartid og minnebruk.
- Samme testsuite kjøres mot lokal modell. Innspilte svar kan ikke gjenbrukes, så lokal modell får egne kassetter og eget scorecard.
- Sammenlign ekstern og lokal modell på prøvesettet: feil fakta, fallback-rate, svartid. Lokal modell må holde kravene i tabellen over før den får røre ekte data.

### H7: Ekte HR-data (først etter H6)
- Manuell port: personvurdering med sjekkliste (hva slags data, hjemmel, hvem har tilgang, hvor lagres det, sletting). Du eier denne beslutningen.
- Ekte data merkes `ekte` og ligger utenfor repoet. Stien leses fra miljøvariabel, aldri committet.
- Tilgang per rolle testes med egne testroller. Ekte data brukes aldri i tester eller kassetter.
- Test som feiler hvis noe fra en `ekte` kilde havner i repoet, i kassett eller i en logg.

### H8: Løpende måling
- `pytest -m llm_live` kjøres manuelt ukentlig.
- Scorecard i `02_deliverables/llm_test/scorecard.md`: feil fakta, fallback-rate, avslagsrate, svartid, tokens og kostnad.
- Feil fakta over 0 % stopper alt annet arbeid.

## Beslutninger som gjenstår

| Spørsmål | Anbefaling |
|---|---|
| Lokal modell og maskinvare | Måles i H6. Velg modell etter test, ikke på forhånd. |
| Kostnadstak for ekstern modell | Fast månedlig tak, tokens logges per svar. |
| Hvem er «roller» i demoen | Bruk rollene i teamoversikten. Demoen lar deg bytte rolle i grensesnittet. |
| Hvor ligger ekte HR-data | Avklares før H7. |
| Syntetisk påfyll | Jeg foreslår filer i H5. Du godkjenner hver enkelt. |

## Filer som berøres (nye i kursiv)

| Fil | Endring |
|---|---|
| `src/kunstpixel/core/llm.py` | `locality`, `LocalLLM` |
| `src/kunstpixel/core/fact_check.py` | Faktakontroll v2, kildekrav |
| *`src/kunstpixel/core/intern/data.py`* | Lesere, klassifisering, funn med kilde og sti |
| *`src/kunstpixel/core/intern/tools.py`* | De fem verktøyene med rollefilter |
| *`src/kunstpixel/core/intern/agent.py`* | `InternAgent` med policy-port |
| *`src/kunstpixel/adapters/intern_hub.py`* | Intern web-chat |
| *`tests/test_intern_*.py`* | Policy, verktøy, agent, faktakontroll, visning |
| *`tests/golden/intern/`*, *`tests/cassettes/intern/`* | Fasit og innspilte svar |
| *`05_data/governance/…`* | Nye syntetiske filer i H5 |
| `AGENTS.md`, `KUNNSKAPSKART.md` | Ny regel om datapolicy og intern assistent |

## Verifisering av hele løpet

1. `py -3.13 -m pytest -v` er grønn uten at `llm_live` kjøres.
2. Test som viser at ekte testdata aldri når en ekstern modell.
3. 40 spørsmål i intern chat: 0 feil fakta, 100 % kilde, 100 % riktig avslag.
4. Mutert YAML-verdi gir den nye verdien i svaret, også når modellen husker den gamle.
5. Samme prøvesett kjørt mot lokal modell, med scorecard side om side med ekstern modell.

## Status (oppdatert 2026-10-26)

| Fase | Status |
|---|---|
| H0 baseline | Ferdig |
| H1 datapolicy | Ferdig, mutasjonstestet |
| H2 datalag, verktøy, 40 spørsmål | Ferdig. 28 av 30 dekkede spørsmål besvares av regelbasert søk |
| H3 intern visning | Ferdig, validator exit 0, prøvd i nettleser |
| H4 ekstern modell | Bygget og testet med falsk modell. **Ikke kjørt mot ekte modell**: ingen nøkkel på maskinen. Kassett mangler |
| H5 syntetisk påfyll | Bestilling og kontroll er bygget. Venter på at du lager filene med en annen språkmodell |
| H6 lokal modell | **På vent.** Lokal modell brukes ikke pt (besluttet 2026-10-27) |
| H7 ekte HR-data | **På vent.** Krever lokal modell, så ingen modell får se ekte data inntil videre |
| H8 løpende måling | Ikke startet |