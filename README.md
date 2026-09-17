# Aura Kunstmuseum — Demo-Prototype

> **En operativ syntetisk SMB-kulturinstitusjon og treningsarena for AI-gründere.**  
> Verifiserer at bedriftskontekst, agentroller, MCP-verktøy og samlingsdatabaser fungerer helhetlig i praksis («Bedriften virker»).

---

## 1. Arkitektur og Systemoversikt

Aura Kunstmuseum er bygget opp som en komplett, trelags arkitektur med Model Context Protocol (MCP) som integrasjonslag og en spesialisert museumsvert-agent som publikumsgrensesnitt:

```
┌─────────────────────────────────────────────────────────────┐
│                    Museumsbesøkende                         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Brukerdialog / Terminal CLI
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Museumsvert-Agent (`src/agent.py`)             │
│  - Masterprompt: `prompts/museumsvert.md`                   │
│  - Væremåte: Varm, entusiastisk, ikke-akademisk vertskap   │
│  - Anti-hallusinasjon: Kun verifiserte fakta fra databasen  │
│  - 4-trinns svarmal: Svar → Detalj → Retning → Forslag      │
│  - Sikkerhet: Strikt read-only, ingen rå SQL                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameteriserte verktøykall
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Aura MCP Server (`src/mcp_server.py`)            │
│  1. `search_collection`     2. `get_artwork_details`        │
│  3. `get_room_artworks`     4. `search_events`              │
│  5. `search_faq`                                            │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameteriserte SQL-spørringer
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Helper (`src/db.py`)                  │
│  - Konfigurasjonshierarki (`AURA_DB_PATH` -> lokal mirror)  │
│  - Norsk tegnstøtte & sikker validering (`mode=ro`)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLite Connection (URI mode=ro)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            SQLite Database (72 rader, 7 tabeller)           │
│  `kunstnere` (12), `saler` (6), `verk` (16),                │
│  `utstillinger` (3), `utstilling_verk` (15),                │
│  `hendelser` (8), `publikum_faq` (12)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Komponenter

| Komponent | Filsti | Beskrivelse |
|---|---|---|
| **Data Layer** | `data/museum.db`, `src/config.py`, `src/db.py` | SQLite-database med 72 rader og `src/db.py` som tilbyr parameteriserte, injeksjonssikre spørringer med norsk tegnnormalisering. |
| **MCP Server** | `src/mcp_server.py` | FastMCP-server som eksponerer de 5 samlingsverktøyene i henhold til Model Context Protocol. |
| **Museumsvert Agent** | `src/agent.py` | Full implementasjon av `MuseumsvertAgent` og `AgentResponse` med intensjonsruting, 4-trinns svarmal og strikt read-only sikkerhet. |
| **Interaktiv CLI** | `src/cli.py` | Lekker terminaldialog bygget med `rich` for publikumssamtaler med museumsverten. |
| **Automatisert Testsuite** | `tests/` | 4-lags testsuite (Tiers 1–4) med 65 verifiserbare tester. |

---

## 3. Forutsetninger og Installasjon

Kjøretidsmiljøet krever **Python 3.13**:

```powershell
# 1. Bekreft Python 3.13
py -3.13 --version

# 2. Installer nødvendige pakker
py -3.13 -m pip install pytest mcp rich
```

---

## 4. Hurtigstart (Quickstart)

### 4.1 Kjøre den interaktive museumsverten (CLI)

Start den interaktive terminaldialogen:

```powershell
py -3.13 src/cli.py
```

Du kan også sende inn et enkeltspørsmål direkte fra kommandolinjen:

```powershell
py -3.13 src/cli.py "Hvor finner jeg Skrik?"
py -3.13 src/cli.py "Hva anbefaler du hvis jeg har 30 minutter?"
py -3.13 src/cli.py "Hva koster det for en student og en voksen?"
```

For oversikt over saler og funksjoner:

```powershell
py -3.13 src/cli.py --help
```

### 4.2 Kjøre FastMCP-serveren

Start MCP-serveren over standard I/O (JSON-RPC):

```powershell
py -3.13 src/mcp_server.py
```

### 4.3 Kjøre E2E-testpakken

Kjør samtlige 65 tester på tvers av Tier 1–4:

```powershell
py -3.13 -m pytest -v
```

Kjør spesifikke testlag:

```powershell
# Tier 1: Datakvalitet og kuratoriske regler (23 tester)
py -3.13 -m pytest tests/test_db_quality.py -v

# Tier 2: MCP Server samlingsverktøy (18 tester)
py -3.13 -m pytest tests/test_mcp_server.py -v

# Tier 3: Museumsvert-agentens persona og adferd (10 tester)
py -3.13 -m pytest tests/test_agent.py -v

