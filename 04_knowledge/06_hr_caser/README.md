# 06_hr_caser – Operative HR- og KI-øvingscaser

Dette området inneholder 14 kvalitetssikrede HR- og etiske øvingscaser for Kunstpixel, tilpasset en moderne museums- og kunstvirksomhet (med referanser til industri, privat sektor og kommune).

Casene tjener tre formål:
1. **Øvingsarena for ansatte og ledere:** Reelle dilemmaer innen arbeidsrett, varsling, fravær og skiftplanlegging.
2. **Grensevern for AI-agenter:** Deterministiske stoppregler mot ulovlig personovervåking (aml. kap. 9), identitetslekkasje ved varsling (aml. kap. 2 A), diagnosegjetting og prompt injections.
3. **Koblede kildereferanser:** Hver case er forankret i museets styringshåndbøker, standardprosedyrer (SOP) og AP9-fasitspørsmål.

---

## Oversikt over Casene og Museumsrelevans

| Case-ID | Tittel | Museumsrelevans | Tema | Kjerne-hjemmel / SOP |
|---|---|---|---|---|
| [`CASE-013`](CASE-013.md) | Varsleren avsløres av den hjelpsomme KI-en | **SVÆRT HØY** | Varsling og personalsak | `SOP-001_rutine_varsling.md` |
| [`CASE-014`](CASE-014.md) | Arbeidsmiljøundersøkelse med tre svar | **SVÆRT HØY** | Psykososialt arbeidsmiljø | `SOP-003_rutine_fravaer_og_sykefravar.md` |
| [`CASE-012`](CASE-012.md) | Sykefraværsradar: bemanning eller diagnose? | **SVÆRT HØY** | Fraværsoppfølging | `SOP-003_rutine_fravaer_og_sykefravar.md` |
| [`CASE-009`](CASE-009.md) | Lønnsgap i et team på fire | **SVÆRT HØY** | Likelønn og analyse | `ADR_007_offentlige_anskaffelser_og_virke_tariff.md` |
| [`CASE-004`](CASE-004.md) | Skiftpress: leveranse eller hviletid? | **SVÆRT HØY** | Bemanningsplanlegging | `SOP-004_rutine_vaktbytte.md` |
| [`CASE-016`](CASE-016.md) | Prompt injection i konfidensiell personalmappe | **HØY** | Informasjonssikkerhet | `ADR_008_konsolidert_fastmcp_tjeneste.md` |
| [`CASE-015`](CASE-015.md) | Turnusoptimalisering eller forskjellsbehandling? | **HØY** | Turnus og arbeidstid | `SOP-004_rutine_vaktbytte.md` |
| [`CASE-017`](CASE-017.md) | HR-eksport til ekstern KI-leverandør | **HØY** | Tredjepartsrisiko | `SOP-002_rutine_ferie.md` |
| [`CASE-005`](CASE-005.md) | Produksjonsdata blir personovervåking | **MIDDELS** | Algoritmisk styring | `ADR_005_operativ_hendelses_og_tilstandsmodell.md` |
| [`CASE-008`](CASE-008.md) | Teams-aktivitet som prestasjonsmål | **MIDDELS** | Kontrolltiltak og prestasjoner | `03_drifts_kvalitetshandbok.md` |
| [`CASE-010`](CASE-010.md) | AI-CV-screening: den skjulte skjevheten | **MIDDELS** | Rekruttering | `SOP_template.md` |
| [`CASE-007`](CASE-007.md) | Kutt i bemanningen: hvem skal ut? | **MIDDELS** | Omstilling og nedbemanning | `01_personalhandbok.md` |
| [`CASE-006`](CASE-006.md) | Kompetansegap og kandidatprofilering | **LAV** | Rekruttering og kvalifisering | `ADR_003_hybrid_leverandormodell_brreg.md` |
| [`CASE-011`](CASE-011.md) | Slutterisiko basert på digitale spor | **LAV** | Beholde kompetanse | `01_personalhandbok.md` |

---

## Særlig Prioriterte Museumscaser (Høyeste Relevans)

1. **[`CASE-013`](CASE-013.md) – Varsleren avsløres av den hjelpsomme KI-en:** Skjerming av varslerens identitet ved henvendelser fra overordnet leder. Forankret i `SOP-001_rutine_varsling.md` og aml. kap 2 A.
2. **[`CASE-014`](CASE-014.md) – Arbeidsmiljøundersøkelse med tre svar:** Vern mot re-identifisering i små museumsteam (Kuratering, Samling). K-anonymitetskrav ($k \ge 5$).
3. **[`CASE-004`](CASE-004.md) – Skiftpress: leveranse eller hviletid:** Overtid og nattarbeid under utstillingsmontering og vernissage. Krav om 11t hviletid (aml. § 10-8).
4. **[`CASE-009`](CASE-009.md) – Lønnsgap i et team på fire:** Likelønnskartlegging (ARP) i små spesialistmiljøer uten å avsløre kollegers individuelle lønn eller fravær.
5. **[`CASE-012`](CASE-012.md) – Sykefraværsradar: bemanning eller diagnose:** Bemanningsprognose uten ulovlig inferens av helseopplysninger eller diagnoser (`SOP-003_rutine_fravaer_og_sykefravar.md`).

---

## Sammenheng med Koden

Koden for å laste, inspisere og evaluere disse casene deterministisk ligger i:
- Modul: [`src/kunstpixel/cases/`](file:///G:/Min%20disk/Kunstpixel/src/kunstpixel/cases/)
- Tester: [`tests/test_hr_cases.py`](file:///G:/Min%20disk/Kunstpixel/tests/test_hr_cases.py)
- CLI-kommandoer: `py -3.13 src/hr_cli.py cases` og `py -3.13 src/hr_cli.py case CASE-013`
