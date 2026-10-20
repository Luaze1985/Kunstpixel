"""
Genererer time-for-time historiske vaktdata OG komplette syntetiske
personopplysninger (alminnelige + GDPR art. 9 særlige kategorier + eksterne OSINT-kilder)
for alle 168 ansatte ved museet i Trondheim.

Eksporterer til:
1. 05_data/colab_personvern_historikk.db (komplett SQLite-database for Colab)
2. 05_data/ansatte_168_komplett_personvern_trondheim.csv (oversikt over alle 168 ansatte)
3. 05_data/vakt_time_for_time_2025_2026.csv (uttrekk av time-for-time vakter)
"""

import os
import csv
import json
import random
import sqlite3
from datetime import datetime, date

# Trøndersk geografisk forankring (Trondheim og omegn)
TRONDHEIM_OMRAADER = [
    ("7011", "Midtbyen (Trondheim)", "Munkegata", "Sykkel / Gange (Midtbyen)"),
    ("7014", "Bakklandet (Trondheim)", "Nedre Bakklandet", "Sykkel / Gange (Bakklandet)"),
    ("7018", "Ila (Trondheim)", "Ilevollen", "Gråkallbanen (Lian–Byåsen–Ila–St. Olavs gt)"),
    ("7020", "Byåsen (Trondheim)", "Byåsveien", "Gråkallbanen (Lian–Byåsen–Ila–St. Olavs gt)"),
    ("7030", "Elgeseter / Øya (Trondheim)", "Elgeseter gate", "AtB Metrobuss M1/M2 (Sør–Midtbyen)"),
    ("7042", "Lade / Møllenberg (Trondheim)", "Innherredsveien", "AtB Metrobuss M3 (Lade–Midtbyen)"),
    ("7052", "Tyholt / Moholt (Trondheim)", "Jonsvannsveien", "AtB Metrobuss M3 (Moholt–Midtbyen)"),
    ("7058", "Ranheim (Trondheim)", "Ranheimsvegen", "SJ Nord Trønderbanen Nord (Stjørdal–Ranheim–Trondheim S)"),
    ("7075", "Tiller (Trondheim)", "Ivar Lykkes veg", "AtB Metrobuss M1/M2 (Tiller/Heimdal–Midtbyen)"),
    ("7088", "Heimdal (Trondheim)", "Rosten", "SJ Nord Trønderbanen Sør (Melhus–Heimdal–Trondheim S)"),
    ("7500", "Stjørdal", "Kjøpmannsgata", "SJ Nord Trønderbanen Nord (Stjørdal–Ranheim–Trondheim S)"),
    ("7224", "Melhus", "Melhusvegen", "SJ Nord Trønderbanen Sør (Melhus–Heimdal–Trondheim S)"),
]

TRONDHEIM_KOLLEKTIV_AVVIK = [
    {
        "avvik_kode": "TRD-AVV-01",
        "dato_fra": "2023-08-07",
        "dato_til": "2023-08-11",
        "linje": "SJ Nord Trønderbanen Nord (Stjørdal–Ranheim–Trondheim S)",
        "hendelse": "Rasfare og stengt jernbanespor ved Hommelvik/Leangen under ekstremvær",
        "type": "Totalstans tog nordfra"
    },
    {
        "avvik_kode": "TRD-AVV-02",
        "dato_fra": "2024-01-03",
        "dato_til": "2024-01-05",
        "linje": "AtB Metrobuss M1/M2 (Tiller/Heimdal–Midtbyen)",
        "hendelse": "Snøkaos og sperret Okstadbakken / E6 Sør – leddbusser fast på tvers",
        "type": "Kollaps busskorridor sør"
    },
    {
        "avvik_kode": "TRD-AVV-03",
        "dato_fra": "2022-10-17",
        "dato_til": "2022-10-21",
        "linje": "Gråkallbanen (Lian–Byåsen–Ila–St. Olavs gt)",
        "hendelse": "Kjørestrømbrudd og sporvekselfeil ved Breidablikk / Kyvannet",
        "type": "Stans trikk Byåsen"
    },
    {
        "avvik_kode": "TRD-AVV-04",
        "dato_fra": "2023-11-18",
        "dato_til": "2023-11-18",
        "linje": "SJ Nord Trønderbanen Sør (Melhus–Heimdal–Trondheim S)",
        "hendelse": "Signalfeil på Dovrebanen/Trønderbanen mellom Heimdal og Selsbakk",
        "type": "Helgestans tog sørfra"
    },
]

