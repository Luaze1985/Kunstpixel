"""Konfigurasjon for syntetiske kundedata i Kunstpixel.

Alle justerbare verdier (volum, priser, medlemstyper, fordeler) ligger i
`05_data/persondata/innstillinger.yaml`. Denne modulen leser fila og gir
faste stier og små hjelpefunksjoner.
"""

from __future__ import annotations

import random
import re
import unicodedata
from datetime import date
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PERSONDATA_DIR = PROJECT_ROOT / "05_data" / "persondata"
INNSTILLINGER_STI = PERSONDATA_DIR / "innstillinger.yaml"
STANDARD_DB_STI = PERSONDATA_DIR / "persondata.db"
CSV_DIR = PERSONDATA_DIR / "csv"
MUSEUM_DB_STI = PROJECT_ROOT / "05_data" / "museum.db"
SCHEMA_STI = Path(__file__).resolve().parent / "schema.sql"

DATAKILDE = "syntetisk (persondata_generator)"
EPOST_DOMENE = "eksempel.invalid"
SKALAER: dict[str, float] = {"test": 0.02, "full": 1.0}


def last_innstillinger(sti: Path = INNSTILLINGER_STI) -> dict:
    """Les innstillingsfila."""
    with open(sti, encoding="utf-8") as f:
        return yaml.safe_load(f)


INNSTILLINGER = last_innstillinger()
KUNDER_START = date.fromisoformat(INNSTILLINGER["periode"]["fra"])
REFERANSEDATO = date.fromisoformat(INNSTILLINGER["periode"]["til"])
STANDARD_SEED: int = INNSTILLINGER["seed"]
VOLUM: dict = INNSTILLINGER["volum"]
ANDELER: dict = INNSTILLINGER["andeler"]
MEDLEMSKAPSTYPER: dict = INNSTILLINGER["medlemskapstyper"]
FORDELER: dict = INNSTILLINGER["fordeler"]
GAVEKORT: dict = INNSTILLINGER["gavekort"]

_ERSTATT = {"æ": "ae", "ø": "o", "å": "aa"}


def _ascii(tekst: str) -> str:
    tekst = tekst.lower()
    for k, v in _ERSTATT.items():
        tekst = tekst.replace(k, v)
    tekst = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", ".", tekst).strip(".")


def lag_epost(fornavn: str, etternavn: str, lopenr: int) -> str:
    """Fiktiv e-post på det reserverte domenet `.invalid`."""
    return f"{_ascii(fornavn)}.{_ascii(etternavn)}.{lopenr}@{EPOST_DOMENE}"


def lag_telefon(rng: random.Random) -> str:
    """8 siffer som starter med 0. Norske abonnentnumre starter aldri med 0."""
    return "0" + "".join(str(rng.randint(0, 9)) for _ in range(7))
