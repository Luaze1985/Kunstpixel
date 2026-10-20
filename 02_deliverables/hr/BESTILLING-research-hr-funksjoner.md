# Bestilling: Research på HR-funksjoner for privat sektor, industri og kommune
*Fra: Lars Erik Brekne Johnsen (Kunstpixel) · Utarbeidet med Claude Code · 2026-10-20 · Status: klar til research*

---

## Til Lars: hvor du kjører dette

**Anbefaling: gjør researchen *utenfor* VS Code, og byggingen *i* VS Code eller Antigravity.**

| Steg | Hvor | Hvorfor |
|---|---|---|
| 1. Research (denne bestillingen) | En modell med nettsøk og kildehenvisninger: dyp research i Claude, ChatGPT eller Perplexity (du har også `sonar-search`) | Dette er lov, tariff og statistikk som må hentes fra nettet med kilder. En kodeagent i VS Code er laget for filer og kode, ikke for å finne og vurdere kilder |
| 2. Du leser og låser | Deg | Du vet mye om kommune, men mindre om privat sektor og industri. Det er der du må sjekke mest |
| 3. Bygg data og funksjoner | Antigravity som orkestrator, med en kodeagent | Følger oppskriften i `docs/DATAPIPELINE.md` (CSV → bygg → test → statusport) |

**Slik bruker du den:** Lim inn alt fra «Selve bestillingen» og ned i research-modellen. Lagre svaret i `01_inbox/hr-research/` og gi det til Antigravity sammen med `docs/DATAPIPELINE.md`.

---

# Selve bestillingen (lim inn herfra)

## 1. Rolle og formål
Du er en research-assistent med kunnskap om norsk arbeidsliv, HR, lønn og personvern. Du skal lage et **faktagrunnlag med kilder** som jeg bruker til to ting:
1. Lage **realistiske, syntetiske (oppdiktede) HR-data og rapporter** for en øvingsvirksomhet.
2. Bygge funksjoner der en ansatt eller leder kan **søke i en personalhåndbok** og få riktig svar, og der en språkmodell kan gi vurderinger oppå faste regler.

Målgruppene er **industri, private selskaper og kommuner**. Jeg kjenner kommunal sektor godt. Vær særlig grundig på **privat sektor og industri**, og vis hvor de skiller seg fra kommune.

## 2. Det som finnes i dag (bygg videre på dette)
En fiktiv virksomhet (et kunstmuseum, 168 ansatte, seks avdelinger) med syntetiske data i SQLite:
- **Vakter:** 54 994 vakter 2010–2026 med dato, start og slutt, stasjon, avdeling og timer. Noen er forlenget til 9–11 timer (overtid).
- **Ansatte:** stilling, avdeling, stillingsprosent, lønnstrinn (Virke-tariff), ansatt fra og til, STYRK-08-kode.
- **Tariff:** timesatser for ordinær, kveld, helg og helligdag per lønnstrinn. Arbeidstidsgrenser (ukenorm, døgn, kveldstillegg fra kl.).
- **Fravær:** egenmelding, sykemelding og permisjon per ansatt, sammenlignet med SSB sitt sykefravær i kultursektoren.
- **Personalhåndbok:** 27 oppslag med kapittel, lovhjemmel, innhold og stikkord (pluss HMS-, drifts- og lederhåndbok).
- **Regler:** faste regler (felt, operator, terskel) som gir vurdering og forslag, med fallback.
- **Kompetanse:** sertifikater med utløpsdato. Innleie av eksterne med timepris og anskaffelsesprosedyre.

Alt er syntetisk. Det skal ikke brukes ekte personopplysninger.

## 3. Hva jeg trenger: åtte områder
For **hvert område**, lever punkt A–G under. Skill alltid mellom **industri**, **privat (service og kontor)** og **kommune** der reglene eller praksisen er ulik.

1. **Personalhåndbok:** typisk innhold og struktur i privat sektor og industri, sammenlignet med kommune. Hva ansatte oftest leter etter.
2. **Lønn og lønnsarter:** tariffavtaler per sektor (f.eks. Industrioverenskomsten/Verkstedsoverenskomsten, Virke-avtaler, KS Hovedtariffavtale). Tillegg (overtid, skift, natt, helg og helligdag), feriepenger, sykepenger og arbeidsgiverperiode, lønnsslippens oppbygning, arbeidsgiveravgift.
3. **Arbeidstid og bemanning:** arbeidsmiljøloven kap. 10 (ukenorm, overtid, hviletid, nattarbeid, gjennomsnittsberegning), skift og turnus, timeregistrering. Hva som typisk avtales lokalt.
4. **Fravær og oppfølging:** egenmelding og sykemelding, oppfølgingsplan og dialogmøter (frister), permisjoner. Typiske sykefraværstall per næring.
5. **Produktivitet: målinger og grensetilfeller.** Hvilke nøkkeltall som brukes i industri, privat og kommune (f.eks. produktivitet per timeverk, OEE, KOSTRA-indikatorer). Hvor grensen går for lovlig måling og kontroll av ansatte (aml. kap. 9, personvern, Datatilsynet). Grensetilfeller som deltid og overtid, presenteisme, hjemmekontor, og individ- mot gruppemåling.
6. **Innsamling fra ansatte:** medarbeiderundersøkelser og pulsmålinger, medarbeidersamtaler, avviksmeldinger (HMS), varsling (aml. kap. 2 A), kompetansekartlegging. Rettslig grunnlag, anonymitet (minste gruppestørrelse) og hvem som får se hva.
7. **Likelønn og redegjørelse:** aktivitets- og redegjørelsesplikten (likestillings- og diskrimineringsloven § 26), lønnskartlegging per kjønn. Hva som kreves for hvilke virksomhetsstørrelser.
8. **Livsløp:** rekruttering, onboarding, prøvetid, omorganisering, oppsigelse og turnover. Typiske tall for turnover og sykefravær per næring.

