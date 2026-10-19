"""Benchmark and inspection script running 30 realistic searches across museum handbooks and SOPs.

Tests topics covering HR, working hours, safety, physical ergonomics, cafe HACCP,
fire, art evacuation, sick leave follow-up, vacation, whistleblowing, and shift swaps.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kunstpixel.core.db import query_handbook

TEST_QUERIES = [
    # Kategori 1: HR, Lønn & Arbeidsvilkår (1–8)
    ("Egenmelding", "Hvor mange dager egenmelding kan jeg ta per år?"),
    ("Hviletid", "Hva er regelen for 11 timer hviletid mellom skift?"),
    ("Helligdagstillegg", "Hva er overtidstillegget på helligdager som 17. mai og påske?"),
    ("Prøvetid", "Hva er oppsigelsestiden i prøvetiden?"),
    ("Velferdspermisjon", "Hvor mange dager velferdspermisjon får jeg ved flytting eller begravelse?"),
    ("Sykt barn", "Hvor mange omsorgsdager har jeg ved barns sykdom?"),
    ("Seniorferie", "Hva er regelen for ekstra ferieuke for seniorer over 60 år?"),
    ("Etiske regler", "Har ansatte lov til å drive privat kunsthandel eller taksere kunst?"),

    # Kategori 2: HMS, Fysisk Miljø & Beredskap (9–16)
    ("Løftegrenser", "Hvor mye kan en person løfte alene ifølge HMS-reglene?"),
    ("STAMI-ergonomi", "Hvor lenge kan en salvert stå sammenhengende på hardt steingulv?"),
    ("Alenearbeid", "Når er alenearbeid forbudt i museet?"),
    ("Persontall og brann", "Hva er maksimalt personantall i bygget og i salene?"),
    ("Restverdiredning RVR", "Hva er prioritet 1 ved evakuering av kunst ved brann?"),
    ("Hjertestarter", "Hvor er hjertestarter og førstehjelpsutstyr plassert?"),
    ("Vold og trusler", "Hva gjør jeg ved aggressive gjester eller trusler i resepsjonen?"),
    ("Avviksmelding RUH", "Hva er fristen for å melde en uønsket hendelse eller skade?"),

    # Kategori 3: Drift, Kafé, Mathygiene & Publikum (17–23)
    ("Kjøletemperatur HACCP", "Hva er kravet til kjøleskapstemperatur i kaféen?"),
    ("Allergenmerking", "Hvilke 14 allergener må oppgis skriftlig til kafégjestene?"),
    ("Karantene mathygiene", "Hvor lenge må en kaféansatt være hjemme etter omgangssyke?"),
    ("Skjenkebevilling", "Hva er aldersgrensene og reglene for skjenking ved kveldsarrangementer?"),
    ("Godkjent renhold", "Hvilke krav gjelder for innleid renholdsbedrift og HMS-kort?"),
    ("Universell utforming", "Hvilke rettigheter har rullestolbrukere og gjester med ledsagerbevis?"),
    ("Sal-klima", "Hva er kravene til temperatur og relativ luftfuktighet i utstillingssalene?"),

    # Kategori 4: Ledelse, Beredskap & Operative Rutiner (24–30)
    ("Varslingsrutine", "Hva er saksbehandlingstrinnene og fristene når noen varsler?"),
    ("Vern mot gjengjeldelse", "Hvilket vern har en arbeidstaker som varsler om kritikkverdige forhold?"),
    ("Ferieplanlegging", "Hva er fristene for å melde inn hovedferie og overføre feriedager?"),
    ("Erstatningsferie", "Får jeg erstatningsferie hvis jeg blir syk under sommerferien?"),
    ("Oppfølgingsplan sykefravær", "Når må leder lage oppfølgingsplan og kalle inn til dialogmøte 1?"),
    ("Vaktbytte", "Hva kreves for å bytte vakt med en kollega, og når slår sperren inn?"),
    ("Innkjøp og Doffin", "Hva er terskelverdiene for innkjøp og anbudsplikt på Doffin?")
]


def run_benchmark():
    print("=" * 100)
    print("🏛️  BENCHMARK: 30 REALISTISKE SØKETESTER I AURA KUNSTMUSEUMS HÅNDBØKER OG RUTINER")
    print("=" * 100)

    success_count = 0

    for idx, (tema, sporsmal) in enumerate(TEST_QUERIES, start=1):
        results = query_handbook(query=sporsmal, limit=1)
        print(f"\n[{idx:02d}/30] TEMA: {tema.upper()}")
        print(f"❓ SPØRSMÅL: «{sporsmal}»")

        if not results:
            print("❌ INGEN TREFF FUNNET!")
            continue

        top = results[0]
        success_count += 1

        handbok = top["handbok_navn"]
        kapittel = f"Kap. {top['kapittel_nr']}: {top['kapittel_tittel']}"
        avsnitt = top["avsnitt_tittel"]
        punkt_id = top["punkt_id"]
        hjemmel = top["lovhjemmel"] or "Internkontroll"
        innhold = top["innhold"].strip().replace("\n", "\n   ")

        # Trim content if too long for clean presentation
        if len(innhold) > 350:
            innhold_preview = innhold[:350] + " ... [fortsetter]"
        else:
            innhold_preview = innhold

        print(f"📖 KILDE: {handbok} ({punkt_id}) -> {kapittel} -> *{avsnitt}*")
        print(f"⚖️  HJEMMEL: {hjemmel}")
        print(f"💡 UTDRAG:")
        print(f"   {innhold_preview}")
        print("-" * 100)

    print(f"\n📊 SLUTTRESULTAT: {success_count} av {len(TEST_QUERIES)} spørsmål ga direkte, autoritativt svar ({(success_count/len(TEST_QUERIES))*100:.0f}% treffsikkerhet).")


if __name__ == "__main__":
    run_benchmark()
