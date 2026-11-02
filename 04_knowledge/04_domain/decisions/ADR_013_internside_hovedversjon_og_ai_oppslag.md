# ADR 013: Internside – én hovedversjon, åpent hostet, AI svarer fra dokumentene

## Status
Godkjent (2026-10-23, grilling med Lars)

## Kontekst
Internsiden har to mål: et oppslagsverk for kvalitetssystemet og dokumentasjonen, og deretter strategisk kompetanseplanlegging for 2027 i tråd med utstillinger og interne prosjekter. Alt er simulert (syntetiske data).

Fram til nå har Datafinner hatt to utgaver: hovedversjonen mot `museum.db` og en demokopi (`build_demo_db.py`, `DATAFINNER_DEMO=1`, `deploy/demo/`) uten e-post, telefon og fødselsår, og uten filverktøy. Demokopien krevde at hvert nytt verktøy ble holdt i takt med tabellutvalget `BEHOLD`, og gjorde at interne verktøy måtte holdes utenfor.

## Beslutning
1. **Én hovedversjon.** Demokopien og demomodusen fjernes helt: `build_demo_db.py`, `DATAFINNER_DEMO`, `bruk_demomodus`, `BEHOLD`/`TOMMES` og testene for dem. Hostingoppsettet i `deploy/` gjenbrukes for hovedversjonen.
2. **Åpent hostet.** Internsiden kjører mot full `museum.db` og er åpen uten innlogging. Det er greit fordi alle data er syntetiske.
3. **Claude via API med kostnadsgrense.** AI-laget bruker `LLM_PROVIDER=anthropic`. Nøkkelen står bare i miljøet til serveren. Grensen for AI-kall per time (`llm.Begrenser`) skal alltid være satt når siden er hostet. Startverdi 20 per time, siden bare Lars bruker siden i første omgang. Den justeres med en miljøvariabel.
4. **AI svarer, dokumentene er fasit.** I oppslagsverket svarer AI på spørsmål og viser hvilke håndbokpunkter svaret bygger på, merket AI-forslag. Finner den ingen kilde, sier den det. AI endrer aldri dokumentene. På siden: ett søkefelt i midten, AI-svaret kort øverst over de vanlige treffene, ingen chat. Siden virker også uten AI. ADR 012 gjelder fortsatt: md-filene er det mennesker leser, `handbok_oppslag` er indeksen.
5. **Én rolleliste for oppslagsverket.** Arbeidsroller (6–8 stk) med kobling fra stilling og fra håndbokenes målgruppe. Ikke roller A–L.

Begrepene er definert i `00_felles/ordliste.yaml`: oppslagsverk, arbeidsrolle, kompetanse, fagomrade, rollekrav, kompetanseplan, internt_prosjekt, kompetansetiltak, skjermet_varsel.

## Konsekvenser
- **Positivt:** Ett sett tabeller, verktøy og tester. Nye interne verktøy kan hviteslistes i Datafinner uten demo-hensyn.
- **Positivt:** Kompetanseplanen og oppslagsverket kan bruke samme `rollekrav`-tabell.
- **Negativt:** Demokopien kan bare gjenopprettes fra git-historikken. Vil noen innføre en demo igjen, må denne ADR-en erstattes først.
- **Risiko:** Åpen side med Claude-nøkkel. Uten kostnadsgrense kan hvem som helst bruke nøkkelen på Lars' regning.
- **Oppfølging:** AGENTS.md og `docs/DATAPIPELINE.md` nevner fortsatt demo og VPS-demo, og må oppdateres når demo-delen fjernes. Skjermingen av varsler (CASE-013) beholdes med vilje.
