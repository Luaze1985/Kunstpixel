# Stjele arkitekturmønstre, ikke andres tekniske gjeld

Ved evaluering av store åpen kildekode-prosjekter fra GitHub (som MintHCM på 45 MB PHP) skal gründeren ikke importere hele kodebasen eller sette opp tunge servere. Den fremtidsrettede AI-native tilnærmingen er å hente ut de verdifulle konseptene (strukturerte systemprompter, MCP-kontrollere og dataskjemaer) og implementere dem i ren, deterministisk Python med FastMCP og SQLite.

## Implications
Fremtidige leksjoner og arkitekturvalg skal fokusere på lettvekts standarder (FastMCP over stdio/HTTP) og 0-driftskostnadsdatabaser (`museum.db`), slik at hele riggen forblir rask, etterprøvbar og fri for eksterne rammeverk-avhengigheter.