FAGFORENINGER_PER_AVD = {
    "Kuratering": ["Forskerforbundet", "Forskerforbundet", "Parat", "Uorganisert"],
    "Samling": ["Forskerforbundet", "NITO", "Fagforbundet", "Uorganisert"],
    "Formidling": ["Fagforbundet", "Creo", "Forskerforbundet", "Uorganisert"],
    "Drift": ["Fagforbundet", "NITO", "Parat", "Uorganisert"],
    "Marked": ["Parat", "Fagforbundet", "Creo", "Uorganisert"],
    "Ledelse": ["Samfunnsviterne", "Econas", "Uorganisert", "Forskerforbundet"],
}

HELSE_PROFILER = [
    ("Ingen registrerte helsebegrensninger", "LAV"),
    ("Ingen registrerte helsebegrensninger", "LAV"),
    ("Ingen registrerte helsebegrensninger", "LAV"),
    ("Ingen registrerte helsebegrensninger", "LAV"),
    ("STAMI-tilrettelegging: Maks 2t sammenhengende ståtid (korsrygg/prolaps)", "HØY"),
    ("BHT-notat: Migrene utløst av flimrende spotbelysning i Sal C og Sal E", "HØY"),
    ("Astma/støvallergi: Skal unngå lengre arbeid i eldre magasin uten åndedrettsvern", "MODERAT"),
    ("Senebetennelse/belastningsskade skulder etter tung utstillingsmontering", "MODERAT"),
    ("Redusert nattesøvn / fritak fra seine kveldsvakter etter kl. 20:00 (BHT)", "HØY"),
    ("Tinnitus / lydsensitivitet: Fritak fra barneverksteder og fullsatte skoleomvisninger", "MODERAT"),
]

SIVILSTAND_VALG = ["Gift", "Samboer", "Enslig", "Skilt"]

FORNAVN_PAARORENDE = [
    "Ingrid", "Håvard", "Marit", "Olav", "Kjersti", "Trond", "Ragnhild",
    "Erlend", "Siri", "Jørgen", "Åse", "Steinar", "Berit", "Øystein"
]


def beregn_virke_lonn(lonnstrinn: int, stillingsprosent: float) -> int:
    # Realistisk Virke-skala 2025/2026: trinn 20 ~ 395 000, trinn 86 ~ 1 120 000
    full_lonn = 395000 + (lonnstrinn - 20) * 10900
    return int(round(full_lonn * stillingsprosent, -2))


