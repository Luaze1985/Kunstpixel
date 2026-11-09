# Plan: UX/UI-opprydding i Datafinner (demo)

**Status:** Grenene er opprettet 2026-11-06. Prototypen bygges på `ux/ett-vindu`. Agentfilene er ikke installert.
**Grunnlag:** demogrenen `claude/kunstpixel-demo-database-fb3af9` (`1e31191`, ikke tagget). Jeg gikk gjennom demoen i nettleseren 2026-11-06, i 1280 × 800.
**Mål:** Når Lars viser demoen, skal publikum få svar med ett klikk og se én tittel per svar. Det skal ikke vises tomme bokser, utviklertekst eller tre ord for KI.

---

## 1. Fakta (deterministisk, 0 tokens)

| Sjekk | Resultat |
|---|---|
| Arbeidsflyt-validator på 6 sider (`index`, `sok`, `arena`, `vaktrom`, `chat`, `arbeidsflyt`) | PASS, 15/15 regler på alle |
| Konsollfeil på forsiden og i rapporten | 0 |
| Tester som leser Datafinner-HTML | Bare `tests/test_datafinner_api.py:125`. Den krever at spørsmålslisten i `index.html` har mønsteret `{ id: "…", tekst:` og stemmer med databasen. Ingen tester låser de konkrete tekstene i funnene (søkt i `tests/`). |
| Rollebeskrivelsene på forsiden | Kommer fra `05_data/roller.csv` og dermed `museum.db`, ikke fra HTML |
| Arena med KI av | Casene kjører (`/api/arena/kjor` P2 → 200, `ok: true`). Grensemodus (5 caser) gir 503: «KI-laget er ikke slått på». |
| Chat med KI av | Send-knappen og tekstfeltet er aktive (`disabled: false`). |

Validatoren sier at reglene for designsystemet holder. Alle funn under gjelder tekst og flyt, som validatoren ikke ser.

## 2. Funn

Alvorlighetsgrad: **H** = synlig feil i demo, **M** = forvirrer publikum, **L** = pynt.

| # | Grad | Hvor | Funn | Bevis |
|---|---|---|---|---|
| F1 | H | `index.html:94` + af.css | KI-boksen vises tom (67 px) når KI er av. `hidden=true`, men `display: grid` overstyrer. | JS: `{hidden:true, display:"grid", h:67.5}` |
| F2 | H | `chat.html:82` | Når KI er av, ser publikum utviklertekst: «Sett LLM_PROVIDER og LLM_MODEL …». Send-knappen er fortsatt aktiv. | Sidetekst `/chat` |
| F3 | M | `index.html` rapportflyt | To klikk til svar: «Finn svar» gir én setning, og «Lag rapport» gir den samme setningen pluss tabell. Tallene 9/10 vises to ganger. | Gjennomgang av «Hvem har vakt i dag?» |
| F4 | M | `index.html` | Samme tittel står fem ganger: meny «Hvem har vakt i dag?», h1 «Vakt i dag», svaretikett, rapport-h1, «Svarer på «Hvem har vakt i dag?» …». | Sidetekst |
| F5 | M | `index.html:106`, `sok.html:89` | Panelet heter «Slik spør LLM-en», også når KI er av. Siden bruker både KI, AI («AI-forslag») og LLM om det samme. | Grep |
| F6 | M | Rapporttabell | Tabellen er 925 px i en ramme på 556 px. Telefon og e-post er skjult bak vannrett rulling. | JS: `scrollW 925 / clientW 556` |
| F7 | M | `index.html:69` | «Utkast så lenge noe mangler.» sier ikke hva som mangler (svaret er at kontrollboksene ikke er huket av). | Sidetekst |
| F8 | M | `chat.html:37`, `arena.html:118` | «Ingen sperrer.» står i et banner som publikum ser. Det er en driftsbeslutning, ikke informasjon til brukeren. | Grep |
| F9 | M | Forsiden | De demoverdige flatene (Arena, Chat) ligger nederst, under ni roller. | Sidetekst `/` |
| F10 | M | Forsiden og `/arbeidsflyt` | To rollesett med ulike navn: 9 «roller» (Museumsdirektør …) og 7 «arbeidsroller» (Salvert …). | Sidetekst |
| F11 | L | `05_data/roller.csv` | Sjargong og «og og og»: «Orkestrator og leder», «QA og etterlevelse», «Kafédrift og IK-Mat og allergener og svar på kafékritikk». | Sidetekst |
| F12 | L | `arena.html:265` | «Live» betyr «kan kjøres» (uten KI), men ordet sier ikke det. Nummereringen hopper også (D5 før D4, P1 mangler). | Sidetekst `/arena`, kall mot `/api/arena/kjor` |
| F15 | H | `arena.html:219` (grensemodus) | De fem grensecasene viser ikke at de krever KI. Med KI av gir kjøringen feil 503. | `/api/grense/kjor` → 503 |
| F13 | L | Rapport | GRUNNLAG viser rå JSON (`get_report_assessment({"sporsmal_id":…})`) uten å være foldet inn. | Sidetekst |
| F14 | L | Forsiden | Museet heter «Aura Kunstmuseum» i appen og «Kunstpixel» i README. | Grep |

