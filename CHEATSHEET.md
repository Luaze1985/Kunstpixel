# HUSKELAPP FOR LARS (CHEATSHEET)
*Prosjekt: Kunstpixel (Aura Kunstmuseum) | Sist oppdatert: 2026-10-19 kl. 06:40*

## 1. Hva vi gjorde sist
- Etablerte **4 realistiske virksomhetshåndbøker** (Personal, HMS & Sikkerhet, Drift & Kvalitet, Ledelse & Beredskap) og **4 kompakte SOP-er** (Varsling AML § 2 A, Ferie, Fravær/sykefraværsoppfølging, Vaktbytte).
- Bygget to-lags oppslagsarkitektur: Markdown-dokumenter + indeksert tabell `handbok_oppslag` i `museum.db` med FastMCP-verktøy `lookup_handbook` (norsk avbøying og vektet relevans).
- Kjørte benchmark på **30 realistiske søketemaer** (100 % treffsikkerhet) og oppnådde **203 av 203 passerte automatiske tester (100 % pass)**.

## 2. Hvor vi slapp
- Håndbokpakken og oppslagsmotoren er 100 % operative og ferdig testet. Klar for demonstrasjon, produksjonsbruk eller utvidelse mot neste modul.

## 3. Første oppgave neste gang du setter deg ned
- **Demonstrere og teste i terminal/web:** Åpne terminalen og test en vilkårlig regeloppslag med `py -3.13 src/cli.py "Hva er regelen for egenmelding?"`, eller gå videre til neste planlagte delmål.

## 4. Nyttige snarveier for dette prosjektet
- Interaktiv museumsvert: `py -3.13 src/cli.py`
- Test 30 håndbok-søk: `py -3.13 src/kunstpixel/data/benchmark_30_searches.py`
- Kjør full testsuite (203 tester): `py -3.13 -m pytest -v`
- Start FastMCP-server: `py -3.13 src/mcp_server.py`
