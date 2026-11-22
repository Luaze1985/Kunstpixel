"""Fjerner det gamle museumsnavnet fra skilt, disker og fasader i 06_kart/bilder (DECISIONS punkt 10).

Leser originalene fra git-commit 1c4d9a4, så kjøringen gir samme resultat hver gang:
1. finner bokstavene i en kjent boks (avvik fra bakgrunnsfargen langs boksens kant),
2. maler over dem med OpenCV-inpainting,
3. skriver eventuelt ny tekst («KUNSTPIXEL» o.l.) i en font som ligner.

Kjør:  py -3.13 scripts/fjern_navn_i_bilder.py
"""

from __future__ import annotations

import io
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BILDER = ROOT / "06_kart" / "bilder"
ORIGINAL_COMMIT = "1c4d9a4"
FONTER = Path("C:/Windows/Fonts")
GEORGIA = FONTER / "georgia.ttf"
SEGOE = FONTER / "segoeui.ttf"
SEGOE_SB = FONTER / "seguisb.ttf" if (FONTER / "seguisb.ttf").exists() else FONTER / "segoeuib.ttf"

# Hver operasjon: boks (x0, y0, x1, y1), om bokstavene er lyse eller mørke, og ny tekst.
# Koordinatene er funnet ved å lese forstørrede utsnitt av hvert bilde (1376 x 768 px).
OPERASJONER: dict[str, list[dict]] = {
    "01_eksterior_fasade.jpg": [
        {"boks": (306, 395, 402, 409), "modus": "hel", "fyll": "kolonne", "linjer": ["KUNSTPIXEL 1912"], "font": GEORGIA, "farge": (70, 60, 52)},
        {"boks": (971, 531, 1046, 548), "modus": "lys", "linjer": ["KUNSTPIXEL"], "font": SEGOE_SB},
    ],
    "02_eksterior_tilbygg_nidelva.jpg": [
        {"boks": (1017, 417, 1101, 443), "modus": "lys", "linjer": ["KUNSTPIXEL", "– SAMTIDSAVDELING"], "font": SEGOE_SB},
    ],
    "02_vestibyle_ankomst.jpg": [
        {"boks": (640, 451, 700, 480), "modus": "lys", "linjer": ["KUNSTPIXEL", "RESEPSJON | BILLETTER"], "font": SEGOE_SB},
        {"boks": (709, 453, 736, 484), "modus": "lys", "linjer": []},
    ],
    "03_sal_a_mytologi.jpg": [
        {"boks": (692, 212, 750, 237), "modus": "lys", "linjer": ["KUNSTPIXEL"], "font": SEGOE},
    ],
    "04_vestibyle_resepsjon.jpg": [
        {"boks": (134, 360, 216, 420), "modus": "mork", "linjer": ["KUNST", "PIXEL"], "font": SEGOE_SB},
        {"boks": (419, 505, 435, 526), "modus": "hel", "linjer": []},
        {"boks": (348, 498, 444, 576), "modus": "lys", "linjer": ["KUNSTPIXEL", "VELKOMMEN"], "font": SEGOE, "vinkel": 18},
    ],
    "05_museumsbutikk.jpg": [
        {"boks": (716, 116, 848, 198), "modus": "begge", "terskel": 22, "linjer": []},
    ],
    "06_museumskafe.jpg": [
        {"boks": (1198, 556, 1264, 612), "modus": "mork", "linjer": [], "fyll": "kolonne"},
    ],
    "11_sal_d_munch.jpg": [
        {"boks": (1252, 333, 1322, 423), "modus": "lys", "linjer": ["KUNSTPIXEL", "– SAL D –", "EKSISTENS OG", "MODERNISME"], "font": GEORGIA},
    ],
}

# Samme motiv lagret under to navn. Kopien får det rettede bildet.
KOPIER = {"04_sal_d_munch.jpg": "11_sal_d_munch.jpg"}


