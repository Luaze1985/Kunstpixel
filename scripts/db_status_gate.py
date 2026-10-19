"""Statusport for museum.db før sammenslåing (0 tokens, deterministisk).

Bygger museum.db til en temp-fil med build_museum_db.bygg (rører aldri 05_data/museum.db),
og sjekker:

  P1  Bygget er deterministisk (to bygg gir samme sha256)
  P2  integrity_check = ok, foreign_key_check tom, user_version = SKJEMAVERSJON
  P3  Alle datakilde-kolonner i bygget starter med «syntetisk»
  P4  Tracer: samme verdi via rå SQL og via verktøyene i db.py (vakt, økonomi, sykefravær, kostnad)
  P5  pytest består 100 %
  Hull (G2-G9 fra briefen): åpen/lukket, informerer, blokkerer ikke

Nivåer: FEIL blokkerer sammenslåing (exit 1). ADVARSEL rapporteres, blokkerer ikke.
Rapport skrives til .scratch/db-status/STATUS-<tid>.md.

Kjøres med:
    py -3.13 scripts/db_status_gate.py            # alt
    py -3.13 scripts/db_status_gate.py --uten-pytest
"""

from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.kunstpixel.core import db
from src.kunstpixel.data import build_museum_db as bygger

FEIL, ADVARSEL, OK = "FEIL", "ADVARSEL", "OK"
resultater: list[tuple[str, str, str]] = []


def logg(sjekk: str, niva: str, detalj: str) -> None:
    resultater.append((sjekk, niva, detalj))
    print(f"[{niva:8}] {sjekk}: {detalj}")


def en(con: sqlite3.Connection, sql: str):
    rad = con.execute(sql).fetchone()
    return rad[0] if rad else None


def tabeller(con: sqlite3.Connection) -> list[str]:
    return [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]


def sjekk_bygg(tmp: Path) -> Path:
    a, b = tmp / "a.db", tmp / "b.db"
    bygger.bygg(a)
    bygger.bygg(b)
    ha, hb = bygger.sha256(a), bygger.sha256(b)
    logg("P1 deterministisk bygg", OK if ha == hb else FEIL, f"sha256 {ha[:12]} / {hb[:12]}")
    return a


def sjekk_integritet(con: sqlite3.Connection) -> None:
    integ = en(con, "PRAGMA integrity_check")
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    uv = en(con, "PRAGMA user_version")
    niva = OK if integ == "ok" and not fk and uv == bygger.SKJEMAVERSJON else FEIL
    logg("P2 integritet", niva, f"integrity={integ}, fk_brudd={len(fk)}, user_version={uv} (forventet {bygger.SKJEMAVERSJON})")


def sjekk_merking(con: sqlite3.Connection) -> None:
    funnet, brudd = 0, []
    for t in tabeller(con):
        for kol in [r[1] for r in con.execute(f"PRAGMA table_info('{t}')")]:
            if kol == "datakilde" or kol.endswith("_datakilde"):
                funnet += 1
                n = en(con, f"SELECT count(*) FROM \"{t}\" WHERE coalesce(\"{kol}\", '') NOT LIKE 'syntetisk%'")
                if n:
                    brudd.append(f"{t}.{kol}: {n} rader")
    logg("P3 syntetisk merking", FEIL if brudd or not funnet else OK,
         f"{funnet} datakilde-kolonner" + (f", brudd: {'; '.join(brudd)}" if brudd else ""))


def sjekk_tracer(con: sqlite3.Connection, dbsti: Path) -> None:
    dato = en(con, "SELECT max(dato) FROM hr_vakter WHERE dato <= date('now')")
    vakt = con.execute(
        "SELECT v.vakt_id, a.navn, v.timer FROM hr_vakter v JOIN hr_ansatte a USING(ansatt_id) "
        "WHERE v.dato = ? ORDER BY v.vakt_id LIMIT 1", (dato,)).fetchone()
    ui = [(r["vakt_id"], r["navn"], r["timer"]) for r in db.query_shifts_on_date(dato, dbsti) if r["vakt_id"] == vakt[0]]
    logg("P4a tracer vakt", OK if ui and ui[0] == tuple(vakt) else FEIL, f"{dato} {vakt[0]}")

    uid = en(con, "SELECT utstilling_id FROM utstilling_okonomi ORDER BY utstilling_id DESC LIMIT 1")
    raw = en(con, f"SELECT netto_resultat_nok FROM utstilling_okonomi WHERE utstilling_id = '{uid}'")
    eco = db.query_exhibition_economy(uid, db_path=dbsti)
    logg("P4b tracer økonomi", OK if eco and eco["netto_resultat_nok"] == raw else FEIL, f"{uid} netto {raw}")

    aar, kv, pst = con.execute("SELECT aar, kvartal, sykefraver_prosent FROM ssb_sykefraver_kultur ORDER BY aar DESC, kvartal DESC LIMIT 1").fetchone()
    syk = db.query_quarterly_absence(aar, kv, db_path=dbsti)
    verdi = syk.get("sykefraver_prosent") if isinstance(syk, dict) else None
    logg("P4c tracer sykefravær", OK if verdi == pst else FEIL, f"{aar}-Q{kv} {pst}")

    mnd = dato[:7]
    kost = db.query_shift_cost(mnd, db_path=dbsti)
    har_kveld = any("kveldstimer" in a for a in kost["avdelinger"])
    kveld_fra = en(con, "SELECT verdi FROM arbeidstid_grenser WHERE navn = 'kveldstillegg_fra'") if har_kveld else None
    # Kveldstimer i rå SQL: min(timer, max(0, slutt - max(start, kveldstillegg_fra)))
    s_t = "(CAST(substr(v.start,1,2) AS REAL) + CAST(substr(v.start,4,2) AS REAL)/60)"
    e_t = "(CAST(substr(v.slutt,1,2) AS REAL) + CAST(substr(v.slutt,4,2) AS REAL)/60)"
    kveld = f"min(v.timer, max(0, {e_t} - max({s_t}, :kf)))" if har_kveld else "0"
    rader = con.execute(
        "SELECT v.avdeling, round(sum(CASE WHEN h.dato IS NOT NULL THEN v.timer * t.timesats_helligdag "
        "WHEN strftime('%w', v.dato) IN ('0','6') THEN v.timer * t.timesats_helg "
        f"ELSE (v.timer - {kveld}) * t.timesats_ordinar + {kveld} * t.timesats_kveld END), 2) "
        "FROM hr_vakter v JOIN hr_ansatte a USING(ansatt_id) JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke "
        "LEFT JOIN norske_helligdager h ON h.dato = v.dato WHERE substr(v.dato, 1, 7) = :mnd GROUP BY v.avdeling",
        {"mnd": mnd, "kf": kveld_fra}).fetchall()
    avvik = [(r[0], r[1], next(a["kostnad_nok"] for a in kost["avdelinger"] if a["avdeling"] == r[0])) for r in rader]
    ulike = [a for a in avvik if a[1] != a[2]]
    storst = max((abs(a[1] - a[2]) for a in ulike), default=0)
    niva = OK if not ulike else (ADVARSEL if storst <= 0.05 else FEIL)
    logg("P4d tracer kostnad", niva,
         f"{mnd}{' med kveldssats' if har_kveld else ''}: {len(ulike)} av {len(avvik)} avdelinger ulike"
         + (f", største avvik {storst:.2f} kr (G11 avrunding)" if ulike else ""))