---

## 3. Beslutninger Lars må ta før grenene starter

Disse endrer hva appen viser eller for hvem. Lars avgjør dem, agentene gjør det ikke.

| ID | Spørsmål | Anbefaling |
|---|---|---|
| B1 | Skal forsiden starte med demoflatene over rollene? (F9) | Ja, med Arena først (virker uten KI). Chat og grensemodus merkes «krever KI», fordi demoen starter med KI av. |
| B2 | Skal «Finn svar» gå rett til full rapport? (F3) | Ja, med svarsetningen som ingress i rapporten. |
| B3 | Ett ord for KI i UI-et? (F5) | «KI» overalt. «AI-forslag» blir «KI-forslag». |
| B4 | Navnet på museet i UI-et? (F14) | Behold «Aura Kunstmuseum», det er datagrunnlaget. Lars skriver én setning i README (ingen gren). |
| B5 | Slå sammen rollesettene? (F10) | Nei, ikke nå. Det er en datamodellendring. Vi gir dem ulike navn i stedet. |

---

## 4. Agenter

Nye agenter, skrevet etter standarden i `instruks-for-agenter`. I tillegg brukes den eksisterende `designsystem-team` (`.claude/agents/designsystem-team.md`) som port for alle HTML-endringer.

### 4.1 `ux-revisor` (bare lesing, brukes som port på hver gren)

```markdown
---
name: ux-revisor
description: Leser Datafinner-sidene i nettleseren og gir en PASS/FAIL-liste for UX-funnene F1–F14 i docs/plans/2026-11-06-datafinner-ux.md. Endrer aldri filer.
---

# Skill: UX-revisor for Datafinner

Sikrer at en gren faktisk fjerner funnene den lover, uten å lage nye.

## Indre sløyfe (0 tokens, kjøres først)
1. `py -3.13 C:/Users/larse/.gemini/config/skills/arbeidsflyt/scripts/verify_arbeidsflyt.py <fil>` for hver endret fil i `src/kunstpixel/adapters/datafinner/`. Exit ≠ 0 → FAIL, stopp.
2. `py -3.13 -m pytest -q -p no:cacheprovider` → exit 0, ellers FAIL, stopp.
3. Start Datafinner direkte på en ledig port, ikke med `start_demo.cmd`, fordi den låser 8010 og stopper når porten er opptatt: `$env:DATAFINNER_PORT=<ledig port>; $env:LLM_PROVIDER=' '; py -3.13 src/kunstpixel/adapters/datafinner.py`.
4. HTTP-sjekker mot den porten: `/`, `/chat`, `/arena`, `/api/status`, `/api/rapport?sporsmal=vakt-i-dag` → 200. `/api/grense/kjor` → 503 er forventet med KI av.

## Ytre sløyfe (skjønn)
- Les HTML-en grenen endret, og vurder hver F-ID grenen eier som PASS/FAIL med bevis (linje eller HTTP-svar).
- Nettlesergjennomgangen (1280 × 800 og 375 × 812, JS-målinger for F1 og F6) gjøres av hovedøkten. Subagenter har ikke nettleserverktøyene. Revisoren lister hva som må måles der.
- Nye funn føres som F16+ i en egen liste, ikke rettes.

## Guardrails
- Ingen skriving til filer, ingen git-kommandoer som endrer noe.
- Bare 127.0.0.1. Ingen eksterne nettsider. Stopp serveren du startet.

## Done-når
1. Validator og pytest har exit 0.
2. HTTP-sjekkene gir forventet status.
3. Hver F-ID grenen eier har PASS med bevis, eller står på listen «må måles i nettleser».
```

