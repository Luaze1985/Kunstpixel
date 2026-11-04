"""Berikelsesskript for Kunstpixel: 0 tokens, 100 % autoritativt fra SNL API.

Henter dype biografier for alle 12 kunstnere i Kunstpixel direkte fra Store norske leksikon
og oppdaterer tabellen 'kunstnere' i 05_data/museum.db og 00_felles/ordliste.yaml.
"""
from __future__ import annotations

import json
import re
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path

# Mapping mellom kunstner i Kunstpixel og offisiell SNL-artikkel
ARTIST_SNL_MAP = {
    "Theodor Kittelsen": "Theodor_Kittelsen",
    "Christian Krohg": "Christian_Krohg",
    "Harriet Backer": "Harriet_Backer",
    "Harald Sohlberg": "Harald_Sohlberg",
    "Nikolai Astrup": "Nikolai_Astrup_-_målar",
    "Edvard Munch": "Edvard_Munch",
    "Adolph Tidemand": "Adolph_Tidemand",
    "Hans Gude": "Hans_Gude",
    "Kitty Kielland": "Kitty_Kielland",
    "Erik Werenskiold": "Erik_Werenskiold",
    "Frits Thaulow": "Frits_Thaulow",
    "Anna-Eva Bergman": "Anna-Eva_Bergman",
}

def clean_html(raw_html: str) -> str:
    """Fjerner HTML-tags og rydder opp i overflødige mellomrom."""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def fetch_snl_biography(slug: str) -> tuple[str, str]:
    """Henter fullstendig ingress og utdypende biografi fra SNL."""
    url = f"https://snl.no/{urllib.parse.quote(slug)}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Kunstpixel-Research/1.0"})
    
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        body = data.get("xhtml_body", "")
        clean_text = clean_html(body)
        
        # Ekstraher de første 2-3 avsnittene som en kompakt ingress (ca. 400-600 tegn)
        sentences = clean_text.split(". ")
        ingress = ". ".join(sentences[:3]) + "." if len(sentences) >= 3 else clean_text[:400]
        
        return ingress, clean_text

def enrich_database(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Sørg for at kolonnen 'full_biografi' finnes
    cur.execute("PRAGMA table_info(kunstnere)")
    cols = [c[1] for c in cur.fetchall()]
    if "full_biografi" not in cols:
        cur.execute("ALTER TABLE kunstnere ADD COLUMN full_biografi TEXT;")
        cur.execute("ALTER TABLE kunstnere ADD COLUMN kilde_url TEXT;")
        print("La til kolonnene 'full_biografi' og 'kilde_url' i kunstnere.")
        
    stats = {}
    for name, slug in ARTIST_SNL_MAP.items():
        try:
            ingress, full_bio = fetch_snl_biography(slug)
            url = f"https://snl.no/{slug}"
            
            # Oppdater både biografi (kompakt) og full_biografi (dyp)
            cur.execute("""
                UPDATE kunstnere 
                SET biografi = :bio, full_biografi = :full, kilde_url = :url
                WHERE navn = :name
            """, {"bio": ingress, "full": full_bio, "url": url, "name": name})
            
            stats[name] = len(full_bio)
            print(f"✓ Beriket {name}: {len(full_bio):,d} tegn (Ingress: {len(ingress)} tegn)")
        except Exception as e:
            print(f"✗ Feil ved henting for {name}: {e}")
            
    conn.commit()
    conn.close()
    return stats

if __name__ == "__main__":
    db_file = Path("05_data/museum.db")
    print(f"Starter 0-token berikelse mot {db_file}...")
    results = enrich_database(db_file)
    print("\nFerdig! Totalt beriket:", len(results), "kunstnere.")
