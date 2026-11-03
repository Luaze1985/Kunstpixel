# AGENT HANDOFF (samlet): Kunstpixel — kundedata, avstemt museum.db, feilmelding og koblingssjekk
*Timestamp: 2026-11-03 | Fra: Claude Code (sky) | Til: neste agent som skal vurdere, kontrollere eller ta arbeidet videre | Eier: Lars*

> **Start her.** Denne fila er inngangen. Den kobler sammen de tidligere overleveringene og lenker alt på GitHub, så du kan vurdere arbeidet uten å ha sett samtalen.

## 0. Rekkefølgen på overleveringene

| # | Fil | Gjelder | Status |
| :--- | :--- | :--- | :--- |
| 1 | [`docs/HANDOFF.md`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/docs/HANDOFF.md) (2026-10-17) | HR/HMS-backend, vaktarkiv | historisk |
| 2 | [`docs/HANDOFF-2026-10-20.md`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/docs/HANDOFF-2026-10-20.md) | Datafinner, API, KI-lag, datadel | historisk. Dette arbeidet ligger i `hr-konsolidering`, som denne greina bygger på |
| 3 | [`docs/HANDOFF-2026-11-03.md`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/docs/HANDOFF-2026-11-03.md) | Kundedata, årsoversikt, feilmelding, årsverk | gjelder, med tillegg her |
| 4 | [`docs/HANDOFF-DATASJO-2026-11-03.md`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/docs/HANDOFF-DATASJO-2026-11-03.md) | Oppdraget: kontrollere og ta dataene inn i en datasjø (K1–K8) | gjelder |
| **5** | **denne fila** | Samlet status, alle endringer og hva som må vurderes | **nyeste** |

Ved motstrid mellom filene er det denne fila som gjelder, deretter 4, deretter 3.

## 1. GitHub

