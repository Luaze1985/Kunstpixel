---
title: "Digital bedrift – pre-clone startpakke"
date: 2026-09-13
status: discovery
category: handoff
---

# Formål

Dette er forarbeid før lokal kloning og før produktkode skrives.

Målet er å undersøke om `TheAgentCompany/TheAgentCompany` kan brukes som grunnlag for en syntetisk norsk KI-bedrift med virtuelle ansatte, interne arbeidsflater, kontrollert verktøybruk og senere MCP-integrasjon.

## Foreløpig beslutning

Ikke behandle TheAgentCompany som en ferdig agentplattform.

Repoet er først og fremst et benchmark for profesjonelle agentoppgaver. Det mest interessante for vårt formål er den ferdige simulerte arbeidsplassen:

- GitLab
- Plane
- ownCloud
- RocketChat
- syntetiske medarbeidere/NPC-er
- forhåndsdefinerte arbeidsoppgaver og evalueringsmønstre

Benchmark-, OpenHands- og evalueringslaget er sekundært for vår første prototype.

## Arbeidsregel

Ingen kodeendring nå. Når repoet senere klones lokalt, skal første lokale sprint være kartlegging og baseline før tilpasning.

## Hvor dette bør bo

Dette bør ikke blandes inn i produktkoden til `vibekode_til_solid_kodebase`.

Når bygging starter, opprett et eget workspace i samme harness, med `coding`-profil, for eksempel:

```text
workspaces/digital_bedrift/
```

Da kan det bruke samme regler for sprintpakker, review, tests og handoff uten å endre den låste produktretningen til Vibekode-prosjektet.


## Tillegg v0.2 - No Excuse som ledelsesgrunnlag

Det er lagt inn en egen kildepakke under `sources/noexcuse/`. Den skal foreløpig brukes som **referanse og scenario-bank**, ikke som låst organisasjonsmodell. Hovedverdien er mønsteret med 60 temaer fordelt på Identitet, Struktur, Menneske og Påvirkning, der hvert tema kobles til refleksjon, tolkningsramme og mulige tiltak.

VIBS-svarene er eksempeldata og skal ikke blandes inn i den syntetiske bedriftens faktiske identitet.

## Ny konseptgren i v0.3 — Kontekstbygger

`concepts/context_builder/` inneholder en egen masterprompt og kontekstmodell inspirert av den strukturerte refleksjonsformen i No Excuse-materialet og Context Architect/Master Prompt-prinsippene i Forte-kilden.

Formålet er å bygge virksomhetskontekst over tid, ikke å kopiere Ledelse 60:2 eller lage en fast 60-spørsmålsdiagnose.

Viktigste fil: `concepts/context_builder/02_MASTERPROMPT_KONTEKSTBYGGER.md`.
