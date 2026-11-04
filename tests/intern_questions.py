"""40 prøvespørsmål for intern assistent (H2/H4/H6) + 20 H5-prøvespørsmål (14 dekket + 6 ubesvarbare).

`fakta` er hentet ordrett fra datafilene, ikke fra agentens svar, slik at testene ikke er sirkulære.
Brukes på tvers av H2 (regelbasert), H4 (ekstern modell), H5 (nye styrings- og rapporteringsdata) og H6 (lokal modell).
"""

HMS = "05_data/governance/hms_arbeidsmiljo.yaml"
IK = "05_data/governance/ik_mat_kafe.yaml"
BRANN = "05_data/governance/brann_sikring_kapasitet.yaml"
TILSYN = "05_data/governance/tilsynskalender.json"
ROSTER = "03_team/team_roster.md"
TILTAK = "05_data/governance/noexcuse_prioriterte_tiltak.yaml"
MYNDIGHET = "05_data/governance/myndighetskontakter.yaml"
TILSYNSBESOK = "05_data/governance/tilsynsbesok_rutine.yaml"
RAPPORTERING = "05_data/governance/rapporteringskalender.yaml"
RAPPORTMALER = "05_data/governance/rapportmaler.yaml"
ARBEIDSOPPGAVER = "05_data/governance/arbeidsoppgaver_tidsbruk.yaml"
HISTORIKK_TALL = "05_data/governance/historikk_tall.yaml"
HISTORIKK_TEKST = "05_data/governance/historikk_tekst.yaml"


def q(sporsmal: str, kilde: str, fakta: list[str], rolle: str = "museumsvert", svak: bool = False) -> dict:
    """`svak=True`: naturlig formulering som det enkle ordsøket i H2 ikke klarer (verifisert 2026-10-26).

    Det regelbaserte søket får lov å svare «ikke funnet» på disse, men aldri svare feil.
    LLM-versjonene (H4, H6) skal klare alle 30.
    """
    return {"sporsmal": sporsmal, "kilde": kilde, "fakta": fakta, "rolle": rolle, "svak": svak}


DEKKET: list[dict] = [
    # HMS og arbeidsmiljø
    q("Hvor lenge kan museumsverter stå sammenhengende?", HMS, ["90 minutter"]),
    q("Hvor ofte skal museumsvertene rullere mellom oppgaver?", HMS, ["Hver 2. time"]),
    q("Hva er maks løftevekt for én person?", HMS, ["Maks 15 kg"]),
    q("Hvor mye kan to personer løfte sammen?", HMS, ["15 til 40 kg"]),
    q("Hva kreves for å løfte over 40 kg?", HMS, ["mekanisk løftehjelpemiddel"]),
    q("Hvilke hansker skal brukes på malerier?", HMS, ["Ublekede hvite bomullshansker"]),
    q("Hvilke hansker brukes for skulptur og glass?", HMS, ["Nitrilhansker"]),
    q("Når er alenearbeid forbudt?", HMS, ["etter kl. 20:00"]),
    q("Hva gjør jeg ved utagering fra publikum?", HMS, ["tilkall vaktkollega"]),
    q("Hvordan varsler jeg om kritikkverdige forhold?", HMS, ["Konfidensiell varslingskanal"], svak=True),
    q("Hvor ofte er det vernerunde?", HMS, ["Kvartalsvis"]),
    q("Hvor raskt må røde avvik lukkes?", HMS, ["24t"]),
    # IK-Mat
    q("Hva er maks temperatur i kjøleskapet?", IK, ["maks +4 °C"]),
    q("Hvilken temperatur skal fryseren ha?", IK, ["maks -18 °C"], svak=True),
    q("Hva er minste kjernetemperatur ved oppvarming?", IK, ["minimum +72 °C"]),
    q("Hvor lenge kan mat stå i varmholding på buffet?", IK, ["4 timer"]),
    q("Hvor lenge er karantenen etter magesyke?", IK, ["48 timer"]),
    q("Hvem har skadedyrkontrollen?", IK, ["Pest Control AS"]),
    # Brann, sikring og kapasitet
    q("Hvor mange personer kan være i Sal A samtidig?", BRANN, ["maks personer: 50"]),
    q("Hvor mange personer kan være i museet samtidig?", BRANN, ["250"]),
    q("Hvilke verk skal evakueres umiddelbart?", BRANN, ["Skrik"]),
    q("Hva betyr rødt klistremerke bak en ramme?", BRANN, ["Evakueres umiddelbart"]),
    # Tilsynskalender
    q("Når er brannøvelsen?", TILSYN, ["Mars"]),
    q("Hvem har ansvar for vernerunden i september?", TILSYN, ["Verneombud"]),
    q("Hvilken myndighet fører tilsyn med IK-Mat?", TILSYN, ["Mattilsynet"]),
    q("Når kalibreres hygrografene?", TILSYN, ["November"]),
    # Roller og ansvar
    q("Hva er Driftsansvarlig sitt ansvar?", ROSTER, ["Samsvar med Mattilsynet"]),
    q("Hva gjør kvalitetsvokteren?", ROSTER, ["Verifiserer mot lover"]),
    q("Hvor mange ord skal en veggtekst ha?", ROSTER, ["50–90 ord"]),
    # Tiltak (kun ledelse)
    q("Hva er ambisjonen for digital formidling?", TILTAK, ["digital formidling"], rolle="museumsdirektor"),
]

