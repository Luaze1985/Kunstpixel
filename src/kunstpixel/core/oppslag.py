"""Oppslag i det interne: håndbøker (oppgave 03) og alle andre interne kilder (internsøk).

Alt her leser bare. Databasen åpnes skrivebeskyttet via core.db, og filene leses som tekst.
Fasit: tests/test_mvp_oppslag.py (sok) og tests/test_internsok.py (sok_internt, sok_filer).

Det interne søket tar ikke med personer: ingen navn, kontaktinfo, fravær, kompetanse per
person, og ingen varsler (CASE-013) eller saker om sykefravær og tilrettelegging (CASE-012).
Slike spørsmål hører til bemanning og vurdering (oppgave 07–09).
"""

from __future__ import annotations

import re
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from src.kunstpixel.core import llm
from src.kunstpixel.core.db import execute_read_query, query_handbook

STOPPORD = {
    "hva", "er", "i", "på", "for", "til", "og", "eller", "om", "det", "den", "som", "hvilke", "hvilket",
    "hvilken", "gjelder", "når", "noen", "må", "kan", "får", "jeg", "vi", "har", "hvor", "mange", "ved",
    "en", "et", "av", "med", "de", "skal", "hvordan", "finn", "vis", "alt", "mine", "min", "vårt",
}

# Hver kilde er en tabell. Kolonnenavnene her er faste og kommer aldri fra brukeren.
# `vis` er de eneste feltene som sendes ut. Ingenting annet fra tabellen forlater databasen.
KILDER: list[dict[str, Any]] = [
    {
        "kode": "hms_avvik", "navn": "HMS-avvik", "tabell": "hms_avvik_tekst", "id": "avvik_id",
        "tittel": "alvorlighetsgrad || ' · ' || avdeling || ' · ' || stasjon",
        "sok": ["beskrivelse", "strakstiltak", "avdeling", "stasjon", "alvorlighetsgrad"],
        "tekst": "beskrivelse",
        "vis": [("Dato", "dato"), ("Avdeling", "avdeling"), ("Stasjon", "stasjon"), ("Alvorlighet", "alvorlighetsgrad"),
                ("Strakstiltak", "strakstiltak"), ("Ansvarlig rolle", "ansvarlig_rolle"), ("Status", "status")],
    },
    {
        "kode": "drift_avvik", "navn": "Avvik i drift og sikkerhet", "tabell": "avvik_hms_drift", "id": "avvik_id",
        "tittel": "kategori || ' · ' || alvorlighetsgrad || ' · ' || dato",
        "sok": ["beskrivelse", "strakstiltak", "kategori", "berort_sal_id"],
        "tekst": "beskrivelse",
        "vis": [("Dato", "dato"), ("Kategori", "kategori"), ("Alvorlighet", "alvorlighetsgrad"), ("Sal", "berort_sal_id"),
                ("Strakstiltak", "strakstiltak"), ("Status", "status")],
    },
    {
        "kode": "henvendelser", "navn": "Interne henvendelser", "tabell": "interne_henvendelser", "id": "sak_id",
        "tittel": "tittel",
        # Varsler og saker om helse og tilrettelegging skjermes (CASE-013 og CASE-012). Personen vises aldri.
        "hvor": "case_ref NOT IN ('CASE-013', 'CASE-012') AND kategori NOT IN ('varsling', 'sykefraver', 'tilrettelegging')",
        "sok": ["tittel", "fritekst", "kategori", "paragraf_hjemmel"],
        "tekst": "fritekst",
        "vis": [("Dato", "dato_tid"), ("Kategori", "kategori"), ("Hjemmel", "paragraf_hjemmel")],
    },
    {
        "kode": "ergonomi", "navn": "Ergonomi og rotasjon", "tabell": "hms_ergonomi_rotasjon", "id": "stasjon_id",
        "tittel": "navn",
        "sok": ["navn", "underlag_type", "stasjon_id"],
        "tekst": "underlag_type",
        "vis": [("Underlag", "underlag_type"), ("Maks sammenhengende timer", "maks_sammenhengende_timer"),
                ("Sittepause i minutter", "krav_om_sittepause_minutter"), ("Anbefalt rotasjon", "anbefalt_rotasjon_stasjon_id")],
    },
    {
        "kode": "arbeidstid", "navn": "Arbeidstidsgrenser", "tabell": "arbeidstid_grenser", "id": "navn",
        "tittel": "beskrivelse",
        "sok": ["navn", "beskrivelse", "enhet", "kilde"],
        "tekst": "beskrivelse",
        "vis": [("Verdi", "verdi"), ("Enhet", "enhet"), ("Kilde", "kilde")],
    },
    {
        "kode": "tariff", "navn": "Virke-tariff", "tabell": "virke_tariff", "id": "lonnstrinn",
        "tittel": "tittel_eksempel",
        "sok": ["tittel_eksempel", "lonnstrinn"],
        "tekst": "tittel_eksempel",
        "vis": [("Lønnstrinn", "lonnstrinn"), ("Årslønn", "aarslonn_nok"), ("Timesats", "timesats_ordinar"),
                ("Kveld", "timesats_kveld"), ("Helg", "timesats_helg"), ("Helligdag", "timesats_helligdag"),
                ("Gjelder fra", "gjeldende_fra")],
    },
    {
        "kode": "regler", "navn": "Regler for HR, HMS og kvalitet", "tabell": "hr_rules", "id": "id",
        "tittel": "domain || ' · ' || topic",
        "hvor": "status = 'active'",
        "sok": ["topic", "domain", "action_json", "condition_json", "owner_role"],
        "tekst": "action_json",
        "vis": [("Domene", "domain"), ("Tema", "topic"), ("Tiltak", "action_json"), ("Eier", "owner_role"), ("Kilde", "source")],
    },
    {
        "kode": "rapportregler", "navn": "Rapportregler", "tabell": "rapport_regler", "id": "regel_id",
        "tittel": "felt || ' ' || operator || ' ' || terskel",
        "sok": ["vurdering", "forslag", "felt", "sporsmal_id"],
        "tekst": "vurdering",
        "vis": [("Vurdering", "vurdering"), ("Forslag", "forslag"), ("Kilde", "kilde"), ("Versjon", "versjon")],
    },
    {
        "kode": "roller", "navn": "Roller", "tabell": "roller", "id": "kode",
        "tittel": "navn",
        "sok": ["navn", "beskrivelse", "trigger"],
        "tekst": "beskrivelse",
        "vis": [("Rolle", "navn"), ("Trigger", "trigger")],
    },
    {
        "kode": "ferdigheter", "navn": "Ferdigheter og kurs", "tabell": "org_ferdigheter", "id": "skill_code",
        "tittel": "navn",
        "sok": ["navn", "skill_code", "kategori"],
        "tekst": "navn",
        "vis": [("Kategori", "kategori"), ("Utløper", "utloper")],
    },
]

