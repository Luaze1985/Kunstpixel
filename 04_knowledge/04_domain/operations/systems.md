# Systemlandskap (Systems & Infrastructure)

For å holde treningen ubyråkratisk og umiddelbart kjørbar lokalt, bruker museet en lettbeint, moderne verktøystack:

## 1. Samlingsdatabase (Collection Database)
- **Teknologi:** SQLite eller lokal strukturert JSON (`data/samling.db` / `data/artworks.json`).
- **Formål:** Primærkilde for alle verk, kunstnere, datering, fysisk plassering (Sal A, Sal B, Magasin 1) og bevaringsstatus.
- **Tilgang:** Aksesseres utelukkende via definerte MCP-verktøy / plugins.

## 2. Dokument- og kunnskapsarkiv (ownCloud / Lokal filstruktur)
- **Formål:** Lagring av ferdiggodkjente utstillingskataloger, veggtekster, audiomanus og kuratornotater.
- **Struktur:** `docs/exhibitions/`, `docs/wall_texts/`, `docs/audio_guides/`.

## 3. Oppgave- og prosjektstyring (Plane / Markdown Backlog)
- **Formål:** Koordinere oppgaver mellom direktør, kurator, formidler og drift.
- **Struktur:** Kanban-tavle med statuser: `Backlog` -> `In Progress` -> `Review` -> `Approved` -> `Live`.

## 4. Kommunikasjonsflate (RocketChat / Agent Channel)
- **Formål:** Tverrfaglig dialog mellom agenter og mennesker for avklaringer og varsler.
- **Kanaler:** `#ledelse`, `#kuratering-formidling`, `#publikumsvert`, `#system-feil`.
