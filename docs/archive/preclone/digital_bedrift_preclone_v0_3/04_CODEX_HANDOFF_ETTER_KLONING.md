---
title: "Codex handoff – etter lokal kloning"
date: 2026-09-13
status: draft
category: handoff
---

# Oppdrag

Arbeid kun som kartlegger for Sprint 000.

Repoet `TheAgentCompany/TheAgentCompany` er nå klonet lokalt. Ikke begynn å bygge vår digitale bedrift ennå.

# Les først

Fra harness:

1. root `AGENTS.md`
2. root `AI_RULES.md`
3. relevant `coding`-workspace `AGENTS.md`
4. denne Sprint 000-pakken

Fra upstream-repo:

1. `README.md`
2. `docs/SETUP.md`
3. `servers/README.md`
4. `servers/docker-compose.yml`
5. `servers/setup.sh` / `setup.bat`
6. `servers/rocketchat/npc/NPC.md`
7. `servers/rocketchat/npc/NPC_CONFIG.md`
8. `servers/rocketchat/npc/npc_definition.json`
9. `workspaces/base_image/npc/`
10. `workspaces/README.md`

# Oppgave

Lag en filbasert teknisk kartlegging av:

- hva som starter lokalt
- hvilke tjenester som er uavhengige
- hvilke data som er forhåndslastet
- hvordan NPC-er defineres og kjøres
- hvordan RocketChat brukes som meldingsflate
- hva api-server faktisk kontrollerer
- hvilke deler som bare finnes for benchmarking/evaluering
- hvilke hardkodede antakelser som må isoleres
- hvilke API-er vi senere kan legge MCP-adaptere foran

# Regler

- Ikke endre produktkode.
- Ikke installer dependencies uten eksplisitt godkjenning.
- Ikke kjør ukjente scripts automatisk.
- Ikke kjør upstream `curl | sh` automatisk.
- Ikke vis lokale secrets i klartekst.
- Ikke koble inn ekte Gmail, kalender, CRM eller kundedata.
- Ikke legg inn LLM/API-kall i vår kode.

# Leveranser

Skriv minst:

```text
planning/
  upstream_baseline.md
  reuse_matrix.md
  architecture_decision.md
  risks.md
  open_questions.md

reviews/
  security_review.md

handoff/
  sprint_000_result.md
```

# Validering

Kjør harness-validering som gjelder for workspacet. Hvis selve upstream-repoet har trygge read-only tester eller lint-kommandoer, dokumenter dem først; ikke kjør ukjente kommandoer automatisk.

# Ferdigmelding

Rapporter:

- analysert upstream commit SHA
- filer lest
- kommandoer kjørt
- resultater
- sikkerhetsfunn
- hva som kan gjenbrukes uten endring
- hva som krever kode
- sidecar vs fork-lite anbefaling
- anbefalt Sprint 001