KILDENAVN = ["Håndbøker"] + [k["navn"] for k in KILDER] + ["Interne dokumenter"]


def _tokens(sporsmal: str) -> list[str]:
    ord_ = [t for t in re.findall(r"\w+", (sporsmal or "").lower()) if len(t) >= 3]
    nyttige = [t for t in ord_ if t not in STOPPORD] or ord_
    ut: list[str] = []
    for t in nyttige:
        for kandidat in (t, t[:-3] if len(t) > 5 and t.endswith("ene") else None,
                         t[:-2] if len(t) > 4 and t.endswith(("en", "et", "er")) else None):
            if kandidat and kandidat not in ut:
                ut.append(kandidat)
    return ut[:7]


def _kort(tekst: Any, maks: int = 700) -> str:
    s = "" if tekst is None else str(tekst).strip()
    return s if len(s) <= maks else s[: maks - 1].rstrip() + "…"


def sok(sporsmal: str, db_path: Path | str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    """Søk i håndbøkene. Hvert treff har punkt_id, handbok_kode, avsnitt_tittel og innhold. Tom streng gir tom liste."""
    if not sporsmal or not sporsmal.strip():
        return []
    return query_handbook(query=sporsmal.strip(), limit=limit, db_path=db_path)


def svar(
    sporsmal: str,
    konfig: llm.LlmKonfig | None,
    begrenser: llm.Begrenser | None,
    apne=urllib.request.urlopen,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Håndbokoppslag med et kort AI-svar over treffene. Treffene kommer alltid med.

    status: "ok" (AI-svar finnes), "ingen_kilde" (null treff, AI blir ikke spurt), "ai_av" (ingen konfig),
    "grense_naadd" (taket på kall per time er nådd) eller "ai_feil" (feil hos leverandøren, `feilkode` sier hvilken).
    """
    treff = sok(sporsmal, db_path=db_path)
    if not treff:
        return {"treff": [], "ai": None, "status": "ingen_kilde"}
    if konfig is None:
        return {"treff": treff, "ai": None, "status": "ai_av"}
    if begrenser is not None and not begrenser.tillat():
        return {"treff": treff, "ai": None, "status": "grense_naadd"}
    try:
        ai = llm.svar_fra_handbok(sporsmal, treff, konfig, apne=apne)
    except llm.LlmFeil as feil:
        return {"treff": treff, "ai": None, "status": "ai_feil", "feilkode": feil.kode, "melding": str(feil)}
    return {"treff": treff, "ai": ai, "status": "ok"}


def _finnes(tabell: str, db_path: Path | str | None) -> bool:
    rader = execute_read_query("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (tabell,), db_path)
    return bool(rader)


def _sok_kilde(kilde: dict[str, Any], tokens: list[str], db_path: Path | str | None, limit: int) -> list[dict[str, Any]]:
    if not _finnes(kilde["tabell"], db_path):
        return []
    params: dict[str, Any] = {"limit": limit}
    treff_uttrykk, poeng = [], []
    for i, tok in enumerate(tokens):
        navn = f"t{i}"
        params[navn] = f"%{tok}%"
        match = " OR ".join(f"LOWER(CAST({kol} AS TEXT)) LIKE :{navn}" for kol in kilde["sok"])
        treff_uttrykk.append(f"({match})")
        poeng.append(f"(CASE WHEN {match} THEN 1 ELSE 0 END)")
    hvor = f"({' OR '.join(treff_uttrykk)})"
    if kilde.get("hvor"):
        hvor += f" AND ({kilde['hvor']})"
    kolonner = {kilde["id"], kilde["tekst"], *(kol for _, kol in kilde["vis"])}
    sql = (
        f"SELECT {kilde['id']} AS _id, {kilde['tittel']} AS _tittel, "
        + ", ".join(f"{k} AS c_{k}" for k in sorted(kolonner))
        + f" FROM {kilde['tabell']} WHERE {hvor} ORDER BY ({' + '.join(poeng)}) DESC, _id ASC LIMIT :limit"
    )
    ut = []
    for r in execute_read_query(sql, params, db_path):
        felt = [[etikett, str(r[f"c_{kol}"])] for etikett, kol in kilde["vis"] if r[f"c_{kol}"] not in (None, "")]
        ut.append({"id": str(r["_id"]), "tittel": _kort(r["_tittel"] or r["_id"], 140),"tekst": _kort(r[f"c_{kilde['tekst']}"]), "felt": felt})
    return ut


def sok_filer(
    sporsmal: str,
    rot: Path,
    mapper: Iterable[str],
    filtyper: set[str],
    maks_storrelse: int,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Finn interne tekstfiler som nevner ordene i spørsmålet. Rangert etter hvor mange ord filen har."""
    tokens = _tokens(sporsmal)
    if not tokens:
        return []
    funn: list[tuple[int, str, int, str]] = []
    for mappe in mapper:
        base = rot / mappe
        if not base.is_dir():
            continue
        for sti in sorted(base.rglob("*")):
            if not sti.is_file() or sti.suffix.lower() not in filtyper or sti.stat().st_size > maks_storrelse:
                continue
            try:
                linjer = sti.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            tekst_lav = "\n".join(linjer).lower()
            poeng = sum(1 for t in tokens if t in tekst_lav)
            if not poeng:
                continue
            beste = max(range(len(linjer)), key=lambda i: sum(1 for t in tokens if t in linjer[i].lower()), default=0)
            funn.append((poeng, sti.relative_to(rot).as_posix(), beste + 1, linjer[beste].strip() if linjer else ""))
    funn.sort(key=lambda f: (-f[0], f[1]))
    return [
        {"id": s, "tittel": s, "tekst": _kort(linje, 300), "felt": [["Linje", str(no)]]}
        for _, s, no, linje in funn[:limit]
    ]


def sok_internt(
    sporsmal: str,
    db_path: Path | str | None = None,
    limit: int = 3,
    filer: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Søk på tvers av håndbøker og alle interne tabeller. Gruppert per kilde, med kilde på hvert treff.

    Returnerer {"sporsmal", "status", "antall", "kilder", "grupper": [{"kode", "navn", "treff": [...]}]}.
    status er "tomt_sporsmal", "ingen_kilde" eller "ok". `filer` er ferdige filtreff (fra sok_filer).
    """
    if not sporsmal or not sporsmal.strip():
        return {"sporsmal": "", "status": "tomt_sporsmal", "antall": 0, "kilder": KILDENAVN, "grupper": []}
    tokens = _tokens(sporsmal)
    grupper: list[dict[str, Any]] = []
    hb = [
        {
            "id": t["punkt_id"],
            "tittel": f"{t['handbok_navn']} · {t['kapittel_tittel']} · {t['avsnitt_tittel']}",
            "tekst": _kort(t["innhold"], 1200),
            "felt": [[etikett, str(t[kol])] for etikett, kol in
                     (("Håndbok", "handbok_kode"), ("Kapittel", "kapittel_tittel"), ("Avsnitt", "avsnitt_tittel"),
                      ("Hjemmel", "lovhjemmel")) if t.get(kol)],
        }
        for t in sok(sporsmal, db_path=db_path, limit=max(limit, 5))
    ]
    if hb:
        grupper.append({"kode": "handbok", "navn": "Håndbøker", "treff": hb})
    for kilde in KILDER:
        treff = _sok_kilde(kilde, tokens, db_path, limit) if tokens else []
        if treff:
            grupper.append({"kode": kilde["kode"], "navn": kilde["navn"], "treff": treff})
    if filer:
        grupper.append({"kode": "dokumenter", "navn": "Interne dokumenter", "treff": filer})
    antall = sum(len(g["treff"]) for g in grupper)
    return {"sporsmal": sporsmal.strip(), "status": "ok" if antall else "ingen_kilde", "antall": antall,
            "kilder": KILDENAVN, "grupper": grupper}
