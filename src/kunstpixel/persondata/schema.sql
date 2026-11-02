-- Syntetiske kundedata for Kunstpixel. Alle personer er oppdiktet.
-- Ansatte refereres med ansatt_id fra museum.db (hr_ansatte).

CREATE TABLE kontakter (
    kontakt_id TEXT PRIMARY KEY,
    fornavn TEXT NOT NULL,
    etternavn TEXT NOT NULL,
    epost TEXT,
    telefon TEXT,
    ansatt_id TEXT,
    opprettet TEXT NOT NULL,
    nyhetsbrev_samtykke INTEGER NOT NULL CHECK (nyhetsbrev_samtykke IN (0, 1)),
    samtykke_dato TEXT,
    samtykke_kilde TEXT CHECK (samtykke_kilde IN ('nettside', 'kasse', 'arrangement')),
    trukket_dato TEXT,
    siste_aktivitet TEXT NOT NULL,
    datakilde TEXT NOT NULL
);

CREATE TABLE medlemskapstyper (
    type TEXT PRIMARY KEY,
    aarspris INTEGER NOT NULL,
    datakilde TEXT NOT NULL
);

CREATE TABLE fordeler (
    fordel TEXT PRIMARY KEY,
    beskrivelse TEXT NOT NULL,
    datakilde TEXT NOT NULL
);

CREATE TABLE medlemskapstype_fordel (
    type TEXT NOT NULL REFERENCES medlemskapstyper(type),
    fordel TEXT NOT NULL REFERENCES fordeler(fordel),
    datakilde TEXT NOT NULL,
    PRIMARY KEY (type, fordel)
);

CREATE TABLE medlemskap (
    medlemskap_id INTEGER PRIMARY KEY,
    kontakt_id TEXT NOT NULL REFERENCES kontakter(kontakt_id),
    type TEXT NOT NULL REFERENCES medlemskapstyper(type),
    startdato TEXT NOT NULL,
    sluttdato TEXT NOT NULL,
    betalt_belop INTEGER NOT NULL,
    fornyelse_av INTEGER REFERENCES medlemskap(medlemskap_id),
    solgt_av_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);

CREATE TABLE medlemsbesok (
    besok_id INTEGER PRIMARY KEY,
    medlemskap_id INTEGER NOT NULL REFERENCES medlemskap(medlemskap_id),
    dato TEXT NOT NULL,
    antall_gjester INTEGER NOT NULL DEFAULT 0,
    datakilde TEXT NOT NULL
);

CREATE TABLE fordel_bruk (
    bruk_id INTEGER PRIMARY KEY,
    medlemskap_id INTEGER NOT NULL REFERENCES medlemskap(medlemskap_id),
    fordel TEXT NOT NULL REFERENCES fordeler(fordel),
    dato TEXT NOT NULL,
    rabatt_belop REAL NOT NULL,
    datakilde TEXT NOT NULL
);

CREATE TABLE gavekort (
    gavekort_id INTEGER PRIMARY KEY,
    kode TEXT NOT NULL UNIQUE,
    belop INTEGER NOT NULL CHECK (belop IN (200, 300, 500, 1000)),
    kjoper_kontakt_id TEXT NOT NULL REFERENCES kontakter(kontakt_id),
    mottaker_kontakt_id TEXT REFERENCES kontakter(kontakt_id),
    utstedt TEXT NOT NULL,
    gyldig_til TEXT NOT NULL,
    kanal TEXT NOT NULL CHECK (kanal IN ('butikk', 'nettbutikk', 'skranke')),
    solgt_av_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);

CREATE TABLE gavekort_bruk (
    bruk_id INTEGER PRIMARY KEY,
    gavekort_id INTEGER NOT NULL REFERENCES gavekort(gavekort_id),
    dato TEXT NOT NULL,
    belop REAL NOT NULL,
    sted TEXT NOT NULL CHECK (sted IN ('billett', 'butikk', 'kafe', 'arrangement')),
    datakilde TEXT NOT NULL
);

CREATE TABLE arrangementer (
    arrangement_id TEXT PRIMARY KEY,
    kilde TEXT NOT NULL CHECK (kilde IN ('generert', 'museum.db')),
    type TEXT NOT NULL,
    tittel TEXT NOT NULL,
    dato TEXT NOT NULL,
    maks_deltakere INTEGER NOT NULL,
    pris_voksen REAL NOT NULL,
    pris_barn REAL NOT NULL,
    ansvarlig_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);

CREATE TABLE pameldinger (
    pamelding_id INTEGER PRIMARY KEY,
    arrangement_id TEXT NOT NULL REFERENCES arrangementer(arrangement_id),
    kontakt_id TEXT NOT NULL REFERENCES kontakter(kontakt_id),
    antall_voksne INTEGER NOT NULL,
    antall_barn INTEGER NOT NULL,
    belop REAL NOT NULL,
    betalt_med TEXT NOT NULL CHECK (betalt_med IN ('kort_kasse', 'vipps', 'gavekort', 'medlemsfordel')),
    registrert TEXT NOT NULL,
    datakilde TEXT NOT NULL
);

CREATE TABLE skolebestillinger (
    bestilling_id INTEGER PRIMARY KEY,
    skole TEXT NOT NULL,
    kontaktlaerer TEXT NOT NULL,
    jobb_epost TEXT NOT NULL,
    klassetrinn INTEGER NOT NULL CHECK (klassetrinn BETWEEN 1 AND 13),
    antall_elever INTEGER NOT NULL,
    dato TEXT NOT NULL,
    ansvarlig_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);

CREATE TABLE utleie (
    foresporsel_id INTEGER PRIMARY KEY,
    kundetype TEXT NOT NULL CHECK (kundetype IN ('privat', 'bedrift')),
    kontaktperson TEXT NOT NULL,
    epost TEXT NOT NULL,
    firmanavn TEXT,
    dato TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('forespurt', 'bekreftet', 'avlyst', 'gjennomfoert')),
    ansvarlig_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);

CREATE TABLE henvendelser (
    henvendelse_id INTEGER PRIMARY KEY,
    tidspunkt TEXT NOT NULL,
    kanal TEXT NOT NULL CHECK (kanal IN ('cli', 'telegram', 'skranke', 'epost')),
    fritekst TEXT NOT NULL,
    kategori TEXT NOT NULL,
    inneholder_persondata INTEGER NOT NULL CHECK (inneholder_persondata IN (0, 1)),
    kontakt_id TEXT REFERENCES kontakter(kontakt_id),
    besvart_av_ansatt_id TEXT,
    datakilde TEXT NOT NULL
);
