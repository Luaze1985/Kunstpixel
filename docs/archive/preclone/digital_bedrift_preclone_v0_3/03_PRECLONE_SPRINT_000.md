---
title: "Sprint 000 – TheAgentCompany pre-clone discovery"
date: 2026-09-13
status: ready-for-local-clone
category: sprint
---

# Mål

Verifiser lokalt hva TheAgentCompany faktisk gir oss før vi tilpasser noe.

# In scope

1. Klon upstream.
2. Les repo-regler og setup.
3. Lag lokal repo-baseline.
4. Kartlegg `servers/`, `workspaces/base_image/npc/` og relevante scenariofiler.
5. Kartlegg hvilke Docker-images og porter som brukes.
6. Identifiser hardkodede credentials og nettverkskrav uten å vise hemmelige lokale verdier.
7. Kartlegg API-er for RocketChat, Plane, ownCloud og GitLab som agentene kan bruke.
8. Lag en beslutning om `sidecar` vs `fork-lite`.
9. Ikke endre upstream-kode i denne sprinten.

# Out of scope

- ingen MCP-integrasjon
- ingen egen UI
- ingen nye ansatte
- ingen oversetting til norsk
- ingen endring i service-images
- ingen ekte kundedata
- ingen ekstern e-post eller kalender

# Kvalitetsporter

Sprinten er blokkert hvis:

- repoet krever usikker bred systemtilgang som ikke kan isoleres
- secrets må legges inn i kode
- installasjon må eksponere tjenester mot eksternt nett for å virke
- vår analyse ikke kan skille upstream-data fra egne fremtidige data

# Akseptansekriterier

- [ ] Upstream commit SHA er registrert.
- [ ] Repo Health Check/baseline er lagret.
- [ ] Tjenestekart med port, data, rolle og risiko finnes.
- [ ] NPC-kjeden fra profil til RocketChat er forklart.
- [ ] MCP-gapet er dokumentert.
- [ ] Sidecar vs fork-lite er besluttet.
- [ ] Ingen upstream-produktkode er endret.
- [ ] Ingen ekte personopplysninger er introdusert.

# Neste sprint etter godkjent Sprint 000

Sprint 001 bør være én svært liten vertikal flyt:

> Eier gir en intern oppgave -> daglig leder fordeler den -> én fagagent leser syntetisk dokument -> lager utkast -> resultat og kilde logges -> eier kan godkjenne/avvise.

Ingen ekstern handling i denne sprinten.
