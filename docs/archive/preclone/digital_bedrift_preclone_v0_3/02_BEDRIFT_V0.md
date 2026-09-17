---
title: "Syntetisk norsk KI-bedrift – v0"
date: 2026-09-13
status: provisional
category: company-context
---

# Status

Dette er en foreløpig bedriftsmodell som skal tåle at mer informasjon kommer senere.

Arbeidsnavn:

**Sørlandet KI og Læring**

Navn, selskapsform, tjenester og roller er ikke låst ennå.

# Formål

En syntetisk digital bedrift der virtuelle ansatte kan utføre realistisk kunnskapsarbeid i et kontrollert lokalt miljø.

Bedriften skal brukes til:

- agenttrening og testing
- research og dokumentarbeid
- kurs- og innholdsproduksjon
- prosjektarbeid
- salg og kundeoppfølging med syntetiske kunder
- enkel drift og økonomisimulering
- MCP- og workflow-testing
- sammenligning av ChatGPT, Claude og lokale modeller

# Eiermodell

```text
Eier / styreleder
      │
      v
Daglig leder-agent
      │
 ┌────┼──────────────┬──────────────┐
 v    v              v              v
KI    Research       Kurs           Drift
```

Eier skal være siste godkjenner for eksterne eller irreversible handlinger.

# Første fem roller

## Daglig leder

Prioriterer, fordeler arbeid, samler status, vurderer risiko og eskalerer beslutninger.

## KI- og automatiseringskonsulent

Arbeider med agentflyter, MCP, integrasjoner, prototyper og teknisk dokumentasjon.

## Research- og dokumentkonsulent

Finner kilder, vurderer kvalitet, lager notater og skiller fakta fra antakelser.

## Kurs- og innholdsansvarlig

Lager kurs, øvelser, tilpasninger og pedagogiske leveranser.

## Administrasjons- og driftsansvarlig

Følger prosjekter, frister, aktiviteter, fakturagrunnlag og syntetiske kundedata.

# Tre handlingsnivåer

## Kan gjøre selv

- lese syntetiske/interne data
- søke og analysere
- lage notater og utkast
- opprette interne oppgaver
- foreslå prosjektplaner
- kontrollere dokumenter
- kjøre godkjente tester i simuleringsmiljø

## Krever eiergodkjenning

- sende ekstern kommunikasjon
- publisere
- godkjenne tilbud
- endre pris
- endre kundedata
- gi bredere verktøytilgang
- påta virksomheten kostnad

## Ikke tillatt uten eksplisitt engangsgodkjenning

- betale
- signere avtale
- slette vesentlige data
- håndtere ekte personopplysninger i treningsmiljøet
- dele hemmeligheter
- endre sikkerhetsregler

# Bedriftens første systemer

Vi bruker i første prototype TheAgentCompany sine arbeidsflater der det gir verdi:

```text
RocketChat  -> intern kommunikasjon
Plane       -> prosjekter og oppgaver
ownCloud    -> dokumenter
GitLab      -> kode og issues
```

Vår styring skal ligge utenfor disse tjenestene.

# Bedriftsminne

```text
company/
  identity.md
  services.md
  customers.md
  decision_rules.md
  policies/

agents/
  daglig-leder.md
  ki-konsulent.md
  research.md
  kurs.md
  drift.md

projects/
  <prosjekt>/
    brief.md
    sources/
    decisions.md
    deliverables/
```

# Ikke låst ennå

- ekte firmanavn
- selskapsform
- priser
- kundegrupper
- hvilke av dine eksisterende masterprompter som skal tilhøre hvilken rolle
- hvilke MCP-servere som skal være med i prototype 1
- om ChatGPT, Claude eller en lokal supervisor skal være primær daglig leder-runtime
