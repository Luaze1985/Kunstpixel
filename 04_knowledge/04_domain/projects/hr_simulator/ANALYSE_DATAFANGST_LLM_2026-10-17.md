# Data, datafangst og språkmodellens virkeområde — 17. oktober 2026

## Konklusjon

Ukeplan-demoen har nok fiktive data til å vise arbeidsflyt, kontaktstatus, kildevisning og menneskelig godkjenning. Den kan foreløpig ikke vise at en språkmodell planlegger bedre enn regelmotoren: de fire ukene gjentar fem oppgavetyper, og regelmotoren dekker alle 16 opprinnelig åpne rolleposter. Det større museumsarkivet er et separat, generert øvingsdatasett. Det er ikke koblet til ukeplanen og har verken klokkeslett eller dokumentert opplæring per rolle.

## Kontrollerte data

| Grunnlag | Kontrollert omfang | Relevans og grense |
|---|---:|---|
| `05_data/hr_simulator/planning_week.json` i feature-grenen | 4 sammenhengende uker, 20 aktiviteter, 11 personer, 32 rolleposter, 16 avtalte tildelinger, 1 opprinnelig kontaktsvar | Valideres av `context.py`; 5 aktivitetstyper gjentas hver uke. 8 ansatte, 1 intern reserve og 2 eksterne kandidater. |
| Regelsimulering mot grunnlaget | 4 åpne rolleposter per uke; 4 forslag per uke; 0 åpne etter forslag | Resultat for det felles grunnlaget, uten OpenAI-kall. Første uke har fortsatt ukjent historikk markert uavklart. |
| Tre isolerte demoer | HR-001: 5→0, HR-002: 4→0, HR-003: 5→1 åpne rolleposter etter regelstyrt forslag | Kontakt-overlay gir ulik starttilstand, men aktivitetene og personene er felles. Foreslått fjerning av avtalt vakt krever egen godkjenning. |
| Syntetiske arkiv-CSV-er i prosjektroten | 168 ansatte, 48 298 vaktposter, 312 innleieoppdrag og 102 utstillinger | ID-referanser fra vakter til ansatte/utstillinger og innleie til godkjenner/utstilling hadde 0 mangler i de kontrollerte CSV-ene. Arkivet ligger lokalt, er uversjonert i `main` og finnes ikke i feature-grenen. |

Arkivets vaktposter dekker 2010–2026, men inneholder bare dato og timetall. Det er 4 795 persondager over 13 timer og 36 over 24 timer i de genererte radene; høyeste sum er 35,5 timer. 693 vaktposter ligger etter analysedatoen 17. oktober 2026. Dette er en konsekvens av tilfeldig datagenerering, ikke observerte driftsforhold. Vaktene egner seg dermed til analyseøvelser, men ikke som bemanningshistorikk for overlapp, hvile eller faktisk belastning. De 66 tomme sluttdatoene for ansettelse tilsvarer pågående fast-/deltidsstatus og ble ikke behandlet som datatap.

Person-ID-er i ukeplanen og arkivet har **0 treff** mellom seg. Ukeplanen har 14 dokumenterte opplæringsoppføringer og én ferdighet uten opplæringsoppføring. Alle 11 personprofiler har samme prosjektkilde-ID `R-03`; dette er en syntetisk prosjektbeslutning, ikke feltvis dokumentasjon for hver ferdighet eller tilgjengelighet. Eksterne museumskilder beskriver driftspraksis, men verifiserer ikke de fiktive personopplysningene.

## Hvor dataene oppstår og lagres

