"""Colab-til-MCP Toveis Bro for Kunstpixel.

Kobler sammen Google Colab (Google Drive sky-arbeidsflate) og Kunstpixels FastMCP-server.
Støtter:
- Utgående bestillinger fra MCP til Colab (forankret i 01_inbox/BESTILLING_COLAB_DATAFANGST.md)
- Inngående mottak, sjekksumkontroll og fletting fra Colab tilbake til MCP og museum.db
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INBOX_DIR = PROJECT_ROOT / "01_inbox" / "incoming"
DATA_DIR = PROJECT_ROOT / "05_data"


def list_colab_deliveries() -> list[dict[str, Any]]:
    """Lister alle innkommende leveranser fra Google Colab og deres status."""
    if not INBOX_DIR.exists():
        return []

    leveranser = []
    for item in sorted(INBOX_DIR.iterdir()):
        if item.is_dir():
            sha_file = item / "SJEKKSUM.sha256"
            metadata_file = item / "METADATA.json"
            has_sha = sha_file.exists()
            has_meta = metadata_file.exists()

            data_files = [f.name for f in item.iterdir() if f.suffix in (".csv", ".yaml", ".json", ".ipynb")]

            leveranser.append({
                "leveranse_navn": item.name,
                "sti": str(item),
                "har_sjekksum": has_sha,
                "har_metadata": has_meta,
                "antall_filer": len(data_files),
                "filer": data_files,
                "klar_for_import": has_sha,
            })
    return leveranser


def verify_colab_delivery(delivery_name: str) -> dict[str, Any]:
    """Verifiserer sjekksummen for en innkommende Colab-leveranse uten å mutere data."""
    delivery_dir = INBOX_DIR / delivery_name
    if not delivery_dir.exists():
        return {"feil": f"Leveranse '{delivery_name}' finnes ikke i {INBOX_DIR}"}

    sha_file = delivery_dir / "SJEKKSUM.sha256"
    if not sha_file.exists():
        return {"feil": f"Mangler SJEKKSUM.sha256 i {delivery_name}"}

    avvik = []
    verifiserte = []

    with open(sha_file, "r", encoding="utf-8") as f:
        for linje in f:
            deler = linje.strip().split()
            if len(deler) >= 2:
                forventet_sha, filnavn = deler[0], deler[1]
                filsti = delivery_dir / filnavn
                if not filsti.exists():
                    avvik.append(f"Fil mangler: {filnavn}")
                    continue

                med = hashlib.sha256(filsti.read_bytes()).hexdigest()
                if med == forventet_sha:
                    verifiserte.append(filnavn)
                else:
                    avvik.append(f"Sha256 matcher ikke for {filnavn}")

    return {
        "delivery_name": delivery_name,
        "godkjent": len(avvik) == 0,
        "verifiserte_filer": verifiserte,
        "avvik": avvik,
    }


def create_colab_order(order_name: str, description: str, tables_required: list[str]) -> dict[str, Any]:
    """Oppretter en utgående datafangst-bestilling til Google Colab i 01_inbox/incoming."""
    target_dir = INBOX_DIR / order_name
    target_dir.mkdir(parents=True, exist_ok=True)

    order_doc = f"""# BESTILLING TIL GOOGLE COLAB: {order_name}

## 1. Oppdrag
{description}

## 2. Nødvendige tabeller og format
{chr(10).join(f"- `{t}` (CSV eller YAML, UTF-8)" for t in tables_required)}

## 3. Retningslinjer for Colab
- Kun syntetiske data merket `syntetisk (colab_{order_name})`.
- Ingen ekte personnavn, telefonnumre eller ekte adresser.
- Kjør validering og sjekksumcelle før levering til Google Drive: `/content/drive/MyDrive/Kunstpixel/01_inbox/incoming/{order_name}/`.
"""
    doc_path = target_dir / "BESTILLING.md"
    doc_path.write_text(order_doc, encoding="utf-8")

    return {
        "status": "OPPRETTET",
        "order_name": order_name,
        "bestillingsfil": str(doc_path),
        "synkroniseres_til_colab": f"/content/drive/MyDrive/Kunstpixel/01_inbox/incoming/{order_name}/",
    }


def ingest_colab_personalmapper(delivery_name: str = "order_personalmapper_163") -> dict[str, Any]:
    """Verifiserer sjekksum og fletter innkommende personalmapper til 05_data/arkiv_hr_personalmapper.csv."""
    verification = verify_colab_delivery(delivery_name)
    if not verification.get("godkjent"):
        return {"feil": "Leveransen besto ikke sjekksumkontroll", "detaljer": verification}

    inbox_csv = INBOX_DIR / delivery_name / "hr_personalmapper.csv"
    target_csv = DATA_DIR / "arkiv_hr_personalmapper.csv"

    if not inbox_csv.exists():
        return {"feil": f"Fant ikke {inbox_csv}"}

    import csv

    eksisterende: list[dict[str, str]] = []
    kjente_saksnr: set[str] = set()
    kjente_ansatte: set[str] = set()

    if target_csv.exists():
        with open(target_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for row in reader:
                eksisterende.append(row)
                kjente_saksnr.add(row["saksnr"])
                kjente_ansatte.add(row["ansatt_id"])
    else:
        fieldnames = [
            "saksnr", "ansatt_id", "navn", "opprettet_dato", "kategori",
            "tittel", "innhold_fortrolig", "gradering", "saksbehandler_rolle", "datakilde"
        ]

    originale_5 = {"KP-ANS-006", "KP-ANS-073", "KP-ANS-017", "KP-ANS-153", "KP-ANS-005"}
    eksisterende = [r for r in eksisterende if r["ansatt_id"] in originale_5]
    kjente_ansatte = set(originale_5)

    nye_lagt_til = 0
    with open(inbox_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ansatt_id"] not in kjente_ansatte:
                eksisterende.append(row)
                kjente_ansatte.add(row["ansatt_id"])
                nye_lagt_til += 1

    with open(target_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(eksisterende)

    return {
        "status": "FLETTET",
        "delivery_name": delivery_name,
        "før_antall": len(eksisterende) - nye_lagt_til,
        "etter_antall": len(eksisterende),
        "nye_lagt_til": nye_lagt_til,
        "fil": str(target_csv),
    }
