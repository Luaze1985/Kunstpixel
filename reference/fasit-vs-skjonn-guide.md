# Samlingsdata for KI i drift: Fasit vs. Skjønn

Dette er referansemalen og sjekklisten for hvordan man designer eller forklarer KI-systemer koblet til samlingsdata, registre og fagsystemer.

## 1. Den 2-delte kjernemodellen

| Dimensjon | FASIT (Sannhetskilde) | SKJØNN (KI / Språkmodell) |
| :--- | :--- | :--- |
| **Teknologi** | Relasjonsdatabase (SQLite/PostgreSQL) + FastMCP | LLM (f.eks. Claude, GPT, Gemini) + Persona |
| **Spørsmålstyper** | "Hvor mange?", "Hvor henger X?", "Hva koster?", "Er Y godkjent?" | "Hvordan forklarer jeg dette til et barn?", "Oppsummer temaene", "Høflig tone" |
| **Toleranse for feil** | **0 % feiltoleranse** (Deterministisk) | Høy fleksibilitet i ordlyd og tilpasning |
| **Typisk felle** | Å la LLM-en "telle" eller "huske" fakta i hodet | Å låse KI-ens svar med stive if/else-tekstmaler uten empati |

---

## 2. RAG vs. Relasjonsdatabase: Når brukes hva?

### Bruk Relasjonsdatabase (SQLite / FastMCP) når:
1. **Eksakt telling:** Du må vite nøyaktig antall verk, ansatte eller ledige skift.
2. **Filtrering på faste attributter:** Sal, årstall, teknikk, pris, status.
3. **Integritet og sikkerhet:** Data må være skrivebeskyttet (`mode=ro`) og reviderbart.
4. **Relasjoner:** Kobling mellom kunstner, verkskort, utstilling og fysisk sal.

### Bruk RAG / Semantisk søk når:
1. **Ustrukturerte fritekst-arkiver:** Gamle styreprotokoller, kuratortekster på 100 sider uten faste felter.
2. **Tematisk utforskning:** "Finn kunstverk eller tekster som handler om melankoli og skog", der nøkkelord ikke nødvendigvis matcher.
3. **Bred research:** Bakgrunnsdokumenter der eksakt telling ikke er målet.

---

## 3. Kunstpixel som referansearkitektur

```
[ Bruker / Publikumsvert ]
         │
         ▼
[ Språkmodell (LLM / Persona) ]
         │ (Kaller definerte verktøy)
         ▼
[ FastMCP Server (src/mcp_server.py) ]
         │ (Kjører SQL-spørringer)
         ▼
[ SQLite Database (05_data/museum.db?mode=ro) ]
```

* **Ingen fri SQL for modellen:** Modellen har kun tilgang til avgrensede, type-trygge verktøy (f.eks. `get_room_artworks`, `search_collection`).
* **Sikkerhet i bunn:** Databasen åpnes alltid som skrivebeskyttet (`mode=ro`).
