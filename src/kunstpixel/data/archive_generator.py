"""Archive & HR Data Generator for Kunstpixel (2010-2026) - Kunstsilo Scale.

Calibrated to the exact size of Kunstsilo (Kristiansand):
- ~35-40 full-time equivalents + ~20-25 part-time gallery hosts/guides (~60 active concurrent staff)
- ~160 unique employees across 16 years (2010-2026) with realistic turnover
- Dedicated contractor & temporary staffing register ('innleie'): ~300 contracts (scenography, Avarn/Securitas, guest curators, conservation, art transport)
- ~50,000 monthly shift records
- 102 curated exhibitions across Sal A-F
- Full export to CSV, Parquet (via DuckDB), and SQLite (05_data/arkiv/kunstpixel_historikk.db)
"""

import calendar
import json
import random
import sqlite3
from datetime import date
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "05_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Random seed for deterministic reproducibility
random.seed(42)

# --- Realism Pools ---

FIRST_NAMES_F = [
    "Ingrid", "Silje", "Astrid", "Marit", "Kari", "Hilde", "Ragnhild", "Sigrid", "Ida",
    "Camilla", "Tone", "Ellen", "Guro", "Sunniva", "Nora", "Thea", "Tuva", "Kirsti",
    "Hege", "Synnøve", "Maren", "Liv", "Anja", "Line", "Frida", "Emilie", "Signe",
    "Benedicte", "Stine", "Sofie", "Marie", "Elin", "Katrine", "Hanna", "Vilde"
]

FIRST_NAMES_M = [
    "Henrik", "Gunnar", "Terje", "Jonas", "Lars", "Erik", "Magnus", "Andreas", "Eirik",
    "Fredrik", "Sverre", "Olav", "Håkon", "Torstein", "Christian", "Espen", "Morten",
    "Bjørn", "Trond", "Geir", "Stian", "Kristian", "Alexander", "Simen", "Vegard",
    "Kjetil", "Per", "Arild", "Thomas", "Even", "Sindre", "Mikkel", "Harald"
]

LAST_NAMES = [
    "Faye-Lund", "Lindqvist", "Viken", "Moen", "Bratt", "Berg", "Eide", "Hansen",
    "Johansen", "Olsen", "Larsen", "Andersen", "Pedersen", "Nilsen", "Kristiansen",
    "Jensen", "Karlsen", "Johnsen", "Pettersen", "Eriksen", "Haugen", "Bakke",
    "Solberg", "Holm", "Lie", "Myhre", "Lund", "Nygård", "Sørensen", "Ruud",
    "Tangen", "Bjerke", "Moe", "Sandvik", "Brekke", "Dahl", "Hagen", "Sæther",
    "Strand", "Aas", "Gulliksen", "Thorvaldsen", "Helgesen", "Sivertsen"
]

DEPARTMENTS = {
    "Ledelse": [
        ("Museumsdirektør", 78, 88, 1.0),
        ("Assisterende direktør", 72, 78, 1.0),
        ("Økonomisjef", 68, 76, 1.0),
        ("HR- og organisasjonsrådgiver", 60, 68, 1.0),
        ("Administrasjonskonsulent", 50, 58, 1.0),
    ],
    "Kuratering": [
        ("Sjefkurator", 70, 78, 1.0),
        ("Seniorkurator", 64, 72, 1.0),
        ("Kurator samtidskunst", 58, 66, 1.0),
        ("Kurator modernisme", 58, 66, 1.0),
        ("Forskningsstipendiat", 54, 60, 1.0),
        ("Kuratorassistent", 46, 54, 0.8),
    ],
    "Samling": [
        ("Samlingsforvalter / Registrar", 62, 70, 1.0),
        ("Malerikonservator NKF-N", 60, 68, 1.0),
        ("Papir- og fotokonservator", 60, 68, 1.0),
        ("Digitaliserings- og samlingstekniker", 50, 58, 1.0),
        ("Magasinforvalter", 48, 56, 1.0),
    ],
    "Formidling": [
        ("Formidlingsleder", 64, 72, 1.0),
        ("DKS-koordinator (Skolesekken)", 56, 64, 1.0),
        ("Senior museumspedagog", 54, 62, 1.0),
        ("Museumspedagog", 48, 56, 0.8),
        ("Audioguide- og innholdsprodusent", 50, 58, 0.6),
        ("Museumsvert og omviser (Deltid)", 36, 44, 0.4),
        ("Seniorvert / Skrankeleder", 42, 48, 0.8),
    ],
    "Drift": [
        ("Drifts- og eiendomssjef", 66, 74, 1.0),
        ("Bygningstekniker / Montør", 48, 56, 1.0),
        ("AV- og utstillingslystekniker", 50, 58, 1.0),
        ("Sikkerhetsleder / RVR", 54, 62, 1.0),
        ("Vekter og sikkerhetsvakt", 38, 46, 0.7),
    ],
    "Marked": [
        ("Kommunikasjons- og markedssjef", 66, 74, 1.0),
        ("Digital innholdsprodusent / Web", 52, 60, 1.0),
        ("Museumsbutikkleder", 48, 56, 1.0),
        ("Butikkmedarbeider (Deltid)", 34, 40, 0.4),
        ("Kaféleder", 46, 54, 1.0),
        ("Kafémedarbeider (Deltid)", 32, 38, 0.4),
    ],
}

UNIVERSITIES = [
    "Universitetet i Oslo (UiO)",
    "Kunsthøgskolen i Oslo (KHiO)",
    "Kunstakademiet i Bergen (KMD)",
    "Universitetet i Bergen (UiB)",
    "NTNU (Trondheim)",
    "Courtauld Institute of Art (London)",
    "Goldsmiths, University of London",
    "Københavns Universitet",
    "Uppsala Universitet",
]

PREV_EMPLOYERS = [
    "Nasjonalmuseet",
    "Henie Onstad Kunstsenter",
    "Astrup Fearnley Museet",
    "KODE Kunstmuseer i Bergen",
    "Lillehammer Kunstmuseum",
    "Haugar Kunstmuseum",
    "Munchmuseet",
    "Galleri F 15",
    "Kunstnernes Hus",
    "Trondheim Kunstmuseum",
    "Stavanger kunstmuseum",
    "Kulturrådet",
]

SALER = ["Sal A", "Sal B", "Sal C", "Sal D", "Sal E"]

