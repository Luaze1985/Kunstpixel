# Chat_hub i Arbeidsflyt-trepanel (arkivert 2026-11-05)

Et forsøk på å gi web-chatten Arbeidsflyt-utseende med tre paneler: roller til venstre, chat i midten og datafinner til høyre. Rollen velges med faste regler (`REGLER` v1), og appen bruker ingen LLM.

**Hvorfor arkivert:** Forsøket bygde på GitHub `origin/main` (7b77017), som var utdatert. Lokal `main` har allerede LLM i `chat_hub.py` og en intern side med roller i `intern_hub.py` (`src/kunstpixel/core/intern/`). Ta ideene videre der, ikke herfra.

- `chat_hub.html`: siden. Den besto Arbeidsflyt-validatoren (15/15).
- `chat_hub_gammel.py`: den gamle chat_hub, som leste HTML fra fil og serverte CSS fra designsystemet.
- `BESLUTNINGER.md`: beslutningene fra økten. Punktet om at appen ikke har LLM, gjaldt bare det gamle grunnlaget.

Ingenting her kjøres eller testes.
