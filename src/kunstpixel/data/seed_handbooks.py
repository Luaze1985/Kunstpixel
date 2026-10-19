"""Seed and indexing script for Aura Kunstmuseum Virksomhetshåndbøker.

Parses Markdown handbooks from 04_knowledge/01_governance/handboker/ and indexes
structured sections into 05_data/museum.db table `handbok_oppslag`.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "05_data"
MUSEUM_DB = DATA_DIR / "museum.db"
HANDBOKER_DIR = ROOT / "04_knowledge" / "01_governance" / "handboker"

HANDBOOK_META = {
    "01_personalhandbok.md": {
        "kode": "PERSONAL",
        "navn": "Personalhåndbok",
        "malgruppe": "Alle ansatte, vikarer og ledere",
        "standard_hjemmel": "Arbeidsmiljøloven (AML) / Virke Landsoverenskomst",
    },
    "02_hms_sikkerhetshandbok.md": {
        "kode": "HMS_SIKKERHET",
        "navn": "HMS- og Sikkerhetshåndbok",
        "malgruppe": "Verneombud, salverter, montører, drift og ledere",
        "standard_hjemmel": "Internkontrollforskriften / AML kap. 3-4 / DSB",
    },
    "03_drifts_kvalitetshandbok.md": {
        "kode": "DRIFT_KVALITET",
        "navn": "Drifts- og Kvalitetshåndbok",
        "malgruppe": "Salverter, resepsjonister, kafépersonale, butikk og drift",
        "standard_hjemmel": "Matloven / Mattilsynet / Renholdsregisteret",
    },
    "04_leder_beredskapshandbok.md": {
        "kode": "LEDER_BEREDSKAP",
        "navn": "Leder- og Beredskapshåndbok",
        "malgruppe": "Museumsdirektør, avdelingsledere, vaktledere og styret",
        "standard_hjemmel": "AML kap. 2 A (Varsling) / LOA / Beredskapsplan",
    },
}


def extract_keywords(text: str, extra: list[str]) -> str:
    """Generate search tags from content."""
    known_tags = [
        "arbeidstid", "hviletid", "11 timer", "35 timer", "skiftsperre", "overtid", "kveldstillegg",
        "helgetillegg", "helligdagstillegg", "egenmelding", "sykmelding", "sykefravær", "sykt barn",
        "ferie", "velferdspermisjon", "prøvetid", "oppsigelse", "taushetsplikt", "styrk", "icom",
        "ergonomi", "stami", "terrazzo", "ståtid", "rotasjon", "løftegrenser", "15 kg", "40 kg",
        "alenearbeid", "trusler", "vold", "konflikthåndtering", "brannvern", "persontall", "250 personer",
        "rømningsvei", "evakuering", "kunstevakuering", "restverdiredning", "rvr", "skrik", "førstehjelp",
        "hjertestarter", "ruh", "avvik", "vernerunde", "verneombud", "amu", "inneklima", "luks",
        "vertskap", "universell utforming", "ledsagerbevis", "rullestol", "teleslynge", "skoleklasser",
        "åpnerutine", "stengerutine", "klima", "rh", "temperatur", "billettpriser", "honnør", "kasseoppgjør",
        "ik-mat", "haccp", "mattilsynet", "kjøletemperatur", "varmholding", "allergener", "gluten",
        "skjenkebevilling", "aldersgrense", "renholdsregisteret", "iss", "hms-kort", "tilstandsrapport",
        "kriseledelse", "beredskapsstab", "presse", "mediehåndtering", "varsling", "gjengjeldelse",
        "offentlige anskaffelser", "doffin", "habilitet", "dialogmøte", "oppfølgingsplan"
    ]
    lower_text = text.lower()
    found = [t for t in known_tags if t in lower_text]
    for e in extra:
        e_clean = e.lower().strip()
        if e_clean and e_clean not in found:
            found.append(e_clean)
    return ", ".join(found[:12])


def parse_handbook_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse a markdown handbook file into discrete chapter sections."""
    filename = file_path.name
    meta = HANDBOOK_META.get(filename)
    if not meta:
        return []

    content = file_path.read_text(encoding="utf-8")
    records = []

    # Regex to split on chapters: ## Kapittel X: Title
    chapter_pattern = re.compile(r"^##\s+Kapittel\s+(\d+):\s+(.+)$", re.MULTILINE)
    section_pattern = re.compile(r"^###\s+(\d+\.\d+)\s+(.+)$", re.MULTILINE)

    chapters = list(chapter_pattern.finditer(content))
    for i, chap_match in enumerate(chapters):
        chap_num = int(chap_match.group(1))
        chap_title = chap_match.group(2).strip()

        start_pos = chap_match.end()
        end_pos = chapters[i + 1].start() if i + 1 < len(chapters) else len(content)
        chap_content = content[start_pos:end_pos]

        sections = list(section_pattern.finditer(chap_content))
        if not sections:
            # Whole chapter as one record
            punkt_id = f"{meta['kode']}-{chap_num}.0"
            rec = {
                "punkt_id": punkt_id,
                "handbok_kode": meta["kode"],
                "handbok_navn": meta["navn"],
                "kapittel_nr": chap_num,
                "kapittel_tittel": chap_title,
                "avsnitt_tittel": chap_title,
                "malgruppe": meta["malgruppe"],
                "lovhjemmel": meta["standard_hjemmel"],
                "innhold": chap_content.strip(),
                "stikkord": extract_keywords(chap_content, [chap_title]),
                "siste_revidert": "2026-10-19",
            }
            records.append(rec)
            continue

        for j, sec_match in enumerate(sections):
            sec_num_str = sec_match.group(1)
            sec_title = sec_match.group(2).strip()

            sec_start = sec_match.end()
            sec_end = sections[j + 1].start() if j + 1 < len(sections) else len(chap_content)
            sec_body = chap_content[sec_start:sec_end].strip()

            # Identify specific law references in section text
            law_match = re.search(r"\((AML\s*§?[^\)]*|Folketrygdloven[^\)]*|Ferieloven[^\)]*|ICOM[^\)]*|STAMI[^\)]*|Mattilsynet[^\)]*|Alkoholloven[^\)]*|DSB[^\)]*)\)", sec_body)
            lovhjemmel = law_match.group(1) if law_match else meta["standard_hjemmel"]

            punkt_id = f"{meta['kode']}-{sec_num_str}"
            rec = {
                "punkt_id": punkt_id,
                "handbok_kode": meta["kode"],
                "handbok_navn": meta["navn"],
                "kapittel_nr": chap_num,
                "kapittel_tittel": chap_title,
                "avsnitt_tittel": sec_title,
                "malgruppe": meta["malgruppe"],
                "lovhjemmel": lovhjemmel,
                "innhold": sec_body,
                "stikkord": extract_keywords(sec_body, [chap_title, sec_title]),
                "siste_revidert": "2026-10-19",
            }
            records.append(rec)

    return records


