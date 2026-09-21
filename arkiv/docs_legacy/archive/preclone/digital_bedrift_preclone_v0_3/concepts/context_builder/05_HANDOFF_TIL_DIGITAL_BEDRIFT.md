# Handoff til digital bedrift

## Anbefalt plassering

Denne grenen bør være et separat kontekstlag ved siden av agent-/office-miljøet.

```text
Digital bedrift
│
├─ owner / human control
│
├─ context_builder      ← denne grenen
│  ├─ masterprompt
│  ├─ interview engine
│  └─ context store
│
├─ policy / approvals
│
├─ agents
│  ├─ daglig leder
│  ├─ KI/automatisering
│  ├─ research/dokument
│  ├─ kurs/innhold
│  └─ administrasjon/drift
│
├─ tools / MCP adapters
│
└─ simulated office
   ├─ RocketChat
   ├─ Plane
   ├─ ownCloud
   └─ GitLab
```

## Første praktiske bruk

Ikke start med full organisasjonskartlegging.

Bruk Kontekstbygger til å gjøre første vertikale arbeidsflyt tydelig nok:

```text
Eier gir oppgave
  ↓
Daglig leder tolker mål
  ↓
Velger spesialist
  ↓
Spesialist bruker riktig kontekst
  ↓
Lager artefakt
  ↓
Review mot kvalitetskrav
  ↓
Eier godkjenner / avviser
  ↓
Beslutning + læring lagres
```

Kontekstbygger skal før denne flyten avklare bare det som trengs:

- eierens hensikt,
- daglig leders mandat,
- spesialistens mandat,
- relevant kildehierarki,
- artefaktets kvalitetskrav,
- når eier må godkjenne,
- hvor resultat og beslutning lagres.

## Anbefalt senere teknisk skille

Masterprompten er styringslogikk og bør kunne kjøres av ulike modeller. Kontekstdata bør lagres i åpne filer/schemas slik at de ikke bindes til ChatGPT, Claude eller én lokal modell.

Dette betyr:

- prompt ≠ database,
- modell ≠ virksomhetsminne,
- connector ≠ sannhetskilde,
- chat ≠ beslutningslogg.
