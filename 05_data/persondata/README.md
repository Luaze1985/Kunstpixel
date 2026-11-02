# Kundedata for Kunstpixel (syntetisk)

> **FIKTIVE DATA.** Alle kunder, medlemmer og gavekortkjøpere er oppdiktet. Ansatte er hentet fra `hr_ansatte` i `05_data/museum.db`, som også er syntetisk.

## Hvor ligger hva

| Fil | Hva | I git? |
| :--- | :--- | :--- |
| `innstillinger.yaml` | Volum, priser, medlemstyper og fordeler. **Endre her.** | Ja |
| `csv/<tabell>.csv` | Alle kundedata, én fil per tabell. Kan åpnes i Excel. | Ja |
| `persondata.db` | SQLite-database bygd fra innstillingene eller CSV-ene. Brukes av MCP-serveren. | Nei, genereres |

## Kom i gang (Windows/PowerShell)

```powershell
py -3.13 -m pip install -e .
py -3.13 -m src.kunstpixel.persondata.generer
```
