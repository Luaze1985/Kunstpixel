# ADR 008: Konsolidert FastMCP-tjeneste for de 6 rollene

**Status:** Godkjent  
**Dato:** 2026-10-18  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
Hittil har verktøyene vært spredt over to servere: `src/mcp_server.py` (8 samlings- og arkivverktøy) og `src/hr_mcp_server.py` (6 HR/bemanningsverktøy). Med databasesammenslåingen i ADR 004 blir dette unødvendig oppstykket for LLM-klienten.

---

## Beslutning
Vi samler alle verktøy i én felles FastMCP-server i `src/mcp_server.py` strukturert etter de 6 rollene:
1. **Kurator & Formidling:** `search_collection`, `get_artwork_details`, `get_room_artworks`, `get_condition_report`
2. **Samlingsforvaltning & Innlån:** `search_loans`, `check_artwork_climate`
3. **Utstillinger & Arkiv:** `search_archive_exhibitions`, `get_exhibition_economy`
4. **Drift & Sikkerhet:** `search_incidents`, `report_incident`, `check_room_capacity`
5. **HR & Bemanning:** `count_documented_skill`, `propose_kiosk_staffing`, `evaluate_kiosk_proposal`, `get_staff_member`, `calculate_shift_cost`
6. **Økonomi & Anskaffelser:** `search_contractors`, `verify_supplier_brreg`, `check_procurement_threshold`
7. **Publikumsvert:** `search_events`, `search_faq`, `calculate_ticket_price`

---

## Konsekvenser
- Én serverprosess over stdio betjener alle roller.
- Strikt read-only tilgang sikres i `src.kunstpixel.core.db`.
