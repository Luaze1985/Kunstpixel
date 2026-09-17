# [SOP-ID]: [Tittel på Standard Operating Procedure]
*Standard Operating Procedure for Kunstpixel (kunstpixel.com) basert på ICOR-metodikken*

---

## 1. Metadata
* **SOP-ID:** SOP-XXX
* **Ansvarlig agent:** `/[rolle]` (se `team/team_roster.md`)
* **Dato opprettet / revidert:** YYYY-MM-DD
* **Tilknyttet myndighet / fagkilde:** [f.eks. Mattilsynet / ICOM / Arbeidstilsynet / Internkontroll]

---

## 2. Formål og omfang
Kort beskrivelse (2–4 setninger) av hva denne prosedyren skal oppnå, og hvem den gjelder for.

---

## 3. ICOR-prosessflyt

### 📥 1. INPUT (Hva utløser prosedyren?)
* **Triggere:** Hva starter oppgaven (f.eks. henvendelse i `team_inbox/`, fast dato i tilsynskalenderen, eller ny utstilling)?
* **Nødvendig underlag:** Hvilke rådata, tabeller eller dokumenter må være tilgjengelige før start?

### ⚙️ 2. CONTROL (Regler, begrensninger og standarder)
* **Juridisk / faglig hjemmel:** Hvilke lover, forskrifter eller bransjestandarder gjelder (Nivå 1–5)?
* **Strenge begrensninger:** 
  * Ordbruksregler (skille mellom *må*, *skal*, *bør*).
  * Anti-hallusinasjon (hvilke databaser/tabeller er fasit).
  * Formatkrav (f.eks. ordgrense 50–90 ord, temperaturkrav $\le +4^\circ\text{C}$).

### 📤 3. OUTPUT (Hva leveres?)
* **Konkret leveranse:** Nøyaktig hva skapes (f.eks. rapport, veggtekst, tabell, oppdatert database-rad).
* **Destinasjon:** Hvor skal filen lagres (f.eks. `deliverables/`, `data/governance/`, eller `docs/`)?
* **Varsling:** Hvem varsles når oppgaven er utført?

### 🔄 4. REFINE (Kvalitetssjekk og forbedring)
* **Kvalitetskontroll (QA):** Hva sjekker `/qa` før leveransen godkjennes?
* **Avvikshåndtering:** Hva gjøres dersom data mangler, eller det oppdages feil?
* **Erfaringslæring:** Hvordan oppdateres denne SOP-en dersom rutinen endres?

---

## 4. Trinnvis sjekkliste for agenten

- [ ] **Steg 1:** Verifiser at all påkrevd input finnes i `team_inbox/` eller databasen.
- [ ] **Steg 2:** Utfør oppgaven strengt i henhold til kontrollreglene i avsnitt 3.2.
- [ ] **Steg 3:** Lagre det ferdige utkastet i `deliverables/` med standard navnestruktur.
- [ ] **Steg 4:** Send utkastet til `/qa` for deterministisk validering og kildekontroll.
- [ ] **Steg 5:** Varsle Museumsdirektøren (`/direktor`) om at leveransen er klar for godkjenning.
