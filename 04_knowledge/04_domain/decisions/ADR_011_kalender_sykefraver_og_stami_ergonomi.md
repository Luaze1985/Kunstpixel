# ADR 011: Kalender (helligdager/skolerute), SSB-sykefravær og STAMI-ergonomi

**Status:** Godkjent  
**Dato:** 2026-10-19  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Vaktplanlegging og driftsøkonomi i et museum er sterkt sesongavhengig. Publikumstall eksploderer i skoleferier og på helligdager, samtidig som helge- og helligdagstillegg øker lønnskostnadene kraftig. Samtidig utsettes salverter for ergonomisk slitasje ved langvarig stående arbeid på museets steingulv.

---

## Beslutning
1. **Norsk helligdags- og feriekalender (2010–2026):**  
   Tabellen `norske_helligdager` opprettes i `museum.db`. Den identifiserer alle offentlige høytidsdager (med 133 % helligdagstillegg) og skoleruter (vinterferie uke 8, påske, sommer, høstferie uke 40, jul).
2. **SSB Sykefraværsstatistikk (tabell 12441):**  
   Reelle kvartalsvise fraværsrater for kultursektoren etableres i `ssb_sykefraver_kultur` for å beregne nødvendig vikarbuffer (f.eks. 6,8 % i Q1 mot 4,9 % i Q3).
3. **STAMI Ergonomiske rotasjonsregler:**  
   Tabellen `hms_ergonomi_rotasjon` innfører krav om maksimalt 2 timer sammenhengende stående vakt i salene (SAL-A til SAL-D), med obligatorisk rotasjon til sittende oppgaver (kiosk/skranke/pause).

---

## Konsekvenser
- **Forutsigbar lønns- og vaktberegning:** Tariffberegninger treffer nøyaktig på røde dager uten manuelle oppslag.
- **HMS og forebygging:** Fjerner risiko for overbelastning og museale slitasjeskader hos salspersonalet.
