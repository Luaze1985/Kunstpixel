# Beslutningslogg (Decision Log)

| ID | Dato | Tema | Beslutning | Besluttet av | Referanse |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEC-001** | 2026-09-14 | Konsept & kjerne | Aura Kunstmuseum etableres som et mellomstort, stedsuavhengig kunstmuseum (SMB-skala). | Eier | `CONTEXT.md` |
| **DEC-002** | 2026-09-14 | Organisasjonsform | Forenklet, uavhengig SMB-modell velges for å minimere byråkrati og maksimere læringsverdi for AI-gründere. | Eier | `docs/adr/0001-lean-independent-museum-model.md` |
| **DEC-003** | 2026-09-14 | Første prosjektfokus | Prosjekt «Fra samling til publikum» etableres som første case for MCP-verktøy, innholdsautomatisering og interaktiv museumsvert. | System | `context/projects/samling_til_publikum/brief.md` |
| **DEC-004** | 2026-09-14 | Godkjenningsgrenser | Tredelt godkjenningsmatrise: Nivå 1 (Autonomt), Nivå 2 (Faglig leder), Nivå 3 (Menneskelig eier). | System | `context/core/approval_boundaries.md` |
| **ADR-001** | 2026-10-18 | Operativ styring | Helhetlig operativ triade: Rolleforankring, hard compliance og formidling/publikum/økonomi. | Eier / System | `ADR_001_helhetlig_operativ_triade.md` |
| **ADR-002** | 2026-10-18 | Formidlingsstandard | Samlingen utvides til 50–100 verk med trelags tekststandard (veggtekst, audioguide, barneformidling). | Eier / System | `ADR_002_samlingsomfang_og_tekststandard.md` |
| **ADR-003** | 2026-10-18 | Leverandørmodell | Hybrid modell koblet mot Brreg API for 12 leverandørselskaper og 318 innleiekontrakter. | Eier / System | `ADR_003_hybrid_leverandormodell_brreg.md` |
| **ADR-004** | 2026-10-18 | Databasearkitektur | Slå sammen samling og intern drift til én felles SSOT-database: `05_data/museum.db`. | Eier / System | `ADR_004_konsolidert_database_arkitektur.md` |
| **ADR-005** | 2026-10-18 | Drift & tilstand | Operativ modell for HMS-avvik, konserveringstilstand og utstillingsøkonomi. | Eier / System | `ADR_005_operativ_hendelses_og_tilstandsmodell.md` |
| **ADR-006** | 2026-10-18 | Samling & innlån | 100 verk: 50 faste verk i salene A–D og Magasin 1 + 50 historiske utstillingsinnlån fra ekte museer. | Eier / System | `ADR_006_samlingsomfang_og_utstillingsinnlan.md` |
| **ADR-007** | 2026-10-18 | Anskaffelser & lønn | Doffin/LOA-terskelkategorier for innleie og Virke museumstariff med lønnstrinn og ubekvemstillegg. | Eier / System | `ADR_007_offentlige_anskaffelser_og_virke_tariff.md` |
| **ADR-008** | 2026-10-18 | MCP-tjeneste | Konsolidert FastMCP-server i `src/mcp_server.py` med 6 rollebaserte verktøygrupper. | Eier / System | `ADR_008_konsolidert_fastmcp_tjeneste.md` |
| **ADR-009** | 2026-10-19 | Arbeidstid & AML | AML kap. 10 compliance: 11t daglig hvile, 35t ukentlig hvile og overtidskontroll. | Eier / System | `ADR_009_aml_kap10_arbeidstid_og_hviletid.md` |
| **ADR-010** | 2026-10-19 | Offentlige registre | STYRK-08 yrkeskoder for samtlige stillinger og Arbeidstilsynets Renholdsregister. | Eier / System | `ADR_010_offentlige_registre_styrk08_renhold.md` |
| **ADR-011** | 2026-10-19 | Kalender & HMS | Norsk helligdags- og skolerutekalender (2010–2026), SSB-sykefravær og STAMI-ergonomi. | Eier / System | `ADR_011_kalender_sykefraver_og_stami_ergonomi.md` |
| **ADR-012** | 2026-10-19 | Virksomhetshåndbøker | To-lags arkitektur for Personal, HMS, Drift og Lederhåndbok (Markdown + SQLite/FastMCP). | Eier / System | `ADR_012_virksomhetshandboker_arkitektur.md` |


| **ADR-013** | 2026-10-23 | Internside | Én hovedversjon uten demokopi, åpent hostet, Claude med kostnadsgrense, AI svarer fra dokumentene, arbeidsroller styrer oppslagsverket. | Lars | `ADR_013_internside_hovedversjon_og_ai_oppslag.md` |
