# ADR 001: Helhetlig operativ triade for Kunstpixels databaser

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Kunstpixel er treningsarena og digital tvilling for Aura Kunstmuseum. Databasene har hittil vært fragmenterte og delvis tynne på faglige og administrative realiteter. For at datagrunnlaget skal fungere sømløst mot museets masterprompt og gi maksimal overføringsverdi til reell virksomhetsdrift, måtte vi avklare styringsformålet for databasene.

---

## Beslutning
Vi låser databasens arkitektur og innhold til en **helhetlig operativ triade** som dekker alle 3 kjerneområder samtidig:

1. **Rolleforankring (De 6 rollene i masterprompten):**  
   Hvert eneste datapunkt som registreres har en definert eierrolle (Direktør, Kurator, Formidler, Samlingsforvalter, Vert, Drift) og tjener en konkret operativ oppgave.
2. **Hard compliance og internkontroll:**  
   Inkluderer reelle registre (Brønnøysundregistrene for leverandører, Mattilsynet for IK-mat/karantener, Arbeidstilsynet for HMS/ergonomi/arbeidstid, og DSB for RVR-brannsikring).
3. **Formidling, publikum og økonomi:**  
   Inkluderer flerlags verksformidling (kuratortekst, audioguide, barneformidling), billettsalg og SSB-kalibrerte dagsbesøk/inntekter.

---

## Konsekvenser
- **Hva fremtidige agenter låses til:**  
  Ingen agent har lov til å legge inn "isolerte leketall". Nye tabeller og felter må eksplisitt plasseres inn i denne triaden og knyttes til en ansvarlig rolle i masterprompten.
- **Forretningsmessig gevinst:**  
  Databasen blir 100 % troverdig både overfor museumsfaglige eksperter, økonomer og tilsynsmyndigheter.
