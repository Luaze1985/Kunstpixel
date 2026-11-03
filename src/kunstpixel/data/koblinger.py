"""Koblingskontroll: finner datalagene hverandre, og forteller de samme historie?

To nivåer:
- A (kobling): hver nøkkel finner en rad i tabellen den peker på.
- B (samsvar): når koblingen virker, stemmer innholdet (personen var i jobb på datoen, navn og tall er like).

Hver kontroll er en SQL som returnerer bruddene. `forventet` er 0 når det skal stemme, eller dagens antall
for et kjent avvik som ikke er rettet ennå. Kontrollen feiler bare hvis antallet øker. Går et kjent avvik ned,
sier rapporten fra, slik at forventningen kan strammes inn.

Kjøres med:  py -3.13 scripts/koblingssjekk.py
Begge databasene åpnes skrivebeskyttet. persondata.db er koblet på som `p`.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

PAKKE_IDAG = "2026-10-27"  # siste dato i HR/HMS-pakken (hr_hms_pakke.IDAG)


@dataclass(frozen=True)
class Kontroll:
    id: str
    niva: str  # "A" kobling, "B" samsvar
    beskrivelse: str
    sql: str  # returnerer én rad per brudd
    forventet: int = 0
    forklaring: str = ""  # hvorfor et kjent avvik står (bare når forventet > 0)
    trenger_persondata: bool = False


@dataclass(frozen=True)
class Resultat:
    kontroll: Kontroll
    antall: int | None  # None = hoppet over
    eksempel: tuple | None

    @property
    def status(self) -> str:
        if self.antall is None:
            return "HOPPET OVER"
        if self.antall == 0:
            return "OK"
        if self.antall < self.kontroll.forventet:
            return "BEDRE"
        if self.antall == self.kontroll.forventet:
            return "KJENT AVVIK"
        return "FEIL"


def _ikke_i_jobb(tabell: str, kolonne: str, dato: str, skjema: str = "main") -> str:
    return (
        f"SELECT t.rowid, t.{kolonne}, substr(t.{dato}, 1, 10) FROM {skjema}.{tabell} t "
        f"JOIN main.hr_ansatte a ON a.ansatt_id = t.{kolonne} "
        f"WHERE a.ansatt_fra > substr(t.{dato}, 1, 10) OR (a.ansatt_til IS NOT NULL AND a.ansatt_til < substr(t.{dato}, 1, 10))"
    )


def _mangler_ansatt(tabell: str, kolonne: str, skjema: str = "main") -> str:
    return (
        f"SELECT rowid, {kolonne} FROM {skjema}.{tabell} "
        f"WHERE {kolonne} IS NOT NULL AND {kolonne} NOT IN (SELECT ansatt_id FROM main.hr_ansatte)"
    )


def _sal_overlapp(tabell: str, id_kol: str, start: str, slutt: str, sal_uttrykk: str) -> str:
    """Par av utstillinger som står i samme sal i overlappende perioder (saler er en kommaliste)."""
    return (
        "WITH RECURSIVE del(id, fra, til, rest, sal) AS ("
        f" SELECT {id_kol}, {start}, {slutt}, saler || ',', '' FROM main.{tabell}"
        " UNION ALL SELECT id, fra, til, substr(rest, instr(rest, ',') + 1), trim(substr(rest, 1, instr(rest, ',') - 1))"
        " FROM del WHERE rest <> ''),"
        f" s AS (SELECT id, fra, til, {sal_uttrykk} AS sal FROM del WHERE sal <> '')"
        " SELECT a.sal, a.id, b.id, max(a.fra, b.fra), min(a.til, b.til) FROM s a JOIN s b"
        " ON a.sal = b.sal AND a.id < b.id AND a.fra <= b.til AND b.fra <= a.til"
    )


_PD_ANSATTREF = [
    ("kontakter", "ansatt_id", None),
    ("medlemskap", "solgt_av_ansatt_id", "startdato"),
    ("gavekort", "solgt_av_ansatt_id", "utstedt"),
    ("arrangementer", "ansvarlig_ansatt_id", "dato"),
    ("skolebestillinger", "ansvarlig_ansatt_id", "dato"),
    ("utleie", "ansvarlig_ansatt_id", "dato"),
    ("henvendelser", "besvart_av_ansatt_id", "tidspunkt"),
]

KONTROLLER: list[Kontroll] = [
    # ------------------------------------------------------------------ A: kobling
    Kontroll("A01", "A", "Erklærte fremmednøkler i museum.db holder", "PRAGMA main.foreign_key_check"),
    Kontroll("A02", "A", "Erklærte fremmednøkler i persondata.db holder", "PRAGMA p.foreign_key_check", trenger_persondata=True),
    Kontroll("A03", "A", "tilstandsrapporter.vurdert_av_ansatt_id finnes i hr_ansatte", _mangler_ansatt("tilstandsrapporter", "vurdert_av_ansatt_id")),
    Kontroll("A04", "A", "personas.id finnes i hr_ansatte", "SELECT id FROM main.personas WHERE id NOT IN (SELECT ansatt_id FROM main.hr_ansatte)"),
    *[
        Kontroll(f"A{5 + i:02d}", "A", f"persondata {t}.{k} finnes i hr_ansatte", _mangler_ansatt(t, k, "p"), trenger_persondata=True)
        for i, (t, k, _) in enumerate(_PD_ANSATTREF)
    ],
    Kontroll(
        "A12", "A", "Arrangementer fra museum.db (MDB-<id>) finnes i hendelser",
        "SELECT arrangement_id FROM p.arrangementer WHERE kilde = 'museum.db' "
        "AND CAST(substr(arrangement_id, 5) AS INTEGER) NOT IN (SELECT id FROM main.hendelser)",
        trenger_persondata=True,
    ),
    Kontroll(
        "A13", "A", "utstillinger.saler (kommaliste) peker på saler.id",
        "WITH RECURSIVE del(id, rest, sal) AS ("
        " SELECT id, saler || ',', '' FROM main.utstillinger"
        " UNION ALL SELECT id, substr(rest, instr(rest, ',') + 1), trim(substr(rest, 1, instr(rest, ',') - 1)) FROM del WHERE rest <> '')"
        " SELECT id, sal FROM del WHERE sal <> '' AND sal NOT IN (SELECT id FROM main.saler)",
    ),
    Kontroll(
        "A14", "A", "utstillinger_historikk.saler («Sal C») peker på saler.id (SAL-C)",
        "WITH RECURSIVE del(id, rest, sal) AS ("
        " SELECT utstilling_id, saler || ',', '' FROM main.utstillinger_historikk"
        " UNION ALL SELECT id, substr(rest, instr(rest, ',') + 1), trim(substr(rest, 1, instr(rest, ',') - 1)) FROM del WHERE rest <> '')"
        " SELECT id, sal FROM del WHERE sal <> '' AND 'SAL-' || upper(substr(sal, 5)) NOT IN (SELECT id FROM main.saler)",
    ),
    Kontroll(
        "A15", "A", "hendelser.ansvarlig_rolle finnes i roller.navn",
        "SELECT id, ansvarlig_rolle FROM main.hendelser WHERE lower(ansvarlig_rolle) NOT IN "
        "(SELECT lower(replace(replace(replace(navn, 'ø', 'o'), 'Ø', 'O'), 'å', 'aa')) FROM main.roller)",
    ),
    Kontroll("A16", "A", "hr_vakter.dato finnes i dagsbesok", "SELECT vakt_id FROM main.hr_vakter WHERE dato NOT IN (SELECT dato FROM main.dagsbesok)"),
    # ------------------------------------------------------------------ B: samsvar
    Kontroll(
        "B01", "B", "Årsoversikten: besøk = sum av dagsbesok",
        "SELECT h.ar FROM main.h5_historikk_2010_2026 h WHERE h.besok_totalt <> "
        "(SELECT SUM(besok_totalt) FROM main.dagsbesok d WHERE d.aar = h.ar)",
    ),
    Kontroll(
        "B02", "B", "Årsoversikten: årsverk = stillingsprosent i hr_ansatte ved årsslutt",
        "SELECT h.ar, h.ansatte_arsverk, s.v FROM main.h5_historikk_2010_2026 h JOIN ("
        " SELECT y.ar, ROUND(SUM(a.stillingsprosent), 1) AS v FROM (SELECT ar, CASE WHEN ar = 2026 THEN '" + PAKKE_IDAG + "' "
        " ELSE ar || '-12-31' END AS d FROM main.h5_historikk_2010_2026) y JOIN main.hr_ansatte a"
        " ON a.ansatt_fra <= y.d AND (a.ansatt_til IS NULL OR a.ansatt_til >= y.d) GROUP BY y.ar) s ON s.ar = h.ar"
        " WHERE abs(h.ansatte_arsverk - s.v) > 0.05",
    ),
    Kontroll(
        "B03", "B", "utstillinger_historikk: besøk per år = sum av dagsbesok",
        "SELECT u.aar FROM main.utstillinger_historikk u GROUP BY u.aar "
        "HAVING SUM(u.besokstall_total) <> (SELECT SUM(besok_totalt) FROM main.dagsbesok d WHERE d.aar = u.aar)",
    ),
    Kontroll("B04", "B", "hr_vakter: ansatt i jobb på vaktdatoen", _ikke_i_jobb("hr_vakter", "ansatt_id", "dato")),
    Kontroll("B05", "B", "hr_fravaer: ansatt i jobb ved fraværsstart", _ikke_i_jobb("hr_fravaer", "ansatt_id", "fra")),
    Kontroll("B06", "B", "tilstandsrapporter: vurdert av ansatt i jobb", _ikke_i_jobb("tilstandsrapporter", "vurdert_av_ansatt_id", "inspeksjonsdato")),
    Kontroll(
        "B07", "B", "personas: navn og stilling = hr_ansatte",
        "SELECT p.id FROM main.personas p JOIN main.hr_ansatte a ON a.ansatt_id = p.id WHERE p.navn <> a.navn OR p.stilling <> a.stilling",
    ),
    Kontroll(
        "B08", "B", "hr_innleie: godkjent_av_navn starter med navnet i hr_ansatte",
        "SELECT i.innleie_id FROM main.hr_innleie i JOIN main.hr_ansatte a ON a.ansatt_id = i.godkjent_av_ansatt_id "
        "WHERE i.godkjent_av_navn NOT LIKE a.navn || '%'",
    ),
    Kontroll(
        "B09", "B", "Kunder som er ansatte har samme navn som i hr_ansatte",
        "SELECT k.kontakt_id FROM p.kontakter k JOIN main.hr_ansatte a USING (ansatt_id) WHERE k.fornavn || ' ' || k.etternavn <> a.navn",
        trenger_persondata=True,
    ),
    *[
        Kontroll(f"B{10 + i:02d}", "B", f"persondata {t}: {k} var i jobb på datoen", _ikke_i_jobb(t, k, d, "p"), trenger_persondata=True)
        for i, (t, k, d) in enumerate([r for r in _PD_ANSATTREF if r[2]])
    ],
    Kontroll(
        "B16", "B", "Arrangementer fra museum.db har samme dato, tittel og kapasitet som hendelser",
        "SELECT a.arrangement_id FROM p.arrangementer a JOIN main.hendelser h ON 'MDB-' || h.id = a.arrangement_id "
        "WHERE a.dato <> h.dato OR a.tittel <> h.tittel OR a.maks_deltakere <> h.maks_deltakere",
        trenger_persondata=True,
    ),
    Kontroll(
        "B17", "B", "Kundeaktivitet (medlemsbesøk, rabattbruk, skolebesøk) bare på åpne dager",
        "SELECT 'medlemsbesok', besok_id FROM p.medlemsbesok m JOIN main.dagsbesok d ON d.dato = m.dato WHERE d.er_aapent = 0 "
        "UNION ALL SELECT 'fordel_bruk', bruk_id FROM p.fordel_bruk f JOIN main.dagsbesok d ON d.dato = f.dato WHERE d.er_aapent = 0 "
        "UNION ALL SELECT 'skolebestillinger', bestilling_id FROM p.skolebestillinger s JOIN main.dagsbesok d ON d.dato = s.dato WHERE d.er_aapent = 0",
        trenger_persondata=True,
    ),
    # --- rettet 2026-11-03 i build_museum_db.rett_koblingsavvik og org_builder (var kjente avvik)
    Kontroll(
        "B18", "B", "hr_vakter: publikumsvakter (sal, kafé, butikk, resepsjon) på dager dagsbesok sier stengt",
        "SELECT v.vakt_id FROM main.hr_vakter v JOIN main.dagsbesok d ON d.dato = v.dato "
        "WHERE d.er_aapent = 0 AND v.stasjon NOT LIKE 'Magasin%' AND v.stasjon NOT LIKE 'Vaktrom%'",
    ),
    Kontroll(
        "B19", "B", "hr_vakter: vaktdato ligger innenfor perioden til utstillingen vakten er knyttet til",
        "SELECT v.vakt_id FROM main.hr_vakter v JOIN main.utstillinger_historikk u USING (utstilling_id) "
        "WHERE v.dato < u.periode_start OR v.dato > u.periode_slutt",
    ),
    Kontroll(
        "B20", "B", "interne_henvendelser: meldt av ansatt i jobb",
        _ikke_i_jobb("interne_henvendelser", "ansatt_id", "dato_tid"),
    ),
    Kontroll(
        "B21", "B", "hr_innleie: godkjent av ansatt i jobb ved oppdragsstart",
        _ikke_i_jobb("hr_innleie", "godkjent_av_ansatt_id", "periode_fra"),
    ),
    Kontroll(
        "B22", "B", "avvik_hms_drift: oppfølgingsansvarlig i jobb på avviksdatoen",
        _ikke_i_jobb("avvik_hms_drift", "oppfolging_ansvarlig_id", "dato"),
    ),
    Kontroll(
        "B23", "B", "hr_people (HR-demo): navn = navnet i hr_ansatte den peker på",
        "SELECT p.id, p.name, a.navn FROM main.hr_people p JOIN main.hr_ansatte a USING (ansatt_id) WHERE p.name <> a.navn",
    ),
    Kontroll(
        "B24", "B", "utstillinger med status aktiv finnes i utstillinger_historikk med overlappende periode og samme tittel",
        "SELECT u.id, u.tittel FROM main.utstillinger u WHERE u.status = 'aktiv' AND NOT EXISTS ("
        " SELECT 1 FROM main.utstillinger_historikk h WHERE h.tittel LIKE u.tittel || '%'"
        " AND h.periode_start <= u.sluttdato AND h.periode_slutt >= u.startdato)",
    ),
    Kontroll(
        "B25", "B", "hendelser bare på dager dagsbesok sier åpent",
        "SELECT h.id FROM main.hendelser h JOIN main.dagsbesok d ON d.dato = h.dato WHERE d.er_aapent = 0",
    ),
    Kontroll(
        "B26", "B", "utstillinger_historikk: ingen to utstillinger i samme sal samtidig",
        _sal_overlapp("utstillinger_historikk", "utstilling_id", "periode_start", "periode_slutt", "'SAL-' || upper(substr(sal, 5))"),
        forventet=64,
        forklaring="Arkivgeneratoren legger fokusrommene (KP-EXH-*-FOKUS-*) i sal D eller E uten å sjekke hva som står der. "
        "Alle 64 overlapp involverer et fokusrom. Ikke rettet: avklar om fokusrom er en egen sal eller deler sal.",
    ),
    Kontroll(
        "B27", "B", "utstillinger (kuratert program): ingen to utstillinger i samme sal samtidig",
        _sal_overlapp("utstillinger", "id", "startdato", "sluttdato", "sal"),
    ),
]


def kjor(museum_db: Path, persondata_db: Path | None) -> list[Resultat]:
    """Kjør alle kontrollene. Mangler persondata.db, hoppes kontrollene som trenger den over."""
    har_pd = persondata_db is not None and Path(persondata_db).is_file()
    ut: list[Resultat] = []
    with closing(sqlite3.connect(f"file:{Path(museum_db).resolve().as_posix()}?mode=ro", uri=True)) as conn:
        if har_pd:
            conn.execute("ATTACH DATABASE ? AS p", (f"file:{Path(persondata_db).resolve().as_posix()}?mode=ro",))
        for k in KONTROLLER:
            if k.trenger_persondata and not har_pd:
                ut.append(Resultat(k, None, None))
                continue
            rader = conn.execute(k.sql).fetchall()
            ut.append(Resultat(k, len(rader), tuple(rader[0]) if rader else None))
    return ut
