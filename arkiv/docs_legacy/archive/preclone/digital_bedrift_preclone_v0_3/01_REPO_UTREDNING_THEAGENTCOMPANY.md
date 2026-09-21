---
title: "Repo-utredning – TheAgentCompany"
date: 2026-09-13
status: preliminary
category: research
---

# Kort konklusjon

TheAgentCompany er relevant som **simulert arbeidsmiljø**, men er ikke en ferdig plattform for å drive en egen agentbedrift.

Det bør derfor brukes som upstream/referanse og mulig prototypegrunnmur, ikke ukritisk som permanent arkitektur.

# Hva repoet faktisk er

Repoets eget formål er et benchmark for LLM-agenter som utfører profesjonelle oppgaver. Det inneholder et selvstendig simulert bedriftsmiljø og 175 oppgaver.

Hovedstruktur:

```text
TheAgentCompany/
├── docs/
├── evaluation/
├── servers/
│   ├── api-server/
│   ├── gitlab/
│   ├── owncloud/
│   ├── plane/
│   └── rocketchat/
└── workspaces/
    ├── base_image/
    └── tasks/
```

# Verdifulle deler

## 1. Ferdig kontormiljø

Serveroppsettet starter blant annet GitLab, Plane, ownCloud og RocketChat med forhåndslastede data. Dette er den sterkeste grunnen til å undersøke repoet videre.

## 2. Syntetiske medarbeidere

Repoet har NPC-profiler med navn, rolle, offentlig informasjon, personlighet og kontekst. NPC-ene er knyttet til RocketChat og Sotopia.

Dette gir oss en eksisterende modell for å representere digitale ansatte, selv om vår profil senere bør være enklere, mer arbeidsrettet og mindre rollespillpreget.

## 3. Reelle arbeidsoppgaver

De 175 oppgavene dekker blant annet HR, økonomi, prosjektstyring, administrasjon, research og software engineering.

Disse er svært interessante som:

- inspirasjon til våre egne øvingsscenarioer
- evalueringsgrunnlag
- test av agentenes verktøybruk
- mønster for tydelige forventede slutt-tilstander

# Begrensninger som betyr noe for oss

## Ikke MCP-basert

Det finnes ingen MCP-integrasjon i repoets nåværende kodebase. MCP må bygges som et eget adapter-/verktøylag.

## NPC-ene er benchmark-kolleger

NPC-ene er laget for samtalescenarioer og evaluering. Dokumentasjonen sier blant annet at flere NPC-er i samme kanal ikke egentlig samtaler med hverandre; de svarer på brukerens melding. Dette er ikke tilstrekkelig som full fleragent-organisasjon.

## Hardkodet benchmark-infrastruktur

Repoet bruker blant annet:

- domenet `the-agent-company.com`
- standardbrukere og standardpassord
- host networking
- Docker socket mount
- ferdigpubliserte images

Dette er greit i et lokalt benchmark, men må ikke bli vår sikkerhetsmodell.

## Tung lokal installasjon

Offisiell setup oppgir minst 30 GB ledig disk. Det betyr at repoet ikke er en liten startpakke.

## Eldre/tunge komponenter

Repoets compose-oppsett bruker blant annet Rocket.Chat 5.3.0 og MongoDB 5.0-variant. Før vi gjør dette til noe varig, må image-versjoner og lisens-/vedlikeholdsstatus gjennomgås.

# Sikkerhetsfunn før vi kloner

Dette er ikke nødvendigvis sårbarheter i benchmarkets tiltenkte bruk, men de er stoppunkter for vår produktvariant:

1. Standardpassord ligger i dokumentasjon og compose.
2. Redis-passord er hardkodet.
3. Docker socket blir montert i api-server.
4. Setup-guiden ber på Linux/Mac om brede rettigheter på Docker socket.
5. Flere tjenester eksponeres direkte på lokale porter.
6. Vår variant må bruke `.env.example`, genererte lokale credentials og least privilege.

# Gjenbruksmatrise

| Del | Direkte | Konfigurasjon | Kode | Vent |
|---|---:|---:|---:|---:|
| Docker-basert lokal arbeidsplass |  | X |  |  |
| RocketChat som intern kommunikasjon | X | X |  |  |
| Plane som oppgave/prosjektflate | X | X |  |  |
| ownCloud som syntetisk dokumentflate | X | X |  |  |
| GitLab som intern kodeflate | X | X |  |  |
| NPC-profilformat |  | X | X |  |
| Sotopia-basert kollegasimulering |  | X | X |  |
| Benchmark evaluation |  |  |  | X |
| OpenHands-integrasjon |  |  |  | X |
| 175 oppgaver |  | X | X |  |
| MCP |  |  | X |  |
| Eiergodkjenning/policy-gates |  |  | X |  |
| Claude/ChatGPT som styringslag |  |  | X |  |

# Foreløpig arkitektur

```text
                 EIER / STYRELEDER
                        │
                        v
              STYRING / GODKJENNING
        (ChatGPT / Claude / lokal agentleder)
                        │
                        v
                 POLICY / ROUTER
          read / draft / write / external
                        │
          ┌─────────────┼─────────────┐
          v             v             v
        MCP          interne       scenario-
      adaptere        API-er        motor
          │             │             │
          └──────┬──────┴──────┬──────┘
                 v             v
              AGENTER       EVALUERING
                 │
                 v
 ┌───────────────┼─────────────────────────┐
 v               v             v           v
RocketChat      Plane        ownCloud     GitLab
```

# Anbefalt upstream-strategi

Første lokale prøve kan gjøres fra en ren clone av upstream for å forstå miljøet.

Men permanent prosjekt bør sannsynligvis bli én av disse:

1. **Fork-lite:** behold relevante server-/NPC-deler, fjern benchmark-bagasje.
2. **Sidecar:** behold TheAgentCompany uendret som simuleringsmiljø, bygg vår styring/MCP i et separat repo som snakker med tjenestene.

Foreløpig anbefaling: **sidecar først**. Det gjør det enklere å oppdatere eller forkaste upstream uten å blande vår forretningslogikk inn i benchmark-koden.

# Kilder

- https://github.com/TheAgentCompany/TheAgentCompany
- https://github.com/TheAgentCompany/TheAgentCompany/blob/main/README.md
- https://github.com/TheAgentCompany/TheAgentCompany/blob/main/docs/SETUP.md
- https://github.com/TheAgentCompany/TheAgentCompany/blob/main/servers/README.md
- https://github.com/TheAgentCompany/TheAgentCompany/blob/main/servers/rocketchat/npc/NPC.md
- https://github.com/TheAgentCompany/TheAgentCompany/blob/main/servers/rocketchat/npc/NPC_CONFIG.md
- https://arxiv.org/abs/2412.14161
