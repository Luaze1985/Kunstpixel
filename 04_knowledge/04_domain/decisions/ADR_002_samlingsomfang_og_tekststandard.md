# ADR 002: Samlingsomfang og 3-lags tekststandard (50–100 verk)

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Tidligere hadde `museum.db` kun 16 verk, hvorav 14 manglet både audioguide og barneformidling. Dette gjorde databasen for tynn til å fungere som en troverdig institusjonell samling, og tvang språkmodellen til å dikte når den skulle formidle utenfor *Skrik* og *Nøkken*.

---

## Beslutning
Vi låser samlingsbasen til et omfang på **50–100 representative verk** fordelt på museets 12 faste kunstnere.

For **hvert eneste verk** i samlingen innføres en obligatorisk **3-lags formidlingsstandard**:
1. **Kuratortekst / Veggtekst (Faglig dybde):** 50–90 ord om synlige trekk, teknikk, epoke og historisk kontekst.
2. **Audioguide-manus (Sanselig formidling):** 130–180 ord tilrettelagt for muntlig opplesning med fokus på detaljer og historiefortelling.
3. **Barneformidling (Pedagogisk dialog):** 60–100 ord med undrende spørsmål og engasjerende historier tilpasset barn og barnefamilier.

---

## Konsekvenser
- **Hva fremtidige agenter låses til:**  
  Ingen verk kan registreres med `NULL` eller tomme strenger i `veggtekst`, `audioguide_manus` eller `barneformidling`.
- **Integritet og kvalitet:**  
  Samlingen skal fordeles logisk på museets 5 saler (`SAL-A` til `SAL-E`) og magasin (`MAG-1`), med korrekte inventarnumre (`AURA-2026-xxx`).