def _les_original(navn: str) -> Image.Image:
    data = subprocess.run(
        ["git", "show", f"{ORIGINAL_COMMIT}:06_kart/bilder/{navn}"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout
    return Image.open(io.BytesIO(data)).convert("RGB")


def _maske(bgr: np.ndarray, boks: tuple[int, int, int, int], modus: str, terskel: int) -> np.ndarray:
    """Markerer pikslene i boksen som skiller seg fra bakgrunnen langs boksens kant."""
    x0, y0, x1, y1 = boks
    lum = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(int)
    felt = lum[y0:y1, x0:x1]
    kant = np.concatenate([felt[0], felt[-1], felt[:, 0], felt[:, -1]])
    bakgrunn = int(np.median(kant))
    if modus == "hel":
        treff = np.ones_like(felt, dtype=bool)
    elif modus == "lys":
        treff = felt > bakgrunn + terskel
    elif modus == "mork":
        treff = felt < bakgrunn - terskel
    else:
        treff = np.abs(felt - bakgrunn) > terskel
    maske = np.zeros(lum.shape, np.uint8)
    maske[y0:y1, x0:x1] = treff.astype(np.uint8) * 255
    if modus == "hel":
        return maske
    return cv2.dilate(maske, np.ones((5, 5), np.uint8), iterations=1)


def _kolonnefyll(bgr: np.ndarray, maske: np.ndarray) -> np.ndarray:
    """Fyller hver maskert stripe loddrett mellom pikselen over og under (for loddrette spiler)."""
    ut = bgr.astype(float).copy()
    hoyde = maske.shape[0]
    for x in np.where(maske.any(axis=0))[0]:
        rader = np.where(maske[:, x] > 0)[0]
        start = rader[0]
        for i in range(1, len(rader) + 1):
            if i == len(rader) or rader[i] != rader[i - 1] + 1:
                slutt = rader[i - 1]
                over = ut[max(start - 3, 0):start, x].mean(axis=0)
                under = ut[slutt + 1:min(slutt + 4, hoyde), x].mean(axis=0)
                for y in range(start, slutt + 1):
                    t = (y - start + 1) / (slutt - start + 2)
                    ut[y, x] = over * (1 - t) + under * t
                if i < len(rader):
                    start = rader[i]
    return ut.clip(0, 255).astype(np.uint8)


def _tekstfarge(rgb: np.ndarray, maske: np.ndarray, modus: str) -> tuple[int, int, int]:
    piksler = rgb[maske > 0]
    lum = piksler.mean(axis=1)
    grense = np.percentile(lum, 85 if modus == "lys" else 15)
    utvalg = piksler[lum >= grense] if modus == "lys" else piksler[lum <= grense]
    return tuple(int(v) for v in np.median(utvalg, axis=0))


def _skriv(bilde: Image.Image, boks, linjer: list[str], font_sti: Path, farge, vinkel: float) -> None:
    """Skriver linjene sentrert i boksen, så store som mulig innenfor 88 % av bredden."""
    x0, y0, x1, y1 = boks
    bredde, hoyde = x1 - x0, y1 - y0
    if vinkel:
        bredde, hoyde = int(bredde * 1.05), int(hoyde * 0.55)
    for storrelse in range(40, 5, -1):
        font = ImageFont.truetype(str(font_sti), storrelse)
        maal = [font.getbbox(t) for t in linjer]
        linjehoyde = max(b[3] - b[1] for b in maal) * (1.35 if len(linjer) > 1 else 1.05)
        if max(b[2] - b[0] for b in maal) <= bredde * 0.88 and linjehoyde * len(linjer) <= hoyde * 0.92:
            break
    lag = Image.new("RGBA", (bredde * 2, hoyde * 2), (0, 0, 0, 0))
    tegn = ImageDraw.Draw(lag)
    total = linjehoyde * len(linjer)
    for i, (tekst, b) in enumerate(zip(linjer, maal)):
        x = lag.width / 2 - (b[2] - b[0]) / 2 - b[0]
        y = lag.height / 2 - total / 2 + i * linjehoyde - b[1]
        tegn.text((x, y), tekst, font=font, fill=(*farge, 235))
    if vinkel:
        lag = lag.rotate(vinkel, resample=Image.BICUBIC, expand=False)
    lag = lag.filter(ImageFilter.GaussianBlur(0.45))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    bilde.paste(lag, (cx - lag.width // 2, cy - lag.height // 2), lag)


def rett_bilde(navn: str, operasjoner: list[dict]) -> Image.Image:
    bilde = _les_original(navn)
    for op in operasjoner:
        rgb = np.array(bilde)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        maske = _maske(bgr, op["boks"], op["modus"], op.get("terskel", 25))
        farge = op.get("farge") or (_tekstfarge(rgb, maske, op["modus"]) if op["linjer"] else None)
        if op.get("fyll") == "kolonne":
            rent = _kolonnefyll(bgr, maske)
        else:
            rent = cv2.inpaint(bgr, maske, 6, cv2.INPAINT_TELEA)
        bilde = Image.fromarray(cv2.cvtColor(rent, cv2.COLOR_BGR2RGB))
        if op["linjer"]:
            _skriv(bilde, op["boks"], op["linjer"], op["font"], farge, op.get("vinkel", 0))
    return bilde


def main() -> None:
    ferdige: dict[str, Image.Image] = {}
    for navn, ops in OPERASJONER.items():
        ferdige[navn] = rett_bilde(navn, ops)
        ferdige[navn].save(BILDER / navn, quality=95, subsampling=0)
        print(f"rettet: {navn}")
    for kopi, kilde in KOPIER.items():
        ferdige[kilde].save(BILDER / kopi, quality=95, subsampling=0)
        print(f"kopiert: {kilde} -> {kopi}")


if __name__ == "__main__":
    main()
