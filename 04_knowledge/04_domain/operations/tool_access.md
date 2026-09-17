# Verktøytilganger og MCP-grenser (Tool Access)

For å opprettholde sikkerhet og ryddighet gjelder prinsippet om **minste privilegium** (least privilege) for alle agenter og plugins:

| Agent / Rolle | Tillatte MCP-verktøy | Tillatte handlinger | Forbudte handlinger |
| :--- | :--- | :--- | :--- |
| **Museumsdirektør** | `plane_*`, `calendar_*`, `db_read` | Lese status, opprette oppgaver, delegere | Direkte sletting av verksdata |
| **Samlingsforvalter** | `sqlite_read`, `sqlite_write`, `filesystem_local` | Søke, opprette og oppdatere verksdata | Offentlig publisering uten godkjenning |
| **Kurator** | `sqlite_read`, `web_search` (kunstfag), `file_write` | Søke i samling, hente kunstkilder, skrive utkast | Endre fysisk plassering uten logg |
| **Formidler** | `sqlite_read`, `file_read`, `file_write` | Lese verksfakta, skrive veggtekster/audiomanus | Dikte opp biografiske data / årstall |
| **Museumsvert** | `sqlite_read_public`, `faq_search` | Søke åpne verk, vise salplassering, besvare FAQ | Skrive til samlingsdatabase, endre priser |
| **Driftsansvarlig** | `calendar_*`, `ticket_read`, `plane_*` | Se kapasitet, logge driftsoppgaver | Slette historiske logger |

## Sikkerhetsregler for plugins
1. **Skrivebeskyttelse av samling:** Skrivekall mot samlingsdatabasen krever validering av obligatoriske felt (inventarnummer, tittel, kunstner, datering).
2. **Ingen rå SQL fra åpne promptflater:** Offentlige henvendelser (museumsvert) benytter kun forhåndsdefinerte, parameteriserte funksjonskall (`search_artwork_by_title`, `get_artworks_by_room`), aldri fri SQL.
3. **Ingen persondata i treningsdata:** Syntetiske henvendelser og besøksdata skal være fri for ekte personopplysninger.
