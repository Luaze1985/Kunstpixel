# ADR 005: Operativ hendelses-, avviks- og tilstandsmodell

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
For at masterpromptens roller `/drift`, `/samlingsforvalter` og `/direktor` skal ha realistiske oppgaver og caser å håndtere, holder det ikke med statiske masterdata. Museet trenger en operativ hendelseshistorikk med avvik (HMS, sikkerhet, teknisk drift), konserveringstilstand på verk, og prosjektøkonomi per utstilling.

---

## Beslutning
Vi etablerer tre nye operative tabeller i `museum.db`:
1. `avvik_hms_drift`:  
   Strukturerte avvikshendelser (2010–2026) med feltene `avvik_id`, `dato`, `alvorlighetsgrad` (GRØNN, GUL, RØD), `kategori` (HMS, SIKKERHET, KLIMA, TEKNISK, PUBLIKUM), `berort_sal_id`, `berort_verk_id`, `beskrivelse`, `strakstiltak`, `oppfolging_ansvarlig_id` og `status` (LUKKET, APEN).
2. `tilstandsrapporter`:  
   Verkskonservering og tilstandskontroll med `rapport_id`, `verk_id`, `dato`, `tilstandsgrad` (1=Utmerket, 2=God, 3=Middels/observasjon, 4=Akutt behov), `lysomfintlighet_luks`, `klimakrav_rh_prosent`, `konserveringshistorikk` og `forsikringsverdi_nok`.
3. `utstilling_okonomi`:  
   Prosjektøkonomi for alle 102 utstillinger med `utstilling_id`, `budsjett_nok`, `faktisk_kostnad_nok`, `billettinntekter_nok`, `katalogsalg_nok`, `sponsorstotte_nok` og `avvik_forklaring`.

---

## Konsekvenser
- **Realistisk saksbehandling:** Rollene `/drift` og `/samlingsforvalter` kan spørre på aktive avvik og uavklarte klimasvingninger.
- **Direktør-innsikt:** `/direktor` kan analysere hvilke utstillinger som gikk med overskudd eller underskudd, og koble kostnader mot innleiekontrakter.
