# Forslag til innføring i Kunstpixel

**Kontrollert kontekst per 20. oktober 2026:** `main` er fortsatt museumsvert og samlingsdatabase. Feature branch `feature/hr-simulator-syntetisk-innleie` + draft PR #1 har HR-001–003, syntetiske scenarioer, planleggingsgrunnlag og Python-/SQLite-komponenter. Issue #2 bestiller fase A. Denne pakken er derfor kun et tillegg for *planlegging* av senere faser.

1. Ikke endre `05_data/museum.db` eller den publikumsrettede museumsverten.
2. Plasser disse dokumentene i `04_knowledge/04_domain/projects/hr_simulator/research_hr_2024_2026/` hvis de tas inn i repoet.
3. Hold `scenarios/HR-004..017.json` atskilt fra motorens eksisterende kjørbare `HR-001..003`. De 14 filene følger et forslagsskjema, **ikke** eksisterende `engine.py`-schema, og kan ikke kjøres uten adapter.
4. Fullfør testet fase A før nye scenarioer. Bygg deretter ett case om gangen som test-fixture med fakta, roller, hard fail-regler, mulige handlinger og expected outcome.
5. Gi hver enkelt case to perspektiver: (a) forsvarlig virksomhetsnytte, (b) målrettet forsøk på å få modellen til å bryte grenser.
6. Legg rettighetskontroll i backend før data inngår i prompt. Logg bare referanser, beslutninger og vurderingsgrunner, ikke konfidensiell fulltekst.
7. Mål nytte som **merverdi over regelmotor** og **sikkerhet ved uønskede forespørsler**. Ikke mål bare antall oppgaver løst.

## Faktisk status og kjent datakvalitetsproblem

`ANALYSE_DATAFANGST_LLM_2026-10-17.md` beskriver fire ukers plan, 11 personer og 20 aktiviteter, hvor regelmotoren dekker alle opprinnelig åpne ordinære roller. Datagrunnlaget har fem oppgavetyper gjentatt ukentlig. Den større syntetiske historikken fra 2010–2026 har umulige dagsummer, manglende klokkeslett og uten person-ID-samsvar med ukeplanen. Dette arkivet skal derfor ikke brukes som sanne personprofiler, lovlighetskontroll, hvileanalyse eller prediksjonsgrunnlag.

## Første tre implementeringer

A. `HR-013`: Rolleskillet i varslerens identitet (autorisasjon, indirekte identifikasjon, fakta/påstand).
B. `HR-005`: Sensor-/produksjonstall som frister til individmåling (formål, drøfting, dataforveksling).
C. `HR-012`: Fraværskapasitet kontra sykdomsprediksjon (høyt press, helseinferens, aggregering).

## Nytt supplement: samtaletrening

`conversation_training/` er importert fra brukerens katalogtekst og **skal ikke ukritisk committes** til offentlig repo. Undersøk gjenbruksrettighet, om navn/persona er fiktive og om metadata inneholder opplysninger om faktiske personer. Etter slik kontroll kan et begrenset utvalg legges i f.eks. `04_knowledge/04_domain/projects/hr_simulator/dialogue_training/`.

Bygg en egen samtalemotor i neste fase i stedet for å sende samtalekort inn i eksisterende `engine.py` som om de var vaktplan-JSON. Hvert kort trenger strukturert persona, mål, informasjonsregler, redaksjonelt manus, kunnskapsgrunnlag og evalueringsrubrikk.

Bruk `conversation_training/links_to_hr_cases.json` til å se sammenhenger uten at scenarioene blir en uoversiktlig datamodell. HTML-visningen kan kjøres lokalt og krever ingen server.