### For hvert område, lever:
- **A. Regler** med kilde: lov og paragraf, forskrift, tariffavtale og punkt. Lenke til primærkilde (Lovdata, Arbeidstilsynet, NAV, Datatilsynet, Skatteetaten, KS, NHO/LO, Virke).
- **B. Forskjeller** mellom industri, privat og kommune, i en tabell.
- **C. 10 typiske spørsmål fra ansatte eller ledere**, med kort riktig svar og kilde. Disse blir fasit når jeg tester søk i personalhåndboken. Ta med minst to vanskelige eller tvetydige spørsmål, og si hva som gjør dem vanskelige.
- **D. Realistiske tall** (fordelinger, ikke enkelttall) med kilde og årstall, f.eks. SSB-tabellnummer. Eksempler: sykefravær per næring, andel deltid, overtid, lønnsnivå per yrke, turnover.
- **E. Forslag til syntetiske data:** tabeller og kolonner, type, tillatte verdier eller fordeling, og hvordan de kobles til det som finnes (ansatt-ID, dato, avdeling, lønnstrinn). Bare data som kan begrunnes i A eller D.
- **F. Forslag til faste regler** (felt + operator + terskel → vurdering + forslag, og en fallback), som kan gi vurderinger uten at en språkmodell bestemmer. Eksempel: «overtid siste 4 uker > X timer → …».
- **G. Grensetilfeller og usikkerhet:** hva som avhenger av lokal avtale, hva som er omstridt, hva som nylig er endret, og hva du ikke fant kilde for.

## 4. Kvalitetskrav (viktigst)
- **Ikke finn på** paragrafer, tariffpunkter, tall eller kilder. Finner du det ikke, skriv «Ikke funnet» og hva du søkte etter.
- **Merk hver påstand:** `[Lov/forskrift]`, `[Tariffavtale]`, `[Offisiell statistikk]`, `[Myndighetsveiledning]`, `[Bransjepraksis]` eller `[Antakelse]`.
- **Oppgi dato eller versjon** for regler og tall. Tariffavtaler og satser endres hvert år, så si hvilken periode tallet gjelder.
- Foretrekk **primærkilder**. Blogger og leverandørsider bare som `[Bransjepraksis]`, og aldri som eneste kilde for en regel.
- Skriv på **norsk bokmål**, i klarspråk.

## 5. Leveranseformat
1. **`rapport.md`:** én seksjon per område (1–8) med A–G. Start med et sammendrag på maks 10 linjer.
2. **`datasett_forslag.yaml`:** alle tabellforslag fra punkt E, maskinlesbart:
   ```yaml
   - tabell: overtid_avtaler
     omraade: 3
     kolonner:
       - {navn: ansatt_id, type: tekst, kobles_til: hr_ansatte.ansatt_id}
       - {navn: overtid_timer_uke, type: tall, fordeling: "lognormal, median 2, maks 10", kilde: "aml § 10-6; SSB tabell XXXXX (2025)"}
     sektor: [industri, privat, kommune]
   ```
3. **`regler_forslag.csv`:** alle regler fra punkt F, med kolonnene `regel_id, omraade, felt, operator, terskel, vurdering, forslag, kilde, sektor`. Én fallback-rad per spørsmål (`operator = fallback`). Tekst med komma skal stå i anførselstegn.
4. **`fasit_sporsmal.csv`:** alle spørsmål fra punkt C, med kolonnene `sporsmal_id, omraade, sektor, sporsmal, kort_svar, kilde, vanskelig (ja/nei), hvorfor_vanskelig`.
5. **`kilder.md`:** alle kilder med lenke, utgiver og dato, og hvilket område de støtter.

## 6. Avgrensning
- Ikke skriv kode og ikke lag selve datasettene. Bare grunnlag og forslag.
- Ikke ta med juridisk rådgivning for enkeltsaker. Dette er generelt grunnlag for øvingsdata.
- Prioriter bredde over dybde. Hvert område skal være brukbart, heller enn at ett område er perfekt.

---

## Etter researchen (for Lars og Antigravity, ikke del av bestillingen)
1. **Les og lås:** marker hvilke forslag i `datasett_forslag.yaml` og `regler_forslag.csv` du vil ha. Sjekk særlig privat sektor og industri.
2. **Gi Antigravity:** de låste filene + `docs/DATAPIPELINE.md`. Be om ett datasett om gangen etter oppskriften: generator med egen tilfeldighet → CSV med `datakilde = "syntetisk …"` → `bygg_*` i `build_museum_db.py` → spørring og verktøy → test → statusport. Bare du bygger `museum.db`.
3. **Fasitspørsmålene** (`fasit_sporsmal.csv`) blir testsettet for søk i personalhåndboken: treffer `lookup_handbook` riktig avsnitt for hvert spørsmål?
4. **Reglene** går i en egen regeltabell, slik `rapport_regler` gjør i dag, så vurderingene er deterministiske og en språkmodell bare forklarer dem.
