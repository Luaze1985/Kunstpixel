# KI-data og lokal ansattdemo — implementasjonsplan

> Utføring: eksisterende arbeidsutsjekking, med separate agenter for datasett, API og visning. Brukeren har bedt om å bygge og fortsette autonomt.

**Mål:** Et reproduserbart syntetisk KI-datasett for alle 168 ansatte og en søkbar demo i eksisterende simulator.

**Arkitektur:** Stabil KP-ANS-ID kobler personregister, versjonert KI-grunnlag og lesende HR-kontekst. Lokale individuelle suppleringer lagres separat med revisjonshistorikk; museum.db endres ikke. Appen beholder bemanningsflyten og får en egen KI- og ansattvisning.

**Teknologi:** Python 3.13, FastAPI, SQLite for lokal tilstand, JSON/CSV for versjonerte demosett, eksisterende HTML/CSS/JavaScript.

**Grunnlag:** `docs/superpowers/specs/2026-10-21-ki-ansatt-demo.md`, med brukerens utvidelse til hele registeret og uttrykkelige autorisasjon til implementasjon.

## Globale krav

- Alle 168 kilde-ID-er, ingen ekstra ansatte eller navnebasert kobling.
- Alle nye observasjoner er syntetiske demodata, ikke påstander om virkelige personer.
- Historiske ansatte har ikke konstruert nåværende KI-bruk før/etter ansettelsen; ukjent og ikke relevant er egne statuser.
- KI-bruk, vurdert KI-kompetanse og modenhet er ulike dimensjoner. Ingen kausal effekt utledes fra vakter/fravær.
- Kilder, genereringsregel, dato og historikk er synlig. Lagret tilstand må tåle omstart.
- Norsk bokmål, HTML-escaping, validerte API-innspill, ingen hemmeligheter i filer eller svar.
- Lokal demo og søk fungerer uten API-nøkkel. Eksisterende OpenAI-planlegging er valgfri.

## Oppgaver og verifikasjon

1. **Datasett:** Test først full ID-dekning, reproduserbarhet, variasjon, skala og historiske datoer. Implementer `ai_data.py`, generator og `05_data/hr_simulator/ai_profiles.json`/CSV med avdelingsgrunnlag og profil per ansatt. Dokumenter skala og begrensninger.
2. **HR-kontekst:** Les konsolidert oktoberdatabase gjennom prosjektets read-only API. Lag et kildeidentifisert snapshot per ansatt for vakt-/fraværskontekst og avdelingskobling. Ingen databaseendring. Test kilde-ID-er, perioder og fravær av foreldreløse rader.
3. **API:** Test liste/søk/filtre/oversikt, persondetaljer, ukjent person, validering og revisionskonflikt. Implementer egne KI-endepunkter og lokalt SQLite-lag for supplering. Bevar grunnprofil og revisjoner. Etterprøv ved ny appinstans.
4. **Visning:** Gjenbruk appens skall og eksisterende Arbeidsflyt-CSS som referanse. Lag søkbar KI-registerflate, avdelings-/status-/verktøyfiltre, oversikt, kilder og persondetaljer. Vis individuell supplering og historikk uten å endre planstatus. Test ekte nettleserflyt hvis verktøy tilgjengelig; ellers dokumenter begrensningen.
5. **Lokal oppstart:** Lag Windows PowerShell- og POSIX-oppskrift med Python3.13/venv, kompatible MCP-avhengigheter og valgfri KI-konfigurasjon. Lag demo-manus. Test installasjonskommandoer og server/API i skymaskinen.
6. **Samlet kontroll:** Kjør hele pytest-pakken, funksjonelle forespørsler og uavhengig kodegjennomgang. Rapporter eksisterende feil separat, reparer egne feil og bekreft at museum.db og kilderegister er uendret. Lagre oppdatert install-/startkonfigurasjon.

## Review focus

- Historiske og manglende svar skal ikke telle som nåværende ikke-brukere.
- Filtre og oversikter må ha tydelig nevner og ukjentkategori.
- Personfelt med HTML-lignende tekst må behandles som tekst.
- Samtidige suppleringer må ikke overskrive hverandre stille.
- KI-profiler og suppleringer må ikke endre bemanningskvalifikasjoner eller arbeidsplan.
