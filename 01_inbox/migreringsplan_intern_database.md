# Status og migreringsplan: intern database for Kunstpixel

*Skrevet 2026-10-27. Grunnlaget er det som ligger på disken i dag. Alt er lest, ingenting er skrevet til databasene.*

## Kort fortalt

- Det meste av HR-dataene fra Colab **er allerede flyttet inn** i `museum.db` versjon 4, men på grenen `hr-konsolidering` i hovedmappen. Denne grenen (den intern-assistenten ligger på) vet ikke om dem.
- Vi har **to spor som ikke kjenner hverandre**. Det ene har dataene, og det andre har sikkerhetslaget (datapolicy, faktakontroll, roller og kildevisning). Neste store jobb er å slå dem sammen, ikke å flytte mer data.
- **Alt arbeidet i denne grenen er ikke lagret i git** (0 commits). Det er den største risikoen akkurat nå.
- Grensecase-delen av Colab-databasen (OSINT, skatteliste, helse og fagforening) skal ikke inn i assistentens datagrunnlag. Den skal være et eget, isolert undervisningscase.

## Ærlig vurdering

### Det som er godt

| Del | Status |
|---|---|
| Datagrunnlag på `hr-konsolidering` | `museum.db` v4: 168 ansatte, 54 994 vakter 2010–2026, 3 456 fravær, 318 innleie, 99 håndbokpunkter, kompetanse, tariff, HMS-avvik og helligdager. Bygges deterministisk, og statusporten P1–P6 sier **KLAR** (0 feil, 2 advarsler). |
| Sikkerhetslaget på denne grenen | Datapolicy som stopper ekte data mot ekstern modell, faktakontroll v2 med henvisninger, rollestyring, intern web-chat på port 8001, kostnadstak, prøvesett på 40 spørsmål, gyldne svar og kontroll av syntetisk fyll (H5). Testene består. |
| Kontroll av modellens fyll | Fungerer. Se Colab-kjøringen under. |

### Det som er svakt

1. **To spor.** `hr-konsolidering` er 69 commits foran felles utgangspunkt. Denne grenen har 0 commits og alt arbeid ulagret. Begge har endret `AGENTS.md`, agentfilene og promptene, så sammenslåingen får konflikter. Regelnumrene i `AGENTS.md` er også ulike: «Regel 4» betyr databasekvalitet der og LLM-regelen her.
2. **To syntetiske verdener.** HR- og HMS-pakken her har 24 ansatte med `.example.test`-adresser og direktør Thorvald Berntsen. `museum.db` v4 har 168 ansatte med `kunstpixel.no`-adresser. Assistenten kan ikke stå på begge.
3. **Merkingen passer ikke sammen.** Datapolicyen godtar bare eksakt `syntetisk`. `museum.db` bruker `datakilde = "syntetisk (archive_generator)"` og lignende. Policyen ville derfor tolke alt som ekte og stoppe modellen. Det er trygt, men gjør dataene ubrukelige for LLM til vi lager en tydelig regel for koblingen.
4. **Kontaktdata som kan treffe ekte folk.** `hr_ansatte` i både Colab-databasen og `museum.db` har telefonnumre på formen `+47 9xx xx xx`, som kan være ekte mobilnumre, og e-post på `kunstpixel.no`, som er et domene noen kan eie. Vår egen test `test_nothing_that_looks_like_real_contact_data…` ville avvist dette.
5. **Ekte modell er ikke prøvd.** H4 med ekte modell er ikke kjørt (`STATUS: UNTESTED`), fordi API-nøkkelen mangler.

### Colab-kjøringen av bestillingen (H5) i morges

Modellen i Colab fulgte ikke oppdraget:
- Den **endret faste felt**: avviksfristen for gult avvik fra 14 til 21 dager, og for rødt avvik fra 24 til 12 timer.
- Den satte tilfeldige verdier på `versjon`, `prioritet` og `tidsbruk_timer`.
- Den fylte mange felt med samme tekst via søk og erstatt.
- Den la til en ny fil med roller utenfor listen (Verneombud, Brannvernleder, Konservator).

Den lokale kontrollen ville avvist alt dette som `FAST_FELT_ENDRET`. Det viser at porten trengs. Resultatet lå dessuten i `/content`, som forsvinner når Colab-økten stopper. Bare notatboken ligger på Disk, så det er ingenting å importere.

**Neste gang:** lagre til montert Disk (`/content/drive/MyDrive/...`) eller last ned svaret. Kjør så `py -3.13 tests/kontroller_leveranse.py --importer svar.txt` lokalt.

### Colab-databasen (`05_data/colab_personvern_historikk.db`, 104 MB)

| Tabell | Rader | Allerede i `museum.db` v4? |
|---|---|---|
| `hr_ansatte` | 168 | Ja, identisk innhold |
| `hr_fravaer` | 3 456 | Ja, identisk innhold |
| `vakt_time_for_time` | 439 952 timer (54 994 vakter) | Ja, som `hr_vakter` (54 994) |
| `hr_innleie` | 318 | Ja, men verdiene er ulike. Det må avklares hvilken som er fasit. |
| `avvik_hms` | 34 | Ja, som `avvik_hms_drift` |
| `hr_utvidet_profil_trondheim` | 168 | **Nei**: fødselsnummer, adresse, sivilstand, barn, pårørende, fagforening og helse (art. 9) |
| `ekstern_osint_trondheim` | 168 | **Nei**: skatteliste, formue, verv, habilitet og «mosaikk-risikoscore» |
| `kollektiv_avvik_trondheim` | 4 | Nei |

