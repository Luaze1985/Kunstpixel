"""Sjekk at alle data henger sammen med kunnskapsgrafen og er tilgjengelige for LLM (0 tokens).

Kontrollerer de 4 leddene når data utvides over tid:
  1. INNBOKS & CSV-FILER (01_inbox/incoming + 05_data/*.csv):
     - Er alle CSV-filer gyldige (ingen komma-forskyvning)?
     - Hvilke CSV-filer og Colab-leveranser er ikke koblet inn i build_museum_db.py ennå?
  2. KUNNSKAPSGRAF & RELASJONER (museum.db):
     - Henger alle fremmednøkler (FOREIGN KEY) sammen?
     - Finnes det _id-kolonner (f.eks. utstilling_id, avvik_id, ansatt_id) uten FOREIGN KEY,
       og peker verdiene deres faktisk på gyldige rader i måltabellen?
  3. LLM-TILGJENGELIGHET (museum.db -> src/kunstpixel/core/ -> MCP/Datafinner):
     - MCP-dekning: hvilke tabeller når demo-Claude via et @mcp.tool? Målt ved å følge kallene
       fra hvert verktøy gjennom funksjoner og konstanter i core/ (tabeller_via_mcp).
     - Nevnt i src/: står tabellnavnet i noen fil i src/ (Datafinner, MCP m.m.)? Svakere mål.
  4. KUNNSKAPSKART-SYNK (KUNNSKAPSKART.md):
     - Hvor mange av tabellene i museum.db er nevnt i KUNNSKAPSKART.md?
     - Skriver alltid et komplett, oppdatert maskin- og lesekart til:
       .scratch/kvalitet/KUNNSKAPSGRAF_FOR_LLM.md
"""

from __future__ import annotations

import argparse
import ast
import csv
import re
import sqlite3
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "05_data"
DB_PATH = DATA_DIR / "museum.db"
BYGGER_PATH = ROOT / "src" / "kunstpixel" / "data" / "build_museum_db.py"
KART_PATH = ROOT / "KUNNSKAPSKART.md"
MCP_PATH = ROOT / "src" / "kunstpixel" / "core" / "mcp_server.py"
OUT_MD = ROOT / ".scratch" / "kvalitet" / "KUNNSKAPSGRAF_FOR_LLM.md"

# CSV-filer i 05_data som allerede ligger bakt inn i det frosne grunnlaget (05_data/kilde/museum_base.db)
BARE_I_BASE_DB = {
    "ansatte_168_komplett_personvern_trondheim.csv": "hr_ansatte grunnlag (ligger i museum_base.db)",
    "arkiv_hr_ansatte.csv": "hr_ansatte (ligger i museum_base.db)",
    "arkiv_hr_innleie.csv": "hr_innleie (ligger i museum_base.db)",
    "arkiv_hr_vakt_historikk.csv": "hr_vakter grunnlag (ligger i museum_base.db)",
    "arkiv_utstillinger_2010_2026.csv": "utstillinger_historikk (ligger i museum_base.db)",
    "dagsbesok_2010_2026.csv": "daglige_besok grunnlag (ligger i museum_base.db)",
    "vakt_time_for_time_2025_2026.csv": "hr_vakter timefordeling grunnlag (ligger i museum_base.db)",
}

# Kjente logiske koblinger for _id-kolonner som bør peke på en hovedentitet i kunnskapsgrafen
LOGISKE_MAAL: dict[str, tuple[str, str]] = {
    "ansatt_id": ("hr_ansatte", "ansatt_id"),
    "vurdert_av_ansatt_id": ("hr_ansatte", "ansatt_id"),
    "sal_id": ("saler", "id"),
    "verk_id": ("verk", "id"),
    "kunstner_id": ("kunstnere", "id"),
    "utstilling_id": ("utstillinger_historikk", "utstilling_id"),
    "avvik_id": ("avvik_hms_drift", "avvik_id"),
    "rolle_id": ("roller", "rolle_id"),
    "stasjon_id": ("hms_ergonomi_rotasjon", "stasjon_id"),
}


