# 06_kart — 2.5D Isometrisk Bygnings- og Sonekart for Aura Museum

Dette er en dedikert og isolert kart- og geometrimodul for Aura Museum, bygget som et **2.5D isometrisk bygningskart** med full soneinndeling.

---

## 1. Oversikt og Funksjoner

* **2.5D Isometrisk projeksjon:** Viser hele museumsbygningen i et interaktivt fugleperspektiv med matematisk 30-graders isometri.
* **Skall / Fasade vs. Røntgen / Interiør:**
  * **Skall:** Viser bygningskroppen utenfra – rød håndbanket tegl på hovedfløyen (1912), patinert kobbertak og moderne glassfløy mot øst (2016).
  * **Røntgen:** Skjærer vekk yttervegger og viser inn i salene, rommene, dørene og heis-/trappesjaktene.
* **Etasjevelger:**
  * *Alle (Eksplodert):* Viser alle tre etasjer (U1, P1, P2) svevende over hverandre forbundet med heis- og trappeløp.
  * *U1 Kjeller:* Magasin 1, kunstmottak og teknisk sentral.
  * *P1 Hovedplan:* Vestibyle, butikk, kafé, Sal A (Kittelsen), Sal B (Krohg), Sal E (Temporær).
  * *P2 Galleri:* Sal C (Backer), Sal D (Munch) og Vaktrom/Sikkerhetssentral.
* **Sonelag:**
  * *Arkitektur:* Nøytralt arkitektonisk uttrykk med rommål og takhøyder.
  * *Sikkerhetssoner:* Sone 1 (Grønn - Publikum), Sone 2 (Gul - Utstilling), Sone 3 (Blå - Drift/Personal), Sone 4 (Rød - Høysikkerhet/Magasin).
  * *Klimasoner:* K1 (Cyan - Høykonservering/Magasin), K2 (Lilla - Standard kunstsal), K3 (Grå - Publikumskomfort).
* **Interaktivt slide-over panel:**
  * Klikk på et hvilket som helst rom for å åpne detaljert faktaskuff med areal, takhøyde, verkskapasitet, lyskrav, sikkerhetsrutiner og aktive sensorer.

---

## 2. Filer i modulen

| Fil | Beskrivelse |
|---|---|
| `bygning_geometri.json` | Autoritativ SSOT for mål, rom, etasjer, fasader og sonedefinisjoner (syntetisk). |
| `build_map.py` | Python-kompilator som leser geometrien og bygger den selvstendige HTML-viseren. |
| `index.html` | Den interaktive kartviseren (0 eksterne avhengigheter, fungerer offline). |

---

## 3. Bruk og Kjøring

### Bygg kartet på nytt (hvis du endrer `bygning_geometri.json`):
```powershell
py -3.13 06_kart/build_map.py
```

### Åpne kartet i nettleseren:
```powershell
Start-Process "06_kart/index.html"
```

### Oppslag via FastMCP i kode:
```python
from src.kunstpixel.core.mcp_server import get_building_map_data

# Hent hele modellen
data = get_building_map_data()

# Hent bare 1. etasje (P1)
p1 = get_building_map_data(etasje=1)

# Hent bare sikkerhetssoner
sikkerhet = get_building_map_data(sone_type="sikkerhet")
```
