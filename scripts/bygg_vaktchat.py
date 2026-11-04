"""Bygg vaktchatten: en publiserbar side der Claude svarer med verktøy over et øyeblikksbilde av museum.db.

    py -3.13 scripts/bygg_vaktchat.py

Skriver .scratch/vaktchat/vaktchat.html (siden), data.json (øyeblikksbildet) og validering.html (kopi med
dokumentskall for Arbeidsflyt-validatoren). .scratch er gitignorert fordi siden har dataene bygd inn.
Kildene ligger i src/kunstpixel/adapters/vaktchat/: verktoy.js (verktøyene, speiler core/vaktrom.py) og mal.html.
Paritet med Python voktes av tests/test_vaktchat_paritet.py. Alle data er syntetiske.
Publiser siden på nytt til samme lenke etter bygging (Artifact med url).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KILDE = ROOT / "src" / "kunstpixel" / "adapters" / "vaktchat"
AF_CSS = ROOT / "src" / "kunstpixel" / "adapters" / "datafinner" / "af.css"
UT = ROOT / ".scratch" / "vaktchat"
VINDU = ("2025-10-01", "2026-12-31")   # datoer kandidatoppslag støtter
VAKTER_FRA = "2024-09-30"              # ett år ekstra bakover, så «vakter siste 12 måneder» blir riktig


def eksporter(db: Path = ROOT / "05_data" / "museum.db") -> dict:
    c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    q = lambda s, *a: [dict(r) for r in c.execute(s, a)]
    fra, til = VINDU
    d = {
        "vindu": list(VINDU),
        "vakter_fra": VAKTER_FRA,
        "ferdigheter": {r["skill_code"]: r["navn"] for r in q("SELECT skill_code, navn FROM org_ferdigheter")},
        "krav": {},
        "grenser": {r["navn"]: r["verdi"] for r in q("SELECT navn, verdi FROM arbeidstid_grenser")},
        "ansatte": q("SELECT a.ansatt_id id, a.navn, a.stilling, a.avdeling, a.stillingsprosent, a.ansatt_fra, a.ansatt_til, a.epost, "
                     "a.telefon, a.lonnstrinn_virke, t.timesats_ordinar FROM hr_ansatte a "
                     "LEFT JOIN virke_tariff t ON t.lonnstrinn = a.lonnstrinn_virke"),
        "kurs": q("SELECT ansatt_id id, skill_code, sertifisert_dato, gyldig_til, status FROM org_ansatt_kompetanse"),
        "fravaer": q("SELECT ansatt_id id, fra, til, type FROM hr_fravaer WHERE til >= ? AND fra <= ?", fra, til),
        "vakter": [[r["vakt_id"], r["ansatt_id"], r["stasjon"], r["dato"], r["start"], r["slutt"], r["timer"]] for r in q(
            "SELECT vakt_id, ansatt_id, stasjon, dato, start, slutt, timer FROM hr_vakter WHERE dato BETWEEN ? AND ? "
            "AND start IS NOT NULL AND slutt IS NOT NULL ORDER BY dato, start, vakt_id", VAKTER_FRA, til)],
        "innleide": q("SELECT innleid_id id, navn, firma, orgnr, kategori, stilling, epost, telefon, timepris_nok, avtale_fra, "
                      "avtale_til, status FROM hr_innleide_personer"),
        "innleid_kurs": q("SELECT innleid_id id, skill_code, sertifisert_dato, gyldig_til, status FROM hr_innleide_kompetanse"),
        "kontaktpersoner": {r["orgnr"]: r["kontaktperson_ekstern"] for r in q(
            "SELECT orgnr, kontaktperson_ekstern FROM hr_innleie WHERE kontaktperson_ekstern IS NOT NULL "
            "AND kontaktperson_ekstern != '' ORDER BY aar")},
        "personalmapper": q("SELECT saksnr, ansatt_id, navn, opprettet_dato, kategori, tittel, innhold_fortrolig FROM hr_personalmapper"),
        "samtaler": q("SELECT samtale_id, ansatt_id, dato, leder_rolle, samlet_vurdering, styrker, utviklingsomrade, erfaring_notat, "
                      "onsker_flere_helgevakter FROM hr_medarbeidersamtaler"),
        "handbok": q("SELECT punkt_id, handbok_navn, kapittel_tittel, avsnitt_tittel, malgruppe, lovhjemmel, innhold, stikkord "
                     "FROM handbok_oppslag ORDER BY punkt_id"),
    }
    for r in q("SELECT stasjon, skill_code FROM stasjon_krav ORDER BY stasjon, skill_code"):
        d["krav"].setdefault(r["stasjon"], []).append(r["skill_code"])
    c.close()
    return d


def bygg(d: dict, ut: Path = UT) -> Path:
    ut.mkdir(parents=True, exist_ok=True)
    data = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    (ut / "data.json").write_text(data, encoding="utf-8")
    mal = (KILDE / "mal.html").read_text(encoding="utf-8")
    deler = {
        "/*AFCSS*/": AF_CSS.read_text(encoding="utf-8"),
        "/*VERKTOY*/": (KILDE / "verktoy.js").read_text(encoding="utf-8").replace("</script", "<\\/script"),
        "/*DATA*/": data.replace("</", "<\\/"),
    }
    for navn, verdi in deler.items():
        if mal.count(navn) != 1:
            raise SystemExit(f"Malen må ha nøyaktig én {navn}")
        mal = mal.replace(navn, verdi)
    side = ut / "vaktchat.html"
    side.write_text(mal, encoding="utf-8")
    skall = '<!DOCTYPE html>\n<html lang="nb">\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n' + mal + "\n</body>\n</html>\n"
    (ut / "validering.html").write_text(skall, encoding="utf-8")
    return side


def main() -> int:
    d = eksporter()
    side = bygg(d)
    print(f"Bygde {side.relative_to(ROOT)} ({side.stat().st_size // 1024} kB): {len(d['ansatte'])} ansatte, "
          f"{len(d['vakter'])} vakter, {len(d['samtaler'])} samtaler, {len(d['handbok'])} håndbokavsnitt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
