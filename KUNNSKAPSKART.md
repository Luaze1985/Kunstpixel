# Kunnskapskart — les dette først, uansett hvilken AI du er

Dette er inngangspunktet for enhver AI som jobber i dette prosjektet — Codex, Claude, eller noe annet. Poenget er at ingen skal måtte lete seg frem til strukturen på nytt, eller anta at én fil forteller hele historien.

## 1. Hva dette er

**Kunstpixel** — en felles treningsarena og teknologisk verktøykasse for to gründere som bygger AI-agenter, MCP-verktøy, innhold og automatisering. Fullt formål og de 4 kjernepunktene finnes i `00_felles/FORMAAL.md`.

## 2. Hvem eier hva — les i denne rekkefølgen

| Trenger du... | Les dette |
|---|---|
| Felles formål for gründerne og samarbeidsmodell | `00_felles/FORMAAL.md` |
| Begrepsdefinisjoner på enkelt norsk | `00_felles/ordliste.yaml` |
| Tekniske fakta, kommandoer, kritiske regler | `AGENTS.md` (roten) |
| Overordnet prosjektforståelse og hurtigstart | `README.md` (roten) |
| Hvilke roller finnes og hva de gjør | `03_team/team_roster.md` |
| Domenebegreper (hva er en «samling», en «veggtekst») | `04_knowledge/04_domain/` og `00_felles/ordliste.yaml` |
| Detaljerte rolle-systemprompter | `04_knowledge/03_prompts/*.md` |
| Selve motoren og verktøyene | `src/kunstpixel/` |

## 3. Roller og struktur

Roller finnes i definerte former (menneskelig oversikt i `03_team/team_roster.md`, detaljert LLM-prompt i `04_knowledge/03_prompts/`, og kjørbare subagenter i `.claude/agents/`).

## 4. Datamodellen som graf (entiteter og relasjoner)

```
Kunstner ──(1:mange)──> Verk ──(mange:1)──> Sal
                          │
                          └──(mange:mange via utstilling_verk)──> Utstilling
Sal ──(1:mange)──> Hendelse
Verk ──(mange:1, valgfri)──> Hendelse (f.eks. omvisning knyttet til et verk)
publikum_faq: fristående oppslagstabell for praktiske spørsmål
```

## 5. Kjent avvik / oppfølging

Rolle-systemprompts i `04_knowledge/03_prompts/` (kurator, formidler, samlingsforvalter, driftsansvarlig, museumsdirektor) bruker en generisk `read_query`/`write_query` SQL-tilgang mot norske tabellnavn (`verk`, `kunstnere`, `saler`...), mens `AGENTS.md` og `README.md` dokumenterer de 5 navngitte FastMCP-verktøyene (`search_collection`, `get_artwork_details`, osv.). Ved endring, husk å bevare read-only skrivebeskyttelse mot databasen.
