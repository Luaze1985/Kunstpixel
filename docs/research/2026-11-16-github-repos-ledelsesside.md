# Hva gjør andre? 74 GitHub-repoer om ledelsessider, museer, HR/HMS og KI over data

*Research 2026-11-16. Fire subagenter, hver sitt segment, kun lesing via `gh api` og dokumentasjon. Stjerner og «sist pushet» er målt samme dag. Bygger videre på [ledelsesside-innhold](2026-11-16-ledelsesside-innhold.md).*

| Segment | Repoer | Typiske eksempler |
|---|---|---|
| Dashboards, BI og admin-maler | 21 | Metabase, Superset, Grafana, Redash, Rill, Evidence, react-admin, Tabler, Huly |
| Museer og samlingsforvaltning | 18 | CollectiveAccess, CollectionSpace, Specify, Omeka, Arches, ResourceSpace, AtoM |
| HR, vakter, HMS-avvik, billett | 20 | OrangeHRM, Frappe HRMS, Odoo, OCA management-system, urlaubsverwaltung, Kimai, pretix |
| KI over data (text-to-SQL, copiloter, MCP) | 18 | Vanna, WrenAI, DB-GPT, Metabot, Lightdash AI, datasette-mcp, dbt-mcp, Cube |

Metabase, Superset og Lightdash er sett fra to vinkler. Det gir 77 gjennomganger og omtrent 74 unike repoer.

**Forbehold:** «ikke funnet» betyr ikke funnet i filene som ble lest. Ingenting er kjørt. Flere KI-funksjoner er ikke åpen kildekode (Lightdash `ee/`, Metabot verified, Cube Cloud). Ideene kan lånes, men ikke koden.

---

## 1. Hva går igjen på tvers av alle fire segmentene

| # | Mønster | Hvor ofte | Hvem gjør det |
|---|---|---|---|
| 1 | **Forside med tellekort / KPI-kort** | 25+ | Nesten alle. Dashboards (8 med sammenligning), HR (11), museum (7) |
| 2 | **Tallet er en lenke til radene bak** | 8 | Metabase, Superset, Lightdash, Grafana, react-admin, refine, Specify, Superset MCP |
| 3 | **Sammenligning mot forrige periode eller mål**, ofte med «lavere er bra»-flagg | 8 | Evidence (`compare_vs`, `down_is_good`), Superset, Metabase, Redash, Rill, refine, Tabler, CoreUI |
| 4 | **Farge etter terskel, og «ukjent» som egen tilstand** | 9 | Grafana (NoData/Error), Redash (UNKNOWN), Superset, Evidence, Tabler, Tremor, Appsmith, Horilla, SafetyMP («0» ≠ «—») |
| 5 | **Status- eller faseflyt for saker og avvik** | 7 | OCA, SafetyMP, Odoo, Horilla, Frappe, Frappe Helpdesk, urlaubsverwaltung |
| 6 | **Frister regnet fra dato + regel, vist relativt til i dag** | 10 | CollectiveAccess, Specify, Heratio, pixeltable, Horilla, Frappe Helpdesk, OCA, SafetyMP, Odoo, urlaubsverwaltung |
| 7 | **Sperre mot doble påminnelser** (flagg eller purreintervall) | 5 | urlaubsverwaltung, Odoo, esyfovarsel, CollectiveAccess, Heratio |
| 8 | **«Mine handlinger»: én samlet kø med antall** | 6 | OrangeHRM «My Actions», ResourceSpace, Huly Planner, Tabler «Tasks due», SafetyMP «Your work», Plane |
| 9 | **Handling fra en rad** (lenke, knapp, eksport) | 10 | NocoDB, Appsmith, Budibase, ToolJet, Grafana, Metabase, refine, react-admin, Superset/Lightdash (CSV) |
| 10 | **Tilstand i URL / permalenke** | 4 | Grafana, Rill, Redash, react-admin. Metabase og Lightdash gjør det **ikke**, og får dermed problemer med deling |
| 11 | **E-post fra faste maler med plassholdere** | 5 | CollectiveAccess, CollectionSpace, Arches, ResourceSpace, Heratio |
| 12 | **Revisjonsspor (gammel → ny verdi)** | 7 | CollectiveAccess, Arches, AtoM, Specify, ResourceSpace, Heratio, SafetyMP |
| 13 | **KI over data** | 11 + 18 | Mest «bygg spørring med KI». **Fri SQL er standard i 12 av 18 KI-repoer.** |

