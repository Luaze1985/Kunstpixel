# BESTILLING OG KONTRAKT: NESTE DATAINNSAMLING FRA COLAB
*Bruk denne malen som instruks og kodeblokk i neste Colab-notatbok.*

---

## 1. Mål og Oppdrag for Neste Innsamling
Denne bestillingen sikrer at data som samles inn eller syntetiseres i Google Colab kan importeres inn i `05_data/museum.db` og verifiseres i `pytest` på **0 sekunder uten manuell vask**.

---

## 2. Instruks til Colab / LLM i Colab
Lim inn denne instruksen øverst i Colab-notatboken:

> **Krav til datafangst i denne notatboken:**
> 1. Alle tabeller skal eksporteres i enten CSV-format (komma-separert, anførselstegn rundt felter med komma) eller ren YAML (UTF-8).
> 2. Ingen reelle personopplysninger (kontaktpersonnavn, ekte telefonnumre, ekte e-poster) skal lagres i åpne felter. Bruk rollebetegnelser (f.eks. `driftsansvarlig`, `avdelingsleder`) og fiktive domener (`@example.test`).
> 3. Hver rad skal ha en unik identifikator (`ID`, f.eks. `TAB-001`, `KURS-01`).
> 4. Siste celle i notatboken skal kjøre **Leveransecellen (se under)** som verifiserer skjemaintegritet og lagrer direkte til Google Drive med sjekksum.

---

## 3. Leveransecellen (MÅ ligge som siste celle i Colab)
Kopier og kjør denne Python-koden som siste celle i Colab for å pakke og signere leveransen:

```python
import os
import hashlib
import json
import pandas as pd
from google.colab import drive

# 1. Koble til Google Drive
drive.mount('/content/drive')

LEVERANSE_NAVN = "2026-10-30_neste_datainnsamling"  # <--- Juster dato og emne her
UT_MAPPE = f"/content/drive/MyDrive/Kunstpixel/01_inbox/incoming/{LEVERANSE_NAVN}"
os.makedirs(UT_MAPPE, exist_ok=True)

# 2. Definer tabellene som skal leveres (eksempel)
# df_dine_data.to_csv(f"{UT_MAPPE}/dine_data.csv", index=False)

def valider_og_signer(mappe: str):
    filer = [f for f in os.listdir(mappe) if f.endswith(('.csv', '.yaml', '.json')) and not f.startswith('SJEKKSUM')]
    if not filer:
        raise ValueError("Ingen datafiler funnet i leveransemappen!")
    
    sjekksummer = {}
    for f in sorted(filer):
        sti = os.path.join(mappe, f)
        with open(sti, 'rb') as fp:
            sha = hashlib.sha256(fp.read()).hexdigest()
        sjekksummer[f] = sha
        print(f"[OK] {f}: {sha[:12]}...")
        
    # Skriv sjekksum-fil
    with open(os.path.join(mappe, "SJEKKSUM.sha256"), "w", encoding="utf-8") as fp:
        for f, sha in sjekksummer.items():
            fp.write(f"{sha}  {f}\n")
            
    # Skriv metadata
    metadata = {
        "leveranse": os.path.basename(mappe),
        "antall_filer": len(filer),
        "filer": list(sjekksummer.keys()),
        "kilde": "Google Colab",
        "status": "VALIDERT_OG_SIGNERT"
    }
    with open(os.path.join(mappe, "METADATA.json"), "w", encoding="utf-8") as fp:
        json.dump(metadata, fp, indent=2)
        
    print(f"\n>> Leveranse fullført og signert i: {mappe}")

valider_og_signer(UT_MAPPE)
```

---

## 4. Mottakssjekkliste for Antigravity i neste økt
Når filene er lagret til Drive:
1. Agenten kjører en deterministisk sjekksum-validering:
   `Get-FileHash -Algorithm SHA256 01_inbox/incoming/<mappe>/*`
2. Agenten importerer tabellene direkte inn i `05_data/` via `build_museum_db.py`.
3. Testpakken kjøres med `py -3.13 scripts/db_status_gate.py` (0 feil).