EXHIBITION_THEMES = [
    ("Nordisk lys og melankoli", ["Sal A", "Sal B"]),
    ("Det post-digitale lerret: Piksel og pigment", ["Sal C", "Sal D"]),
    ("Skogens hvisken: Myter fra Kittelsen til samtiden", ["Sal A", "Sal D"]),
    ("Stillhetens Rom: Kunst i Isolasjon", ["Sal B", "Sal C"]),
    ("Tekstil, vev og motstand: Hannah Ryggen i dialog", ["Sal E", "Sal D"]),
    ("Geometri og abstraksjon: Anna-Eva Bergman retrospektiv", ["Sal A", "Sal C"]),
    ("Munchs ekko: Ekspresjonisme i det 21. århundre", ["Sal D", "Sal B"]),
    ("Havet, stormen og det sublime", ["Sal A", "Sal B"]),
    ("Arkivets skjulte stemmer: Kvinner i modernismen", ["Sal E", "Sal D"]),
    ("Skulpturens materialitet: Bronse, leire og 3D-print", ["Sal C", "Sal E"]),
    ("Mellom drøm og virkelighet: Surrealistiske impulser", ["Sal A", "Sal D"]),
    ("Algoritmisk skjønnhet: Generativ kunst og persepsjon", ["Sal C", "Sal D"]),
    ("Nattens farger: Fra Backer til nattfotografi", ["Sal A", "Sal B"]),
    ("Jord, mineraler og økologisk bevissthet", ["Sal E", "Sal D"]),
    ("Taktile grenser: Keramikk og form", ["Sal B", "Sal E"]),
    ("Stille kraft: Nordisk modernisme 1910-1970", ["Sal A", "Sal C", "Sal D"]),
]

CONTRACTOR_POOLS = [
    {
        "leverandor": "Norsk Utstillingsmontasje AS",
        "orgnr": "984 512 876",
        "kategori": "Montering & Scenografi",
        "oppgaver": [
            "Oppbygging av spesialvegger og sokler før hovedutstilling",
            "Maler- og overflatearbeid i Sal A og Sal B før sesongåpning",
            "Snekring av tilpassede glassmontre for skulpturverk",
            "Nedrigging og pakking av temporære utstillingsarkitekturer"
        ],
        "timepris_range": (850, 1150),
        "timer_range": (60, 140),
        "kontakt": "Eirik Tveit"
    },
    {
        "leverandor": "Avarn Security AS",
        "orgnr": "917 234 112",
        "kategori": "Eksternt vakthold / Vernissasje",
        "oppgaver": [
            "Adgangskontroll og uniformert vakthold ved åpningsgalla",
            "Nattlig stasjonærvakt ved mottak av høysikkerhetsverk",
            "Ekstra sikkerhetsbemanning ved kveldsåpent jubileumsarrangement",
            "VIP-sikring og publikumshåndtering under festivalhelg"
        ],
        "timepris_range": (680, 890),
        "timer_range": (24, 72),
        "kontakt": "Trond Bakken"
    },
    {
        "leverandor": "Securitas AS",
        "orgnr": "912 876 543",
        "kategori": "Eksternt vakthold / Vernissasje",
        "oppgaver": [
            "Vektertjenester ved kveldsvernissasje for sommerutstillingen",
            "Tilleggssikring av Sal D under lån av internasjonale mesterverk",
            "Områdeovervåking og brannvakt under tekniske monteringsuker"
        ],
        "timepris_range": (690, 920),
        "timer_range": (30, 80),
        "kontakt": "Stian Haugen"
    },
    {
        "leverandor": "Atelier Konservering DA",
        "orgnr": "993 118 452",
        "kategori": "Tilstandsvurdering & Konservering",
        "oppgaver": [
            "Kurerovertakelse og tilstandsrapport for innlån fra Tate Gallery",
            "Avansert overflaterensing av 1930-talls oljemaleri før utstilling",
            "Papirkonservering og planering av eldre grafiske blad",
            "Klimatisk risikovurdering for særskilt sensitive papirverk"
        ],
        "timepris_range": (1100, 1550),
        "timer_range": (18, 50),
        "kontakt": "Kirsti Holte (Malerikonservator NKF)"
    },
    {
        "leverandor": "Nordic Art Transport AS",
        "orgnr": "921 789 443",
        "kategori": "Spesialtransport & Lånehåndtering",
        "oppgaver": [
            "Klimastyrt spesialtransport av verk fra Nasjonalmuseet",
            "Spesialinnpakning i klimakasser for innlån fra København",
            "Returtransport og tollbehandling for lånte kunstverk",
            "Bæring og heising av monumentalt skulpturverk til 2. etasje"
        ],
        "timepris_range": (1200, 1650),
        "timer_range": (16, 45),
        "kontakt": "Morten Ruud"
    },
    {
        "leverandor": "Lys & Rom Scenoteknikk AS",
        "orgnr": "988 345 911",
        "kategori": "AV & Multimedieteknikk",
        "oppgaver": [
            "Programmering av DMX-lysstyring for mørkerom i Sal C",
            "Kalibrering av 4K laserprojektorer for videoverk",
            "Lydteknisk akustikkdemping og høyttalerposisjonering for lydkunst",
            "Oppsett av interaktiv sensorkunst for publikum"
        ],
        "timepris_range": (950, 1350),
        "timer_range": (25, 65),
        "kontakt": "Torstein Solberg"
    },
    {
        "leverandor": "Frilans Kuratortjenester (ENK)",
        "orgnr": "924 156 879",
        "kategori": "Gjestekurator",
        "oppgaver": [
            "Kuratering og katalogessay for høstutstillingen",
            "Faglig research og verksutvalg for tematisk fokusutstilling",
            "Moderering av kunstnersamtale og symposium under åpningshelg"
        ],
        "timepris_range": (800, 1100),
        "timer_range": (80, 160),
        "kontakt": "Dr. Elena M. Viken"
    }
]


