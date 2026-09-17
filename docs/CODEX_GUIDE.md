# Hvordan bruke ChatGPT Codex med Aura Kunstmuseum

Dette dokumentet forklarer hvordan de to gründerne kan bruke **OpenAI Codex** (i ChatGPT Desktop-appen eller via Codex CLI) til å jobbe, eksperimentere og kode videre på Aura Kunstmuseum.

---

## 💡 Hva er ChatGPT Codex?

OpenAI Codex fungerer som et utviklermiljø inne i ChatGPT (og via terminalen) som kan:
1. **Lese prosjektets kode og regler** automatisk via [`AGENTS.md`](../AGENTS.md).
2. **Kjøre lokale verktøy og tester** (f.eks. `pytest` og Python-skript).
3. **Kalle museets MCP-verktøy direkte** over stdio via konfigurasjonen i [`.codex/config.toml`](../.codex/config.toml).

---

## 🛠️ Oppsett og Forutsetninger

Codex trenger ingen kompliserte sky-oppsett eller OpenAPI-tunneler for å fungere. Alt er satt opp lokalt i repoet:

- **Instruksjonsfil:** [`AGENTS.md`](../AGENTS.md) i roten blir automatisk lest av Codex ved oppstart.
- **MCP-konfigurasjon:** [`.codex/config.toml`](../.codex/config.toml) peker direkte til museets MCP-server:
  ```toml
  [mcp.servers.aura-museum]
  command = "py"
  args = ["-3.13", "-m", "src.kunstpixel.core.mcp_server"]
  ```

---

## 🚀 Slik starter du Codex

### Alternativ 1: I ChatGPT Desktop App
1. Åpne **ChatGPT Desktop App** på maskinen din.
2. Åpne **Codex / Workspaces**-fanen.
3. Velg prosjektmappen: `g:\Min disk\Fellesprosjekt KI`.
4. Codex vil umiddelbart registrere `AGENTS.md` og `[mcp.servers.aura-museum]`.

### Alternativ 2: Fra Terminalen (Codex CLI)
Dersom du har installert OpenAI Codex CLI:
```powershell
cd "g:\Min disk\Fellesprosjekt KI"
codex
```

---

## 💬 Eksempler på hva du kan be Codex om

Siden Codex kjenner hele arkitekturen, databasen og testene, kan du gi den konkrete oppgaver i vanlig dagligtale:

### 1. Eksperimentere med nye agent-verktøy
> *"Kan du lage et nytt verktøy for kuratoren som lister alle uutstilte verk i magasinet MAG-1, og legge det til i MCP-serveren?"*

### 2. Kjøre og verifisere tester
> *"Kjør alle testene i prosjektet og sjekk om samlingsverktøyene oppfører seg som forventet."*

### 3. Utforske eller berike samlingen
> *"Bruk MCP-verktøyet search_collection til å finne alle verk av Theodor Kittelsen, og fortell meg hvilke saler de henger i."*

### 4. Lage nye automatiseringer
> *"Lag et Python-skript som genererer en ukentlig e-post-oppsummering av alle kommende arrangementer fra databasen."*

---

## 🔒 Sikkerhetsgarantier
- Databasen `05_data/museum.db` åpnes alltid som `mode=ro` (read-only).
- Codex kan aldri overskrive eller slette kunstverk eller kuratoriske tekster ved et uhell.
- Alle endringer kan til enhver tid verifiseres med `py -3.13 -m pytest`.