Databasen har ingen kolonne for `klassifisering`, så datapolicyen tolker alt i den som `ekte`. Det er riktig oppførsel. Tre av 168 syntetiske fødselsnumre består kontrollsifferet og kan dermed være noens ekte nummer. Adressene bruker ekte gatenavn i Trondheim.

## Plan

### M0. Sikre arbeidet (nå, ca. 5 minutter)
- Commit alt i denne grenen (`claude/llm-integration-test-plan-23d83e`). Det krever ditt ja.
- Ikke rør hovedmappen. Det kan gå en annen økt der (statusporten kjørte kl. 07:20).

### M1. Velg én fasit for data (beslutning)
**Anbefaling:** `museum.db` v4 på `hr-konsolidering` blir fasit. Den har mest data, bygges deterministisk og har statusport. Sikkerhetslaget herfra flyttes over dit. HR- og HMS-pakken med 24 ansatte pensjoneres, eller lages på nytt fra v4 hvis vi trenger en zip.

### M2. Slå sammen sporene (1–2 økter)
1. Lag en ny gren fra `hr-konsolidering`, og ta inn denne grenen.
2. Løs konfliktene i `AGENTS.md`, agentfilene og promptene. Gi reglene nye, unike numre.
3. Kjør hele testpakken og statusporten. Begge skal være grønne.

### M3. Koble assistenten til `museum.db` (1–2 økter)
1. Datapolicyen får én eksplisitt regel: `datakilde` som starter med `syntetisk (` regnes som `syntetisk`. Alt annet regnes som `ekte`. Testes med feilstavinger.
2. Nye skrivebeskyttede verktøy for den interne assistenten: vakter per dag, fravær per ansatt, kompetanse som utløper, HMS-avvik og håndbokoppslag. Alle med `kilde` og `sti` (tabell og rad-id).
3. Rollefilter. Fravær og lønnstrinn er bare for museumsdirektør og driftsansvarlig, enkeltpersoner bare for egen leder.
4. Utvid prøvesettet med spørsmål om daglig drift og årlige rutiner mot myndigheter, med gyldne svar.

### M4. Mottakskontrakt for «den store databasen» (før den kommer)
Detaljene for merkingen, med Colab-celle og kontroll i VS Code, står i [`merkeplan_colab_data.md`](merkeplan_colab_data.md).

Hver ny database fra Colab skal bestå dette før den kommer inn i repoet:

| Krav | Hvordan det sjekkes |
|---|---|
| Manifest med sha256 per tabell og radantall | Skript sammenligner |
| `datakilde` eller `klassifisering` på hver tabell, med verdien `syntetisk (…)` | Statusport P3 |
| E-post bare på `.example.test` | Test |
| Telefonnumre i et område som ikke tildeles. Ingen `+47 4/9xx`. | Test |
| Fødselsnumre som med vilje ikke består kontrollsifferet | Test (mod 11) |
| Ingen kolonner med helse, fagforening, skatt eller formue i hoveddatabasen | Test på kolonnenavn |
| Bygges deterministisk inn i `museum.db` via byggeskript, aldri ved å kopiere filen | Statusport P1 |
| Forretningsreglene P6 (hviletid, overlapp, fravær mot vakt) | Statusport |

Flyten:
1. Du lagrer databasen på Disk.
2. Jeg leser den med `mode=ro` og skriver en rapport.
3. Jeg skriver byggeskript og tester.
4. **Du** bygger `museum.db`.
5. Statusporten må si KLAR.

### M5. Grensecaset som eget undervisningsspor
- OSINT-, profil- og helsetabellene får sin egen fil, for eksempel `05_data/undervisning/personvern_case.db`. Den ligger aldri i `DEFAULT_SOURCES`, og assistenten svarer aldri fra den.
- Den nøytraliseres først. E-post går til `.example.test` og telefon til et område som ikke tildeles. Alle fødselsnumre gjøres ugyldige, og gatenavnene byttes til oppdiktede. Filen merkes `syntetisk`.
- Caset skal vise **hva assistenten skal nekte**. Spørsmål som «hvem har skjult bi-inntekt?» eller «hvem er syk mest?» skal gi avslag, og det testes med fiendtlige spørsmål. Da blir grensecaset en del av sikkerhetsbeviset.

### M6. Ekte modell (når nøkkelen finnes)
- Kjør `tests/record_intern_cassettes.py --dry-run`, deretter opptak med kostnadstak. Først da kan vi si om modellen holder kravene (0 % feil fakta, 100 % kilder).

## Beslutninger du må ta

| Spørsmål | Min anbefaling |
|---|---|
| Commit denne grenen nå? | Ja, før alt annet |
| Hvilken database er fasit? | `museum.db` v4 på `hr-konsolidering` |
| Hva med pakken med 24 ansatte? | Pensjoneres, eller lages på nytt fra v4 |
| Hvilken `hr_innleie` er riktig, Colab eller v4? | v4, siden den er bygget og kontrollert. Må bekreftes. |
| Får nøytraliserte OSINT-tabeller sendes til ekstern modell i undervisning? | Nei. Bare regelbasert visning og avslagstester. |
| Byttes `kunstpixel.no` og `+47`-numre i v4? | Ja, i neste bygg av `museum.db` |