def generate_employees() -> tuple[list[dict], list[dict]]:
    """Generate ~160 employees matching Kunstsilo's organizational scale across 2010 to 2026."""
    employees = []
    personas = []
    emp_counter = 1

    # Key roles matching ICOR roster
    key_roles = [
        {
            "id": "KP-ANS-001",
            "navn": "Henrik Faye-Lund",
            "kjonn": "M",
            "fodselsaar": 1968,
            "avdeling": "Ledelse",
            "stilling": "Museumsdirektør",
            "ansatt_fra": "2010-01-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 86,
            "kontor_sal": "Administrasjonsfløyen 3. etg",
            "utdanning": [
                {"grad": "Dr.philos. Kunsthistorie", "institusjon": "Universitetet i Oslo (UiO)", "aar": 1999},
                {"grad": "Cand.philol. Kunsthistorie og filosofi", "institusjon": "UiO", "aar": 1994}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Henie Onstad Kunstsenter", "rolle": "Sjefkurator", "periode": "2002-2009"},
                {"institusjon": "Nasjonalgalleriet", "rolle": "Kurator", "periode": "1999-2002"}
            ],
            "publikasjoner": [
                "Modernismens grenseland: Nordisk kunst etter 1945 (2005)",
                "Institusjonsbygging og samfunnsansvar i kunstmuseet (2018)"
            ],
            "icor_rolle": "Museumsdirektør (/direktor)"
        },
        {
            "id": "KP-ANS-002",
            "navn": "Silje Lindqvist",
            "kjonn": "K",
            "fodselsaar": 1977,
            "avdeling": "Kuratering",
            "stilling": "Sjefkurator",
            "ansatt_fra": "2012-03-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 76,
            "kontor_sal": "Kuratorfløyen 2. etg",
            "utdanning": [
                {"grad": "MA Curating Contemporary Art", "institusjon": "Goldsmiths, University of London", "aar": 2003},
                {"grad": "Bachelor i Estetiske studier", "institusjon": "Universitetet i Oslo (UiO)", "aar": 2000}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Astrup Fearnley Museet", "rolle": "Kurator", "periode": "2006-2012"},
                {"institusjon": "Kunstnernes Hus", "rolle": "Formidlingskonsulent", "periode": "2003-2006"}
            ],
            "publikasjoner": [
                "Det post-digitale blikk: Nye medier i norsk samtidskunst (2016)",
                "Stillhetens Rom: Kuratoriske refleksjoner under pandemien (2021)"
            ],
            "icor_rolle": "Kurator (/kurator)"
        },
        {
            "id": "KP-ANS-003",
            "navn": "Gunnar Viken",
            "kjonn": "M",
            "fodselsaar": 1974,
            "avdeling": "Samling",
            "stilling": "Samlingsforvalter / Registrar",
            "ansatt_fra": "2010-01-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 68,
            "kontor_sal": "Hovedmagasinet U1",
            "utdanning": [
                {"grad": "Master i Konservering (NKF-N)", "institusjon": "Universitetet i Oslo (UiO)", "aar": 2001},
                {"grad": "Museumspedagogikk og arkivfag", "institusjon": "Universitetet i Bergen (UiB)", "aar": 1997}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "KODE Kunstmuseer i Bergen", "rolle": "Registrator", "periode": "2001-2009"}
            ],
            "publikasjoner": [
                "Standarder for magasinering og klimakontroll i kystklima (2012)",
                "Proveniensforskning i norske privatsamlinger (2019)"
            ],
            "icor_rolle": "Samlingsforvalter (/samlingsforvalter)"
        },
        {
            "id": "KP-ANS-004",
            "navn": "Astrid Moen",
            "kjonn": "K",
            "fodselsaar": 1983,
            "avdeling": "Formidling",
            "stilling": "Formidlingsleder",
            "ansatt_fra": "2014-08-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 70,
            "kontor_sal": "Formidlingssenteret 1. etg",
            "utdanning": [
                {"grad": "Master i Kunstformidling og drama", "institusjon": "Kunsthøgskolen i Oslo (KHiO)", "aar": 2009},
                {"grad": "Pedagogisk grunnmodul", "institusjon": "UiO", "aar": 2006}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Munchmuseet", "rolle": "Museumspedagog", "periode": "2009-2014"}
            ],
            "publikasjoner": [
                "Sanselig møte med kunsten: DKS i det 21. århundre (2017)"
            ],
            "icor_rolle": "Formidler (/formidler)"
        },
        {
            "id": "KP-ANS-005",
            "navn": "Terje Bratt",
            "kjonn": "M",
            "fodselsaar": 1969,
            "avdeling": "Drift",
            "stilling": "Drifts- og eiendomssjef",
            "ansatt_fra": "2010-01-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 72,
            "kontor_sal": "Driftssentralen U1",
            "utdanning": [
                {"grad": "Fagbrev Byggdrift & Sertifisert RVR-leder", "institusjon": "Forsvarsbygg / Teknisk Fagskole", "aar": 1993}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Forsvarsbygg", "rolle": "Eiendomssjef", "periode": "1995-2009"}
            ],
            "publikasjoner": [
                "Beredskapsplan for uerstattelig kulturarv ved brann og flom (2015)"
            ],
            "icor_rolle": "Driftsansvarlig (/drift)"
        },
        {
            "id": "KP-ANS-006",
            "navn": "Jonas Berg",
            "kjonn": "M",
            "fodselsaar": 2000,
            "avdeling": "Formidling",
            "stilling": "Seniorvert / Skrankeleder",
            "ansatt_fra": "2021-09-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 0.8,
            "lonnstrinn_virke": 45,
            "kontor_sal": "Skranken / Vestibylen",
            "utdanning": [
                {"grad": "Bachelor i Kunsthistorie", "institusjon": "Universitetet i Oslo (UiO)", "aar": 2023}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Kunstnernes Hus", "rolle": "Galleriassistent", "periode": "2020-2021"}
            ],
            "publikasjoner": [],
            "icor_rolle": "Museumsvert (/museumsvert)"
        },
        {
            "id": "KP-ANS-007",
            "navn": "Ragnhild Eide",
            "kjonn": "K",
            "fodselsaar": 1976,
            "avdeling": "Ledelse",
            "stilling": "Kvalitets- og complianceansvarlig",
            "ansatt_fra": "2015-01-01",
            "ansatt_til": None,
            "status": "Fast",
            "stillingsprosent": 1.0,
            "lonnstrinn_virke": 74,
            "kontor_sal": "Administrasjonsfløyen 3. etg",
            "utdanning": [
                {"grad": "Cand.jur. Forvaltningsrett og opphavsrett", "institusjon": "Universitetet i Oslo (UiO)", "aar": 2002}
            ],
            "tidligere_arbeidsgivere": [
                {"institusjon": "Kulturrådet", "rolle": "Seniorrådgiver juridisk", "periode": "2005-2014"}
            ],
            "publikasjoner": [
                "Opphavsrett og digitale museer: En veileder (2018)"
            ],
            "icor_rolle": "Kvalitetsvokter (/qa)"
        }
    ]

    for p in key_roles:
        employees.append({
            "ansatt_id": p["id"],
            "navn": p["navn"],
            "kjonn": p["kjonn"],
            "fodselsaar": p["fodselsaar"],
            "avdeling": p["avdeling"],
            "stilling": p["stilling"],
            "ansatt_fra": p["ansatt_fra"],
            "ansatt_til": p["ansatt_til"],
            "status": p["status"],
            "stillingsprosent": p["stillingsprosent"],
            "lonnstrinn_virke": p["lonnstrinn_virke"],
            "epost": f"{p['navn'].lower().replace(' ', '.').replace('-', '')}@kunstpixel.no",
            "telefon": f"+47 {random.randint(900, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            "kontor_sal": p["kontor_sal"]
        })
        personas.append(p)
        emp_counter += 1

    # Kunstsilo Scale Distribution:
    # Baseline in 2010: ~45 staff members
    # Annual replenishment/turnover: ~7-9 new staff members per year
    # Yields ~160 total unique staff over 16 years (exactly Kunstsilo scale)
    cohort_distribution = [
        (2010, 42),
        (2011, 7), (2012, 8), (2013, 7), (2014, 8),
        (2015, 8), (2016, 7), (2017, 8), (2018, 7),
        (2019, 8), (2020, 6), (2021, 7), (2022, 10),
        (2023, 9), (2024, 8), (2025, 7), (2026, 4)
    ]

    for year, count in cohort_distribution:
        for _ in range(count):
            gender = random.choice(["K", "M"])
            first_name = random.choice(FIRST_NAMES_F if gender == "K" else FIRST_NAMES_M)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"

            # Pick department and role
            dept_name = random.choices(
                list(DEPARTMENTS.keys()),
                weights=[0.08, 0.16, 0.12, 0.36, 0.14, 0.14],
                k=1
            )[0]
            role_spec = random.choice(DEPARTMENTS[dept_name])
            role_title, min_pay, max_pay, standard_pct = role_spec

            if "leder" in role_title.lower() or "sjef" in role_title.lower() or "senior" in role_title.lower():
                birth_year = random.randint(1965, 1985)
            elif "vert" in role_title.lower() or "kafé" in role_title.lower() or "butikk" in role_title.lower():
                birth_year = random.randint(1992, 2004)
            else:
                birth_year = random.randint(1975, 1995)

            if year == 2010:
                start_month = 1
                start_day = 1
            else:
                start_month = random.randint(1, 12)
                start_day = random.choice([1, 15])
            ansatt_fra = f"{year:04d}-{start_month:02d}-{start_day:02d}"

            is_student_or_temp = "vert" in role_title.lower() or "deltid" in role_title.lower() or "kafé" in role_title.lower()
            if is_student_or_temp:
                tenure_years = random.choices([2, 3, 4, 5], weights=[0.35, 0.35, 0.20, 0.10])[0]
            else:
                tenure_years = random.choices([3, 6, 10, 16], weights=[0.25, 0.40, 0.20, 0.15])[0]

            end_year = year + tenure_years
            if end_year < 2026:
                end_month = random.randint(1, 12)
                ansatt_til = f"{end_year:04d}-{end_month:02d}-28"
                status = "Sluttet"
            else:
                ansatt_til = None
                status = "Fast" if standard_pct >= 0.8 else "Deltid / Sesong"

            pct = standard_pct
            if pct < 1.0:
                pct = round(random.choice([0.3, 0.4, 0.5, 0.6]), 2)

            pay = random.randint(min_pay, max_pay)
            emp_id = f"KP-ANS-{emp_counter:03d}"
            emp_counter += 1

            email_name = full_name.lower().replace(' ', '.').replace('ø', 'o').replace('æ', 'ae').replace('å', 'a')
            email = f"{email_name}@kunstpixel.no"
            phone = f"+47 {random.randint(400, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"

            if dept_name == "Ledelse":
                location = "Administrasjonsfløyen 3. etg"
            elif dept_name == "Kuratering":
                location = "Kuratorfløyen 2. etg"
            elif dept_name == "Samling":
                location = "Konserveringsatelier U1 / Magasin"
            elif dept_name == "Drift":
                location = "Driftssentralen U1 / Sikkerhetsrom"
            elif dept_name == "Marked":
                location = "Kafé / Butikk / Markedskontor"
            else:
                location = random.choice(SALER + ["Resepsjon / Skranke", "Formidlingsrom"])

            employees.append({
                "ansatt_id": emp_id,
                "navn": full_name,
                "kjonn": gender,
                "fodselsaar": birth_year,
                "avdeling": dept_name,
                "stilling": role_title,
                "ansatt_fra": ansatt_fra,
                "ansatt_til": ansatt_til,
                "status": status,
                "stillingsprosent": pct,
                "lonnstrinn_virke": pay,
                "epost": email,
                "telefon": phone,
                "kontor_sal": location
            })

            # For senior/curator/head roles, append detailed CV to personas
            if dept_name in ("Kuratering", "Samling", "Ledelse") and pct >= 0.8 and len(personas) < 28:
                personas.append({
                    "id": emp_id,
                    "navn": full_name,
                    "avdeling": dept_name,
                    "stilling": role_title,
                    "utdanning": [
                        {
                            "grad": f"Master i {random.choice(['Kunsthistorie', 'Konservering', 'Kuratering', 'Estetikk'])}",
                            "institusjon": random.choice(UNIVERSITIES),
                            "aar": birth_year + 26
                        }
                    ],
                    "tidligere_arbeidsgivere": [
                        {
                            "institusjon": random.choice(PREV_EMPLOYERS),
                            "rolle": f"Tidligere {role_title.lower()}",
                            "periode": f"{year - random.randint(2, 6)}-{year}"
                        }
                    ],
                    "publikasjoner": [
                        f"Refleksjoner om {random.choice(['nordisk modernisme', 'materiell bevaring', 'digital kuratering', 'veggtekstens dramaturgi'])} ({year - 1})"
                    ]
                })

    return employees, personas


