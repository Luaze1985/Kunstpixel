# Spesifikasjon: Datafinner i ett vindu

**Status:** ready-for-agent (unntak er merket i hver oppgave) · **Dato:** 2026-11-06
**Grunnlag:** prototypen på `ux/ett-vindu` (`a31600c`), [plan](../plans/2026-11-06-datafinner-ux.md) med funn F1–F15, `docs/DECISIONS.md` (2026-11-06), `02_deliverables/arbeidsflyt/SPEC.md:5` (tre paneler)
**Oppgaver:** [ett-vindu/](ett-vindu/)

## Mål (besluttet av Lars 2026-11-06)
Alt i Datafinner skal være i **ett vindu med tre paneler**:
- **Venstre:** «Jeg er» (rolle), rollens rapporter, Arena og flatene.
- **Midten:** arbeidet. Ett klikk gir svar, og hver visning har én tittel.
- **Høyre:** «Fasit», med verktøykall, kilde, regel og KI-status.

Rapportforslagene er **tilpasset rollen** (`rolle_sporsmal` i `museum.db`). Demoen virker uten KI. Det som krever KI, er merket «Krever KI».

## Rekkefølge og avhengigheter
```
01 rolleforslag (data) ── Lars bygger museum.db ──────────────┐
02 rapportvisning ──> 04 chat inn ──> 05 søk inn ──> 06 vaktrom inn ──> 07 arbeidsflyter inn ──> 08 ny forside
03 tekst (andre sider) ──────────────────────────────────────────────────────────────────────────────┘
09 samlingsrapporter (venter på avklaring, deretter 01)
```
- 02, 04, 05, 06 og 07 endrer samme fil (`ett-vindu.html`). De må tas **etter hverandre**.
- 03 endrer bare de gamle sidene og kan gå **parallelt** med 02.
- 01 er ferdig kodet. Den venter bare på at Lars bygger databasen.

## Felles regler for alle oppgaver
- Bare data fra eksisterende API-er (`/api/rapport`, `/api/verktoy`, `/api/verktoyskjema`, `/api/arena/*`, `/api/chat`, `/api/status`). Ny Python-logikk bare når oppgaven sier det.
- Bare klasser fra `af.css`. Ingen endring i `af.css`, som er designsystemet. Merk at `display` i `af.css` overstyrer `hidden` (F1). Skjul med `style.display = "none"` eller en klasse som har `[hidden]`-regel.
- Innhold settes med `textContent`, aldri `innerHTML`.
- Én tittel (`h1`) per visning. Ett ord for KI: «KI», ikke AI eller LLM.
- Den gamle siden for en flate blir stående til oppgave 08.

## Prompt til bygger (bytt ut NN med oppgavenummeret)
```text
Repo: G:\Min disk\Kunstpixel. Windows og PowerShell. Python: py -3.13.
Les først: AGENTS.md, docs/specs/ett-vindu.md og oppgavefilen docs/specs/ett-vindu/NN-*.md.
Bygg bare oppgave NN, på grenen oppgaven oppgir. Lag den fra tuppen av ux/ett-vindu hvis den ikke finnes.

Følg «Indre sløyfe» før du endrer noe. Stopp hvis den feiler.
Ferdig når alle punktene i «Done når» er PASS. Kjør:
  py -3.13 C:/Users/larse/.gemini/config/skills/arbeidsflyt/scripts/verify_arbeidsflyt.py <endret html>
  py -3.13 -m pytest -q -p no:cacheprovider
Testen test_latency_under_50ms kan feile under last. Kjør den alene på nytt før du konkluderer.
Tester kan skrive om 05_data/mock_*.csv med CRLF. Tilbakestill dem med git checkout før commit.

Commit bare egne filer (git add <fil>). Ikke push, ikke merge, ikke tagg.
Forbudt: skrive til 05_data/museum.db, kjøre build_museum_db.py uten --check, endre af.css.

Lever: endrede filer, PASS/FAIL per «Done når», siste linje fra pytest og commit-hash.
Skriv «STATUS: UNTESTED» for det som ikke ble kjørt.
```
