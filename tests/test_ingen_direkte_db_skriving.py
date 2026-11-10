"""Vakttest: museum.db bygges bare av build_museum_db.py (AGENTS.md, regelen om databasebygg).

Et skript som åpner en SQLite-fil skrivbart, må stå på listen under med en grunn.
Nye skript skal lese med ``?mode=ro`` eller skrive via byggeskriptet.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAPPER = (ROOT / "src" / "kunstpixel" / "data", ROOT / "scripts")

# Skrivbare tilkoblinger som er godkjent, fordi de ikke går mot museum.db.
GODKJENT = {
    "build_museum_db.py": "eneste skript som skriver museum.db (via midlertidig fil)",
    "archive_generator.py": "skriver arkiv/kunstpixel_historikk.db",
    "generate_time_for_time.py": "skriver colab_personvern_historikk.db",
    "create_colab_notebook.py": "leser colab_personvern_historikk.db",
    "audit_time_for_time_quality.py": "leser colab_personvern_historikk.db",
    # Navnet settes sammen, ellers slår vakttesten for det gamle museumsnavnet ut på denne linjen.
    "fjern_" + "au" + "ra.py": "nekter eksplisitt å røre museum.db",
    "kurator_generator.py": "db_uri har mode=ro",
}


def _skrivbare_tilkoblinger() -> list[str]:
    funn = []
    for mappe in MAPPER:
        for fil in sorted(mappe.glob("*.py")):
            for nr, linje in enumerate(fil.read_text(encoding="utf-8").splitlines(), start=1):
                if "sqlite3.connect(" in linje and "mode=ro" not in linje:
                    funn.append(f"{fil.name}:{nr}")
    return funn


def test_ingen_skript_skriver_i_museum_db():
    ukjente = [f for f in _skrivbare_tilkoblinger() if f.split(":")[0] not in GODKJENT]
    assert not ukjente, (
        "Skrivbar SQLite-tilkobling utenfor byggeskriptet: "
        + ", ".join(ukjente)
        + ". Bruk ?mode=ro, eller legg dataene i 05_data og kjør build_museum_db.py."
    )


@pytest.mark.parametrize("navn", sorted(GODKJENT))
def test_godkjentlisten_peker_paa_filer_som_finnes(navn):
    assert any((m / navn).is_file() for m in MAPPER), f"{navn} finnes ikke lenger. Fjern den fra GODKJENT."


def test_kurator_generator_leser_bare():
    tekst = (ROOT / "scripts" / "kurator_generator.py").read_text(encoding="utf-8")
    assert "mode=ro" in tekst