### 4.2 `ux-tekstvasker` (bare synlig tekst)

```markdown
---
name: ux-tekstvasker
description: Retter synlig tekst i Datafinner-sidene til klarspråk etter docs/plans/2026-11-06-datafinner-ux.md. Rører ikke JavaScript-logikk, CSS eller data.
---

# Skill: Tekstvasker for Datafinner

Fjerner unødvendig tekst og utviklerspråk som publikum ser i demoen.

## Indre sløyfe (0 tokens, kjøres først)
1. `rg -n "LLM|AI-|Ingen sperrer|Live\"|Utkast så lenge" src/kunstpixel/adapters/datafinner/` og lagre treffene som før-liste.
2. `rg -n "<tekst du endrer>" tests/` for hver streng. Treff → stopp og rapporter, ikke endre testen.

## Ytre sløyfe (skjønn)
- Ett ord per ting: «KI» (B3). Ingen miljøvariabler i UI-et.
- Kortest mulig: fjern tekst som gjentar tittelen eller forklarer det åpenbare.
- KI av i chat (F2): «KI er av i denne demoen. Start med -KI for å slå den på.» Send-knappen og feltet deaktiveres når `/api/status` sier `llm: false`. Er det mer enn noen linjer JS, føres det som funn i stedet.
- Grensemodus (F15): merk casene «Krever KI», og vis samme tekst som i chat når KI er av.
- F12: «Live» blir «Kan kjøres».
- Norsk bokmål, klarspråk, ingen smiger.

## Guardrails
- Bare filene grenen eier (se §5). Aldri `af.css`, aldri `05_data/` på grenen `ux/tekst-sider`.
- Endre bare tekstnoder og attributter (`aria-label`, `title`), ikke ID-er og klassenavn som JS bruker.

## Done-når
1. Etter-søket fra indre sløyfe gir 0 treff for F2, F5, F8 og F12 i eide filer.
2. `ux-revisor` gir PASS for F2, F5, F8, F12 og F15.
3. pytest exit 0.
```

### 4.3 `ux-flytbygger` (rapportflyten i `index.html`)