def generate_exhibitions(employees: list[dict]) -> list[dict]:
    """Generate 16 years of exhibitions (2010-2026) across Sal A-F."""
    exhibitions = []
    exh_counter = 1

    curators = [e for e in employees if e["avdeling"] == "Kuratering" or e["ansatt_id"] == "KP-ANS-002"]

    seasons = [
        ("Vinter", "01-15", "03-01", 12000),
        ("Vår", "03-20", "05-30", 24000),
        ("Sommer", "06-15", "08-30", 38000),
        ("Høst", "09-15", "12-15", 32000),
    ]

    for year in range(2010, 2027):
        for season_name, start_md, end_md, base_attendance in seasons:
            exh_id = f"KP-EXH-{year}-{exh_counter:03d}"
            exh_counter += 1

            theme_title, rooms = random.choice(EXHIBITION_THEMES)
            curator_cand = [c for c in curators if c["ansatt_fra"] <= f"{year}-01-01" and (c["ansatt_til"] is None or c["ansatt_til"] >= f"{year}-12-31")]
            curator_name = curator_cand[0]["navn"] if curator_cand else "Silje Lindqvist"

            attendance_factor = random.uniform(0.85, 1.25)
            status_note = "Gjennomført"
            if year == 2020:
                attendance_factor *= 0.35
                status_note = "Gjennomført med kohort- og smittevernsrestriksjoner"
            elif year == 2021:
                attendance_factor *= 0.55
                status_note = "Gjennomført med kapasitetsbegrensning (50 pers per sal)"
            elif year == 2026:
                status_note = "Pågående / Planlagt sesong 2026"

            attendance = int(base_attendance * attendance_factor)
            budget = random.randint(450, 2200) * 1000

            exhibitions.append({
                "utstilling_id": exh_id,
                "aar": year,
                "sesong": season_name,
                "tittel": f"{theme_title} ({year})",
                "kurator": curator_name,
                "saler": ", ".join(rooms),
                "periode_start": f"{year}-{start_md}",
                "periode_slutt": f"{year}-{end_md}",
                "antall_verk": random.randint(18, 65),
                "besokstall_total": attendance,
                "budsjett_nok": budget,
                "katalog_isbn": f"978-82-99812-{random.randint(10, 99)}-{random.randint(1, 9)}",
                "status": status_note
            })

        # Add 2 focus project room exhibitions in Sal D or Sal E
        for extra in [1, 2]:
            exh_id = f"KP-EXH-{year}-FOKUS-{extra}"
            room = random.choice(["Sal D", "Sal E"])
            exhibitions.append({
                "utstilling_id": exh_id,
                "aar": year,
                "sesong": "Prosjektrom",
                "tittel": f"Fokusrom {year}.{extra}: Samtidens materialer",
                "kurator": "Silje Lindqvist",
                "saler": room,
                "periode_start": f"{year}-04-01",
                "periode_slutt": f"{year}-10-31",
                "antall_verk": random.randint(6, 14),
                "besokstall_total": int(random.randint(8000, 16000) * (0.4 if year in (2020, 2021) else 1.0)),
                "budsjett_nok": random.randint(150, 450) * 1000,
                "katalog_isbn": f"978-82-99812-{random.randint(10, 99)}-{random.randint(1, 9)}",
                "status": "Prosjektrom gjestekunstner"
            })

    return exhibitions