# Dataene har bevisst ikke personal-, lønns- eller navnedata. Riktig svar er et ærlig «ikke i dataene».
UBESVARBARE: list[dict] = [
    {"sporsmal": s, "rolle": "museumsvert"}
    for s in [
        "Hvor mange feriedager har en museumsvert?",
        "Hva er lønnen til en kurator?",
        "Hva står det om overtid i arbeidskontrakten?",
        "Hva heter verneombudet vårt?",
        "Hvor mye sykepenger får jeg ved sykdom?",
        "Hvem sitter i styret?",
        "Hvor mange dager permisjon kan jeg ta?",
        "Hva er reglene for hjemmekontor?",
        "Hvilken pensjonsordning har vi?",
        "Hva er været i morgen?",
    ]
]

# H5: 14 spørsmål som de nye styringsdataene dekker + 6 spørsmål som skal avslås
H5_DEKKET: list[dict] = [
    q("Hvem har kontakten med Mattilsynet?", MYNDIGHET, ["Mattilsynet", "Kafeansvarlig"]),
    q("Hva gjør vi første dagen etter varsel om tilsyn?", TILSYNSBESOK, ["Driftsansvarlig", "kvalitetssystemet"]),
    q("Hva trenger Arbeidstilsynet av dokumentasjon?", MYNDIGHET, ["risikovurdering", "avvikslogger"]),
    q("Hvem er kontaktpunkt mot Kulturdirektoratet?", MYNDIGHET, ["Kulturdirektoratet", "Museumsdirektør"]),
    q("Hvilken rapport skal leveres i mars?", RAPPORTERING, ["Mars"]),
    q("Hvem godkjenner rapporter før de sendes ut?", RAPPORTERING, ["eier"]),
    q("Hvilke datakilder bruker driftsrapporten?", RAPPORTERING, ["driftslogg"]),
    q("Hva skal stå i en avviksrapport?", RAPPORTMALER, ["Hva skjedde"]),
    q("Hvem skriver styrerapporten?", RAPPORTERING, ["Styrerapport", "Museumsdirektør"]),
    q("Hvilke rapporter går til eksterne mottakere?", RAPPORTERING, ["ekstern"]),
    q("Hvor mange timer bruker vi på tilskuddsrapportering?", ARBEIDSOPPGAVER, ["36"], rolle="museumsdirektor"),
    q("Hva bruker vi mest tid på innen myndighetskontakt?", ARBEIDSOPPGAVER, ["Tilskuddssøknad"], rolle="museumsdirektor"),
    q("Hvilke oppgaver bør automatiseres først?", ARBEIDSOPPGAVER, ["Høy"], rolle="museumsdirektor"),
    q("Hvor lenge har vi på å lukke et gult avvik etter tilsyn?", TILSYNSBESOK, ["14 dager"]),
]

H5_UBESVARBARE: list[dict] = [
    {"sporsmal": s, "rolle": "museumsvert"}
    for s in [
        "Hva er telefonnummeret til Mattilsynet?",
        "Hva stod i rapporten fra forrige tilsyn?",
        "Hvor mye fikk vi i tilskudd i fjor?",
        "Hva sier loven om oppbevaring av temperaturlogger?",
        "Hvem kommer fra tilsynet neste gang?",
        "Hvor mange timer bruker jeg personlig på rapporter?",
    ]
]

assert len(DEKKET) == 30 and len(UBESVARBARE) == 10
assert len(H5_DEKKET) == 14 and len(H5_UBESVARBARE) == 6
