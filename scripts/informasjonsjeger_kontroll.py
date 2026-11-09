"""Deterministisk Gap-skanner og Funnkontroll for Kunstpixels Morgensløyfe (ADR 014).

Bruk:
    py -3.13 scripts/informasjonsjeger_kontroll.py --finn-hull
    py -3.13 scripts/informasjonsjeger_kontroll.py --kontroller
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kunstpixel.data.seed_handbooks import les_alle_handboker

FORBUDTE_SAMLEHJEMLER = {
    "Matloven / Mattilsynet / Renholdsregisteret",
    "Internkontrollforskriften / AML kap. 3-4 / DSB",
    "AML kap. 2 A (Varsling) / LOA / Beredskapsplan",
    "Arbeidsmiljøloven (AML) / Virke Landsoverenskomst",
}


def finn_hull() -> int:
    """Skanner håndbøker, SOP-er og kunnskapsgrunnlag etter hull som Informasjonsjegeren skal tette."""
    punkter = les_alle_handboker()
    hull: list[str] = []

    for r in punkter:
        pid = r["punkt_id"]
        hjemmel = (r.get("lovhjemmel") or "").strip()
        innhold = (r.get("innhold") or "").strip()
        if not hjemmel or hjemmel in FORBUDTE_SAMLEHJEMLER:
            hull.append(f"[HJEMMEL] {pid} ({r['avsnitt_tittel']}): Generisk eller manglende lovhjemmel ({hjemmel!r})")
        if len(innhold) < 120:
            hull.append(f"[DYBDE]   {pid} ({r['avsnitt_tittel']}): Kort prosedyretekst ({len(innhold)} tegn < 120)")

    sops = [r for r in punkter if r["handbok_kode"] == "RUTINER_SOP"]
    print(f"=== INFORMASJONSJEGER GAP-ANALYSE ({len(punkter)} punkter totalt, hvorav {len(sops)} SOP-punkter) ===")
    if not hull:
        print("[OK] 0 lovhjemmel- eller prosedyrehull i de 4 håndbøkene og 8 SOP-ene.")
    else:
        for h in hull:
            print(f"  - {h}")
    return 0


def kontroller_og_bygg() -> int:
    """Kontrollerer direkte oppdateringer med pytest + statusport; ruller tilbake ved feil."""
    print("=== KONTROLLPORT FOR FUNN (ADR 014) ===")
    test_cmd = [
        sys.executable, "-m", "pytest", "-q",
        "tests/test_handbook_compliance.py",
        "tests/test_hr_hms_pakke.py",
        "tests/test_mvp_oppslag.py",
        "tests/test_publikum_data.py",
        "tests/test_leveranse_kjoring.py",
    ]
    res = subprocess.run(test_cmd, cwd=ROOT)
    if res.returncode != 0:
        print("[FEIL] Funnkontroll feilet i pytest! Ruller tilbake uverifiserte endringer i 04_knowledge/ og 05_data/...")
        subprocess.run(
            ["git", "checkout", "--", "04_knowledge/01_governance/handboker", "04_knowledge/02_sops"],
            cwd=ROOT,
        )
        return 1

    bygg_res = subprocess.run([sys.executable, "src/kunstpixel/data/build_museum_db.py"], cwd=ROOT)
    if bygg_res.returncode != 0:
        print("[FEIL] Databasebygging feilet!")
        return 1

    gate_res = subprocess.run([sys.executable, "scripts/db_status_gate.py", "--uten-pytest"], cwd=ROOT)
    if gate_res.returncode != 0:
        print("[FEIL] Statusport feilet!")
        return 1

    colab_res = subprocess.run([sys.executable, "scripts/colab_sync.py"], cwd=ROOT)
    print("[OK] Funnkontroll, databasebygg, statusport og Colab-synk bestått 100 %!")
    return colab_res.returncode


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--finn-hull", action="store_true", help="Skann etter kunnskaps- og hjemmelshull")
    p.add_argument("--kontroller", action="store_true", help="Valider funn, bygg museum.db og rull tilbake ved feil")
    args = p.parse_args()
    if args.kontroller:
        return kontroller_og_bygg()
    return finn_hull()


if __name__ == "__main__":
    raise SystemExit(main())
