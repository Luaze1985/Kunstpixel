# Beslutninger

> **WIP – utdatert grunnlag.** Denne grenen er laget fra GitHub `origin/main` (7b77017), ikke fra lokal `main` (a0ab2fe). Lokal `main` har allerede LLM i `chat_hub.py` og en intern side med roller i `intern_hub.py`. Punktet «ingen LLM» under gjelder derfor bare denne grenen. Ikke flett grenen inn uten å bygge den på nytt oppå `main`.

## 2026-11-05 – Datafinner-chatten

- **LLM-laget:** Claude i Claude Code-økten er intent-laget foreløpig. Appen kaller ingen LLM og trenger ingen API-nøkkel. En ekte LLM-kobling i appen er et eget valg senere, fordi det koster penger.
- **Likt hver gang:** Appen velger rolle med faste regler (`REGLER` v1 i `src/kunstpixel/adapters/chat_hub.html`): samling → Samlingsforvalter, utstilling → Kurator, praktisk/billett/hendelse → Museumsvert, sikkerhet → Direktør, ellers → Direktør (avklar manuelt).
- **Utseende:** Chatten følger Arbeidsflyt med tre paneler: roller til venstre, chat i midten og datafinner til høyre. CSS-en leses fra `G:/Min disk/Designssystemer/arbeidsflyt` (kan overstyres med `ARBEIDSFLYT_DIR`).
- **Intern side:** Eksempelspørsmålene gjelder samling, saler, utstillinger og omvisninger, ikke billettpris.
