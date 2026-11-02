# Kundedata for Kunstpixel (syntetisk)

> **FIKTIVE DATA.** Alle kunder, medlemmer og gavekortkjøpere er oppdiktet. E-postene ender på `@eksempel.invalid`, og telefonnumrene starter med 0, så ingen av dem kan tilhøre noen. Ansatte er hentet fra `hr_ansatte` i `05_data/museum.db`, som også er syntetisk. Navnene på ansatte er like i begge databasene.

Periode: **2021-11-02 til 2026-11-02** (5 år).

## Hvor ligger hva

| Fil | Hva | I git? |
| :--- | :--- | :--- |
| `innstillinger.yaml` | Volum, priser, medlemstyper og fordeler. **Endre her for nye data.** | Ja |
| `csv/<tabell>.csv` | Alle kundedata, én fil per tabell. Kan åpnes i Excel. **Endre her for å justere enkeltrader.** | Ja |
| `persondata.db` | SQLite-database bygd fra innstillingene eller CSV-ene. Brukes av MCP-serveren. | Nei, genereres |

Koden ligger i `src/kunstpixel/persondata/`, og tabelloppsettet i `schema.sql`.

## Tabellene (full skala, seed 2026)

| Tabell | Rader | Innhold |
| :--- | ---: | :--- |
| `kontakter` | 5 098 | 5 000 kunder og 98 ansatte (`ansatt_id` satt, samme navn og e-post som i `hr_ansatte`) |
| `medlemskapstyper` | 6 | student, enkelt, senior, familie, venn, ansatt, med årspris |
| `fordeler` | 8 | fri inngang, butikk- og kaférabatt, forhåndsvisning, åpninger, gratis omvisning, gjest |
| `medlemskapstype_fordel` | 26 | hvilke typer som har hvilke fordeler |
| `medlemskap` | 4 091 | ett år per rad. Fornyelser peker på forrige rad (`fornyelse_av`). Ca. 780 aktive per 2026-11-02 |
| `medlemsbesok` | 14 376 | besøk per medlem, bare på åpne dager og innenfor `dagsbesok` |
| `fordel_bruk` | 6 000 | bruk av rabatter og fordeler, med rabattbeløp |
| `gavekort` | 1 501 | kode `GK-XXXX-XXXX`, beløp, kjøper, eventuell mottaker, gyldig i 3 år |
| `gavekort_bruk` | 2 554 | innløsninger. Summen er aldri høyere enn beløpet |
| `arrangementer` | 315 | 300 genererte og 15 fra `hendelser` i museum.db |
| `pameldinger` | 2 182 | aldri over kapasiteten. Betalt med kort, Vipps, gavekort eller medlemsfordel |
| `skolebestillinger` | 500 | skole, kontaktlærer og klassetrinn, ingen elevnavn |
| `utleie` | 100 | privat eller bedrift |
| `henvendelser` | 3 000 | spørsmål fra publikum. 5 % inneholder persondata (`inneholder_persondata = 1`) |
| **Totalt** | **39 757** | Bygges på under ett sekund. Databasen er 3,5 MB og CSV-ene 3,3 MB |

Alle ansatt-ID-er (`solgt_av_ansatt_id`, `ansvarlig_ansatt_id`, `besvart_av_ansatt_id`) peker på en ansatt som var i jobb den datoen. Noen poster er med vilje lagret for lenge, som øvingsmateriale for en slettesjekk i fase 2.

## Kom i gang (Windows/PowerShell)

```powershell
py -3.13 -m pip install -e .
py -3.13 -m src.kunstpixel.persondata.generer
```

Hvis databasen eller CSV-ene finnes fra før, stopper kommandoen med en melding i stedet for å overskrive dem.

## Justere data senere

**A. Endre mengde, priser, typer eller fordeler:** rediger `innstillinger.yaml` og kjør:

```powershell
py -3.13 -m src.kunstpixel.persondata.generer --overskriv
```

Dette lager **alle** data på nytt, og CSV-filene overskrives. Endringer du har gjort for hånd i CSV-ene går tapt.

**B. Endre enkeltrader for hånd:** åpne CSV-fila i Excel, gjør endringen, lagre som CSV (semikolondelt, UTF-8) og kjør:

```powershell
py -3.13 -m src.kunstpixel.persondata.generer --fra-csv --overskriv
```

Da bygges databasen fra CSV-ene, så endringene dine blir med.

> Pass på i Excel: telefonnumre som `01234567` mister den første nullen hvis kolonnen tolkes som tall. Datoer kan også bli omformatert. Formater kolonnene som tekst før du lagrer.

## MCP-tilgang (fase 1, ingen tilgangssperrer)

```powershell
py -3.13 src/persondata_mcp.py
```

| Verktøy | Hva |
| :--- | :--- |
| `list_tabeller()` | Alle tabeller med antall rader |
| `beskriv_tabell(tabell)` | Kolonner og 3 eksempelrader |
| `sporring(sql, limit=200)` | Fri SELECT, maks 5 000 rader. `museum.db` er koblet på som `museum` |
| `innsyn_kontakt(kontakt_id)` | Alt som er lagret om én kontakt |
| `gavekort_saldo(kode)` | Beløp, brukt, saldo og kjøper |

Alt er lesetilgang. Skriving avvises.

**Koble til Claude Desktop:** legg dette inn under `mcpServers` i `%APPDATA%\Claude\claude_desktop_config.json`. Bytt ut stien med din egen, og start Claude Desktop på nytt:

```json
"kunstpixel-kundedata": {
  "command": "py",
  "args": ["-3.13", "C:\\sti\\til\\Kunstpixel\\src\\persondata_mcp.py"]
}
```

### Eksempelspørringer

```sql
-- Aktive medlemmer per type i dag
SELECT type, COUNT(*) FROM medlemskap
WHERE startdato <= '2026-11-02' AND sluttdato >= '2026-11-02' GROUP BY type;

-- Ansatte som har solgt flest gavekort
SELECT a.navn, COUNT(*) AS antall FROM gavekort g
JOIN museum.hr_ansatte a ON a.ansatt_id = g.solgt_av_ansatt_id
GROUP BY a.navn ORDER BY antall DESC LIMIT 10;

-- Gavekort med penger igjen som går ut innen 3 måneder
SELECT g.kode, ROUND(g.belop - COALESCE(SUM(b.belop), 0), 2) AS saldo, g.gyldig_til
FROM gavekort g LEFT JOIN gavekort_bruk b USING (gavekort_id)
WHERE g.gyldig_til BETWEEN '2026-11-02' AND '2027-02-02'
GROUP BY g.gavekort_id HAVING saldo > 0;
```
