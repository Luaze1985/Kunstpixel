# KI- og ansattdemo: leveransens design

Brukeren har bedt om et nytt syntetisk datasett for hele ansattregisteret, der KI-bruk og vurdert kompetanse kan knyttes til HR-kontekst og berikes senere, samt en lokal demonstrasjon i eksisterende app.

## Data og identitet

Alle 168 KP-ANS-ID-er fra staff_source.csv har én KI-profil i ai_profiles.json og CSV. Referansedato er 2026-10-21. Avdelings- og rollemaler gir dokumenterte genereringsregler, med stabil SHA256-seed per ID. Bruk, kompetanse og modenhet er forskjellige dimensjoner. Ukjent, aldri-bruk og ikke relevant er ulike statuser. Historiske og fremtidige ansatte har egne kategorier og tidsavgrensning.

hr_context.json inneholder et skrivebeskyttet uttrekk av syntetiske vakter og fravær fra konsolideringscommit ce6fbfc7b3726527f01d3f29e7bc35a441e92059. Koblingen er ansatt-ID. Det endrer ikke museum.db og utleder ikke produktivitet eller KI-effekt. Fravær er kalenderdager med overlapp fjernet.

## App og supplering

Den eksisterende FastAPI-simulatoren utvides med /api/ai/people, /summary og persondetaljer/supplering. Registeret støtter tekstsøk, avdeling, verktøy, ansettelsesstatus og paginering. Alle oversikter viser nevner og ukjentkategori. Nettleseren viser grunnprofil og senere supplering med hver sin kilde/dato.

Individuell beskrivelse, kilde og kompetanse-/modenhetsskår kan lagres i separat lokal SQLite, med forventet revisjon, append-only historikk og atomisk konfliktkontroll. Grunnprofilen beholdes. Supplering endrer ikke bemanningskvalifikasjoner eller arbeidsplan.

## Lokal demo og begrensninger

Python 3.13 og requirements-demo.txt gir avhengighetene. Lokal søking og syntetisk berikelse trenger ingen API-nøkkel. Eksisterende OpenAI-bemanningsforslag trenger OPENAI_API_KEY og KUNSTPIXEL_OPENAI_MODEL i serverprosessen. Ekte modellkall og Windows-kjøring må ikke omtales som testet uten faktisk bevis.

Startveiledning og demospor finnes i docs/DEMO_KI.md. Akseptanse omfatter full ID-dekning, reproduserbare filer, tidsgrenser, fungerende filtre/søk, bevarte grunnprofiler, revisjonskonflikt, omstart, HTML-escaping og uendret museumsdatabase.
