# ADR 007: Offentlige anskaffelser (Doffin/LOA) og Virke museumstariff

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Kunstpixel krever høy forretningsmessig og administrativ realisme. For å trene roller som `/direktor`, `/drift` og HR på økonomisk styring og compliance, må innleiekontrakter følge norsk anskaffelsesrett og personalet avlønnes etter etablerte tariffavtaler i kultursektoren.

---

## Beslutning
1. **Doffin / LOA-anskaffelsesmodell for de 318 innleiekontraktene:**  
   Kontraktene kobles mot de 12 Brreg-selskapene og kategoriseres etter norske terskelverdier:
   - **Under 100 000 kr:** Direkteanskaffelse (forenklet protokoll)
   - **100 000 – 1,4 MNOK:** Nasjonal kunngjøringsplikt (Doffin)
   - **Over 1,4 MNOK:** EØS-terskelverdi (anbudskonkurranse med karensperiode)
   - Alle kontrakter har tildelingsdato, Doffin-ID, SAF-T MVA-kode og leverandørens org.nr.
2. **Virke Landsoverenskomst for museer (Tariff og lønn):**  
   - Etablere tabellen `virke_tariff` med lønnstrinn (20–65), grunnlønn per år og timesats.
   - Modellere ubekvemstillegg: Kveldstillegg (etter kl. 17:00), helgetillegg (lørdag/søndag) og helligdagstillegg (100–133 %).
   - Koble de 28 personas og 54 994 vaktene mot disse tariffene for nøyaktig beregning av vaktkostnader og avvikshåndtering.

---

## Konsekvenser
- **Revisjonssikkerhet:** AI-agentene kan deterministisk varsle hvis en direkteanskaffelse overstiger 100 000 kr, eller hvis et skift bryter overtidsbestemmelsene i Arbeidsmiljøloven.
