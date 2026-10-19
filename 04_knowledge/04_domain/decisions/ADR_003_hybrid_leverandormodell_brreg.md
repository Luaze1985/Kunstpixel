# ADR 003: Hybrid leverandørmodell koblet mot Brreg API

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
For å gi realistisk grunnlagsdata for Kunstpixels interne drift, leverandørkontroll og administrative roller (f.eks. Driftsansvarlig, Samlingsforvalter og Direktør), må `hr_innleie` og innkjøpsprosessene gjenspeile ekte norsk næringsliv.

---

## Beslutning
Vi etablerer en **hybrid leverandørmodell**:
1. **Reelle selskapsdata fra Brreg API:**  
   12 reelle norske selskaper hentes direkte via Brønnøysundregistrenes Enhetsregister API (`data.brreg.no/enhetsregisteret/api/enheter`). Dette inkluderer 40 autoritative felter per selskap: ekte organisasjonsnummer, fullt foretaksnavn, organisasjonsform (`AS`/`Stiftelse`), MVA-registrering, antall ansatte, aksjekapital, konkurs-status og næringskoder (f.eks. Securitas, Avarn, DHL, NIKU, ISS, Anticimex, Caverion, GK, EY, Bring Cargo, Gyldendal, Creative Technology).
2. **Skreddersydde utstillingsoppdrag i `kunstpixel_historikk.db`:**  
   De 318 kontraktene i `hr_innleie` kobles direkte til disse 12 reelle selskapene og til de 102 utstillingene, med realistiske timepriser, fakturerte timer og godkjenninger fra museets personas (f.eks. Henrik Faye-Lund eller Terje Bratt).

---

## Konsekvenser
- **Hva fremtidige agenter låses til:**  
  Når agenter skal vurdere innkjøp, anskaffelser eller leverandørfakturaer, skal de utføre deterministisk sjekk mot Brreg-dataene (f.eks. at leverandøren ikke er konkurs og er registrert i MVA-registeret).
