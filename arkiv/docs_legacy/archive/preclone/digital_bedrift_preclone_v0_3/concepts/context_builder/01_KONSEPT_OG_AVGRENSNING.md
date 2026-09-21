# Konsept og avgrensning

## Fra refleksjonsintervju til kontekstintervju

No Excuse-materialet viser en nyttig tredeling:

- virksomhetens refleksjon,
- en forklarende sammenheng/tolkning,
- mulige handlinger.

Kontekstbygger beholder denne tankegangen, men endrer formålet. Resultatet skal ikke bare være en rapport. Det skal bli vedlikeholdbar kontekst som senere kan brukes av daglig-leder-agent, spesialistagenter, review-agenter og mennesker.

Derfor utvides hvert funn med:

- kilde,
- dato,
- status,
- sikkerhetsnivå,
- om det er fakta, beslutning, verdi, hypotese, risiko eller ukjent,
- hvilken kontekstmodul det tilhører,
- hvilke andre opplysninger det avhenger av,
- om noe motsier det,
- når det bør vurderes på nytt.

## Fra Master Prompt til kontekstsystem

Forte-materialet beskriver Master Prompt som stabil menneskelig basiskontekst. Det er nyttig, men for en virksomhet blir én stor prompt for tung og utsatt for context rot.

Kontekstbygger bruker derfor to nivåer:

### Nivå 1 — liten stabil kjerne

- virksomhetens formål,
- eier og mandat,
- verdier,
- beslutningsprinsipper,
- kvalitetskrav,
- godkjenningsgrenser,
- språk og arbeidsform.

### Nivå 2 — modulær kontekst

- roller,
- prosjekter,
- kunder (syntetiske i testfasen),
- beslutninger,
- kilder,
- historikk,
- arbeidsflyter,
- risikoer,
- åpne spørsmål.

Agenten skal hente nivå 2 selektivt etter oppgaven.

## Arbeidsobjektet er ikke «svaret»

Målet er en konteksttilstand som kan brukes senere. En god intervjurunde skal derfor etterlate:

1. mer eksplisitt kunnskap,
2. færre skjulte antakelser,
3. tydeligere usikkerhet,
4. dokumentert beslutningshistorikk,
5. bedre neste spørsmål.

## Ikke score virksomheten

Første versjon skal ikke gi modenhetsscore, karakter eller «AI-score». Den skal bruke statusord:

- **bekreftet** — eksplisitt oppgitt og kildebelagt,
- **foreløpig** — eksplisitt sagt, men kan endre seg,
- **tolket** — rimelig slutning, ikke eksplisitt bekreftet,
- **motstridende** — to kilder/utsagn peker ulikt,
- **ukjent** — viktig kontekst mangler,
- **utdatert** — var tidligere gyldig, men er erstattet.

Dette gjør systemet mer egnet som kilde for agentarbeid enn en generell konsulentrapport.