**De tre viktigste funnene:**

1. **Forsiden svarer sjelden på «hva må jeg gjøre i dag?».** Museumssystemene viser «nylig endret» (CollectionSpace, Omeka). BI-verktøyene viser tall. Bare noen få har en handlingskø med frister: OrangeHRM, Tabler, Huly og SafetyMP. Her kan Datafinner skille seg ut.
2. **Ingen har norske sykefraværsfrister.** Det nærmeste er urlaubsverwaltung med sitt sykelønnsvarsel. Uke 4 og uke 7 må vi lage selv, og mønsteret finnes.
3. **Ingen av de 18 KI-repoene sjekker tallene i KI-teksten mot verktøysvaret** mens programmet kjører. Datafinners faktasjekk og hviteliste er strengere enn standardoppsettet i alle 18. Det er en styrke vi bør vise fram, ikke bygge bort.

---

## 2. Det beste i hvert segment (med kode å se på)

| Hva | Beste eksempel | Hvorfor | Lenke |
|---|---|---|---|
| Fra tall til rader | **Specify 7** | Hvert tall er en navngitt, lagret spørring. Klikk åpner nettopp den. Tallet og fasiten henger sammen. | [StatsSpec.tsx](https://github.com/specify/specify7/blob/HEAD/specifyweb/frontend/js_src/lib/components/Statistics/StatsSpec.tsx) |
| Fra tall til rader, med filter i URL | **react-admin-demo** | Kortet «Pending reviews» lenker til `/reviews?filter={"status":"pending"}`. Tilbake og permalenke virker uten ekstra kode. | [PendingReviews.tsx](https://github.com/marmelab/react-admin/blob/master/examples/demo/src/dashboard/PendingReviews.tsx) |
| Sammenligning | **Evidence BigValue** | `compare_vs` = forrige periode, forrige år, mål eller benchmark. `down_is_good` for avvik. Teksten lages automatisk. | [schema.ts](https://github.com/evidence-dev/evidence/blob/main/core/src/user-components/tags/bigvalue/schema.ts) |
| Frister og purring | **CollectiveAccess** | Skiller «kommer til forfall» (7 dager før) fra «forfalt», har fast purreintervall og maler med plassholdere, alt i én konfigurasjonsfil. | [library_services.conf](https://github.com/collectiveaccess/providence/blob/HEAD/app/conf/library_services.conf) |
| Sykefraværsfrist | **urlaubsverwaltung** | Startdato + N dager, varsel X dager før, flagg mot dobbel utsending. Startdatoen telles med, og det står eksplisitt i koden. Kolleger ser bare fravær, ikke årsak. | [SickNoteMailService.java](https://github.com/urlaubsverwaltung/urlaubsverwaltung/blob/HEAD/src/main/java/org/synyx/urlaubsverwaltung/sicknote/sicknote/SickNoteMailService.java) |
| Avviksflyt | **OCA management-system** | Kan ikke lukkes uten evaluering og uten at alle tiltak er lukket. Tiltak har ansvarlig, frist og type. | [mgmtsystem_nonconformity.py](https://github.com/OCA/management-system/blob/HEAD/mgmtsystem_nonconformity/models/mgmtsystem_nonconformity.py) |
| Lederforside | **SafetyMP (EHS-konsoll)** | Fire tall, «0» ≠ «—», «Tall per kl. HH:MM», én primær neste handling. KI foreslår, mennesket lukker. (Umodent prosjekt med 9 ★, men god dokumentasjon.) | [user-manual-ehs-console.md](https://github.com/SafetyMP/Autonomous-EHS-Management/blob/HEAD/docs/user-manual-ehs-console.md) |
| Frister som liste | **Tabler «Tasks due»** og **Huly Planner** | Tellemerke, avkrysning, forfall «I dag/I morgen/dato» og farget prikk. Ren HTML/Bootstrap. | [TasksDue.astro](https://github.com/tabler/tabler/blob/main/shared/components/cards/TasksDue.astro) |
| KI med hviteliste | **datasette-mcp** | Ferdigskrevne spørringer (canned queries) som verktøy, tilgangssjekk per kall, SQLite. Det som ligner Datafinner mest. | [README](https://github.com/datasette/datasette-mcp) |
| Test av KI | **dbt-mcp evals** og **Cube evals** | Tester at KI valgte **riktig verktøy med riktige argumenter**. Cube har pass/fail/review/error. | [test_eval_semantic_layer.py](https://github.com/dbt-labs/dbt-mcp/blob/main/evals/semantic_layer/test_eval_semantic_layer.py) |
| «Spør KI om dette» | **Lightdash AI** | En graf eller et dashboard festes som kontekst. Oppfølgingsknapper får bare bruke felt som finnes. Startspørsmål vises først når et menneske har verifisert flere enn 6. (Source-available.) | [suggestionGenerator.ts](https://github.com/lightdash/lightdash/blob/main/packages/backend/src/ee/services/ai/agents/suggestionGenerator.ts) |
| KI-svar lenker til appen | **Superset MCP** | Verktøybeskrivelsen krever «MUST display chart URL». Forhåndsvisning er standard, og noe lagres bare når brukeren ber om det. | [generate_chart.py](https://github.com/apache/superset/blob/master/superset/mcp_service/chart/tool/generate_chart.py) |

---

## 3. Anbefaling for Datafinner, koblet til etappene

### Etappe 2: «I dag / Denne uka»
- **Kort med tall, Δ og %, mot normalt.** «Normalt» er snittet for samme ukedag de siste 4 ukene, regnet i Python. Hvert måltall får flagget `lavere_er_bra` (avvik og hendelser). *(Evidence, Superset)*
- **Fire statuser: Normal, Følg med, Over terskel og Ukjent.** Vis aldri grønt ved tomt svar. «0» betyr null, «—» betyr at data mangler. Linje øverst: «Tall per 16.11 kl. 08:02». *(Redash, Grafana, SafetyMP)*
- **Hvert tall er en lenke med filteret i adressen** til radene bak. Vi har allerede `#…?args&rad=` fra etappe 1. *(react-admin, Specify)*
- **Dager uten besøk fylles inn** (rekursiv CTE i SQLite), så snittet blir riktig. *(Hi.Events)*

### Etappe 3: «Mine frister» og handlinger
- **Frister regnes ut, ikke lagres:** startdato + regel fra en liten regeltabell (`frist_type`, `dager_etter_start`, `varsle_dager_foer`). Uke 4 og 7 for sykefravær, tilstandskontroll (`neste_kontroll`, ellers siste + intervall) og innlån. *(urlaubsverwaltung, Heratio, CollectiveAccess)*
- **Grupper i Forfalt, I dag, Denne uka, Senere og Ferdig.** Tellemerke i menyen og farget prikk. *(Tabler, Huly, Horilla)*
- **E-postutkast fra fast mal.** Fakta settes inn fra SQLite. KI kan bare pusse språket, og faktasjekken verner tallene. Vis aldri årsak eller diagnose, bare fristtype og dato. *(CollectiveAccess, urlaubsverwaltung)*
- **Ett flagg «fulgt opp»** i nettleseren hindrer at samme påminnelse vises to ganger. *(urlaubsverwaltung, Odoo)*
- **Enkel avviksflyt hvis vi vil ha den:** Meldt → Under behandling → Lukket. Lukking krever evaluering. *(OCA, forenklet)*

### Etappe 4: KI og kvalitet
- **Fasitsett per rolle:** spørsmål → forventet verktøy + argumenter + tall. Utfallene er pass, fail, review eller error. Knappen «Legg til i testsett» fra en samtale. *(dbt-mcp, Cube, Lightdash)*
- **Godkjent «AI-forslag» blir eksempel.** Ferdige spørsmål per rolle hentes bare fra godkjente svar. *(Dataherald, Lightdash)*
- **KI-svar får en lenke laget av koden** (verktøy + argumenter → rapportadresse), ikke av KI. *(Superset)*
- **Valgfri streng modus der KI ikke ser tallene.** KI beskriver, og tallene vises fra verktøyet. *(DataLine, Lightdash)*
- **Ordliste for begreper** (hva «besøk», «betalende» og «avvik» betyr). Bruk Kulturdirektoratets definisjoner. *(Metabot glossary, WrenAI MDL)*

## 4. Unngå

1. **Fri SQL, også med vern.** Prefikssjekk, blokklister og «ikke skriv DML» i prompten er eneste vern i flere repoer. Behold hvitelisten.
2. **LLM-konfidens vist som «tillit».** Bruk bare deterministiske merker: «tall bekreftet mot verktøy» eller «godkjent av person».
3. **Automatisk utsending og planlagte jobber** (Superset krever Celery, headless browser og SMTP). Regn ut status når siden lastes, og lag bare utkast.
4. **Filtre som ikke ligger i URL** (Metabase, Lightdash). Det knekker tilbake-knappen og fasitlenkene.
5. **Generelle «ved endring → send e-post»-regler** (Horilla) og frie arbeidsflytmotorer. De er vanskelige å etterprøve.
6. **Tung stakk og døde prosjekter som mal:** Kafka, Elasticsearch og Jasper, Sentrifugo (2017), Footfall (2019), TimeTrex (2018).
7. **Forside som bare viser «nylig endret».** Den svarer ikke på hva lederen skal gjøre.
8. **Automatisk læring av «vellykkede» KI-svar uten et menneske imellom** (Vanna auto-train).

## 5. Fakta, tolkning og råd

- **Fakta:** funksjonene i tabellene over er sett i kode eller dokumentasjon. Merket i delrapportene: (K) = kode, (R) = README.
- **Tolkning:** at «handlingskø med frister» er det som mangler mest i feltet. Det bygger på at bare 6 av 74 har det.
- **Råd:** rekkefølgen i del 3. Lars avgjør.

## Repoliste (alle 74)

**Dashboards og admin (21):** [metabase](https://github.com/metabase/metabase) · [superset](https://github.com/apache/superset) · [redash](https://github.com/getredash/redash) · [grafana](https://github.com/grafana/grafana) · [lightdash](https://github.com/lightdash/lightdash) · [evidence](https://github.com/evidence-dev/evidence) · [rill](https://github.com/rilldata/rill) · [appsmith](https://github.com/appsmithorg/appsmith) · [budibase](https://github.com/Budibase/budibase) · [ToolJet](https://github.com/ToolJet/ToolJet) · [nocodb](https://github.com/nocodb/nocodb) · [baserow](https://github.com/baserow/baserow) · [refine](https://github.com/refinedev/refine) · [react-admin](https://github.com/marmelab/react-admin) · [tabler](https://github.com/tabler/tabler) · [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) · [coreui](https://github.com/coreui/coreui-free-bootstrap-admin-template) · [tremor](https://github.com/tremorlabs/tremor) · [plane](https://github.com/makeplane/plane) · [focalboard](https://github.com/mattermost-community/focalboard) · [huly](https://github.com/hcengineering/platform)

**Museer og samlinger (18):** [CollectiveAccess providence](https://github.com/collectiveaccess/providence) · [CollectionSpace services](https://github.com/collectionspace/services) / [cspace-ui.js](https://github.com/collectionspace/cspace-ui.js) · [omeka-s](https://github.com/omeka/omeka-s) · [Omeka Classic](https://github.com/omeka/Omeka) · [arches](https://github.com/archesproject/arches) · [specify7](https://github.com/specify/specify7) · [islandora](https://github.com/Islandora/islandora) · [archivematica](https://github.com/artefactual/archivematica) · [atom](https://github.com/artefactual/atom) · [resourcespace](https://github.com/resourcespace/resourcespace) · [arctos-chatbot](https://github.com/ArctosDB/arctos-chatbot) · [heratio](https://github.com/ArchiveHeritageGroup/heratio) · [Curatix](https://github.com/Eng-MohammadAlShahrour/Curatix-FullStack-SpringBoot-Angular-PostgreSQL-Docker-Tailwind) · [pixeltable-museum-loans](https://github.com/pierrebrunelle/pixeltable-museum-loans) · [museum-inventory-reader](https://github.com/sebastianruffberlin/museum-inventory-reader) · [ham-dashboard](https://github.com/harvardartmuseums/ham-dashboard) · [Museum_Dashboard_Project](https://github.com/holga24/Museum_Dashboard_Project) · [DiMu-API-documentation](https://github.com/nasjonalmuseet/DiMu-API-documentation)

**HR, HMS og billett (20):** [orangehrm](https://github.com/orangehrm/orangehrm) · [frappe/hrms](https://github.com/frappe/hrms) · [frappe/helpdesk](https://github.com/frappe/helpdesk) · [odoo](https://github.com/odoo/odoo) · [OCA/management-system](https://github.com/OCA/management-system) · [horilla](https://github.com/horilla/horilla-hr) · [icehrm](https://github.com/gamonoid/icehrm) · [kimai](https://github.com/kimai/kimai) · [timetrex (speil)](https://github.com/aydancoskun/timetrex-community-edition) · [urlaubsverwaltung](https://github.com/urlaubsverwaltung/urlaubsverwaltung) · [engelsystem](https://github.com/engelsystem/engelsystem) · [SafetyMP EHS](https://github.com/SafetyMP/Autonomous-EHS-Management) · [pretix](https://github.com/pretix/pretix) · [Hi.Events](https://github.com/HiEventsDev/Hi.Events) · [Attendize](https://github.com/Attendize/Attendize) · [Footfall](https://github.com/WatershedArts/Footfall) · [tcedi-ovms](https://github.com/tcedi/tcedi-ovms) · [navikt/esyfovarsel](https://github.com/navikt/esyfovarsel) + [syfomodiaperson](https://github.com/navikt/syfomodiaperson) · [sentrifugo](https://github.com/Sentrifugo/sentrifugo) · [timeoff-management](https://github.com/timeoff-management/timeoff-management-application)

**KI over data (18):** [vanna](https://github.com/vanna-ai/vanna) · [WrenAI](https://github.com/Canner/WrenAI) · [DB-GPT](https://github.com/eosphoros-ai/DB-GPT) · [dataherald](https://github.com/Dataherald/dataherald) · [pandas-ai](https://github.com/sinaptik-ai/pandas-ai) · [Chat2DB](https://github.com/OtterMind/Chat2DB) · Metabase Metabot · Superset MCP · [dataline](https://github.com/RamiAwar/dataline) · [cube](https://github.com/cube-js/cube) · [dbt-mcp](https://github.com/dbt-labs/dbt-mcp) · Lightdash AI · [datasette-mcp](https://github.com/datasette/datasette-mcp) · [MCP sqlite (arkivert)](https://github.com/modelcontextprotocol/servers-archived) · [sqlite-explorer-mcp](https://github.com/hannesrudolph/sqlite-explorer-fastmcp-mcp-server) · [langchain-community SQL](https://github.com/langchain-ai/langchain-community) · [llama_index NLSQL](https://github.com/run-llama/llama_index) · [sqlcoder](https://github.com/defog-ai/sqlcoder) / [sql-eval](https://github.com/defog-ai/sql-eval)