1. `src/kunstpixel/data/archive_generator.py` i `main` lager arkivdata med fast tilfeldig frø og skriver CSV, Parquet, JSON og en egen historikkdatabase. Ved ny kjøring erstattes den historikkdatabasen. Dette er ikke en innsamling fra et faktisk museum.
2. `scripts/generate_planning_week.py` i feature-grenen bygger ukeplanen fra HR-001 og faste aktivitetssjabloner og skriver `planning_week.json`. Regenerering kan overskrive manuelle JSON-endringer. `context.py` kontrollerer typer, fireukersstruktur, referanser og kilde-ID-er.
3. `api.py` og `store.py` leser JSON-grunnlaget og lagrer kontaktsvar, tildelinger, forslag, beslutninger og hendelseslogg i lokal `local_state.sqlite3`. Denne statusen er atskilt fra `museum.db`, som er skrivebeskyttet samlingsdatabase.
4. `redigeringsbord/UTKAST-aktiviteter.csv` er en flat arbeidskopi for `datasett-redigerer`. «Lagre direkte til disk» skriver bare denne CSV-filen og tar `.bak` ved lagring. Ingen validert import tilbake til `planning_week.json` finnes. Brukeren har valgt **ansatte og kandidater** som neste redigeringsvisning; den er ennå ikke åpnet.

Det mangler derfor én tydelig, kontrollert vei fra innsamling/redigering av person- og aktivitetsdata til autoritativt ukegrunnlag. Et hovedvalg er om ukeplan-JSON eller en mer redigerbar tabell skal være kilden. Arkivet må ikke blandes inn før ID-er og feltbetydning er mappet.

## Virkeområder for språkmodellen

| Oppgave | Med dagens data? | Ansvar |
|---|---|---|
| Tolke en leders fritekst om oppgave, behov eller avbud til et forslag om strukturerte felt | Som øvelse, etter menneskelig bekreftelse | Modellen kan foreslå felt og peke på mangler; lagring krever validering og beslutning. |
| Forklare kandidatvalg, udekket behov og alternative handlingsveier på vanlig norsk | Ja, med eksplisitte ID-er og regelresultat | Fakta og kontroller må komme fra data/regelmotor; modellen kan formulere forklaringen. |
| Foreslå person/rolle-kombinasjoner for en uke | Teknisk koblet til, men nytte ikke bevist | `openai_planner.py` tar strukturert svar og etterkontrollerer det. Nåværende regelmotor løser alle ordinære ukegap uten modell. Ingen ekte modellkjøring er dokumentert. |
| Bestemme kompetanse, opplæring, arbeidstidsgrenser, lovlig innleie eller gi endelig ukeplan | Nei | Krever dokumenterte data, deterministiske sperrer og menneskelig godkjenning. Manglende opplysninger skal vises som uavklart. |
| Bruke 16 års arkiv til prediksjon eller rettferdig belastningsfordeling | Ikke nå | Arkivet mangler klokkeslett/opplæring, har umulige dagsummer og er ikke koblet til ukeplanens personer. |

## Minste neste steg

1. Lag en flat, merket **arbeidskopi for ansatte og kandidater**. Definer hvilke felter som kan redigeres, og en validert import til `planning_week.json` med ID-, kilde-, tids- og referansekontroll. Ikke bruk «Lagre direkte til disk» på hele den nestede original-JSON-en.
2. Legg til 2–3 fiktive øvelser som faktisk skiller gode og dårlige forslag: delvis tilgjengelighet, dokumentert/udokumentert opplæring, avbud og konkurrerende arrangementer. Fasiten skal angi harde krav, uavklarte behov og om avtalte vakter ble bevart.
3. Kjør samme øvelser først med regelmotor, deretter med konfigurert OpenAI-modell. Mål gyldige forslag, udekkede roller, endringer i avtalte vakter, kildepresisjon og behov for menneskelig retting. Først da kan demoen vise en konkret merverdi av språkmodellen fremfor en pen presentasjon av eksisterende regler.

## Metode og grenser

Tallene er opptalt fra lokale CSV-/JSON-filer 17. oktober 2026, uten lesing eller skriving direkte mot `museum.db`. Ukegrunnlaget ble lastet gjennom `load_planning_context`; regelmotor og scenarioer ble kjørt i minne/midlertidig lokal database. Det er ikke kjørt ekte OpenAI-modell eller full testpakke i denne analysen. At dataene er oppdiktede er et brukerbekreftet premiss og støttes av generatorene, men er ikke en uavhengig revisjon av hver rad. Dette er en vurdering av demoens data og arbeidsflyt, ikke av faktiske arbeidsforhold eller juridisk etterlevelse.