def sjekk_alle_csv() -> tuple[list[str], list[str], list[str]]:
    """Returnerer (formatfeil, ikke_koblet_i_bygger, i_base_db)."""
    bygger_tekst = BYGGER_PATH.read_text(encoding="utf-8")
    brukte_csv = set(re.findall(r"([a-z0-9_]+\.csv)", bygger_tekst))

    formatfeil: list[str] = []
    ubrukte: list[str] = []
    i_base: list[str] = []

    for sti in sorted(DATA_DIR.glob("*.csv")):
        navn = sti.name
        try:
            with sti.open(encoding="utf-8", newline="") as f:
                rader = list(csv.reader(f))
            if rader:
                antall = len(rader[0])
                avvik = [(i, len(r)) for i, r in enumerate(rader[1:], start=2) if len(r) != antall]
                if avvik:
                    formatfeil.append(
                        f"05_data/{navn}: linje {avvik[0][0]} har {avvik[0][1]} felt (overskrift har {antall}). Komma i tekst må ha anførselstegn."
                    )
        except Exception as exc:
            formatfeil.append(f"05_data/{navn}: kunne ikke leses ({exc})")

        if navn not in brukte_csv:
            if navn in BARE_I_BASE_DB:
                i_base.append(f"{navn} -> {BARE_I_BASE_DB[navn]}")
            else:
                ubrukte.append(navn)

    return formatfeil, ubrukte, i_base


def sjekk_innboks() -> list[tuple[str, str]]:
    """Sjekker leveranser i 01_inbox/incoming/."""
    inc = ROOT / "01_inbox" / "incoming"
    if not inc.is_dir():
        return []
    funn: list[tuple[str, str]] = []
    for mappe in sorted(p for p in inc.iterdir() if p.is_dir()):
        filer = [f.name for f in mappe.iterdir() if f.is_file()]
        har_sha = "SJEKKSUM.sha256" in filer
        har_meta = "METADATA.json" in filer
        csv_eller_db = [f for f in filer if f.endswith((".csv", ".db", ".ipynb"))]
        status = "KLAR" if (har_sha and har_meta and csv_eller_db) else "UFULLSTENDIG"
        funn.append((mappe.name, f"{status} ({len(filer)} filer: {', '.join(csv_eller_db) or 'ingen datafil'})"))
    return funn


def kodefiler_for_mcp() -> list[Path]:
    """Filene MCP-verktøyene kan kalle inn i (kjernemodulene, ikke datagenereringen)."""
    return sorted((ROOT / "src" / "kunstpixel" / "core").rglob("*.py"))


def tabeller_via_mcp(tabeller: list[str], verktoyfil: Path, kodefiler: list[Path]) -> set[str]:
    """Tabeller demo-Claude faktisk når: følger kall fra hvert @mcp.tool gjennom funksjoner og konstanter.

    Et tabellnavn som bare står i Datafinner, byggeskript eller et verktøy som ikke er registrert, telles ikke.
    """
    defs: dict[str, list[str]] = {}
    for fil in kodefiler:
        kilde = fil.read_text(encoding="utf-8")
        tre = ast.parse(kilde)
        for node in ast.walk(tre):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defs.setdefault(node.name, []).append(ast.get_source_segment(kilde, node) or "")
        for node in tre.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                maal = node.targets if isinstance(node, ast.Assign) else [node.target]
                for m in maal:
                    if isinstance(m, ast.Name):
                        defs.setdefault(m.id, []).append(ast.get_source_segment(kilde, node) or "")

    def er_verktoy(fn: ast.AST) -> bool:
        return any("tool" in ast.unparse(d) for d in getattr(fn, "decorator_list", []))

    kilde = verktoyfil.read_text(encoding="utf-8")
    ko = [
        ast.get_source_segment(kilde, n) or ""
        for n in ast.walk(ast.parse(kilde))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and er_verktoy(n)
    ]
    sett: set[str] = set()
    tekst: list[str] = []
    while ko:
        seg = ko.pop()
        tekst.append(seg)
        try:
            noder = ast.walk(ast.parse(textwrap.dedent(seg)))
        except SyntaxError:
            continue
        for n in noder:
            navn = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else None
            if navn and navn in defs and navn not in sett:
                sett.add(navn)
                ko.extend(defs[navn])
    samlet = "\n".join(tekst)
    return {t for t in tabeller if re.search(rf"\b{re.escape(t)}\b", samlet)}