def generate_contractors(exhibitions: list[dict]) -> list[dict]:
    """Generate ~300 realistic contractor / innleie contracts over 16 years (Kunstsilo scale)."""
    contracts = []
    contract_counter = 1

    approvers = [
        ("KP-ANS-001", "Henrik Faye-Lund (Museumsdirektør)"),
        ("KP-ANS-002", "Silje Lindqvist (Sjefkurator)"),
        ("KP-ANS-005", "Terje Bratt (Drifts- og eiendomssjef)"),
        ("KP-ANS-003", "Gunnar Viken (Samlingsforvalter)"),
    ]

    for year in range(2010, 2027):
        # Find exhibitions for this year
        year_exhs = [e for e in exhibitions if e["aar"] == year]

        # Generate ~18-20 contracts per year
        num_contracts = random.randint(17, 21) if year != 2020 else 12  # fewer in pandemic 2020

        for _ in range(num_contracts):
            pool_item = random.choice(CONTRACTOR_POOLS)
            exh = random.choice(year_exhs) if year_exhs else None
            exh_id = exh["utstilling_id"] if exh else f"KP-EXH-{year}-001"

            hours = random.randint(*pool_item["timer_range"])
            rate = random.randint(*pool_item["timepris_range"])
            total_nok = hours * rate
            task_desc = random.choice(pool_item["oppgaver"])

            month = random.randint(1, 12)
            start_d = f"{year:04d}-{month:02d}-05"
            end_d = f"{year:04d}-{month:02d}-24"

            # Assign responsible internal manager
            if pool_item["kategori"] in ("Montering & Scenografi", "AV & Multimedieteknikk", "Eksternt vakthold / Vernissasje"):
                approver_id, approver_name = approvers[2]  # Terje Bratt
            elif pool_item["kategori"] == "Tilstandsvurdering & Konservering":
                approver_id, approver_name = approvers[3]  # Gunnar Viken
            elif pool_item["kategori"] == "Gjestekurator":
                approver_id, approver_name = approvers[1]  # Silje Lindqvist
            else:
                approver_id, approver_name = approvers[0]  # Henrik Faye-Lund

            contract_id = f"KP-INN-{year}-{contract_counter:04d}"
            contract_counter += 1

            contracts.append({
                "innleie_id": contract_id,
                "aar": year,
                "leverandor": pool_item["leverandor"],
                "orgnr": pool_item["orgnr"],
                "kategori": pool_item["kategori"],
                "oppdragsbeskrivelse": task_desc,
                "knyttet_utstilling_id": exh_id,
                "periode_fra": start_d,
                "periode_til": end_d,
                "fakturerte_timer": hours,
                "timepris_nok": rate,
                "totalbelop_nok": total_nok,
                "kontaktperson_ekstern": pool_item["kontakt"],
                "godkjent_av_ansatt_id": approver_id,
                "godkjent_av_navn": approver_name,
                "status": "Utført og fakturert" if year < 2026 else "Aktiv rammeavtale / Pågående"
            })

    return contracts


def generate_shift_history(employees: list[dict], exhibitions: list[dict]) -> list[dict]:
    """Generate ~55,000 monthly duty logs (Kunstsilo scale) using calendar & demand model.
    
    Guarantees:
    - 0 persondays > 13h (max 1 shift per person per day)
    - 0 persondays > 24h
    - 0 Monday public shifts (museum closed on Mondays, only internal Magasin 1 and Vaktrom)
    - Dager 1..28/29/30/31 all represented via calendar.monthrange
    - Stations 100% harmonized with museum.db (Sal A-E, Magasin 1, Resepsjon, Butikk, Kafé, Vaktrom)
    - Shift workload scaled appropriately to stillingsprosent with weekly rest limits
    """
    shifts = []
    shift_counter = 1

    def get_active_exhibition(year: int, month: int) -> str:
        for ex in exhibitions:
            if ex["aar"] == year:
                start_m = int(ex["periode_start"].split("-")[1])
                end_m = int(ex["periode_slutt"].split("-")[1])
                if start_m <= month <= end_m:
                    return ex["utstilling_id"]
        return "KP-EXH-FASTE-SAMLING"

    duty_stations_open = [
        ("Resepsjon og billett", ["Formidling", "Marked"]),
        ("Museumsbutikk", ["Marked", "Formidling"]),
        ("Museumskafé", ["Marked", "Formidling"]),
        ("Vaktrom / Sikkerhetssentral", ["Drift"]),
        ("Magasin 1 (Klimastyrt lager)", ["Samling", "Drift"]),
        ("Sal A (Mytologi og natur)", ["Formidling"]),
        ("Sal B (Realisme og samfunn)", ["Formidling"]),
        ("Sal C (Lys, farge og interiør)", ["Formidling"]),
        ("Sal D (Eksistens og modernisme)", ["Formidling"]),
        ("Sal E (Temporær utstilling)", ["Formidling"]),
    ]

    duty_stations_monday = [
        ("Magasin 1 (Klimastyrt lager)", ["Samling", "Drift"]),
        ("Vaktrom / Sikkerhetssentral", ["Drift"]),
    ]

    emp_recent_days: dict[str, list[date]] = {}
    monthly_counts: dict[tuple[str, int, int], int] = {}

    for year in range(2010, 2027):
        for month in range(1, 13):
            active_exh = get_active_exhibition(year, month)
            max_days = calendar.monthrange(year, month)[1]

            for day in range(1, max_days + 1):
                cur_date = date(year, month, day)
                date_str = cur_date.isoformat()
                weekday = cur_date.weekday()

                active_staff = [
                    e for e in employees
                    if e["ansatt_fra"] <= date_str and (e["ansatt_til"] is None or e["ansatt_til"] >= date_str)
                    and e["avdeling"] in ("Formidling", "Drift", "Marked", "Samling")
                ]

                stations = duty_stations_monday if weekday == 0 else duty_stations_open
                daily_assigned = set()

                for station_name, pref_depts in stations:
                    def is_eligible(emp, max_week_shifts=5):
                        emp_id = emp["ansatt_id"]
                        if emp_id in daily_assigned:
                            return False
                        recent = emp_recent_days.get(emp_id, [])
                        week_shifts = [dt for dt in recent if 0 < (cur_date - dt).days < 7]
                        if len(week_shifts) >= max_week_shifts:
                            return False
                        return True

                    cands = [e for e in active_staff if is_eligible(e, 5)]
                    pref_cands = [e for e in cands if e["avdeling"] in pref_depts]
                    pool = pref_cands if pref_cands else cands

                    if not pool:
                        cands = [e for e in active_staff if is_eligible(e, 6)]
                        pref_cands = [e for e in cands if e["avdeling"] in pref_depts]
                        pool = pref_cands if pref_cands else cands

                    if not pool:
                        pool = [e for e in active_staff if e["ansatt_id"] not in daily_assigned]

                    if not pool:
                        continue

                    def sort_key(emp):
                        emp_id = emp["ansatt_id"]
                        current_m = monthly_counts.get((emp_id, year, month), 0)
                        target_m = int(emp["stillingsprosent"] * 21)
                        return (current_m / max(1, target_m), current_m)

                    pool.sort(key=sort_key)
                    chosen = pool[0]
                    emp_id = chosen["ansatt_id"]

                    daily_assigned.add(emp_id)
                    if emp_id not in emp_recent_days:
                        emp_recent_days[emp_id] = []
                    emp_recent_days[emp_id].append(cur_date)
                    emp_recent_days[emp_id] = [dt for dt in emp_recent_days[emp_id] if (cur_date - dt).days <= 7]

                    monthly_counts[(emp_id, year, month)] = monthly_counts.get((emp_id, year, month), 0) + 1

                    shifts.append({
                        "vakt_id": f"VAKT-{shift_counter:07d}",
                        "ansatt_id": emp_id,
                        "aar": str(year),
                        "maaned": str(month),
                        "dato": date_str,
                        "stasjon": station_name,
                        "avdeling": chosen["avdeling"],
                        "rolle": chosen["stilling"],
                        "timer": 7.5,
                        "utstilling_id": active_exh
                    })
                    shift_counter += 1

    return shifts