- **Repo:** [Luaze1985/Kunstpixel](https://github.com/Luaze1985/Kunstpixel)
- **Grein:** [`claude/affectionate-einstein-1g8q56`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56)
- **PR:** [Luaze1985/Kunstpixel#6](https://github.com/Luaze1985/Kunstpixel/pull/6). Utkast, base [`hr-konsolidering`](https://github.com/Luaze1985/Kunstpixel/tree/hr-konsolidering), mergebar, ingen CI og ingen review-kommentarer.
- **Hele endringen:** [`hr-konsolidering...claude/affectionate-einstein-1g8q56`](https://github.com/Luaze1985/Kunstpixel/compare/hr-konsolidering...claude/affectionate-einstein-1g8q56)
- **`hr-konsolidering` er ikke slått inn i `main`**, og har ingen egen PR.

## 2. Status nå (målt 2026-11-03)

| Kontroll | Kommando | Resultat |
| :--- | :--- | :--- |
| Tester | `py -3.13 -m pytest` | 1780 bestått, 2 feilet, 10 hoppet over, 22 xfail. De 2 (`test_anthropic_llm`, `test_chat_hub`) krever den valgfrie pakken `anthropic`, som ikke er installert i skymiljøet, og feilet også før arbeidet |
| Statusport | `py -3.13 scripts/db_status_gate.py` | blokkerer bare på de samme 2 testene |
| Bygget `museum.db` | `py -3.13 src/kunstpixel/data/build_museum_db.py --check` | LIK. sha256 begynner med `dae3d0cd7f163b62` |
| Kundedata | `py -3.13 -m src.kunstpixel.persondata.generer --fra-csv` | 49 513 rader. sha256 begynner med `4186666f4d1de18e` |
| Koblingssjekk | `py -3.13 scripts/koblingssjekk.py --vis-kjente` | 42 OK, 1 KJENT AVVIK (B26), 0 FEIL |
| Windows | – | **ikke testet**. Alt er kjørt på Linux |

## 3. Låste beslutninger (Lars, 2026-11-02 og -03)

1. Virksomheten heter **Kunstpixel**.
2. **`dagsbesok` er sannheten** for besøk og åpne dager.
3. **`hr_ansatte` er sannheten** for ansatte. HR/HMS-pakken, kundedataene og HR-demoen bruker de samme `KP-ANS-…`-ID-ene og navnene.
4. **Det kuraterte programmet i `utstillinger` er sannheten** for hva som går nå.
5. **Fase 1 har ingen tilgangssperrer**, men all lesing er skrivebeskyttet. Sperrer kommer i fase 2.
6. **Alt er syntetisk.** Feil rettes i kildefiler, generatorer eller byggesteget, aldri for hånd i en database.
7. **Feil meldes utenom chatboten**, via `scripts/meld_feil.py`, av en ansatt som er i jobb.

## 4. Hva som er gjort, med commits

| Tema | Commits | Hovedfiler |
| :--- | :--- | :--- |
| Forslag og plan | [59a15f9](https://github.com/Luaze1985/Kunstpixel/commit/59a15f9), [a79fd0e](https://github.com/Luaze1985/Kunstpixel/commit/a79fd0e), [b0e882d](https://github.com/Luaze1985/Kunstpixel/commit/b0e882d) | [`01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/01_inbox/2026-11-02_forslag_persondata_ansatte_kunder.md), [`04_knowledge/04_domain/projects/persondata/`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56/04_knowledge/04_domain/projects/persondata) |
| Bygger på `hr-konsolidering` | [d8a16d6](https://github.com/Luaze1985/Kunstpixel/commit/d8a16d6) (merge) | – |
| Kundedata (generator, CSV, MCP) | [e2e573b](https://github.com/Luaze1985/Kunstpixel/commit/e2e573b), [683768c](https://github.com/Luaze1985/Kunstpixel/commit/683768c), [376ad45](https://github.com/Luaze1985/Kunstpixel/commit/376ad45), [0a13612](https://github.com/Luaze1985/Kunstpixel/commit/0a13612), [4a1340b](https://github.com/Luaze1985/Kunstpixel/commit/4a1340b), [cd9e843](https://github.com/Luaze1985/Kunstpixel/commit/cd9e843) | [`src/kunstpixel/persondata/`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56/src/kunstpixel/persondata), [`05_data/persondata/`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56/05_data/persondata), [`src/persondata_mcp.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/persondata_mcp.py) |
| Funn fra uavhengig gjennomgang (atomisk bygg, CSV-validering, YAML) | [7bb7fa5](https://github.com/Luaze1985/Kunstpixel/commit/7bb7fa5) | `generer.py`, `config.py`, `innstillinger.yaml` |
| Kalibrering mot `dagsbesok` (K1–K5) | [d60696f](https://github.com/Luaze1985/Kunstpixel/commit/d60696f), [e74fbb2](https://github.com/Luaze1985/Kunstpixel/commit/e74fbb2) | `kunder.py`, [inspeksjonen](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/04_knowledge/04_domain/projects/persondata/2026-11-02_inspeksjon_integrasjon.md) |
| Årsoversikten avstemt mot `dagsbesok` | [8c4c5b3](https://github.com/Luaze1985/Kunstpixel/commit/8c4c5b3) | [`src/kunstpixel/core/intern/leveranse.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/kunstpixel/core/intern/leveranse.py) (`_H`) |
| Feilmelding uten chatbot | [77832c7](https://github.com/Luaze1985/Kunstpixel/commit/77832c7) | [`src/kunstpixel/feilmelding/`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56/src/kunstpixel/feilmelding), [`scripts/meld_feil.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/scripts/meld_feil.py), [`05_data/feilmeldinger/`](https://github.com/Luaze1985/Kunstpixel/tree/claude/affectionate-einstein-1g8q56/05_data/feilmeldinger) |
| HR/HMS-pakken bruker `hr_ansatte`, årsverk stemmer | [c4b0b44](https://github.com/Luaze1985/Kunstpixel/commit/c4b0b44) | [`src/kunstpixel/core/intern/hr_hms_pakke.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/kunstpixel/core/intern/hr_hms_pakke.py) |
| Gamle personnavn | [660f330](https://github.com/Luaze1985/Kunstpixel/commit/660f330), [06b3512](https://github.com/Luaze1985/Kunstpixel/commit/06b3512) | migreringsplanen og casepakken SYK-06 (Astrid Holmvik) |
| Overleveringer | [d0b44fa](https://github.com/Luaze1985/Kunstpixel/commit/d0b44fa), [b4742eb](https://github.com/Luaze1985/Kunstpixel/commit/b4742eb) | `docs/HANDOFF-2026-11-03.md`, `docs/HANDOFF-DATASJO-2026-11-03.md` |
| Koblingssjekk (A/B) | [ec4ed4d](https://github.com/Luaze1985/Kunstpixel/commit/ec4ed4d) | [`src/kunstpixel/data/koblinger.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/kunstpixel/data/koblinger.py), [`scripts/koblingssjekk.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/scripts/koblingssjekk.py), [`tests/test_koblinger.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/tests/test_koblinger.py) |
| 8 koblingsavvik rettet (B18–B25) | [ebf2e3e](https://github.com/Luaze1985/Kunstpixel/commit/ebf2e3e) | `rett_koblingsavvik` i [`build_museum_db.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/kunstpixel/data/build_museum_db.py), [`org_builder.py`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/src/kunstpixel/data/org_builder.py), [`05_data/hr_demo/seed.json`](https://github.com/Luaze1985/Kunstpixel/blob/claude/affectionate-einstein-1g8q56/05_data/hr_demo/seed.json) |
| Kontroll for overlapp i salene (B26, B27) | [26b800d](https://github.com/Luaze1985/Kunstpixel/commit/26b800d) | `koblinger.py` |

## 5. Hva du bør vurdere (i prioritert rekkefølge)

1. **Rettingene i `museum.db` er gjort i byggesteget** (`rett_koblingsavvik`), ikke i det frosne grunnlaget eller i arkivgeneratoren.
   - Fordel: grunnlaget er urørt, og alt er deterministisk.
   - Ulempe: kildefila for vakter har 54 994 vakter, mens databasen har 54 258.
   - Vurder om rettingene på sikt bør flyttes inn i `archive_generator.py`.
2. **Agenten har bygget `museum.db` selv,** tre ganger, etter eksplisitt ønske fra Lars. `AGENTS.md` sier at bare Lars bygger. Hvert bygg er kontrollert tabell for tabell mot det forrige, slik at bare de tiltenkte tabellene endret seg.
3. **B26: 64 saloverlapp i arkivet**, alle med fokusrom. Ikke rettet. Lars må avklare hva et fokusrom er:
   - et eget rom;
   - deler sal med en hovedutstilling;
   - tar over salen.
4. **Skjønnsvalg som bør ses over:**
   - B18: publikumsvakter på stengte dager er **fjernet**, ikke flyttet.
   - B24: «Lys innenfra» har fått 1/3 av besøket og budsjettet.
   - B19: 6 952 vakter i monteringsuker har tom `utstilling_id`.
   - B21/B22: erstatteren er den lengst ansatte i samme stilling.
   - HR/HMS-pakken: rollekoblingen `ROLLE_FOR_STILLING`.
5. **Klassifisering:** 29 av 44 tabeller i `museum.db` mangler `datakilde` og regnes derfor som ekte av `datapolicy.py`. Se overlevering 4, §5.
6. **Hosting:** `deploy/demo/Dockerfile` kopierer hele `museum.db` til en VPS. Kundedataene ligger derfor med vilje i en egen `persondata.db`.
7. **Ikke rettet, mindre:**
   - `faker` har ingen øvre versjonsgrense.
   - MCP-spørringer har ingen tidsgrense.
   - Feilmeldingssiden har ingen innlogging.
   - To eksisterende skript skriver om CSV-er med CRLF. Det gjelder `tests/test_org_builder.py` og `h5_governance_builder.eksporter_csv_filer()`, og påvirker `05_data/mock_*.csv`. Kjør `git checkout -- <fil>` før du committer.
8. **Kildeteksten i casepakken** (`source_paste_2026-10-20.txt`) har fortsatt det opprinnelige personanavnet, med vilje for sporbarhet.

## 6. Slik vurderer du raskt (15 minutter)

Kjør fra rotmappa i repoet:

```bash
git fetch origin claude/affectionate-einstein-1g8q56 && git checkout claude/affectionate-einstein-1g8q56
```

```bash
python -m pip install -e . pytest
```

```bash
python -m src.kunstpixel.persondata.generer --fra-csv
```

```bash
python scripts/koblingssjekk.py --vis-kjente
```

```bash
python src/kunstpixel/data/build_museum_db.py --check
```

```bash
python -m pytest -q
```

Forventet: 42 OK og 1 kjent avvik, `LIK`, og 1780 bestått (2 feiler uten `anthropic`). Etter pytest må du kjøre `git checkout -- 05_data/mock_*.csv`, fordi testene skriver om de fire filene.

## 7. Neste steg som venter på Lars

1. Svar på B26 (fokusrom).
2. Test på Windows med kommandoene i §6 (bruk `py -3.13` i stedet for `python`).
3. Bestem plattform for datasjøen. Se overlevering 4.
4. Bestem om PR #6 skal slås sammen inn i `hr-konsolidering`, og om `hr-konsolidering` skal inn i `main`.
