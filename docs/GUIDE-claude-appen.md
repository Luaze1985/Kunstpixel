# Guide: Kunstpixel-demo i Claude-appen, hvor som helst

Med denne guiden kan du kjøre demoen i Claude på nett, på PC og (trolig) på mobil, uten at PC-en din er på.
Databasen, et lesende SQL-skript og definisjonene ligger i én skill som du laster opp én gang.

**Tid:** ca. 5 minutter. **Krever:** en Claude-konto. Skills virker på alle planer.

## 1. Bygg pakken (på PC-en, i Kunstpixel-mappa)

```powershell
py -3.13 scripts/lag_claude_skill.py
```

Den skriver `.scratch\claude-app\kunstpixel-demo.zip` (ca. 3 MB). Står det `STOPP`, er pakken over 30 MB. Si fra til Claude Code.

## 2. Slå på kodekjøring i claude.ai

Menynavnene under er slik claude.ai ser ut på norsk (sett 2026-11-19).

1. Åpne [claude.ai](https://claude.ai) i nettleseren på PC-en.
2. Trykk på navnet ditt nederst til venstre, så **Innstillinger → Funksjoner**.
3. Under **Kodekjøring og filoppretting**: sjekk at **Kjør kode i skyen** er på («Kreves for Skills»).

Skillen trenger dette for å kjøre SQL-skriptet.

## 3. Last opp skillen

1. Trykk **Programtillegg** i menyen til venstre.
2. Trykk **Legg til** (svart knapp øverst til høyre), så **Last opp plugin**.
3. Velg `kunstpixel-demo.zip` fra `.scratch\claude-app\`.
4. Trykk filteret **Skills**. Sjekk at **kunstpixel-demo** står under «Dine programtillegg», merket «Av deg».

**IKKE TESTET:** at «Last opp plugin» tar imot en skill-zip. Skillene dine «Arbeidsflyt» og «Cv og soknad» ligger der allerede, så veien finnes.

Skillen følger kontoen din. Du trenger ikke laste den opp på hver enhet.

## 4. Bruk prosjektet Kunstpixel, så demoen er lett å finne

1. Trykk **Prosjekter** i menyen til venstre, og åpne **Kunstpixel** (finnes allerede og er festet).
2. Til høyre: trykk **Rediger** ved **Instruksjoner**, og lim inn:
   ```
   Jeg er museumsdirektør på Kunstpixel og spør i vanlig språk, uten ID-er.
   Bruk alltid skillen kunstpixel-demo og hent alle tall med SQL.
   Finn ID-en selv ut fra navn, tittel, sal eller periode. Passer flere, spør meg hvilken.
   Når svaret er flere tall som kan sammenlignes (over tid, per utstilling, per avdeling), vis et enkelt diagram under svaret. Ett enkelt tall trenger ikke diagram. Kilde-linjen kommer sist.
   ```
3. Prosjektet er festet, så det ligger øverst under «Festet», også i mobilappen.

**IKKE TESTET:** at skillen virker inne i et prosjekt.

## 5. Prøv demoen

Start en ny samtale i prosjektet og spør som du ville gjort til vanlig:

| Du spør | Fasit |
|---|---|
| Hvor mange jobber hos oss nå? | 74 |
| Hvordan gikk prosjektrommet i Sal E i år? | 657 556 kr i overskudd (Fokusrom 2026.2) |
| Hvordan gikk Fokusrommet i år? | Claude skal spørre hvilket. Det er to: 335 089 kr og 657 556 kr. |
| Hvilken utstilling tjente mest i år? | Nattens farger, sommer: 3 404 877 kr. Den gikk også i høst, så svaret må si sesong. |
| Hvor mange besøkte oss i oktober, og hvor fornøyde var de? | 9 644 besøk. Tilfredshet ca. 4,1 av 5. |
| Hvem er Anja Eriksen? | Claude skal si at det er to, og spørre hvem du mener. |
| Hva vises nå? | Ikke ett navn. To tabeller er uenige. Claude bør oppdage det og vise begge. |

Fasit er regnet med SQL 2026-11-19. Hullene står med vilje ikke i skillen. Poenget er at Claude finner dem selv.

Skriv **sjekk** etter et svar. Da regner Claude hver påstand på nytt med SQL og viser ✅ eller ❌.

Svarer Claude uten å kjøre SQL, eller sier den at den ikke finner databasen? Skriv «Bruk skillen kunstpixel-demo».

## 6. På mobil

Åpne Claude-appen, logg inn med samme konto og start en ny samtale. Skillen skal være der.
**IKKE TESTET:** Anthropics hjelpeside nevner ikke mobil for skills. Prøv én gang med spørsmålet «Hvor mange ansatte har Kunstpixel?» før du viser demoen for noen.

## Når databasen er bygget på nytt

Kjør steg 1 igjen. I claude.ai: slett den gamle **kunstpixel-demo** under **Programtillegg → Skills** (de tre prikkene ved skillen) og last opp den nye zip-filen.

## Hva skillen kan og ikke kan

| | Skill i appen | Demo i Claude Code / Datafinner |
|---|---|---|
| Virker uten PC-en din | Ja | Nei |
| Data | Hele `museum.db`, lest med SQL | MCP-verktøy og Datafinner |
| Rollesperrer (f.eks. personalmappe) | Nei, Claude leser alle tabeller | Ja |
| «sjekk» | Samme KI sjekker sitt eget svar | Egen kontrollør (`/sjekk`) |
| Kjente hull | Står i `references/kjente-hull.md`, regnet ved bygging | Statusporten |

Dataene er syntetiske øvingsdata. Når du laster opp skillen, ligger databasen hos Anthropic, knyttet til kontoen din. Det er greit for øvingsdata. Gjør det ikke med ekte persondata.

## Hvis noe feiler

| Det du ser | Gjør dette |
|---|---|
| «ZIP exceeds size limits» | Si fra. Databasen kan krympes, eller deles opp. |
| «Upload failed» uten mer | Sjekk at du lastet opp zip-filen, ikke mappa. |
| Claude finner ikke skriptet | Sjekk at kodekjøring er på (steg 2). Start en ny samtale. |
| `AVVIST: not authorized` | Spørringen prøvde noe annet enn å lese. Be Claude skrive en ren `SELECT`. |

Kilder: [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [Agent Skills, størrelsesgrense](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

## Storskjerm: «Kunstpixel i dag»

Dashbordet for storskjerm ligger her: <https://claude.ai/artifact/PHo2wkd94Pmgo1qr1PzKXw>
Det er privat. Andre kan ikke åpne lenken før du deler den (menyen **Del** på siden).

**Vise det**
1. Åpne lenken over, eller trykk **Kunstpixel i dag** under **Festet** i menyen til venstre i claude.ai hvis du har festet den.
2. Trykk **Fullskjerm** øverst til høyre på siden.
3. Flaten under de fire tallene bytter selv hvert 12. sekund. **Stopp bytting** holder den fast. **Vis underlaget** viser radene bak flaten. Et trykk på et av de fire tallene hopper til flaten det hører til.

**Spørre**
- **KI-chat** står fast til høyre for dashbordet når siden er åpnet i claude.ai. Første gang du spør, spør claude.ai om siden får bruke Claude. Svar på Tillat. Hvert spørsmål bruker din egen Claude-kvote og tar ofte 30–90 sekunder. Sier du nei, forsvinner chatten og dashbordet får hele skjermen.
- **Drift og HR** åpner tre faste rapporter (prestasjon, fravær og belastning, innleie). Ingen navn.
- Første gang en av dem åpnes, lastes databasen inn i siden. Det tar noen sekunder.

**Oppdatere tallene**
Si «oppdater dashbordet» til Claude Code i Kunstpixel-mappa. Claude kjører

```powershell
py -3.13 scripts/lag_storskjerm.py
```

og publiserer de fire filene fra `.scratch\claude-app\` til samme lenke: `storskjerm.html`, `data.json`, `museum.db.gz.txt` og `chat-instruks.txt`, med kapabiliteten `sample`. «I dag» er dagen skriptet kjøres, og chatten bruker samme dag.

**I prosjektet Kunstpixel** kan du lime inn denne linjen under **Instruksjoner**:

```
Dashbordet «Kunstpixel i dag» for storskjerm: https://claude.ai/artifact/PHo2wkd94Pmgo1qr1PzKXw
```

Design: `docs/specs/2026-11-19-storskjerm-dashbord.md` og `docs/specs/2026-11-19-storskjerm-chat.md`. Beslutninger: DECISIONS D1–D8 og SC1–SC13.