# Tier 4: E2E Helhetlig bedriftsintegrasjon & scenarier (14 tester)
py -3.13 -m pytest tests/test_integration.py -v
```

---

## 5. Samlingsverktøyene (De 5 MCP-verktøyene)

1. **`search_collection(query, artist, title, technique, theme, room_id, limit)`**
   - Fleksibelt søk i museets samling på tvers av kunstnernavn, tittel, teknikk, temaer og sal.
   - Eksempel: Søk etter `Kittelsen` returnerer både *Nøkken* og *Soria Moria slott*.

2. **`get_artwork_details(artwork_id)`**
   - Henter fullstendige metadata, kuratert veggtekst (50–90 ord) og dokumentert proveniens.
   - Returnerer strukturert `code="NOT_FOUND"` ved ukjent ID eller tittel.

3. **`get_room_artworks(room_id)`**
   - Returnerer alle utstilte verk i en gitt sal ordnet etter visningsrekkefølge (`rekkefølge ASC`).
   - Eksempel: `SAL-D` returnerer *Skrik*, *Pikene på broen* og *N. 7 – Stor blå fjellform*.

4. **`search_events(event_type, date_from, date_to, limit)`**
   - Henter kommende arrangementer (omvisninger, verksteder, foredrag) med dato, klokkeslett, sal og billettpriser.
   - Ekskluderer avlyste og historiske hendelser.

5. **`search_faq(query, category)`**
   - Nøkkelordsøk med norsk synonymutvidelse for praktiske publikumsspørsmål.
   - Returnerer konkrete åpningstider og billettpriser i NOK.

---

## 6. Faglige Retningslinjer og Sikkerhet

### 6.1 Låst Terminologi (fra `CONTEXT.md`)
Agenten og formidlingen følger museets offisielle begrepsapparat:
- Bruk **Kunstmuseum** — *aldri* Galleri, kunsthall eller utstillingslokale.
- Bruk **Samling** — *aldri* Varelager, beholdning eller inventar.
- Bruk **Verk** — *aldri* Vare, objekt eller artefakt.
- Bruk **Veggtekst** — *aldri* Skilt, etikett eller produktbeskrivelse.
- Bruk **Museumsvert** — *aldri* Supportagent, helpdesk eller billettselger.

### 6.2 Nulltoleranse for Hallusinasjoner
- Agenten dikter aldri opp kunstnerfakta, årstall, salplasseringer eller billettpriser.
- Ukjente verk eller kunstnere (f.eks. *Mona Lisa*) avkreftes ærlig og høflig med henvisning til museets fokus på norsk kunst.
- Verk som befinner seg i magasin (f.eks. *Brudeferd i Hardanger* i `MAG-1`) anbefales aldri som utstilt.

### 6.3 Strikt Read-Only Sikkerhet
- Museumsvert-agenten har kun lesetilgang til samlingsdatabasen.
- Databasetilkoblingen kjører med SQLite `?mode=ro`.
- Alle skriveoperasjoner (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`) avvises umiddelbart med `PermissionError` på applikasjonsgrensen.
- Ingen fri eller rå SQL tillates fra åpne agentflater.

---

## 7. Status og Verifikasjon (Iterasjon 2 — Remediation)

Etter grundig gjennomgang og remediering i Iterasjon 2 er systemet fullstendig frigjort fra statiske test-fasader og koblet ekte mot MCP-verktøylaget:
- **Ekte MCP-verktøykjøring**: `MuseumsvertAgent` kaller nå verktøyene fra `src/mcp_server.py` via `InProcessMCPClient`.
- **Autentisk `tools_used`-sporing**: `AgentResponse.tools_used` inneholder utelukkende verktøy som faktisk ble eksekvert i løpet av meldingsturnen.
- **Dynamisk faktauttrekk**: Billettpriser, barneaktiviteter, omvisninger og FAQ-svar ekstraheres dynamisk fra databasens poster.
- **Ordgrense- og stoppordsøk i FAQ**: `src/db.py` filtrerer nå ut støy og grammatiske 2-bokstavsord (`se`, `do`, `er`), slik at urelaterte spørsmål aldri feilkobles.

```powershell
py -3.13 -m pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.0.2, pluggy-1.6.0
rootdir: G:\Min disk\Fellesprosjekt KI
configfile: pyproject.toml
testpaths: tests
plugins: logfire-4.35.0, agent-eval-0.2.0, anyio-4.13.0
collected 112 items

tests/test_adversarial_mcp.py ..............................             [ 26%]
tests/test_agent.py ..........                                           [ 35%]
tests/test_challenger_2_adversarial.py .................                 [ 50%]
tests/test_db_quality.py .......................                         [ 71%]
tests/test_integration.py ..............                                 [ 83%]
tests/test_mcp_server.py ..................                              [100%]

============================= 112 passed in 3.10s =============================
```