def analyser_database(con: sqlite3.Connection) -> dict:
    tabeller = [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]

    # Les all kode i src/kunstpixel (utenom data-byggerne) for å se hvilke tabeller som faktisk spørres av LLM-verktøy
    verktøy_kode: dict[str, str] = {}
    for pyfil in (ROOT / "src").rglob("*.py"):
        if "data" in pyfil.parts:
            continue
        verktøy_kode[pyfil.relative_to(ROOT).as_posix()] = pyfil.read_text(encoding="utf-8")

    index_path = KART_PATH.parent / "05_data" / "index.md"
    kart_tekst = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (KART_PATH, index_path)
        if p.is_file()
    )

    tabell_info = []
    usynlige_for_llm = []
    via_mcp = tabeller_via_mcp(tabeller, MCP_PATH, kodefiler_for_mcp())
    usynlige_for_mcp = []
    ubevoktede_koblinger = []
    brutte_logiske_koblinger = []

    for t in tabeller:
        rader = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        kolonner_info = con.execute(f"PRAGMA table_info('{t}')").fetchall()
        kolonner = [r[1] for r in kolonner_info]
        pk_kolonner = {r[1] for r in kolonner_info if r[5] > 0}
        fks = con.execute(f"PRAGMA foreign_key_list('{t}')").fetchall()
        fk_map = {r[3]: f"{r[2]}.{r[4]}" for r in fks}

        # Hvilke filer i src/ spør mot denne tabellen?
        brukt_i = [
            fil
            for fil, tekst in verktøy_kode.items()
            if re.search(rf"\b{re.escape(t)}\b", tekst)
        ]
        if not brukt_i:
            usynlige_for_llm.append((t, rader))
        if t not in via_mcp:
            usynlige_for_mcp.append((t, rader))

        # Sjekk om tabellen har logiske _id-kolonner uten FOREIGN KEY
        for kol in kolonner:
            if kol in pk_kolonner or kol in fk_map:
                continue
            if kol in LOGISKE_MAAL:
                maal_tabell, maal_kol = LOGISKE_MAAL[kol]
                if maal_tabell == t:
                    continue
                ubevoktede_koblinger.append((t, kol, f"{maal_tabell}.{maal_kol}"))
                # Sjekk deterministisk om alle verdier faktisk finnes i måltabellen!
                if maal_tabell in tabeller:
                    foreldrelose = con.execute(
                        f'SELECT count(DISTINCT "{kol}") FROM "{t}" '
                        f'WHERE "{kol}" IS NOT NULL AND "{kol}" != "" '
                        f'AND "{kol}" NOT IN (SELECT "{maal_kol}" FROM "{maal_tabell}")'
                    ).fetchone()[0]
                    if foreldrelose > 0:
                        brutte_logiske_koblinger.append((t, kol, maal_tabell, maal_kol, foreldrelose))

        i_kart = bool(re.search(rf"\b{re.escape(t)}\b", kart_tekst))
        tabell_info.append(
            {
                "tabell": t,
                "rader": rader,
                "kolonner": kolonner,
                "fks": fk_map,
                "brukt_i": brukt_i,
                "i_kunnskapskart": i_kart,
                "via_mcp": t in via_mcp,
            }
        )

    return {
        "tabeller": tabell_info,
        "usynlige_for_llm": usynlige_for_llm,
        "usynlige_for_mcp": usynlige_for_mcp,
        "ubevoktede_koblinger": ubevoktede_koblinger,
        "brutte_logiske_koblinger": brutte_logiske_koblinger,
    }


