# ADR 009: Arbeidsmiljøloven kap. 10 (Arbeidstid, hviletid og overtid)

**Status:** Godkjent  
**Dato:** 2026-10-19  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Kunstpixel har 54 994 historiske vakter og en operativ vaktplan for 28 personas og 168 ansatte. For at AI-agenter som opptrer som Driftsleder, HR-leder eller Direktør skal opptre faglig forsvarlig, må de underlegges strenge compliance-regler i tråd med norsk arbeidsmiljølov (AML).

---

## Beslutning
Vi låser vaktplanlegging og bemanningsforslag til en **deterministisk AML kap. 10 compliance-motor**:
1. **§ 10-8 Daglig arbeidsfri (Hviletid):**  
   Arbeidstaker skal ha minst 11 timer sammenhengende arbeidsfri i løpet av 24 timer. Ethvert skiftforslag som bryter denne grensen (f.eks. kveldsvakt til 22:00 etterfulgt av morgenvakt kl. 08:00) skal deterministisk blokkeres med status `AML_VIOLATION_DAILY_REST`.
2. **§ 10-8 Ukentlig arbeidsfri:**  
   Minst 35 timer sammenhengende hvile i løpet av 7 dager.
3. **§ 10-4 Alminnelig arbeidstid:**  
   Maks 9 timer per 24 timer og 37,5 timer per uke (tariffestet for museer).
4. **§ 10-6 Overtid:**  
   Overtid skal kun benyttes ved ekstraordinære, tidsavgrensede behov (f.eks. akutte sykdomsforfall eller vernissasje), og utløser overtidstillegg (50 %, 100 % eller 133 %).

---

## Konsekvenser
- **Automatisk kontroll:** AI-agenter kan aldri godkjenne en vaktplan uten å kjøre `audit_shift_compliance`.
- **Revisjonssikkerhet:** Ledelsen har full sporbarhet på at ingen ansatte settes opp i strid med norsk lov.
