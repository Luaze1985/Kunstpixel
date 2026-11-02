# 01: Håndbøkene leses inn i bygget

**Hva som skal bygges:** Når Lars endrer en håndbok eller SOP i md og bygger `museum.db`, står endringen i
`handbok_oppslag`. Ingen skript skriver i databasen utenom byggeskriptet.

**Må gjøres først:** 02, fordi begge endrer `docs/DATAPIPELINE.md`. Oppgaven er ikke del av MVP og tas etter 05.
Dataene er allerede riktige: paritet ble bekreftet 2026-10-24.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] `bygg()` i `build_museum_db.py` sletter `handbok_oppslag` og bygger den på nytt fra
      `04_knowledge/01_governance/handboker/*.md` og `04_knowledge/02_sops/SOP-*.md`. Steget står i
      docstringen sammen med de andre stegene, og antallet står i returverdien.
- [ ] `seed_handbooks.py` bare leser og deler opp filene. Den har ingen `sqlite3.connect` og ingen referanse
      til `museum.db`. En test sjekker dette.
- [ ] En test bygger til en midlertidig database og viser at `handbok_oppslag` har nøyaktig de radene
      parseren gir. I dag er det 99 rader med 5 håndbokkoder.
- [ ] `siste_revidert` kommer ikke fra dagens dato. To bygg gir likt innhold i tabellen.
- [ ] Skjemaet er uendret, og `SKJEMAVERSJON` er ikke endret. Kolonnene i `init_handbook_table` er sjekket
      2026-10-24 og er like dem i `museum_base.db`. `DROP TABLE` fjerner også indeksene, så
      `idx_handbok_kode` og `idx_handbok_kapittel` må lages på nytt. En test sjekker at begge finnes.
- [ ] ADR-012 har fått et tillegg: endringer leses inn ved bygg, og Lars bygger. `docs/DATAPIPELINE.md`
      er oppdatert.
- [ ] `py -3.13 -m pytest -q` er grønn, og `py -3.13 scripts/db_status_gate.py` gir **KLAR**. Porten
      sammenligner to temp-bygg (P1), ikke mot `museum.db`, så KLAR er mulig før Lars bygger.
      `build_museum_db.py --check` vil derimot vise ULIK til Lars har bygget, fordi tabellen skrives på nytt
      selv om innholdet er likt. Det er forventet og er ikke en feil.
- [ ] Siste steg: be Lars bygge `museum.db`.

### Prompt til bygger (Codex eller annen LLM)
```text
Repo: G:\Min disk\Kunstpixel. Windows og PowerShell. Python: py -3.13.
Les først: AGENTS.md, docs/specs/internside-oppslagsverk.md (særlig «Regler for agenten som bygger»)
og denne oppgavefilen. Bygg bare oppgave 01. Akseptkravene over er fasit.

Utgangspunkt (målt 2026-10-24): pytest 387 består. scripts/db_status_gate.py gir KLAR.

Arbeidsmåte:
1. Lag grenen codex/01-handboker-i-bygget fra hr-konsolidering.
2. Skriv testene først, og se at de feiler. Implementer så til de består.
3. Kjør `py -3.13 -m pytest -q` og `py -3.13 scripts/db_status_gate.py`. Begge skal være grønne / KLAR.
4. Commit bare filene du har endret, med `git add <fil>` og aldri `git add -A` eller `git add .`. Ikke push.

Forbudt: å skrive til 05_data/museum.db, å kjøre build_museum_db.py uten --check og å endre
05_data/kilde/museum_base.db.

Lever: en liste over endrede filer, siste linje fra pytest, siste linje fra statusporten og
commit-hash. Skriv «STATUS: UNTESTED» hvis noe ikke ble kjørt.
```