SOPS_DIR = ROOT / "04_knowledge" / "02_sops"


def parse_sop_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse an operative SOP markdown file into indexed routine points."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    first_line = lines[0] if lines else ""
    title_match = re.search(r"#\s*(SOP-\d+):\s*(.+)", first_line)
    if not title_match:
        return []
    sop_code = title_match.group(1)
    sop_title = title_match.group(2).strip()

    law_match = re.search(r"\*\*Hjemmel:\*\*\s*([^\n\|]+)", content)
    hjemmel = law_match.group(1).strip() if law_match else "Arbeidsmiljøloven / Internkontroll"

    section_pattern = re.compile(r"^###\s+(\d+)\.\s+(.+)$", re.MULTILINE)
    sections = list(section_pattern.finditer(content))
    records = []
    sop_num = int(re.search(r"\d+", sop_code).group())

    for j, sec_match in enumerate(sections):
        sec_num = sec_match.group(1)
        sec_title = sec_match.group(2).strip()
        sec_start = sec_match.end()
        sec_end = sections[j + 1].start() if j + 1 < len(sections) else len(content)
        sec_body = content[sec_start:sec_end].strip()

        records.append({
            "punkt_id": f"{sop_code}-{sec_num}",
            "handbok_kode": "RUTINER_SOP",
            "handbok_navn": "Operative Rutiner (SOP)",
            "kapittel_nr": sop_num,
            "kapittel_tittel": f"{sop_code}: {sop_title}",
            "avsnitt_tittel": sec_title,
            "malgruppe": "Alle ansatte og ledere",
            "lovhjemmel": hjemmel,
            "innhold": sec_body,
            "stikkord": extract_keywords(sec_body, [sop_title, sec_title, "rutine", "sop", "prosedyre"]),
            "siste_revidert": "2026-10-19",
        })
    return records


def init_handbook_table(conn: sqlite3.Connection) -> None:
    """Create handbok_oppslag table and indexes."""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS handbok_oppslag (
                punkt_id TEXT PRIMARY KEY,
                handbok_kode TEXT NOT NULL,
                handbok_navn TEXT NOT NULL,
                kapittel_nr INTEGER NOT NULL,
                kapittel_tittel TEXT NOT NULL,
                avsnitt_tittel TEXT NOT NULL,
                malgruppe TEXT NOT NULL,
                lovhjemmel TEXT,
                innhold TEXT NOT NULL,
                stikkord TEXT NOT NULL,
                siste_revidert TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_handbok_kode ON handbok_oppslag(handbok_kode);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_handbok_kapittel ON handbok_oppslag(kapittel_nr);")


def populate_handbooks() -> int:
    """Parse all handbooks and SOPs and insert records into database."""
    all_records: list[dict[str, Any]] = []
    for file_name in HANDBOOK_META:
        path = HANDBOKER_DIR / file_name
        if path.exists():
            recs = parse_handbook_file(path)
            all_records.extend(recs)

    # Also parse standalone SOP routines in 04_knowledge/02_sops/
    if SOPS_DIR.exists():
        for sop_file in sorted(SOPS_DIR.glob("SOP-*.md")):
            all_records.extend(parse_sop_file(sop_file))

    conn = sqlite3.connect(MUSEUM_DB)
    init_handbook_table(conn)

    with conn:
        conn.execute("DELETE FROM handbok_oppslag;")
        for r in all_records:
            conn.execute("""
                INSERT INTO handbok_oppslag (
                    punkt_id, handbok_kode, handbok_navn, kapittel_nr, kapittel_tittel,
                    avsnitt_tittel, malgruppe, lovhjemmel, innhold, stikkord, siste_revidert
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["punkt_id"], r["handbok_kode"], r["handbok_navn"], r["kapittel_nr"],
                r["kapittel_tittel"], r["avsnitt_tittel"], r["malgruppe"], r["lovhjemmel"],
                r["innhold"], r["stikkord"], r["siste_revidert"]
            ))

    count = conn.execute("SELECT count(*) FROM handbok_oppslag").fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    count = populate_handbooks()
    print(f"Vellykket indeksert {count} håndbok-punkter i museum.db under handbok_oppslag.")