def export_all(employees: list[dict], personas: list[dict], exhibitions: list[dict], contracts: list[dict], shifts: list[dict]):
    """Export datasets to CSV, Parquet, JSON, and SQLite."""
    import duckdb  # lastes her: blokkeres av Windows på noen maskiner
    import pandas as pd

    print("Converting to Pandas DataFrames...")
    df_emp = pd.DataFrame(employees)
    df_exh = pd.DataFrame(exhibitions)
    df_inn = pd.DataFrame(contracts)
    df_shifts = pd.DataFrame(shifts)

    # 1. CSV
    print("Writing CSV files to 05_data/...")
    df_emp.to_csv(DATA_DIR / "arkiv_hr_ansatte.csv", index=False, encoding="utf-8")
    df_exh.to_csv(DATA_DIR / "arkiv_utstillinger_2010_2026.csv", index=False, encoding="utf-8")
    df_inn.to_csv(DATA_DIR / "arkiv_hr_innleie.csv", index=False, encoding="utf-8")
    df_shifts.to_csv(DATA_DIR / "arkiv_hr_vakt_historikk.csv", index=False, encoding="utf-8")

    # 2. JSON for Personas & CVs
    print("Writing JSON personas to 05_data/...")
    with open(DATA_DIR / "arkiv_cv_personas.json", "w", encoding="utf-8") as f:
        json.dump(personas, f, ensure_ascii=False, indent=2)

    # 3. Parquet via DuckDB
    print("Writing Parquet files via DuckDB...")
    duckdb.query("SELECT * FROM df_emp").write_parquet(str(DATA_DIR / "arkiv_hr_ansatte.parquet"))
    duckdb.query("SELECT * FROM df_exh").write_parquet(str(DATA_DIR / "arkiv_utstillinger_2010_2026.parquet"))
    duckdb.query("SELECT * FROM df_inn").write_parquet(str(DATA_DIR / "arkiv_hr_innleie.parquet"))
    duckdb.query("SELECT * FROM df_shifts").write_parquet(str(DATA_DIR / "arkiv_hr_vakt_historikk.parquet"))

    # 4. SQLite Enterprise Archive Database
    db_file = DATA_DIR / "arkiv" / "kunstpixel_historikk.db"
    print(f"Creating and populating SQLite database: {db_file}...")
    if db_file.exists():
        db_file.unlink()

    conn = sqlite3.connect(db_file)
    df_emp.to_sql("hr_ansatte", conn, index=False)
    df_exh.to_sql("utstillinger_historikk", conn, index=False)
    df_inn.to_sql("hr_innleie", conn, index=False)
    df_shifts.to_sql("hr_vakter", conn, index=False)

    # Store personas table
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE personas (
            id TEXT PRIMARY KEY,
            navn TEXT,
            avdeling TEXT,
            stilling TEXT,
            icor_rolle TEXT,
            cv_json TEXT
        )
    """)
    for p in personas:
        cur.execute(
            "INSERT INTO personas (id, navn, avdeling, stilling, icor_rolle, cv_json) VALUES (?, ?, ?, ?, ?, ?)",
            (p["id"], p["navn"], p["avdeling"], p["stilling"], p.get("icor_rolle", ""), json.dumps(p, ensure_ascii=False))
        )
    conn.commit()
    conn.close()

    print("\nKunstsilo-scale dataset generation completed successfully!")
    print(f"- Total employees in HR history (2010-2026): {len(df_emp):,}")
    print(f"- Key personas with deep CVs: {len(personas):,}")
    print(f"- Exhibitions cataloged (2010-2026): {len(df_exh):,}")
    print(f"- Contractor / innleie contracts: {len(df_inn):,} (Total: {df_inn['totalbelop_nok'].sum():,} NOK)")
    print(f"- Shift & duty logs recorded: {len(df_shifts):,}")
    print(f"- Total rows across archive: {len(df_emp) + len(df_exh) + len(df_inn) + len(df_shifts):,}")


# --- Syntetiske klokkeslett og arbeidstidsgrenser (Datafinner) ---
# Egne datafiler som byggeskriptet (build_museum_db.py) leser inn i museum.db. Klokkeslettene trekkes
# med en egen Random per vakt_id, så de påvirker ikke resten av arkivet og er stabile mellom kjøringer.
KLOKKESLETT_CSV = DATA_DIR / "arkiv_hr_vakt_klokkeslett.csv"
GRENSER_CSV = DATA_DIR / "arbeidstid_grenser.csv"
SYNTETISK = "syntetisk (archive_generator)"
LUNSJ_TIMER = 0.5  # Personalhåndbok: 7,5 t per dag ekskl. 30 min ulønnet lunsj
STARTVALG_HVERDAG = ["08:00", "08:30", "09:00", "09:30"]
STARTVALG_HELG = ["10:00", "10:30"]
STARTVALG_STASJON = {
    "Vaktrom / Sikkerhetssentral": ["07:00", "15:00"],
    "Museumskafé": ["09:00", "10:00"],
}
ARBEIDSTID_GRENSER = [
    ("ukenorm_timer", 37.5, "timer per uke", "Ordinær ukentlig arbeidstid for heltid", "Personalhåndbok (handbok_oppslag) og Virke"),
    ("dognmaks_timer", 9.0, "timer per døgn", "Alminnelig arbeidstid per døgn", "AML § 10-4 (ADR 009)"),
    ("daglig_hvile_timer", 11.0, "timer", "Sammenhengende daglig arbeidsfri", "AML § 10-8 (ADR 009)"),
    ("ukehvile_timer", 35.0, "timer", "Sammenhengende ukentlig arbeidsfri", "AML § 10-8 (ADR 009)"),
    ("lunsj_timer", LUNSJ_TIMER, "timer", "Ulønnet lunsjpause per vakt", "Personalhåndbok (handbok_oppslag)"),
    ("kveldstillegg_fra", 17.0, "klokketime", "Kveldstillegg for vakter som slutter etter dette", "Virke (calculate_shift_cost)"),
]


def _til_klokke(timer: float) -> str:
    minutter = round(timer * 60)
    return f"{minutter // 60:02d}:{minutter % 60:02d}"


def generate_shift_times(vakter_csv: Path = DATA_DIR / "arkiv_hr_vakt_historikk.csv",
                         ut_csv: Path = KLOKKESLETT_CSV) -> int:
    """Lag syntetisk start og slutt for hver vakt: start fra faste valg, slutt = start + timer + lunsj."""
    import csv

    rader = []
    with open(vakter_csv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rng = random.Random(f"klokkeslett-{r['vakt_id']}")
            dag = date.fromisoformat(r["dato"])
            valg = STARTVALG_STASJON.get(r["stasjon"]) or (STARTVALG_HELG if dag.weekday() >= 5 else STARTVALG_HVERDAG)
            start = rng.choice(valg)
            start_t = int(start[:2]) + int(start[3:]) / 60
            slutt_t = start_t + float(r["timer"]) + LUNSJ_TIMER
            if slutt_t >= 24:
                raise ValueError(f"Vakt {r['vakt_id']} går over midnatt")
            rader.append((r["vakt_id"], start, _til_klokke(slutt_t), SYNTETISK))
    with open(ut_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["vakt_id", "start", "slutt", "datakilde"])
        w.writerows(rader)
    return len(rader)


def generate_working_time_limits(ut_csv: Path = GRENSER_CSV) -> int:
    """Skriv arbeidstidsgrensene som data, merket syntetisk, med kilde for hver grense."""
    import csv

    with open(ut_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["navn", "verdi", "enhet", "beskrivelse", "kilde", "datakilde"])
        for navn, verdi, enhet, beskrivelse, kilde in ARBEIDSTID_GRENSER:
            w.writerow([navn, verdi, enhet, beskrivelse, kilde, SYNTETISK])
    return len(ARBEIDSTID_GRENSER)


def generate_virke_tariff_tillegg(ut_csv: Path = DATA_DIR / "virke_tariff_tillegg.csv") -> int:
    """Generer tariff-trinn 66-86 med jevn stigning fra trinn 65."""
    import csv

    # Trinn 65: aarslonn = 815 000, trinn 64: 798 400 (stigning 16 600 per trinn)
    # kveldstillegg = +56 kr/t, helgetillegg = +75 kr/t, helligdag = ordinaer * (973.82 / 417.95)
    rader = []
    base_lonn = 815000
    stigning = 16600
    for trinn in range(66, 87):
        aarslonn = base_lonn + (trinn - 65) * stigning
        timesats_ordinar = round(aarslonn / 1950, 2)
        timesats_kveld = round(timesats_ordinar + 56.0, 2)
        timesats_helg = round(timesats_ordinar + 75.0, 2)
        timesats_helligdag = round(timesats_ordinar * 2.3299916, 2)
        if trinn == 86:
            tittel = "Museumsdirektør"
        elif trinn >= 78:
            tittel = f"Virke trinn {trinn} (Toppledelse / Direktør)"
        elif trinn >= 72:
            tittel = f"Virke trinn {trinn} (Assisterende direktør / Sjefkurator / Avdelingssjef)"
        else:
            tittel = f"Virke trinn {trinn} (Leder / Fagspesialist)"
        rader.append([
            trinn, tittel, aarslonn, timesats_ordinar, timesats_kveld, timesats_helg,
            timesats_helligdag, "2024-05-01", SYNTETISK
        ])

    with open(ut_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([
            "lonnstrinn", "tittel_eksempel", "aarslonn_nok", "timesats_ordinar",
            "timesats_kveld", "timesats_helg", "timesats_helligdag", "gjeldende_fra", "datakilde"
        ])
        w.writerows(rader)
    return len(rader)


def generate_absence_records(ut_csv: Path = DATA_DIR / "arkiv_hr_fravaer.csv") -> int:
    """Generer syntetisk sykefravær og permisjon (2010-2026).

    Krav:
    - Kvartalsvis sykefraversprosent innenfor +-1.5 prosentpoeng av ssb_sykefraver_kultur.
    - INGEN fravaersdag kan kollidere med vakt i hr_vakter for samme ansatt.
    - Fravaer registreres for aktive ansatte i kvartalet.
    """
    import csv
    from datetime import timedelta

    base_db_path = DATA_DIR / "kilde" / "museum_base.db"
    if not base_db_path.is_file():
        raise FileNotFoundError(f"Mangler {base_db_path}")

    con = sqlite3.connect(f"file:{base_db_path.resolve().as_posix()}?mode=ro", uri=True)
    try:
        emps = con.execute("SELECT ansatt_id, ansatt_fra, ansatt_til, stillingsprosent FROM hr_ansatte").fetchall()
        ssb_quarters = con.execute(
            "SELECT aar, kvartal, sykefraver_prosent, egenmeldt_prosent, legemeldt_prosent "
            "FROM ssb_sykefraver_kultur ORDER BY aar, kvartal"
        ).fetchall()
        shift_days: set[tuple[str, str]] = set(
            con.execute("SELECT ansatt_id, dato FROM hr_vakter").fetchall()
        )
    finally:
        con.close()

    quarter_dates = {
        1: (date(2000, 1, 1), date(2000, 3, 31)),
        2: (date(2000, 4, 1), date(2000, 6, 30)),
        3: (date(2000, 7, 1), date(2000, 9, 30)),
        4: (date(2000, 10, 1), date(2000, 12, 31)),
    }

    absence_records = []
    fravaer_idx = 1
    rng = random.Random("kunstpixel-fravaer-2010-2026-v1")

    for aar, kvartal, ssb_tot, ssb_egen, ssb_lege in ssb_quarters:
        q_start = date(aar, (kvartal - 1) * 3 + 1, 1)
        if kvartal == 1:
            q_end = date(aar, 3, 31)
        elif kvartal == 2:
            q_end = date(aar, 6, 30)
        elif kvartal == 3:
            q_end = date(aar, 9, 30)
        else:
            q_end = date(aar, 12, 31)

        # Aktive ansatte i kvartalet
        aktive_i_kvartal = []
        mulige_dagsverk = 0.0
        for emp_id, fra_s, til_s, st_pros in emps:
            e_fra = date.fromisoformat(fra_s) if fra_s else date(2010, 1, 1)
            e_til = date.fromisoformat(til_s) if til_s else date(2099, 12, 31)
            if e_fra <= q_end and e_til >= q_start:
                pros = float(st_pros or 1.0)
                aktive_i_kvartal.append((emp_id, pros, e_fra, e_til))
                mulige_dagsverk += pros * 58.75

        # Mål for antall sykedager (sykefraver_prosent)
        target_sick_days = (ssb_tot / 100.0) * mulige_dagsverk
        actual_sick_days = 0

        # Alle tilgjengelige hverdager i kvartalet
        all_q_weekdays = []
        cur_d = q_start
        while cur_d <= q_end:
            if cur_d.weekday() < 5:
                all_q_weekdays.append(cur_d)
            cur_d += timedelta(days=1)

        # Trekk fraværsepisoder deterministisk
        used_employee_days: set[tuple[str, str]] = set()
        attempts = 0
        while actual_sick_days < target_sick_days and attempts < 3000:
            attempts += 1
            emp_id, pros, e_fra, e_til = rng.choice(aktive_i_kvartal)
            # Velg type: egenmelding (1-3 dager) eller sykemelding (4-12 dager)
            is_egen = rng.random() < (ssb_egen / ssb_tot if ssb_tot > 0 else 0.2)
            varighet = rng.randint(1, 3) if is_egen else rng.randint(4, 10)
            ftype = "egenmelding" if is_egen else "sykemelding"

            start_cand = rng.choice(all_q_weekdays)
            # Episode må ligge helt innenfor kvartalet og ansettelsesperioden
            slutt_cand = start_cand + timedelta(days=varighet - 1)
            if slutt_cand > q_end or slutt_cand > e_til or start_cand < e_fra:
                continue

            # Sjekk HVER kalenderdag i intervallet [start_cand, slutt_cand]
            kollisjon = False
            cur_check = start_cand
            while cur_check <= slutt_cand:
                d_iso = cur_check.isoformat()
                if (emp_id, d_iso) in shift_days or (emp_id, d_iso) in used_employee_days:
                    kollisjon = True
                    break
                cur_check += timedelta(days=1)

            if not kollisjon:
                cur_mark = start_cand
                added_sick = 0
                while cur_mark <= slutt_cand:
                    used_employee_days.add((emp_id, cur_mark.isoformat()))
                    if cur_mark.weekday() < 5:
                        added_sick += 1
                    cur_mark += timedelta(days=1)
                actual_sick_days += added_sick
                fid = f"FRAV-{fravaer_idx:06d}"
                fravaer_idx += 1
                absence_records.append([fid, emp_id, start_cand.isoformat(), slutt_cand.isoformat(), ftype, SYNTETISK])

        # Legg til permisjoner per kvartal for variasjon (kun hvis ingen kollisjon)
        if rng.random() < 0.5 and aktive_i_kvartal:
            emp_id, pros, e_fra, e_til = rng.choice(aktive_i_kvartal)
            start_cand = rng.choice(all_q_weekdays)
            slutt_cand = start_cand + timedelta(days=4)
            if slutt_cand <= q_end and slutt_cand <= e_til and start_cand >= e_fra:
                kollisjon = False
                cur_check = start_cand
                while cur_check <= slutt_cand:
                    d_iso = cur_check.isoformat()
                    if (emp_id, d_iso) in shift_days or (emp_id, d_iso) in used_employee_days:
                        kollisjon = True
                        break
                    cur_check += timedelta(days=1)
                if not kollisjon:
                    cur_mark = start_cand
                    while cur_mark <= slutt_cand:
                        used_employee_days.add((emp_id, cur_mark.isoformat()))
                        cur_mark += timedelta(days=1)
                    fid = f"FRAV-{fravaer_idx:06d}"
                    fravaer_idx += 1
                    absence_records.append([fid, emp_id, start_cand.isoformat(), slutt_cand.isoformat(), "permisjon", SYNTETISK])

    with open(ut_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["fravaer_id", "ansatt_id", "fra", "til", "type", "datakilde"])
        w.writerows(absence_records)

    return len(absence_records)


def generate_shift_adjustments(ut_csv: Path = DATA_DIR / "arkiv_hr_vakt_justering.csv") -> int:
    """Generer justeringer for 2-4 % av vaktene som forlenges til 9-11 timer.

    Knyttet til datoer for utstillingsaapninger (vernissasjer), kveldsarrangementer og fredag/loerdag.
    Endrer IKKE arkiv_hr_vakt_historikk.csv.
    """
    import csv

    base_db_path = DATA_DIR / "kilde" / "museum_base.db"
    if not base_db_path.is_file():
        raise FileNotFoundError(f"Mangler {base_db_path}")

    con = sqlite3.connect(f"file:{base_db_path.resolve().as_posix()}?mode=ro", uri=True)
    try:
        exh_dates = set(r[0] for r in con.execute("SELECT DISTINCT periode_start FROM utstillinger_historikk WHERE periode_start IS NOT NULL").fetchall())
        ev_dates = set(r[0] for r in con.execute("SELECT DISTINCT dato FROM hendelser WHERE dato IS NOT NULL").fetchall())
        special_dates = exh_dates | ev_dates

        # Hent alle vakter
        shifts = con.execute("SELECT vakt_id, dato FROM hr_vakter ORDER BY vakt_id").fetchall()
    finally:
        con.close()

    # Prioriter vakter på spesialdatoer og fredager/lørdager
    candidate_shifts = []
    other_shifts = []
    for vakt_id, dato in shifts:
        d = date.fromisoformat(dato)
        if dato in special_dates or d.weekday() in (4, 5):
            candidate_shifts.append((vakt_id, dato))
        else:
            other_shifts.append((vakt_id, dato))

    rng = random.Random("kunstpixel-vakt-justering-overtid-2026")
    # Mål: ~3 % av 54 994 = ~1650 vakter
    target_count = round(len(shifts) * 0.03)

    # Velg ~80 % fra kandidater og ~20 % fra andre
    cand_sample_count = min(len(candidate_shifts), round(target_count * 0.85))
    selected_cands = rng.sample(candidate_shifts, cand_sample_count)
    rem_count = target_count - len(selected_cands)
    selected_others = rng.sample(other_shifts, rem_count)

    chosen = sorted(selected_cands + selected_others, key=lambda x: x[0])

    rader = []
    for vakt_id, dato in chosen:
        # Forleng til 9.0, 9.5, 10.0, 10.5 eller 11.0 timer
        nye_timer = rng.choice([9.0, 9.5, 10.0, 10.5, 11.0])
        rader.append([vakt_id, nye_timer, SYNTETISK])

    with open(ut_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["vakt_id", "nye_timer", "datakilde"])
        w.writerows(rader)

    return len(rader)


if __name__ == "__main__" and "--bare-klokkeslett" in __import__("sys").argv:
    print(f"Klokkeslett: {generate_shift_times()} vakter -> {KLOKKESLETT_CSV.name}")
    print(f"Grenser: {generate_working_time_limits()} rader -> {GRENSER_CSV.name}")
elif __name__ == "__main__" and "--bare-tariff" in __import__("sys").argv:
    print(f"Tariff tillegg: {generate_virke_tariff_tillegg()} trinn -> virke_tariff_tillegg.csv")
elif __name__ == "__main__" and "--bare-fravaer" in __import__("sys").argv:
    print(f"Sykefravær: {generate_absence_records()} rader -> arkiv_hr_fravaer.csv")
elif __name__ == "__main__" and "--bare-overtid" in __import__("sys").argv:
    print(f"Vaktjusteringer (overtid): {generate_shift_adjustments()} vakter -> arkiv_hr_vakt_justering.csv")
elif __name__ == "__main__":
    print("Generating Kunstpixel HR, Innleie & Exhibition History (Kunstsilo Scale 2010-2026)...")
    emps, pers = generate_employees()
    exhs = generate_exhibitions(emps)
    contracts = generate_contractors(exhs)
    shfts = generate_shift_history(emps, exhs)
    export_all(emps, pers, exhs, contracts, shfts)
    generate_shift_times()
    generate_working_time_limits()
    generate_virke_tariff_tillegg()
    generate_absence_records()