def skriv_kunnskapsgraf_md(
    formatfeil: list[str],
    ubrukte_csv: list[str],
    i_base: list[str],
    innboks: list[tuple[str, str]],
    analyse: dict,
) -> None:
    tabeller = analyse["tabeller"]
    usynlige = analyse["usynlige_for_llm"]
    blinde_mcp = analyse["usynlige_for_mcp"]
    ubevoktede = analyse["ubevoktede_koblinger"]
    brutte = analyse["brutte_logiske_koblinger"]
    i_kart_antall = sum(1 for t in tabeller if t["i_kunnskapskart"])

    linjer = [
        "# Kunnskapsgraf & LLM-tilgjengelighet (Autogenerert helsesjekk)",
        "",
        "Denne filen oppdateres automatisk av `scripts/sjekk_kunnskapsgraf.py` (0 tokens).",
        "Gi denne filen til Claude / Codex / Antigravity når du vil koble på nye data eller fikse hull i kunnskapsgrafen.",
        "",
        "## 1. Sammendrag",
        "",
        f"- **Tabeller i `museum.db`:** {len(tabeller)} tabeller",
        f"- **Når demo-Claude via MCP (`@mcp.tool` i `core/mcp_server.py`):** {len(tabeller) - len(blinde_mcp)} av {len(tabeller)} tabeller",
        f"- **Nevnt i `src/` (Datafinner, MCP m.m.):** {len(tabeller) - len(usynlige)} av {len(tabeller)} tabeller",
        f"- **Blinde for MCP:** {len(blinde_mcp)} tabeller ({', '.join(t for t, _ in blinde_mcp) or 'ingen'})",
        f"- **CSV-filer i `05_data/` som ikke er koblet inn i `build_museum_db.py` ennå:** {len(ubrukte_csv)} filer",
        f"- **Logiske koblinger (`_id`) med ugyldige verdier:** {len(brutte)} brudd",
        f"- **Tabeller nevnt i `KUNNSKAPSKART.md`:** {i_kart_antall} av {len(tabeller)}",
        "",
        "---",
        "",
        "## 2. Tiltaksliste for LLM (Hva som bør kobles på)",
        "",
    ]

    if formatfeil:
        linjer.append("### [FEIL] CSV-formatfeil som må rettes først")
        for f in formatfeil:
            linjer.append(f"- ❌ `{f}`")
        linjer.append("")

    if brutte:
        linjer.append("### [OBS] Logiske koblinger der ID-er ikke finnes i måltabellen")
        for t, kol, mt, mk, ant in brutte:
            linjer.append(
                f"- ⚠️ **`{t}.{kol}` → `{mt}.{mk}`:** {ant} unike ID-verdier i `{t}.{kol}` finnes ikke i `{mt}.{mk}`."
            )
        linjer.append("")

    if blinde_mcp:
        linjer.append("### [OBS] Tabeller demo-Claude ikke når via MCP")
        linjer.append("Ingen `@mcp.tool` i `src/kunstpixel/core/mcp_server.py` leser disse (målt ved å følge kallene fra hvert verktøy):")
        for t, rader in blinde_mcp:
            linjer.append(f"- **`{t}`** ({rader} rader) → lag lesende funksjon i `core/db.py` og et `@mcp.tool` i `core/mcp_server.py`.")
        linjer.append("")

    if usynlige:
        linjer.append("### [OBS] Tabeller i `museum.db` som mangler LLM-verktøy («Blinde tabeller»)")
        linjer.append(
            "Disse tabellene bygges inn i `museum.db`, men ingen funksjon i `src/kunstpixel/core/` eller `src/mcp_server.py` leser dem:"
        )
        for t, rader in usynlige:
            linjer.append(
                f"- **`{t}`** ({rader} rader) → *Instruks til LLM: Lag lesefunksjon i `src/kunstpixel/core/db.py` og eksponer verktøy i `src/mcp_server.py` / `datafinner.py`.*"
            )
        linjer.append("")

    if ubrukte_csv:
        linjer.append("### [INFO] Nye/ubrukte CSV-filer i `05_data/` (ikke i `build_museum_db.py`)")
        for navn in ubrukte_csv:
            linjer.append(
                f"- **`05_data/{navn}`** → *Instruks til LLM: Hvis denne skal brukes, legg til `bygg_*`-funksjon i `src/kunstpixel/data/build_museum_db.py` med fremmednøkkel til kunnskapsgrafen.*"
            )
        linjer.append("")

    if ubevoktede:
        linjer.append("### [INFO] Nøkkelkolonner (`_id`) uten eksplisitt SQLite `FOREIGN KEY`")
        for t, kol, maal in ubevoktede:
            linjer.append(f"- `{t}.{kol}` peker logisk på `{maal}`, men har ikke `REFERENCES` i `CREATE TABLE`.")
        linjer.append("")

    if innboks:
        linjer.append("### [INFO] Leveranser i `01_inbox/incoming/`")
        for navn, status in innboks:
            linjer.append(f"- **`01_inbox/incoming/{navn}`**: {status}")
        linjer.append("")

    linjer += [
        "---",
        "",
        "## 3. Komplett Kunnskapsgraf (Alle tabeller i `museum.db`, koblinger og LLM-status)",
        "",
        "| Tabell | Rader | Koblinger (FOREIGN KEY) | MCP | Nevnt i `src/` |",
        "|---|---:|---|---|---|",
    ]

    for t in tabeller:
        fk_str = ", ".join(f"`{k}` → `{v}`" for k, v in t["fks"].items()) or "*(rot-tabell / oppslag)*"
        llm_str = "✅ " + ", ".join(f"`{Path(p).name}`" for p in t["brukt_i"][:2]) if t["brukt_i"] else "⚠️ **Mangler verktøy**"
        mcp_str = "✅" if t["via_mcp"] else "⚠️ nei"
        linjer.append(f"| `{t['tabell']}` | {t['rader']} | {fk_str} | {mcp_str} | {llm_str} |")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(linjer) + "\n", encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", action="store_true", help="Skriv PROBLEM-linjer til VS Code Problems-panelet")
    args = ap.parse_args()

    formatfeil, ubrukte_csv, i_base = sjekk_alle_csv()
    innboks = sjekk_innboks()

    con = sqlite3.connect(DB_PATH.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        analyse = analyser_database(con)
    finally:
        con.close()

    skriv_kunnskapsgraf_md(formatfeil, ubrukte_csv, i_base, innboks, analyse)

    tabeller = analyse["tabeller"]
    usynlige = analyse["usynlige_for_llm"]
    blinde_mcp = analyse["usynlige_for_mcp"]
    brutte = analyse["brutte_logiske_koblinger"]

    print("KUNNSKAPSGRAF & LLM-TILGJENGELIGHET")
    print("=" * 70)
    print(f"[ {'FEIL' if formatfeil else 'OK '} ] Alle {len(list(DATA_DIR.glob('*.csv')))} CSV-filer i 05_data/ sjekket for komma- og kolonnefeil ({len(formatfeil)} feil)")
    print(f"[ {'OBS' if blinde_mcp else 'OK '} ] MCP-dekning (demo-Claude): {len(tabeller) - len(blinde_mcp)} av {len(tabeller)} tabeller")
    if blinde_mcp:
        print(f"         Blinde for MCP: {', '.join(t for t, _ in blinde_mcp)}")
    print(f"[ {'OBS' if usynlige else 'OK '} ] Nevnt i src/ (Datafinner, MCP m.m.): {len(tabeller) - len(usynlige)} av {len(tabeller)} tabeller")
    if usynlige:
        print(f"         Blinde tabeller uten LLM-verktøy: {', '.join(t for t, _ in usynlige)}")
        print("         Gjør dette: Be LLM lese .scratch/kvalitet/KUNNSKAPSGRAF_FOR_LLM.md og lage verktøy for dem.")
    print(f"[ {'OBS' if brutte else 'OK '} ] Logiske relasjoner (_id-kolonner på tvers av tabeller): {len(brutte)} brudd")
    for t, kol, mt, mk, ant in brutte:
        print(f"         - {t}.{kol} -> {mt}.{mk}: {ant} ID-er finnes ikke i {mt}")
    print(f"[ INFO] Ubrukte CSV-filer i 05_data/ som ikke står i build_museum_db.py: {len(ubrukte_csv)} stk")
    if ubrukte_csv:
        print(f"         ({', '.join(ubrukte_csv[:5])}{' ...' if len(ubrukte_csv) > 5 else ''})")
    print("[ OK  ] Oppdatert kunnskapsgraf for LLM skrevet til: .scratch/kvalitet/KUNNSKAPSGRAF_FOR_LLM.md")
    print("=" * 70)

    if args.problems:
        for f in formatfeil:
            fil = f.split(":")[0]
            print(f"PROBLEM|error|{fil}|1|{f}")
        if blinde_mcp:
            print(f"PROBLEM|warning|src/kunstpixel/core/mcp_server.py|1|MCP: {len(blinde_mcp)} tabeller i museum.db har ikke noe MCP-verktøy ({', '.join(t for t, _ in blinde_mcp)}).")
        if usynlige:
            navn_liste = ", ".join(t for t, _ in usynlige)
            print(
                f"PROBLEM|warning|src/kunstpixel/core/db.py|1|Kunnskapsgraf/LLM: {len(usynlige)} tabeller i museum.db mangler LLM-verktøy ({navn_liste}). Se .scratch/kvalitet/KUNNSKAPSGRAF_FOR_LLM.md"
            )
        for t, kol, mt, mk, ant in brutte:
            print(
                f"PROBLEM|warning|src/kunstpixel/data/build_museum_db.py|1|Kunnskapsgraf: {t}.{kol} har {ant} ID-verdier som ikke finnes i {mt}.{mk}."
            )

    return 1 if formatfeil else 0


if __name__ == "__main__":
    raise SystemExit(main())
