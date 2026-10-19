# SOP-004: Rutine for vaktbytte og vikarinnkalling

> **ID:** `SOP-004` | **Revisjon:** 2026-10-19 | **Hjemmel:** Arbeidsmiljøloven (AML) § 10-8, Virke Landsoverenskomst  
> **Formål:** Sikre smidig vaktbytte uten brudd på lovpålagt hviletid eller museets bemanning.

---

### 1. Betingelser for ordinært vaktbytte
* Vaktbytte skal skje mellom to ansatte med **samme kompetansekrav** (f.eks. vert mot vert, kassekompetent mot kassekompetent).
* **AML 11-timers sperre:** Vaktbyttet avvises automatisk dersom det gir mindre enn 11 timer sammenhengende hvile for en av partene (AML § 10-8).
* Søknad registreres i vaktplansystemet senest **24 timer før vaktstart** og godkjennes av vaktleder.

### 2. Akutt vikarinnkalling ved sykdom
Når fravær meldes inn kl. 07:30:
1. Vaktleder slår opp i museets godkjente vikarbank (`hr_ansatte` med status `aktiv=1`).
2. Kandidater rangeres deterministisk etter:
   - Ledig status og fravær av registrert vakt samme døgn.
   - Oppfylt 11t hviletid fra foregående dag.
   - Lavest akkumulert mertid/overtid inneværende måned.
3. Forespørsel sendes prioritert per SMS/telefon. Ved bekreftelse oppdateres vaktplanen straks.