```markdown
---
name: ux-flytbygger
description: Endrer svar- og rapportflyten i src/kunstpixel/adapters/datafinner/index.html (ett klikk, ingen tomme bokser, én tittel). Rører ikke andre sider, data eller af.css.
---

# Skill: Flytbygger for rapporten

Gjør «Finn svar» til ett klikk med én tittel, og skjuler det som er tomt.

## Indre sløyfe (0 tokens, kjøres først)
1. Les `index.html` linje 60–110 (rapportmarkup) og 495–520 (kontroll og utkast-logikk) og 645–680 (KI-knappen).
2. `rg -n "hidden" src/kunstpixel/adapters/datafinner/af.css` for å se om `[hidden]` er håndtert.
3. pytest exit 0 før start (baseline).

## Ytre sløyfe (skjønn)
- F1: KI-boksen skal ha `display: none` når den er skjult. Løs det i `index.html`, ikke i `af.css`. Er en endring i `af.css` nødvendig, stopp og spør `designsystem-team` (nivå 2).
- F3/B2: «Finn svar» kjører rapporten direkte. Svarsetningen blir ingress. «Lag rapport»-knappen fjernes.
- F4: Én h1 per visning. Spørsmålsteksten står én gang.
- F6: Telefon og e-post flyttes til en foldbar detalj per rad eller fjernes fra rapportvisningen. Ingen ny CSS.
- F7: Teksten ved «Utkast» sier hva som mangler: «Huk av kontrollpunktene for å gjøre rapporten ferdig.»
- F13: GRUNNLAG legges i `<details>`, lukket som standard.
- Kontrollboksene, faktasjekken og «Last ned rapport» skal virke som før.

## Guardrails
- Bare `index.html`. Ingen endring i `datafinner.py`, `datafinner_api.py` eller `05_data/`.
- Spørsmålslisten må beholde mønsteret `{ id: "…", tekst:` (låst av `tests/test_datafinner_api.py:125`).
- Ingen nye avhengigheter eller biblioteker.

## Done-når
1. JS-måling: KI-boksens høyde er 0 når KI er av.
2. Fra forsiden til full rapport tar det ett klikk på «Finn svar».
3. `ux-revisor` gir PASS for F1, F3, F4, F6, F7 og F13. pytest exit 0.
```

---

## 5. Undergrener

Lars vil ha alt i ett vindu med tre paneler, slik det ble besluttet før (`02_deliverables/arbeidsflyt/SPEC.md:5`, arkivet `arkiv/2026-11-05_chat_hub_trepanel/`):
- **Venstre:** alle flater og spørsmål.
- **Midten:** arbeidet.
- **Høyre:** verktøykall og kilde.

Skallet kommer derfor først, og de andre grenene bygger på det. Alle grenene lages fra demogrenen `claude/kunstpixel-demo-database-fb3af9`. `ux/rapportflyt` og `ux/tekst` flyttes opp til tuppen av `ux/ett-vindu` (`git branch -f`) før arbeidet på dem starter. De har ingen commits før det.

| Gren | Agent | Eier filer | Funn | Avhenger av |
|---|---|---|---|---|
| `ux/ett-vindu` | hovedøkten | `ett-vindu.html` (ny, på `/ett-vindu`), én linje i `ASSETS` i `datafinner.py` | F9, F10, F15, og B1 og B2 i prototypen | — |
| `ux/rapportflyt` | `ux-flytbygger` | Rapportdelen i skallet | F1, F3, F4, F6, F7, F13 | `ux/ett-vindu` |
| `ux/tekst` | `ux-tekstvasker` | Synlig tekst i skallet og i sidene som blir igjen | F2, F5, F8, F12 | `ux/ett-vindu`, B3 |
| `ux/rolletekster` | `ux-tekstvasker` | `05_data/roller.csv` | F11 | B5. **Lars bygger `museum.db`.** Porten er «pytest grønn etter at Lars har bygget». Agenten bygger aldri selv. |

Prototypen står ved siden av dagens sider, og ingenting fjernes. Når Lars godkjenner skallet, flyttes Chat, Vaktrom, Søk og Arbeidsflyt inn som visninger i midten, én om gangen. Til da åpnes de som i dag.

`ux-revisor` kjøres én gren av gangen, eller med hver sin port (se §4.1).

Port for hver gren før merge:
1. `designsystem-team` vurderer HTML-endringene mot Arbeidsflyt (validator exit 0 og sjekkliste).
2. `ux-revisor` gir PASS for grenens F-ID-er.
3. Lars ser på grenen i nettleseren og merger. Ingen agent merger, pusher eller tagger.

Etter at alle tre er merget: ny tagg `demo-v2` (Lars).

## 6. Utenfor planen
- Å slå sammen rollesett eller endre datamodellen (B5).
- Endringer i `af.css` og designsystemet (krever nivå 2 i `designsystem-team`).
- Mobiltilpasning utover det `ux-revisor` måler i 375 × 812.
- Ekte KI-test (`-KI`), som krever `.env`.
