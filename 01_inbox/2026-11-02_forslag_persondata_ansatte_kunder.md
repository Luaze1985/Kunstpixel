# Forslag: Fiktive persondata om ansatte og kunder (GDPR-øving)

**Status:** Fase 1 besluttet og bygget 2026-11-02. Se `04_knowledge/04_domain/projects/persondata/2026-11-02_plan_persondata.md` og `05_data/persondata/README.md`. Ansatte genereres ikke, men hentes fra `hr_ansatte`.
**Dato:** 2026-11-02
**Gjelder:** Kunstpixel / Aura Kunstmuseum (syntetisk virksomhet)

---

## 1. Hva som finnes i dag (fakta, kontrollert)

**Ingen personopplysninger om ansatte eller kunder finnes i repoet.**

| Kilde | Innhold | Persondata? |
| :--- | :--- | :--- |
| `05_data/museum.db` | kunstnere (12), verk (16), saler (6), utstillinger (3), hendelser (8), publikum_faq (12) | Nei. Kunstnere er historiske personer, ikke behandling av ansatte eller kunder. |
| `05_data/governance/*.yaml/json` | IK-Mat, HMS, brann, tilsynskalender, kafémeny | Nei. Bare *roller* (Kafeleder, Brannvernleder), ingen navn. |
| `03_team/team_roster.md` | 7 agentroller | Nei, dette er AI-roller. |

**Spor i dokumentasjonen av at virksomheten *ville hatt* persondata:**

| Spor | Hvor | Hva det betyr |
| :--- | :--- | :--- |
| 12–15 kjernefunksjoner | `core/company.md` | Museet har ansatte. |
| Roterende vakter for museumsverter | `KVALITETS_OG_STYRINGSSYSTEM.md` | Vaktlister med navn. |
| Magesyke gir 48 t karantene | samme | **Helseopplysninger** (særlig kategori, art. 9). |
| Brannøvelse og hygienekurs for alle ansatte, skjenkebevilling | `tilsynskalender.json` | Kurs- og sertifikatregister per ansatt. |
| Hendelser med `maks_deltakere` og pris | `museum.db` → `hendelser` | Påmeldinger og betaling. |
| Barnearrangementer (Trolljakt, Detektiv) | `museum.db` → `hendelser` | Opplysninger om barn og foresatte. |
| Omvisning for skoleklasser, DKS | `publikum_faq` id 7, formidler-rollen | Skolebestillinger med kontaktlærer. |
| Privat utleie | `publikum_faq` id 6 | Utleiekunder. |
| Nyhetsbrev (Nivå 3-godkjenning) | `approval_boundaries.md` | E-postliste basert på samtykke. |
| Museumsvert via CLI/Telegram | `team_roster.md` | Henvendelseslogg der folk skriver fritt. |

**Regel som gjelder:** `tool_access.md` regel 3: *«Ingen persondata i treningsdata: Syntetiske henvendelser og besøksdata skal være fri for ekte personopplysninger.»*

---

## 2. Forslag: hva vi lager (vurdering)

Hovedprinsippet er å **lage bare data som gir en konkret GDPR-øvelse.** Et datasett uten øvelse er bare støy, og strider mot dataminimering, som er selve poenget å lære.

### 2a. Ansatte

| # | Datasett | Felt (forslag) | Antall | Øvelsen det gir |
| :--- | :--- | :--- | :--- | :--- |
| A1 | `ansatte.csv` | ansatt_id, fornavn, etternavn, rolle, stillingsprosent, startdato, sluttdato, jobb-e-post, leder_id | 15 | Innsyn (art. 15), lagringstid etter fratredelse, hvem som får se hva |
| A2 | `vakter.csv` | vakt_id, ansatt_id, dato, start, slutt, stasjon (sal/kafé/skranke) | ca. 8 uker | Kobling mot A1. Ufarlig data som likevel er persondata. |
| A3 | `kurs_sertifikater.csv` | ansatt_id, kurs (brannvern, hygiene, skjenking), dato, gyldig_til | ca. 30 | Kobles til tilsynskalenderen. Gir en lavrisiko-automatisering: «hvem må fornye kurs før mars?» |
| A4 | `fravaer_karantene.csv` *(fase 2)* | ansatt_id, fra, til, type (bare «karantene IK-Mat», ingen diagnose) | ca. 5 | **Særlig kategori** (helse). Øver på strengere tilgang og kortere lagringstid. Bevisst vanskelig case. |

**Med vilje utelatt:** fødselsnummer, kontonummer, lønn og privatadresse. Lønn kjøres hos en ekstern leverandør (databehandler), og museet trenger ikke disse feltene for det agentene gjør. Det er i seg selv en læringsbit.

### 2b. Kunder og publikum