def sjekk_hull(con: sqlite3.Connection, dbsti: Path) -> None:
    alle = set(tabeller(con))
    utenfor = en(con, "SELECT count(*) FROM hr_vakter v JOIN hr_ansatte a USING(ansatt_id) "
                      "LEFT JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke WHERE t.lonnstrinn IS NULL")
    maks_uke = en(con, "SELECT max(s) FROM (SELECT sum(timer) s FROM hr_vakter GROUP BY ansatt_id, strftime('%Y-%W', dato))")
    ukenorm = en(con, "SELECT verdi FROM arbeidstid_grenser WHERE navn = 'ukenorm_timer'") if "arbeidstid_grenser" in alle else None
    siste_hendelse = en(con, "SELECT max(dato) FROM hendelser")
    uten_fk = [t for t in ("hr_innleie", "avvik_hms_drift", "utstillingsinnlan", "hendelser", "hms_ergonomi_rotasjon")
               if not con.execute(f"PRAGMA foreign_key_list('{t}')").fetchall()]
    hull = [
        ("G1 klokkeslett og grenser", {"start", "slutt"} <= {r[1] for r in con.execute("PRAGMA table_info('hr_vakter')")} and ukenorm is not None, ""),
        ("G2 tariff 66-86", utenfor == 0, f"{utenfor} vakter uten tariff"),
        ("G3 eget fravær", "hr_fravaer" in alle, ""),
        ("G4 vurderingsregler", "rapport_regler" in alle, ""),
        ("G5 roller", "roller" in alle, ""),
        ("G6 overtid mulig", ukenorm is not None and maks_uke > ukenorm, f"høyeste ukesum {maks_uke}"),
        ("G8 arrangementer", (siste_hendelse or "") >= "2026-12-01", f"siste {siste_hendelse}"),
        ("G9 fremmednøkler", not uten_fk, f"mangler: {', '.join(uten_fk) or '-'}"),
    ]
    for navn, lukket, detalj in hull:
        logg(f"Hull {navn}", OK if lukket else ADVARSEL, ("lukket" if lukket else "åpen") + (f" ({detalj})" if detalj else ""))


def sjekk_pytest() -> None:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    feilet = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
    logg("P5 pytest", OK if r.returncode == 0 else FEIL, "alle besto" if r.returncode == 0 else f"{len(feilet)} feilet: {feilet[:3]}")


def skriv_rapport() -> Path:
    ut = ROOT / ".scratch" / "db-status"
    ut.mkdir(parents=True, exist_ok=True)
    fil = ut / f"STATUS-{datetime.now():%Y%m%d-%H%M%S}.md"
    feil = sum(1 for _, n, _ in resultater if n == FEIL)
    linjer = ["# Databasestatus før sammenslåing", f"*{datetime.now():%Y-%m-%d %H:%M}* · "
              f"**{'BLOKKERT' if feil else 'KLAR'}** ({feil} feil)", "", "| Sjekk | Nivå | Detalj |", "|---|---|---|"]
    linjer += [f"| {s} | {n} | {d} |" for s, n, d in resultater]
    fil.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    return fil


def main() -> int:
    ap = argparse.ArgumentParser(description="Statusport for museum.db før sammenslåing")
    ap.add_argument("--uten-pytest", action="store_true")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="kunstpixel-port-") as t:
        dbsti = sjekk_bygg(Path(t))
        con = sqlite3.connect(dbsti.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            sjekk_integritet(con)
            sjekk_merking(con)
            sjekk_tracer(con, dbsti)
            sjekk_hull(con, dbsti)
        finally:
            con.close()
    if not args.uten_pytest:
        sjekk_pytest()
    fil = skriv_rapport()
    feil = sum(1 for _, n, _ in resultater if n == FEIL)
    print(f"\n{'BLOKKERT' if feil else 'KLAR'} for sammenslåing ({feil} feil). Rapport: {fil}")
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(main())
