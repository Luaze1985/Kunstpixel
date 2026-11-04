"""Kommandolinje for bestilling og kontroll av syntetisk fyll (H5).

    py -3.13 tests/kontroller_leveranse.py --lag-bestilling              # skriver bestillinger i 01_inbox/h5_bestilling
    py -3.13 tests/kontroller_leveranse.py 01_inbox/h5_leveranse         # kontrollerer en leveranse, skriver retteliste
    py -3.13 tests/kontroller_leveranse.py 01_inbox/h5_leveranse --retteliste ut.md
    py -3.13 tests/kontroller_leveranse.py 01_inbox/h5_leveranse --installer A,C --yes   # menneskets handling

Avslutter med 0 når alt består, 1 når kontrollen finner feil, 2 ved feil bruk.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.kunstpixel.core.intern import leveranse as L  # noqa: E402
from src.kunstpixel.core.intern.leveranse_bestilling import bestilling_for, skriv_bestillinger, skriv_colab_pakke  # noqa: E402
from src.kunstpixel.core.intern.leveranse_kjoring import importer_svar  # noqa: E402

STANDARD_LEVERANSE = ROOT / "01_inbox" / "h5_leveranse"
STANDARD_BESTILLING = ROOT / "01_inbox" / "h5_bestilling"
STANDARD_COLAB = ROOT / "01_inbox" / "h5_colab"
STANDARD_MAL = ROOT / "05_data" / "governance"


def kopier_til_utklippstavle(fil: Path) -> bool:
    """Kopierer innholdet i en UTF-8-fil til utklippstavlen (Windows). Returnerer om det lyktes."""
    import subprocess

    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Get-Content -Raw -Encoding UTF8 -LiteralPath '{fil}' | Set-Clipboard"],
            capture_output=True,
            timeout=30,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("leveranse", nargs="?", help="mappe med de fem filene")
    ap.add_argument("--lag-historikk-tall", action="store_true", help="skriver historikk_tall.yaml (2010 til 2026) til --til. Laget av koden")
    ap.add_argument("--kopier", help="kopier bestillingen for A, B, C, D, E eller ALLE til utklippstavlen")
    ap.add_argument("--importer", help="tekstfil med modellens svar (kan ha tekst rundt YAML-blokken)")
    ap.add_argument("--fil", help="filkode A-E hvis svaret ikke har kodeblokker")
    ap.add_argument("--til", default=str(STANDARD_LEVERANSE), help="mappe leveransen skrives til")
    ap.add_argument("--lag-bestilling", action="store_true")
    ap.add_argument("--lag-colab-pakke", action="store_true", help="kopierer kontrollen og løkken til 01_inbox/h5_colab for opplasting i Colab")
    ap.add_argument("--ut", default=str(STANDARD_BESTILLING), help="mappe for bestillinger")
    ap.add_argument("--retteliste", help="skriv rettelisten til denne filen")
    ap.add_argument("--installer", help="filkoder å kopiere til datamappen, for eksempel A,C")
    ap.add_argument("--mal", default=str(STANDARD_MAL), help="datamappe som filene installeres i")
    ap.add_argument("--overskriv", action="store_true")
    ap.add_argument("--yes", action="store_true", help="bekreft installering")
    args = ap.parse_args(argv)

    if args.kopier:
        kode = args.kopier.strip().upper()
        if kode != "ALLE" and kode not in L.FILER:
            print("Bruk --kopier A, B, C, D, E eller ALLE")
            return 2
        tekst = bestilling_for(list(L.FILER) if kode == "ALLE" else [kode])
        fil = ROOT / "01_inbox" / "h5_bestilling" / ("komplett.md" if kode == "ALLE" else f"fil_{kode}_{L.FILER[kode].removesuffix('.yaml')}.md")
        if not fil.is_file():
            skriv_bestillinger(fil.parent)
        if kopier_til_utklippstavle(fil):
            print(f"Kopiert til utklippstavlen: {fil.name} ({len(tekst)} tegn). Lim den inn i modellen.")
        else:
            print(f"Kunne ikke kopiere automatisk. Åpne {fil} og kopier innholdet selv.")
        return 0

    if args.lag_historikk_tall:
        p = L.skriv_historikk_tall(Path(args.til))
        print(f"Skrev {p} (laget av koden, ikke av en modell)")
        return 0

    if args.importer:
        svarfil = Path(args.importer)
        if not svarfil.is_file():
            print(f"Finner ikke filen {svarfil}")
            return 2
        mal = Path(args.til)
        skrevet, adv = importer_svar(svarfil.read_text(encoding="utf-8", errors="replace"), mal, args.fil)
        for a in adv:
            print(f"ADVARSEL {a}")
        if not skrevet:
            print("Ingen filer ble importert.")
            return 2
        feil_totalt = 0
        for k in skrevet:
            funn = L.kontroller_tekst(k, (mal / L.FILER[k]).read_text(encoding="utf-8"))
            feil = [f for f in funn if f.alvor == "FEIL"]
            feil_totalt += len(feil)
            print(f"{k}  {L.FILER[k]:<32} {'OK' if not feil else f'{len(feil)} FEIL'}  ({len(funn) - len(feil)} advarsler)")
            if feil:
                print(f"\n--- LIM DETTE TILBAKE TIL MODELLEN ({L.FILER[k]}) ---\n{L.retteliste_fil(funn)}")
        return 1 if feil_totalt else 0

    if args.lag_colab_pakke:
        ut = Path(args.ut) if args.ut != str(STANDARD_BESTILLING) else STANDARD_COLAB
        for f in skriv_colab_pakke(ut):
            print(f"Skrev {f}")
        return 0

    if args.lag_bestilling:
        ut = Path(args.ut)
        filer = skriv_bestillinger(ut)
        L.skriv_skjelett(ut / "skjelett")
        for f in filer:
            print(f"Skrev {f}")
        print(f"Skrev skjelett i {ut / 'skjelett'}")
        return 0

    if not args.leveranse:
        ap.print_usage()
        return 2
    mappe = Path(args.leveranse)
    if not mappe.is_dir():
        print(f"Finner ikke mappen {mappe}")
        return 2

    r = L.kontroller_mappe(mappe)
    for kode, fil in {**L.FILER, **{k: f for k, f in L.GENERERT_FIL.items() if k in r.filer}}.items():
        print(f"{kode}  {fil:<32} {'OK' if r.filer.get(kode) else 'FEIL'}")
    print(f"\n{len(r.feil)} feil, {len(r.advarsler)} advarsler")
    for w in r.advarsler[:20]:
        print(f"  ADVARSEL {w.fil} {w.sti} [{w.kode}]: {w.melding}")

    if args.installer:
        if not args.yes:
            print("Installering krever --yes. Dette kopierer filer til datamappen.")
            return 2
        koder = [k for k in args.installer.split(",") if k.strip()]
        ok, avvist = L.installer(mappe, koder, Path(args.mal), args.overskriv)
        for k in ok:
            print(f"Installert {k}: {L.FILNAVN[k]}")
        for a in avvist:
            print(f"Avvist {a}")
        return 0 if not avvist else 1

    liste = L.retteliste(r)
    if liste:
        if args.retteliste:
            Path(args.retteliste).write_text(liste, encoding="utf-8")
            print(f"Skrev retteliste til {args.retteliste}")
        else:
            print("\n--- RETTELISTE (lim denne til modellen) ---\n" + liste)
        return 1
    print("Alt består. Neste steg er menneskelig godkjenning av innholdet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
