"""Colab-synkronisering for Pixel-Bygger.

Sjekker 01_inbox for innkommende Colab-leveranser og bekrefter eventuelle utestående bestillinger.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.colab_bridge import (
    list_colab_deliveries,
    verify_colab_delivery,
    create_colab_order,
)


def sync_colab():
    print("=== PIXEL-BYGGER: SJEKKER COLAB-BRO VIA MCP ===")

    # 1. Sjekk eksisterende leveranser
    deliveries = list_colab_deliveries()
    print(f"Fant {len(deliveries)} leveranse(r) i 01_inbox/incoming:")
    for d in deliveries:
        navn = d["leveranse_navn"]
        status = "KLAR" if d["klar_for_import"] else "UFULLSTENDIG"
        print(f"  - [{status}] {navn} ({d['antall_filer']} filer)")

    # 2. Sjekk datagap for 163 manglende personalmapper
    order_name = "order_personalmapper_163"
    order_dir = PROJECT_ROOT / "01_inbox" / "incoming" / order_name
    if not order_dir.exists():
        print(f"Oppretter databestilling til Colab: {order_name}...")
        res = create_colab_order(
            order_name=order_name,
            description=(
                "Generer 163 dype, syntetiske personalmapper for ansatte i hr_ansatte "
                "som mangler oppføring i hr_personalmapper. Sikre Modulo 11-validering og syntetisk merking."
            ),
            tables_required=["hr_personalmapper", "hr_ansatte_oppfolging"],
        )
        print(f"Bestilling opprettet: {res.get('status')}")
    else:
        print(f"Bestilling allerede registrert og venter på Colab-kjøring: {order_name}")

    print("Colab-bro synkronisert.")


if __name__ == "__main__":
    sync_colab()