def generate_hourly_records():
    rng = random.Random(42)
    data_dir = os.path.abspath("05_data")
    vakt_hist_csv = os.path.join(data_dir, "arkiv_hr_vakt_historikk.csv")
    vakt_klokke_csv = os.path.join(data_dir, "arkiv_hr_vakt_klokkeslett.csv")
    vakt_just_csv = os.path.join(data_dir, "arkiv_hr_vakt_justering.csv")
    ansatte_csv = os.path.join(data_dir, "arkiv_hr_ansatte.csv")
    fravaer_csv = os.path.join(data_dir, "arkiv_hr_fravaer.csv")
    innleie_csv = os.path.join(data_dir, "arkiv_hr_innleie.csv")

    db_out = os.path.join(data_dir, "colab_personvern_historikk.db")
    sample_csv_out = os.path.join(data_dir, "vakt_time_for_time_2025_2026.csv")
    komplett_ansatte_csv_out = os.path.join(data_dir, "ansatte_168_komplett_personvern_trondheim.csv")

    print("[1/7] Laster inn klokkeslett og overtidsjusteringer for vakter...")
    times = {}
    with open(vakt_klokke_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            times[row["vakt_id"]] = (row["start"], row["slutt"])

    overtid_map = {}
    if os.path.exists(vakt_just_csv):
        with open(vakt_just_csv, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                overtid_map[row["vakt_id"]] = float(row["nye_timer"])

    if os.path.exists(db_out):
        os.remove(db_out)

    conn = sqlite3.connect(db_out)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE vakt_time_for_time (
        vakt_id TEXT,
        ansatt_id TEXT,
        dato TEXT,
        aar INTEGER,
        maaned INTEGER,
        time_slot TEXT,
        klokketime INTEGER,
        stasjon TEXT,
        avdeling TEXT,
        rolle TEXT,
        utstilling_id TEXT,
        faktiske_timer_vakt REAL
    )
    """)

    print("[2/7] Ekspanderer vakter til time-for-time rader...")
    batch = []
    sample_rows = []
    total_hourly_rows = 0
    ansatt_overtid_count = {}
    ansatt_stasjon_timer = {}

    with open(vakt_hist_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            vid = row["vakt_id"]
            if vid not in times:
                continue
            start_str, slutt_str = times[vid]
            start_h = int(start_str.split(":")[0])
            slutt_h = int(slutt_str.split(":")[0])
            if slutt_h < start_h:
                slutt_h += 24

            faktiske_timer = overtid_map.get(vid, float(row.get("timer", 7.5)))
            aid = row["ansatt_id"]
            if faktiske_timer >= 10.0:
                ansatt_overtid_count[aid] = ansatt_overtid_count.get(aid, 0) + 1

            aar = int(row["aar"])
            maaned = int(row["maaned"])
            dato = row["dato"]
            stasjon = row["stasjon"]
            avdeling = row["avdeling"]
            rolle = row["rolle"]
            utstilling = row["utstilling_id"]

            ansatt_stasjon_timer.setdefault(aid, {})
            ansatt_stasjon_timer[aid][stasjon] = ansatt_stasjon_timer[aid].get(stasjon, 0) + (slutt_h - start_h)

            for h in range(start_h, slutt_h):
                actual_h = h % 24
                slot_str = f"{actual_h:02d}:00"
                rec = (
                    vid, aid, dato, aar, maaned, slot_str, actual_h,
                    stasjon, avdeling, rolle, utstilling, faktiske_timer
                )
                batch.append(rec)
                if aar in (2025, 2026):
                    sample_rows.append(rec)

                if len(batch) >= 50000:
                    cur.executemany("INSERT INTO vakt_time_for_time VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", batch)
                    total_hourly_rows += len(batch)
                    batch = []

    if batch:
        cur.executemany("INSERT INTO vakt_time_for_time VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", batch)
        total_hourly_rows += len(batch)

    print(f"       Totalt generert: {total_hourly_rows} time-for-time rader.")

    print("[3/7] Bygger indekser...")
    cur.execute("CREATE INDEX idx_vakt_tid_stasjon ON vakt_time_for_time (dato, time_slot, stasjon)")
    cur.execute("CREATE INDEX idx_vakt_ansatt ON vakt_time_for_time (ansatt_id, dato)")
    cur.execute("CREATE INDEX idx_vakt_aar ON vakt_time_for_time (aar)")

    print("[4/7] Analyserer fraværsdata og kobler mot kollektivavvik i Trondheim...")
    cur.execute("""
    CREATE TABLE hr_fravaer (
        fravaer_id TEXT,
        ansatt_id TEXT,
        fra TEXT,
        til TEXT,
        type TEXT
    )
    """)
    fravaer_per_ansatt = {}
    if os.path.exists(fravaer_csv):
        with open(fravaer_csv, mode="r", encoding="utf-8") as f:
            fravaer_batch = []
            for r in csv.DictReader(f):
                aid = r["ansatt_id"]
                fra = r["fra"]
                til = r["til"]
                ftype = r["type"]
                fravaer_batch.append((r.get("fravaer_id", ""), aid, fra, til, ftype))
                d1 = datetime.strptime(fra, "%Y-%m-%d").date()
                d2 = datetime.strptime(til, "%Y-%m-%d").date()
                days = max(1, (d2 - d1).days + 1)
                info = fravaer_per_ansatt.setdefault(aid, {"episoder": 0, "dager": 0, "egenmeldinger": 0, "datoer": []})
                info["episoder"] += 1
                info["dager"] += days
                if ftype == "egenmelding":
                    info["egenmeldinger"] += 1
                info["datoer"].append((fra, til, ftype))
            cur.executemany("INSERT INTO hr_fravaer VALUES (?,?,?,?,?)", fravaer_batch)

    # Lag tabell for kollektivavvik i Trondheim
    cur.execute("""
    CREATE TABLE kollektiv_avvik_trondheim (
        avvik_kode TEXT PRIMARY KEY,
        dato_fra TEXT,
        dato_til TEXT,
        linje TEXT,
        hendelse TEXT,
        type TEXT
    )
    """)
    for av in TRONDHEIM_KOLLEKTIV_AVVIK:
        cur.execute(
            "INSERT INTO kollektiv_avvik_trondheim VALUES (?,?,?,?,?,?)",
            (av["avvik_kode"], av["dato_fra"], av["dato_til"], av["linje"], av["hendelse"], av["type"])
        )

    # Innleie-tabell for habilitetssjekk
    cur.execute("""
    CREATE TABLE hr_innleie (
        innleie_id TEXT,
        aar INTEGER,
        leverandor TEXT,
        orgnr TEXT,
        kategori TEXT,
        totalbelop_nok REAL,
        kontaktperson_ekstern TEXT,
        godkjent_av_ansatt_id TEXT,
        godkjent_av_navn TEXT
    )
    """)
    if os.path.exists(innleie_csv):
        with open(innleie_csv, mode="r", encoding="utf-8") as f:
            inn_batch = [
                (
                    r["innleie_id"], int(r["aar"]), r["leverandor"], r["orgnr"],
                    r["kategori"], float(r["totalbelop_nok"]), r["kontaktperson_ekstern"],
                    r["godkjent_av_ansatt_id"], r["godkjent_av_navn"]
                )
                for r in csv.DictReader(f)
            ]
            cur.executemany("INSERT INTO hr_innleie VALUES (?,?,?,?,?,?,?,?,?)", inn_batch)

    print("[5/7] Genererer rike personopplysninger og sensitiv mosaikkprofil for alle 168 ansatte i Trondheim...")
    cur.execute("""
    CREATE TABLE hr_ansatte (
        ansatt_id TEXT PRIMARY KEY,
        navn TEXT,
        kjonn TEXT,
        fodselsaar INTEGER,
        avdeling TEXT,
        stilling TEXT,
        status TEXT,
        stillingsprosent REAL,
        lonnstrinn_virke INTEGER,
        epost TEXT,
        telefon TEXT,
        kontor_sal TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE hr_utvidet_profil_trondheim (
        ansatt_id TEXT PRIMARY KEY,
        navn TEXT,
        fodselsdato TEXT,
        syntetisk_fnr TEXT,
        adresse_trondheim TEXT,
        postnummer TEXT,
        bydel_kommune TEXT,
        pendlerlinje_atb TEXT,
        sivilstand TEXT,
        antall_barn_under_12 INTEGER,
        naermeste_paarorende TEXT,
        fagforening_art9 TEXT,
        helse_ergonomi_art9 TEXT,
        sykefravaer_episoder INTEGER,
        sykefravaer_dager INTEGER,
        overtid_aml_brudd_antall INTEGER,
        primar_stasjon TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE ekstern_osint_trondheim (
        ansatt_id TEXT PRIMARY KEY,
        virke_aarslonn_nok INTEGER,
        skatteliste_nettoinntekt INTEGER,
        skatteliste_nettoformue INTEGER,
        inntektsavvik_forklaring TEXT,
        brreg_roller_verv TEXT,
        habilitet_flagg TEXT,
        kollektiv_avvik_treff TEXT,
        mosaikk_risikoscore INTEGER,
        risikonivaa TEXT,
        avslort_sensitiv_innsikt TEXT
    )
    """)

    # Spesifikke familiekoblinger / habilitetskoblinger basert på faktiske etternavn i innleie-tabellen
    HABILITET_ETTERNAVN = {
        "Viken": ("Frilans Kuratortjenester (ENK) v/ Dr. Elena M. Viken", "Nær familierelasjon til ekstern konsulent (45 kontrakter)"),
        "Ruud": ("Nordic Art Transport AS v/ Morten Ruud", "Slektskap/styreverv hos fast kunsttransportør (49 kontrakter)"),
        "Solberg": ("Lys & Rom Scenoteknikk AS v/ Torstein Solberg", "Familierelasjon til leverandør av utstillingslys (48 kontrakter)"),
        "Haugen": ("Securitas AS / Sikkerhet v/ Stian Haugen", "Bånd til kontaktperson for vakthold (49 kontrakter)"),
        "Bratt": ("Bratt Eiendomsdrift ENK", "Godkjenner egne driftskontrakter og har slekt i vakthold"),
    }

    ansatt_rows = []
    utvidet_rows = []
    osint_rows = []
    komplett_csv_rows = []

    with open(ansatte_csv, mode="r", encoding="utf-8") as f:
        for idx, r in enumerate(csv.DictReader(f)):
            aid = r["ansatt_id"]
            navn = r["navn"]
            etternavn = navn.split()[-1]
            kjonn = r.get("kjonn", "K")
            faar = int(r.get("fodselsaar", 1980) or 1980)
            avd = r["avdeling"]
            stilling = r["stilling"]
            status = r.get("status", "Fast")
            stillingspst = float(r.get("stillingsprosent", 1.0) or 1.0)
            ltrinn = int(r.get("lonnstrinn_virke", 45) or 45)
            epost = r.get("epost", "")
            tlf = r.get("telefon", "")
            kontor = r.get("kontor_sal", "")

            ansatt_rows.append((aid, navn, kjonn, faar, avd, stilling, status, stillingspst, ltrinn, epost, tlf, kontor))

            # Fødselsdato & Syntetisk FNR
            mnd = rng.randint(1, 12)
            dag = rng.randint(1, 28)
            fdato = f"{faar}-{mnd:02d}-{dag:02d}"
            fnr = f"{dag:02d}{mnd:02d}{str(faar)[2:]}-99{idx+100:03d}"

            # Geografi i Trondheim (hvis ansatt har fravær under et spesifikt kollektivavvik, koble til den pendlerlinjen!)
            f_info = fravaer_per_ansatt.get(aid, {"episoder": 0, "dager": 0, "egenmeldinger": 0, "datoer": []})
            matched_kollektiv = "Ingen treff mot kollektivstans"
            valgt_omraade = rng.choice(TRONDHEIM_OMRAADER)

            for (ffra, ftil, ftype) in f_info["datoer"]:
                for av in TRONDHEIM_KOLLEKTIV_AVVIK:
                    if ffra <= av["dato_til"] and ftil >= av["dato_fra"]:
                        matched_kollektiv = f"{av['avvik_kode']}: Fravær ({ftype}) sammenfaller med '{av['hendelse']}'"
                        # Velg område som matcher denne pendlerlinjen for å demonstrere geografisk re-identifisering
                        matching_areas = [o for o in TRONDHEIM_OMRAADER if o[3] == av["linje"]]
                        if matching_areas:
                            valgt_omraade = rng.choice(matching_areas)
                        break

            postnr, bydel, gate, pendlerlinje = valgt_omraade
            husnr = rng.randint(2, 140)
            adresse = f"{gate} {husnr}, {postnr} {bydel}"

            sivilstand = rng.choice(SIVILSTAND_VALG)
            alder = 2026 - faar
            barn = rng.choice([0, 1, 2, 3]) if 27 <= alder <= 48 else 0

            # Nærmeste pårørende
            p_fornavn = rng.choice(FORNAVN_PAARORENDE)
            paarorende = f"{p_fornavn} {etternavn} ({'Ektefelle/Samboer' if sivilstand in ('Gift', 'Samboer') else 'Søsken/Forelder'})"

            # GDPR Art 9: Fagforening & Helse
            fagforening = rng.choice(FAGFORENINGER_PER_AVD.get(avd, ["Fagforbundet", "Uorganisert"]))
            if f_info["dager"] > 35:
                helse_tekst, helse_grad = rng.choice([p for p in HELSE_PROFILER if p[1] in ("HØY", "MODERAT")])
            else:
                helse_tekst, helse_grad = rng.choice(HELSE_PROFILER)

            overtid_cnt = ansatt_overtid_count.get(aid, 0)
            st_map = ansatt_stasjon_timer.get(aid, {})
            primar_stasjon = max(st_map, key=st_map.get) if st_map else kontor

            utvidet_rows.append((
                aid, navn, fdato, fnr, adresse, postnr, bydel, pendlerlinje,
                sivilstand, barn, paarorende, fagforening, helse_tekst,
                f_info["episoder"], f_info["dager"], overtid_cnt, primar_stasjon
            ))

            # OSINT: Lønn vs Skatteliste & Brønnøysund
            virke_lonn = beregn_virke_lonn(ltrinn, stillingspst)
            habilitet_flagg = "Ingen registrert konflikt"
            brreg_rolle = "Ingen registrerte næringsroller i Brønnøysund"

            if etternavn in HABILITET_ETTERNAVN:
                selskap, grunn = HABILITET_ETTERNAVN[etternavn]
                brreg_rolle = f"Tilknyttet {selskap}"
                habilitet_flagg = f"OBS HABILITET: {grunn}"

            # Skatteliste-avvik
            if etternavn in HABILITET_ETTERNAVN or idx % 11 == 0:
                # Høy bi-inntekt fra konsulent/utleie
                ekstra = rng.randint(220000, 680000)
                skatt_inntekt = int(virke_lonn * 0.88) + ekstra
                skatt_formue = rng.randint(1500000, 9800000)
                inntekt_forklaring = f"Skatteliste er +{ekstra:,} kr høyere enn museets lønn -> avslører skjult bi-inntekt/næring"
            elif idx % 9 == 0:
                # Tung gjeldsbelastning (nettoinntekt presset ned av gjeldsrenter)
                skatt_inntekt = max(0, int(virke_lonn * 0.35))
                skatt_formue = 0
                inntekt_forklaring = "Skatteliste viser dramatisk lavere nettoinntekt enn bruttolønn -> avslører høy privat gjeldsgrad/rentefradrag"
            else:
                skatt_inntekt = int(virke_lonn * rng.uniform(0.76, 0.86))
                skatt_formue = rng.choice([0, 0, rng.randint(150000, 2400000)])
                inntekt_forklaring = "Normal samsvar mellom Virke-lønnstrinn og skatteliste"

            # Beregn samlet mosaikk-risikoscore (0-100)
            score = 25  # Grunnsårbarhet fordi k=1 på vaktliste
            innsikter = [f"k=1 på '{primar_stasjon}' gir eksakt lokasjonssporing time-for-time"]

            if helse_grad != "LAV" or f_info["dager"] > 25:
                score += 25
                innsikter.append(f"Art. 9 Helse: {helse_tekst} ({f_info['dager']} fraværsdager)")
            if matched_kollektiv != "Ingen treff mot kollektivstans":
                score += 20
                innsikter.append(f"Geolokasjon avslørt via AtB/Trønderbanen: Bor i {bydel} ({postnr})")
            if habilitet_flagg != "Ingen registrert konflikt":
                score += 20
                innsikter.append(habilitet_flagg)
            if "avslører" in inntekt_forklaring:
                score += 15
                innsikter.append(inntekt_forklaring)
            if overtid_cnt >= 10:
                score += 10
                innsikter.append(f"AML-risiko: {overtid_cnt} vakter med 10-11 timers varighet")

            score = min(100, score)
            if score >= 75:
                rnivaa = "KRITISK"
            elif score >= 55:
                rnivaa = "HØY"
            elif score >= 40:
                rnivaa = "MODERAT"
            else:
                rnivaa = "LAV"

            samlet_innsikt = " | ".join(innsikter)

            osint_rows.append((
                aid, virke_lonn, skatt_inntekt, skatt_formue, inntekt_forklaring,
                brreg_rolle, habilitet_flagg, matched_kollektiv, score, rnivaa, samlet_innsikt
            ))

            komplett_csv_rows.append({
                "ansatt_id": aid,
                "navn": navn,
                "kjonn": kjonn,
                "fodselsdato": fdato,
                "syntetisk_fnr": fnr,
                "avdeling": avd,
                "stilling": stilling,
                "status": status,
                "stillingsprosent": stillingspst,
                "lonnstrinn_virke": ltrinn,
                "virke_aarslonn_nok": virke_lonn,
                "skatteliste_nettoinntekt": skatt_inntekt,
                "skatteliste_nettoformue": skatt_formue,
                "inntektsavvik_analyse": inntekt_forklaring,
                "adresse_trondheim": adresse,
                "postnummer": postnr,
                "bydel_kommune": bydel,
                "pendlerlinje_atb": pendlerlinje,
                "kollektiv_avvik_kobling": matched_kollektiv,
                "sivilstand": sivilstand,
                "antall_barn_under_12": barn,
                "naermeste_paarorende": paarorende,
                "fagforening_art9": fagforening,
                "helse_ergonomi_art9": helse_tekst,
                "sykefravaer_episoder": f_info["episoder"],
                "sykefravaer_dager": f_info["dager"],
                "overtid_aml_brudd": overtid_cnt,
                "primar_stasjon": primar_stasjon,
                "brreg_roller_verv": brreg_rolle,
                "habilitet_flagg": habilitet_flagg,
                "mosaikk_risikoscore": score,
                "risikonivaa": rnivaa,
                "avslort_sensitiv_innsikt": samlet_innsikt,
            })

    cur.executemany("INSERT INTO hr_ansatte VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ansatt_rows)
    cur.executemany("INSERT INTO hr_utvidet_profil_trondheim VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", utvidet_rows)
    cur.executemany("INSERT INTO ekstern_osint_trondheim VALUES (?,?,?,?,?,?,?,?,?,?,?)", osint_rows)

    # Kopier avvik fra museum.db (read-only)
    cur.execute("""
    CREATE TABLE avvik_hms (
        avvik_id TEXT,
        dato TEXT,
        kategori TEXT,
        alvorlighetsgrad TEXT,
        berort_sal_id TEXT,
        beskrivelse TEXT
    )
    """)
    src_db = os.path.join(data_dir, "museum.db")
    if os.path.exists(src_db):
        ro_conn = sqlite3.connect(f"file:{src_db}?mode=ro", uri=True)
        avvik_rows = ro_conn.cursor().execute(
            "SELECT avvik_id, dato, kategori, alvorlighetsgrad, berort_sal_id, beskrivelse FROM avvik_hms_drift"
        ).fetchall()
        cur.executemany("INSERT INTO avvik_hms VALUES (?,?,?,?,?,?)", avvik_rows)
        ro_conn.close()

    conn.commit()
    conn.close()
    print(f"[6/7] Eksportert komplett SQLite-database: {db_out} ({os.path.getsize(db_out) / (1024*1024):.1f} MB)")

    print("[7/7] Skriver komplett CSV for alle 168 ansatte i Trondheim og vakt-uttrekk...")
    with open(komplett_ansatte_csv_out, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(komplett_csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(komplett_csv_rows)

    with open(sample_csv_out, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vakt_id", "ansatt_id", "dato", "aar", "maaned", "time_slot", "klokketime", "stasjon", "avdeling", "rolle", "utstilling_id", "faktiske_timer_vakt"])
        writer.writerows(sample_rows)

    print(f"       Skrevet 168 ansatte til: {komplett_ansatte_csv_out}")


if __name__ == "__main__":
    generate_hourly_records()
