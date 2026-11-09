"""Seed and indexing script for Aura Kunstmuseum Virksomhetshåndbøker og SOP-er.

Parses Markdown handbooks from 04_knowledge/01_governance/handboker/ and SOPs from
04_knowledge/02_sops/ into table `handbok_oppslag`.
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
SOPS_DIR = ROOT / "04_knowledge" / "02_sops"

HANDBOOK_META = {
    "01_personalhandbok.md": {
        "kode": "PERSONAL",
        "navn": "Personalhåndbok",
        "malgruppe": "Alle ansatte, vikarer og ledere",
        "standard_hjemmel": "Arbeidsmiljøloven (AML) § 1-1 og Virke Landsoverenskomst",
    },
    "02_hms_sikkerhetshandbok.md": {
        "kode": "HMS_SIKKERHET",
        "navn": "HMS- og Sikkerhetshåndbok",
        "malgruppe": "Verneombud, salverter, montører, drift og ledere",
        "standard_hjemmel": "Internkontrollforskriften § 5 og AML kap. 3-4",
    },
    "03_drifts_kvalitetshandbok.md": {
        "kode": "DRIFT_KVALITET",
        "navn": "Drifts- og Kvalitetshåndbok",
        "malgruppe": "Salverter, resepsjonister, kafépersonale, butikk og drift",
        "standard_hjemmel": "ICOM Code of Ethics og Internkontrollforskriften § 5",
    },
    "04_leder_beredskapshandbok.md": {
        "kode": "LEDER_BEREDSKAP",
        "navn": "Leder- og Beredskapshåndbok",
        "malgruppe": "Museumsdirektør, avdelingsledere, vaktledere og styret",
        "standard_hjemmel": "AML § 2-1 (arbeidsgivers plikter) og Internkontrollforskriften § 4",
    },
}

# Eksakte, seksjonsspesifikke lov-, forskrifts- og standardhjemler per punkt_id
SECTION_HJEMLER: dict[str, str] = {
    # 01_personalhandbok.md
    "PERSONAL-1.1": "ICOM Code of Ethics § 1 og Museumsforbundets retningslinjer",
    "PERSONAL-1.2": "AML §§ 4-1 og 4-3 (psykososialt arbeidsmiljø og vern mot trakassering)",
    "PERSONAL-2.1": "AML §§ 14-5 og 14-6, SSB STYRK-08 yrkesklassifisering",
    "PERSONAL-2.2": "AML § 15-6 og § 15-3 (7) (prøvetid og 14 dagers oppsigelsesfrist)",
    "PERSONAL-2.3": "AML §§ 3-2 og 4-2 (opplæring og medvirkning ved oppstart)",
    "PERSONAL-3.1": "AML § 10-4 (alminnelig arbeidstid) og Virke Landsoverenskomst",
    "PERSONAL-3.2": "AML § 10-8 første og annet ledd (11t daglig og 35t ukentlig hviletid)",
    "PERSONAL-3.3": "AML § 10-3 (arbeidsplan og 14 dagers varslingsfrist)",
    "PERSONAL-4.1": "AML § 14-15 (lønnsutbetaling) og Virke Landsoverenskomst lønnstrinn 20–65",
    "PERSONAL-4.2": "Virke Landsoverenskomst for museer (kvelds-, helge- og 133 % helligdagstillegg)",
    "PERSONAL-4.3": "AML § 10-6 (vilkår for overtid og minst 40–100 % overtidstillegg)",
    "PERSONAL-5.1": "AML § 2-3 (medvirknings- og varslingsplikt ved sykdom) og Folketrygdloven § 8-18",
    "PERSONAL-5.2": "Folketrygdloven §§ 8-23 til 8-27 (egenmelding etter 2 mnd, inntil 3 dager × 4)",
    "PERSONAL-5.3": "AML § 4-6 og Folketrygdloven § 8-7 (sykmelding fra 4. dag og oppfølgingsplan)",
    "PERSONAL-5.4": "Folketrygdloven kap. 9 (§§ 9-5 til 9-9 omsorgspenger ved barns sykdom) og AML § 12-9",
    "PERSONAL-6.1": "Ferieloven § 5 (25 virkedager og ekstra ferieuke fra 60 år) og Virke-tariffen",
    "PERSONAL-6.2": "Ferieloven §§ 6 og 7 (hovedferie 1. juni–30. september og varsling)",
    "PERSONAL-7.1": "Virke Landsoverenskomst (korte velferdspermisjoner med lønn)",
    "PERSONAL-7.2": "AML kapittel 12 (§§ 12-1 til 12-13 lovfestet rett til permisjon)",
    "PERSONAL-7.3": "ICOM medlemsvilkår og Skatteloven § 5-15 (skattefrie personalrabatter)",
    "PERSONAL-8.1": "ICOM Code of Ethics §§ 8.2–8.5 (forbud mot privat kunsthandel og taksering)",
    "PERSONAL-8.2": "Straffeloven § 387 (korrupsjon) og Statens etiske retningslinjer for gaver",
    "PERSONAL-8.3": "Forvaltningsloven § 13, Personopplysningsloven (GDPR) og Sikkerhetsloven",
    "PERSONAL-9.1": "Personopplysningsloven (GDPR art. 32) og forskrift om arbeidsgivers innsyn i e-post",
    "PERSONAL-9.2": "Grunnloven § 100, AML § 2-3 (lojalitetsplikt) og ICOM Code of Ethics",
    "PERSONAL-10.1": "AML § 15-3 (oppsigelsesfrister 1–6 måneder etter ansettelsestid og alder)",
    "PERSONAL-10.2": "Ferieloven § 11 (3) og AML § 14-15 (sluttoppgjør og feriepenger ved fratreden)",

    # 02_hms_sikkerhetshandbok.md
    "HMS_SIKKERHET-1.1": "AML § 1-1 og Internkontrollforskriften § 1 (formål og forsvarlig arbeidsmiljø)",
    "HMS_SIKKERHET-1.2": "Internkontrollforskriften §§ 3–4 og AML §§ 2-1 til 2-3 (ansvarsfordeling)",
    "HMS_SIKKERHET-2.1": "AML §§ 6-1 til 6-3 (verneombud og stansingsrett ved umiddelbar fare)",
    "HMS_SIKKERHET-2.2": "AML §§ 7-1 og 7-2 (arbeidsmiljøutvalg AMU og oppgaver)",
    "HMS_SIKKERHET-3.1": "AML § 4-4, Arbeidsplassforskriften § 2-1 og STAMI retningslinjer for stående arbeid",
    "HMS_SIKKERHET-3.2": "Arbeidsplassforskriften §§ 2-10 og 2-14 (belysning og inneklima) og NS-EN 15757",
    "HMS_SIKKERHET-4.1": "Forskrift om utførelse av arbeid kap. 23 (§§ 23-1 og 23-2 tunge løft) og AML § 4-4",
    "HMS_SIKKERHET-4.2": "Forskrift om organisering, ledelse og medvirkning kap. 15 (personlig verneutstyr PPE)",
    "HMS_SIKKERHET-5.1": "AML § 4-1 (3) (særskilt risikovurdering og vern mot alenearbeid)",
    "HMS_SIKKERHET-5.2": "AML § 4-1 (3) og Arbeidsplassforskriften § 2-21 (varslings- og nødsamband)",
    "HMS_SIKKERHET-6.1": "Forskrift om utførelse av arbeid kap. 23A (§§ 23A-1 til 23A-5 vold og trusler)",
    "HMS_SIKKERHET-6.2": "AML § 4-3 (4) og Forskrift om utførelse av arbeid § 23A-4 (rutiner ved akutt trussel)",
    "HMS_SIKKERHET-7.1": "Brann- og eksplosjonsvernloven § 11 og Forskrift om brannforebygging § 11 (persontall 250)",
    "HMS_SIKKERHET-7.2": "Forskrift om brannforebygging § 12 og Arbeidsplassforskriften § 2-21 (rømningsveier og nødlys)",
    "HMS_SIKKERHET-7.3": "Forskrift om brannforebygging § 12 (evakueringsplaner og brannøvelser)",
    "HMS_SIKKERHET-8.1": "ICOM Disaster Risk Management Guidelines og DSB veileder for Restverdiredning (RVR)",
    "HMS_SIKKERHET-8.2": "ICOM Code of Ethics § 2.21 (beskyttelse av samlinger i krise) og RVR-standard",
    "HMS_SIKKERHET-9.1": "Arbeidsplassforskriften § 2-22 (førstehjelpsutstyr, øyeskyll og hjertestarter AED)",
    "HMS_SIKKERHET-9.2": "AML § 5-1 og Straffeloven § 287 (hjelpeplikt og varsling ved akutt personskade)",
    "HMS_SIKKERHET-10.1": "Internkontrollforskriften § 5 annet ledd nr. 7 (avviksbehandling RUH innen 24t)",
    "HMS_SIKKERHET-10.2": "Internkontrollforskriften § 5 annet ledd nr. 8 (systematisk overvåking og gjennomgang)",

    # 03_drifts_kvalitetshandbok.md
    "DRIFT_KVALITET-1.1": "ICOM Code of Ethics § 4 (tilgjengelighet og formidling til publikum)",
    "DRIFT_KVALITET-1.2": "ICOM Code of Ethics § 4.1 og Forskrift om sikkerhet ved skole- og barnehagebesøk",
    "DRIFT_KVALITET-2.1": "Likestillings- og diskrimineringsloven §§ 17–18 og Byggteknisk forskrift (TEK17) kap. 12",
    "DRIFT_KVALITET-3.1": "Internkontrollforskriften § 5, FG-regler for skallsikring og ICOM sikkerhetsstandard",
    "DRIFT_KVALITET-3.2": "AML § 4-1 (3) (to verter ved salssveip), FG-sikringskrav og Bokføringsforskriften § 5-3-2",
    "DRIFT_KVALITET-4.1": "NS-EN 15757 (konserveringsklima 18–22 °C / 45–55 % RH) og ICOM samlingsforvaltning",
    "DRIFT_KVALITET-4.2": "CIE 157:2004 / ICOM lysnorm for museumsgjenstander (50 luks papir, 200 luks olje)",
    "DRIFT_KVALITET-5.1": "Merverdiavgiftsloven § 6-19 (unntak for museumsbilletter) og Kulturdepartementets retningslinjer",
    "DRIFT_KVALITET-5.2": "Bokføringsloven § 10, Kassasystemlova og Bokføringsforskriften § 5-3-2 (dagsoppgjør)",
    "DRIFT_KVALITET-6.1": "Matloven § 10 og Næringsmiddelhygieneforskriften § 5 (IK-Mat og HACCP-temperaturkrav)",
    "DRIFT_KVALITET-7.1": "Matinformasjonsforskriften § 4 og vedlegg II (14 deklarasjonspliktige allergener)",
    "DRIFT_KVALITET-7.2": "Næringsmiddelhygieneforskriften vedlegg II kap. VIII (personlig hygiene og 48t karantene)",
    "DRIFT_KVALITET-8.1": "Alkoholloven §§ 1-5 (aldersgrenser 18/20 år), 4-7 og 8-9 (forbud mot skjenking til berusede)",
    "DRIFT_KVALITET-9.1": "Forskrift om offentlig godkjenning av renholdsvirksomheter §§ 3 og 13 (Renholdsregisteret og HMS-kort)",
    "DRIFT_KVALITET-9.2": "Arbeidsplassforskriften § 2-8 (renhold) og ICOM retningslinjer for forebyggende konservering",
    "DRIFT_KVALITET-10.1": "ICOM Guidelines for Loans og Kulturdirektoratets vilkår for statlig innlånsforsikring",
    "DRIFT_KVALITET-10.2": "SPECTRUM 5.0 (standard for tilstandskontroll og dokumentasjon TG 1–4)",

    # 04_leder_beredskapshandbok.md
    "LEDER_BEREDSKAP-1.1": "AML § 2-1 (arbeidsgivers plikter) og Museumsforbundets prinsipper for god virksomhetsstyring",
    "LEDER_BEREDSKAP-1.2": "AML §§ 4-1 og 4-2 (krav til tilrettelegging, medvirkning og psykososialt arbeidsmiljø)",
    "LEDER_BEREDSKAP-2.1": "Stiftelsesloven / Aksjeloven kap. 6 og Økonomireglementet (fullmaktsmatrise nivå 1–3)",
    "LEDER_BEREDSKAP-3.1": "AML § 4-6 og Folketrygdloven § 8-7 (oppfølgingsplan innen 4 uker, dialogmøte 1 innen 7 uker)",
    "LEDER_BEREDSKAP-3.2": "AML § 4-6 første ledd (særlig plikt til individuell tilrettelegging av arbeid)",
    "LEDER_BEREDSKAP-4.1": "Internkontrollforskriften § 5 og DSB veileder for kriseorganisering og beredskapsstab",
    "LEDER_BEREDSKAP-4.2": "Forskrift om brannforebygging § 12 og museets beredskapsplan (primært og sekundært stabslokale)",
    "LEDER_BEREDSKAP-5.1": "Straffeloven §§ 321–324 (grovt tyveri av kulturgjenstander) og ICOM Museum Security",
    "LEDER_BEREDSKAP-5.2": "Brann- og eksplosjonsvernloven § 11 og DSB prosedyre for Restverdiredning (RVR)",
    "LEDER_BEREDSKAP-5.3": "Politiloven § 7, Sikkerhetsloven og nasjonal PLIVO-veileder (Løp – Skjul – Varsle)",
    "LEDER_BEREDSKAP-6.1": "Museets krisekommunikasjonsplan og fullmaktsmatrise (direktør som eneste talsperson)",
    "LEDER_BEREDSKAP-6.2": "Offentlighetsprinsippet, Personopplysningsloven (GDPR) og DSB krisekommunikasjonsveileder",
    "LEDER_BEREDSKAP-7.1": "AML §§ 2 A-1 og 2 A-2 (rett og plikt til å varsle om kritikkverdige forhold)",
    "LEDER_BEREDSKAP-7.2": "AML §§ 2 A-3, 2 A-4 og 2 A-6 (aktivitetsplikt, varslingsrutiner og totalforbud mot gjengjeldelse)",
    "LEDER_BEREDSKAP-8.1": "Lov om offentlige anskaffelser (LOA) § 4 og Anskaffelsesforskriften (FOA) §§ 1-1 og 5-1 (Doffin)",
    "LEDER_BEREDSKAP-8.2": "Forvaltningsloven § 6 (habilitet), FOA § 7-9 og Forskrift om godkjenning av renholdsvirksomheter",
    "LEDER_BEREDSKAP-9.1": "AML § 4-2 (2) (faglig og personlig utvikling gjennom årlig medarbeidersamtale)",
    "LEDER_BEREDSKAP-9.2": "Virke Landsoverenskomst for museer kap. 3 (lokale lønnsforhandlinger og kriterier)",
    "LEDER_BEREDSKAP-10.1": "Internkontrollforskriften § 5 annet ledd nr. 8 (årlig gjennomgang av internkontrollen)",
    "LEDER_BEREDSKAP-10.2": "AML § 18-4, Matloven § 14 og Brann- og eksplosjonsvernloven § 33 (opplysningsplikt ved tilsyn)",
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
    rev_match = re.search(r"\*\*Siste revisjon:\*\*\s*(\d{4}-\d{2}-\d{2})", content)
    revisjon = rev_match.group(1) if rev_match else "2026-10-19"
    records = []

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
            punkt_id = f"{meta['kode']}-{chap_num}.0"
            rec = {
                "punkt_id": punkt_id,
                "handbok_kode": meta["kode"],
                "handbok_navn": meta["navn"],
                "kapittel_nr": chap_num,
                "kapittel_tittel": chap_title,
                "avsnitt_tittel": chap_title,
                "malgruppe": meta["malgruppe"],
                "lovhjemmel": SECTION_HJEMLER.get(punkt_id, meta["standard_hjemmel"]),
                "innhold": chap_content.strip(),
                "stikkord": extract_keywords(chap_content, [chap_title]),
                "siste_revidert": revisjon,
            }
            records.append(rec)
            continue

        for j, sec_match in enumerate(sections):
            sec_num_str = sec_match.group(1)
            sec_title = sec_match.group(2).strip()

            sec_start = sec_match.end()
            sec_end = sections[j + 1].start() if j + 1 < len(sections) else len(chap_content)
            sec_body = chap_content[sec_start:sec_end].strip()

            punkt_id = f"{meta['kode']}-{sec_num_str}"
            if punkt_id in SECTION_HJEMLER:
                lovhjemmel = SECTION_HJEMLER[punkt_id]
            else:
                law_match = re.search(
                    r"\((AML\s*§?[^\)]*|Folketrygdloven[^\)]*|Ferieloven[^\)]*|ICOM[^\)]*|STAMI[^\)]*|Mattilsynet[^\)]*|Alkoholloven[^\)]*|DSB[^\)]*|NS-EN[^\)]*|TEK17[^\)]*|LOA[^\)]*)\)",
                    sec_body,
                )
                lovhjemmel = law_match.group(1) if law_match else meta["standard_hjemmel"]

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
                "siste_revidert": revisjon,
            }
            records.append(rec)

    return records


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

    rev_match = re.search(r"\*\*Revisjon:\*\*\s*(\d{4}-\d{2}-\d{2})", content)
    revisjon = rev_match.group(1) if rev_match else "2026-10-19"

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
            "siste_revidert": revisjon,
        })
    return records


def les_alle_handboker() -> list[dict[str, Any]]:
    """Returnerer alle indekserte punkter fra de 4 håndbøkene og samtlige SOP-filer."""
    all_records: list[dict[str, Any]] = []
    for file_name in HANDBOOK_META:
        path = HANDBOKER_DIR / file_name
        if path.exists():
            all_records.extend(parse_handbook_file(path))
    if SOPS_DIR.exists():
        for sop_file in sorted(SOPS_DIR.glob("SOP-*.md")):
            all_records.extend(parse_sop_file(sop_file))
    return all_records


def init_handbook_table(conn: sqlite3.Connection) -> None:
    """Create handbok_oppslag table and indexes."""
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


def bygg_handboker(conn: sqlite3.Connection) -> int:
    """Bygger handbok_oppslag i en åpen SQLite-tilkobling fra Markdown-kildene."""
    all_records = les_alle_handboker()
    conn.execute("DROP TABLE IF EXISTS handbok_oppslag;")
    init_handbook_table(conn)
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
    return len(all_records)


def populate_handbooks(db_path: Path = MUSEUM_DB) -> int:
    """Parse all handbooks and SOPs and insert records into database."""
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            count = bygg_handboker(conn)
        return count
    finally:
        conn.close()


if __name__ == "__main__":
    count = populate_handbooks()
    print(f"Vellykket indeksert {count} håndbok-punkter i museum.db under handbok_oppslag.")
