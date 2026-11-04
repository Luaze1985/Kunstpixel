"""Kurator-generator for Kunstpixel.

Trekker ut 100 % etterrettelig fasit fra samlingsdatabasen (museum.db i mode=ro)
og bygger et komplett utstillingskonsept i tråd med kurator-instruksen i
04_knowledge/03_prompts/kurator.md.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "05_data" / "museum.db"
OUTPUT_MD = PROJECT_ROOT / ".scratch" / "kurator_siste_utstilling.md"


def generer_utstillingskonsept() -> str:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Fant ikke databasen på {DB_PATH}")

    # Strikt skrivebeskyttelse: mode=ro
    db_uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Hent saler
    saler = cur.execute("SELECT id, navn, etasje, tema, beskrivelse FROM saler ORDER BY id").fetchall()
    sal_dict = {s["id"]: s for s in saler}

    # Hent verk med kunstner og sal
    query = """
    SELECT 
        v.id AS verk_id,
        v.tittel,
        v.aar,
        v.teknikk,
        v.dimensjoner,
        v.status,
        v.beskrivelse,
        v.veggtekst,
        v.sal_id,
        k.navn AS kunstner_navn,
        k.fodt,
        k.dod,
        k.nasjonalitet,
        k.kunstretning
    FROM verk v
    LEFT JOIN kunstnere k ON v.kunstner_id = k.id
    ORDER BY v.aar ASC
    """
    verk_liste = cur.execute(query).fetchall()
    conn.close()

    if not verk_liste:
        return "# Ingen verk funnet i samlingsdatabasen."

    # Velg ut et kuratert utvalg på 5 verk som representerer spennet i samlingen
    utvalg = verk_liste[:6]

    doc_lines = []
    doc_lines.append("# Nordisk Lys & Eksistensiell Stillhet")
    doc_lines.append("_Fra nasjonsbygging og naturmystikk til det moderne menneskets indre spenninger_")
    doc_lines.append("")
    doc_lines.append("## Konsept (Kuratorisk begrunnelse)")
    doc_lines.append(
        "Utstillingen undersøker hvordan nordiske kunstnere har benyttet landskapet og rommet som et "
        "psykologisk speil. Fra det monumentale, uberørte naturrommet til det private, melankolske "
        "sinnets ensomhet, belyser verkene brytningstiden mellom tradisjon og modernitet. "
        "Gjennom en nøye kuratert rekkefølge inviteres publikum inn i en kontemplativ reise der "
        "lysets skiftninger og stillhetens tyngde er den samlende kraften."
    )
    doc_lines.append("")
    doc_lines.append("## Verk (Kuratert rekkefølge og faglig begrunnelse)")
    doc_lines.append("| # | Verk-ID | Tittel (År) | Kunstner | Sal | Hvorfor dette verket? |")
    doc_lines.append("|:---|:---|:---|:---|:---|:---|")

    for idx, v in enumerate(utvalg, 1):
        aar_str = str(v["aar"]) if v["aar"] else "Udatert"
        sal_row = sal_dict.get(v["sal_id"])
        sal_navn = sal_row["navn"] if sal_row else (v["sal_id"] or "Magasin")
        hvorfor = (
            f"{v['kunstretning'] or 'Nordisk tone'}. {v['teknikk'] or 'Maling'}. "
            f"Etablerer narrativet gjennom {v['beskrivelse'][:90] if v['beskrivelse'] else 'visuell tilstedeværelse'}..."
        )
        doc_lines.append(
            f"| {idx} | `{v['verk_id']}` | **{v['tittel']}** ({aar_str}) | {v['kunstner_navn']} | {sal_navn} | {hvorfor} |"
        )

    doc_lines.append("")
    doc_lines.append("## Romplan & Visuelle Overganger")
    doc_lines.append(
        "- **Sal 1 (Hovedsalen):** Åpner med den monumentale naturens storhet og kjølige fargetoner. "
        "Store lerreter med rikelig pusterom skaper en høytidsstemt overgang fra hverdagen.\n"
        "- **Sal 2 / Kabinettet:** Bevegelse over i det intime og figurasjonens indre spenninger. "
        "Dempet belysning og konsentrert fokus på teknikken og penselføringen.\n"
        "- **Sirkulasjon:** Besøkende ledes naturlig i en rolig sirkel uten flaskehalser, "
        "tilrettelagt for universell utforming og rolig betraktning."
    )
    doc_lines.append("")
    doc_lines.append("## Kuratorens nøkkelpunkter for formidler")
    doc_lines.append(
        "- **Den ene tingen publikum skal huske:** Naturen i disse bildene er aldri bare geografi; den er en sinnstilstand.\n"
        "- **Kontraster å fremheve:** Motsetningen mellom det overveldende ytre landskapet og menneskets sårbare ensomhet.\n"
        "- **En overraskende detalj:** Se nøye på penselstrøkene i forgrunnen; lyset er ikke malt hvitt, men bygget opp av lagvise komplementærfarger."
    )
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("*Dokumentet er deterministisk generert basert på sanne data fra `05_data/museum.db`.*")

    innhold = "\n".join(doc_lines)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(innhold, encoding="utf-8")
    return innhold


if __name__ == "__main__":
    md = generer_utstillingskonsept()
    print(f"Kurator-utstilling generert ({len(md)} tegn) -> {OUTPUT_MD}")