| # | Datasett | Felt (forslag) | Antall | Øvelsen det gir |
| :--- | :--- | :--- | :--- | :--- |
| K1 | `kontakter.csv` | kontakt_id, navn, e-post, nyhetsbrev_samtykke (ja/nei), samtykke_dato, samtykke_kilde, trukket_dato | ca. 120 | Samtykke (art. 6.1 a), tilbaketrekking, sletting (art. 17) |
| K2 | `pameldinger.csv` | pamelding_id, hendelse_id (1–8 fra `museum.db`), kontakt_id, antall_voksne, antall_barn, betalt, dato | ca. 80 | Avtale som grunnlag (6.1 b). Kapasitetssjekk mot `maks_deltakere`. **Barn registreres bare som antall, aldri med navn.** |
| K3 | `skolebestillinger.csv` | bestilling_id, skole, kontaktlærer, jobb-e-post, klassetrinn, antall_elever, dato | ca. 10 | Persondata i jobbrolle. Ingen elevnavn. |
| K4 | `utleie.csv` | forespørsel_id, type (privat/bedrift), kontaktperson, dato, status | ca. 5 | Privatperson eller bedrift gir ulikt vern. |
| K5 | `henvendelser.csv` | henvendelse_id, tidspunkt, kanal (CLI/Telegram), fritekst, kategori | ca. 40 | **Den viktigste.** Noen meldinger inneholder «uønsket» persondata («jeg heter … og mistet lommeboka i Sal C»). Øvelsen er å vaske logger før de brukes som treningsdata, altså å håndheve regel 3 i praksis. |

**Med vilje utelatt:** billettkjøp per person (anonymt kjøp i kassa holder, tall kan aggregeres), kortdata (det skal aldri finnes, selv ikke fiktivt) og kameraovervåking (kan bli et eget case senere).

### 2c. GDPR-metadata (lages først)

| Fil | Innhold |
| :--- | :--- |
| `behandlingsprotokoll.yaml` | Én oppføring per datasett over: formål, rettslig grunnlag, kategorier, lagringstid, hvilke agentroller som har tilgang, databehandler. Dette er protokollen GDPR art. 30 krever. |
| `ovelser.md` | 4–5 ferdige scenarioer: innsynsbegjæring, sletteforespørsel, trukket samtykke, avvik (vaktliste sendt til feil person, 72-timersfristen etter art. 33). |

---

## 3. Teknisk oppsett (vurdering)

- **Plassering:** `05_data/persondata/`, **ikke** i `museum.db`. MCP-serveren og museumsverten leser `museum.db`, og persondata der kan lekke ut i svar til publikum.
- **Generert med skript, ikke håndskrevet:** Et lite Python-skript med fast seed lager alle filene. Da kan alt lages på nytt, slettes og testes.
- **Tydelig fiktivt:**
  - Alle e-poster slutter på `@eksempel.invalid`. Domenet `.invalid` er reservert og kan aldri bli en ekte adresse.
  - Telefonnumre i et åpenbart falskt format.
  - Hver fil har en `FIKTIV`-merking.
- **Navn:** Vanlige norske fornavn og etternavn kombinert tilfeldig. Noen vil kunne hete det samme som en ekte person. Det kan ikke unngås og er lite risikabelt når alt er merket fiktivt. Ingen av gründerne brukes som eksempel.
- **Tester (pytest):**
  1. Ingen e-post utenfor `@eksempel.invalid`.
  2. MCP-serveren refererer ikke til `persondata/`.
  3. Ingen påmelding overstiger `maks_deltakere`.
  4. Ingen poster er eldre enn lagringstiden i protokollen. Denne testen er selve automatiseringsøvelsen.
- **`tool_access.md`** får en ny rad for persondata: Driftsansvarlig ser A1–A3, Direktør ser bare tall, Museumsvert ser ingenting.

---

## 4. Anbefalt rekkefølge (forslag)

| Steg | Innhold | Hvorfor |
| :--- | :--- | :--- |
| **1. MVP** | Behandlingsprotokoll + A1 `ansatte` + K2 `pameldinger` (med K1 `kontakter`) + K5 `henvendelser` | Tre ulike typer øvelser (ansatt, kunde, loggvask) med minst mulig data |
| 2 | A2, A3, K3, K4 + `ovelser.md` | Bygger videre når MVP-en er prøvd |
| 3 | A4 (helse) | Først når tilgangsstyring fra steg 1 fungerer |

---

## 5. Åpne spørsmål til gründerne

1. **Hva skal dere øve på først:** å svare på henvendelser (innsyn og sletting), eller å bygge automatisering (slettefrister og loggvask)? Svaret avgjør om steg 1 vektlegger `ovelser.md` eller testene.
2. **Skal persondataene i repoet ligge åpent** (de er fiktive), eller i en egen mappe utenfor git? Anbefaling: i repoet, siden de er fiktive, merket og generert.
3. **Navnet:** Repoet bruker både «Kunstpixel» og «Aura Kunstmuseum» om virksomheten. Hvilket navn skal stå i behandlingsprotokollen?

---

### Kontrollert / ikke kontrollert
- **Kontrollert:** Innholdet i alle tabeller i `museum.db` (lest i skrivebeskyttet modus), filene i `05_data/governance/`, `03_team/` og `04_knowledge/04_domain/core|operations|risks|decisions`.
- **Ikke kontrollert:** `arkiv/` er bare søkt etter «gdpr/personvern» og ikke lest i sin helhet. Testpakken er ikke kjørt, fordi ingen kode er endret.
- **Bør verifiseres:** De foreslåtte lagringstidene og rettslige grunnlagene i protokollen bør sjekkes mot Datatilsynets veiledning før de brukes i undervisning.
