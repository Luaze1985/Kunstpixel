# ADR 006: Samlingsomfang og utstillingsinnlån (100 verk)

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Tidligere hadde Aura Kunstmuseum kun 16 registrerte verk i `museum.db`, hvorav kun to (*Skrik* og *Nøkken*) hadde fullstendige formidlingstekster. For å speile et fullverdig mellomstort museum med reell variasjon for kuratorer og formidlere, trengs et større volum forankret i ekte norsk kunsthistorie.

---

## Beslutning
Samlingen utvides til **100 registrerte verk**, delt i to kategorier:
1. **50 faste verk i Aura Kunstmuseum:**  
   Fordelt på Sal A, Sal B, Sal C, Sal D og Magasin 1. Representerer de 12 norske mesterne (Kittelsen, Munch, Krohg, Backer, Sohlberg, Astrup, Kielland, Werenskiold, Thaulow, Bergman, Tidemand, Gude).
2. **50 historiske utstillingsinnlån (2010–2026):**  
   Innlånt til de 102 temporære utstillingene i Sal E fra reelle norske institusjoner (Nasjonalmuseet, KODE, Lillehammer Kunstmuseum, Haugar, Stavanger kunstmuseum, Henie Onstad).
3. **Komplett trelags tekststandard (jf. masterprompt):**  
   Hvert eneste verk har:
   - Veggtekst (50–90 ord)
   - Audioguide (130–180 ord / 60–90 sekunder)
   - Barneformidling (60–100 ord)
   - Proveniens og tilstandshistorikk

---

## Konsekvenser
- **Ingen fiktive verk:** Alle verk er historisk attesterte malerier/grafikk med ekte tilblivelsesår, teknikk og dimensjoner.
- **Formidler- og vertseffekt:** Rollene `/formidler` og `/museumsvert` kan betjene et bredt publikum og foreslå varierte tematiske omvisningsruter.
