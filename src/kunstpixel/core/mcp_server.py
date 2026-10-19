"""FastMCP server for Aura Kunstmuseum exposing 5 collection and visitor tools.

Strictly read-only, SQL-injection safe, and adhering to museum domain terminology.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.kunstpixel.core.db import (
    VALID_ROOM_IDS,
    audit_shift_aml_compliance,
    normalize_room_identifier,
    query_archive_exhibitions,
    query_artwork_details,
    query_cleaning_registry,
    query_collection,
    query_condition_report,
    query_contractors,
    query_employee_cv,
    query_events,
    query_exhibition_economy,
    query_faq,
    query_handbook,
    query_holidays,
    query_incidents,
    query_loans,
    query_quarterly_absence,
    query_room_artworks,
    query_station_ergonomics,
    query_styrk_job_code,
    query_supplier_brreg,
    query_tariff_pay,
)

from src.kunstpixel.core.hr_eval import evaluate_staffing_proposal
from src.kunstpixel.core.hrdemo import (
    candidates,
    count_skill,
    find_rules,
    get_person,
    list_skills,
    search_hms_guidance as find_hms_guidance,
)

# Initialize FastMCP application
mcp = FastMCP("Kunstpixel")



@mcp.tool()
def search_collection(
    query: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    technique: str | None = None,
    theme: str | None = None,
    room_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i museets samling etter verk basert på kunstner, tittel, teknikk, tema eller sal.

    Args:
        query: Fritekstsøk i tittel, kunstner, teknikk, temaer, sal og beskrivelse.
        artist: Filtrer på kunstnerens navn (f.eks. 'Theodor Kittelsen' eller 'Kittelsen').
        title: Filtrer på verktittel (f.eks. 'Skrik' eller 'Nøkken').
        technique: Filtrer på teknikk (f.eks. 'Olje på lerret' eller 'Pastell').
        theme: Filtrer på tematisk emneord (f.eks. 'mytologi', 'natur', 'angst').
        room_id: Filtrer på sal-ID (f.eks. 'SAL-A', 'SAL-D').
        limit: Maksimalt antall verk (standard 10, maks 50).

    Returns:
        Liste med verkskort som matcher kriteriene.
    """
    return query_collection(
        query=query,
        artist=artist,
        title=title,
        technique=technique,
        theme=theme,
        room_id=room_id,
        limit=limit,
    )


@mcp.tool()
def get_artwork_details(artwork_id: str) -> dict[str, Any]:
    """Hent komplette og autoritative metadata for et spesifikt kunstverk, inkludert veggtekst og proveniens.

    Args:
        artwork_id: Kunstverkets unike inventarnummer (f.eks. 'AURA-2026-009') eller eksakt tittel.

    Returns:
        Fullstendig verkskort med kunstnerbiografi, teknikk, sal, tilstand, veggtekst og proveniens.
        Returnerer strukturert feilobjekt med code='NOT_FOUND' dersom verket ikke finnes.
    """
    details = query_artwork_details(artwork_id)
    if details is None:
        return {
            "error": f"Verk med ID eller tittel '{artwork_id}' ble ikke funnet i samlingsdatabasen.",
            "artwork_id": artwork_id,
            "code": "NOT_FOUND",
        }
    return details


@mcp.tool()
def get_room_artworks(room_id: str) -> list[dict[str, Any]] | dict[str, Any]:
    """List alle utstilte verk i en gitt sal, ordnet etter visningsrekkefølge.

    Args:
        room_id: Salens identifikator (f.eks. 'SAL-A', 'SAL-B', 'SAL-C', 'SAL-D', 'SAL-E', 'MAG-1').

    Returns:
        Liste over utstilte verk i salen ordnet etter visningsrekkefølge.
        Returnerer feilmelding dersom sal-ID er ugyldig.
    """
    norm_room = normalize_room_identifier(room_id)
    if norm_room not in VALID_ROOM_IDS:
        return {
            "error": f"Ukjent sal-ID '{room_id}'",
            "valid_rooms": VALID_ROOM_IDS,
            "code": "INVALID_ROOM",
        }
    return query_room_artworks(room_id)


@mcp.tool()
def search_events(
    event_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Finn kommende hendelser og arrangementer på museet (omvisninger, verksteder, foredrag).

    Args:
        event_type: Type hendelse (f.eks. 'omvisning', 'verksted', 'foredrag', 'barnearrangement').
        date_from: Fra og med dato (ISO-format YYYY-MM-DD). Standard er dagens dato.
        date_to: Til og med dato (ISO-format YYYY-MM-DD).
        limit: Maksimalt antall hendelser som returneres (standard 5).

    Returns:
        Liste over bekreftede og planlagte arrangementer med dato, tid, sal og billettpriser.
    """
    return query_events(
        event_type=event_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@mcp.tool()
def search_faq(
    query: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Søk i publikums-FAQ etter autoritative svar på praktiske spørsmål.

    Args:
        query: Søkeord fra den besøkendes spørsmål (f.eks. 'åpningstider', 'pris', 'billett', 'kafé', 'parkering').
        category: Valgfri kategori for filtrering (f.eks. 'billett', 'praktisk', 'fasiliteter', 'formidling').

    Returns:
        Liste med relevante FAQ-oppslag rangert etter relevans og hyppighet.
    """
    return query_faq(query=query, category=category)


@mcp.tool()
def search_archive_exhibitions(
    query: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    curator: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i Kunstpixels 16-årige utstillingsarkiv (2010–2026) etter temaer, kuratorer, saler og budsjett.

    Args:
        query: Fritekstsøk i tittel eller saler (f.eks. 'modernisme', 'Bergman', 'Sal D').
        year_from: Fra og med årstall (f.eks. 2015).
        year_to: Til og med årstall (f.eks. 2024).
        curator: Filtrer på ansvarlig kurator (f.eks. 'Silje Lindqvist').
        limit: Maksimalt antall utstillinger som returneres (standard 10).

    Returns:
        Liste over historiske utstillinger med sesong, saler, kurator, publikumstall, budsjett og status.
    """
    return query_archive_exhibitions(
        query=query,
        year_from=year_from,
        year_to=year_to,
        curator=curator,
        limit=limit,
    )


@mcp.tool()
def search_contractors(
    kategori: str | None = None,
    leverandor: str | None = None,
    aar: int | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i museets innleie- og konsulentregister for drift, scenografi, sikkerhet og konservering.

    Args:
        kategori: Type innleie (f.eks. 'Montering & Scenografi', 'Eksternt vakthold / Vernissasje', 'Gjestekurator', 'AV & Multimedieteknikk', 'Tilstandsvurdering & Konservering', 'Spesialtransport & Lånehåndtering').
        leverandor: Navn på leverandør (f.eks. 'Securitas AS', 'Avarn Security AS', 'Norsk Utstillingsmontasje AS', 'Atelier Konservering DA').
        aar: Spesifikt årstall for oppdraget (2010–2026).
        limit: Maksimalt antall kontrakter som returneres (standard 10).

    Returns:
        Liste over innleieavtaler med fakturerte timer, timepris, totalbeløp, oppdragsbeskrivelse og intern godkjenner.
    """
    return query_contractors(
        kategori=kategori,
        leverandor=leverandor,
        aar=aar,
        limit=limit,
    )


@mcp.tool()
def get_employee_cv(
    ident: str,
) -> dict[str, Any] | None:
    """Hent detaljert CV, personas, utdanning og publikasjonsliste for en ansatt eller fagperson.

    Args:
        ident: Ansatt-ID (f.eks. 'KP-ANS-001') eller fullt/delvis navn (f.eks. 'Henrik Faye-Lund', 'Silje Lindqvist', 'Gunnar Viken').

    Returns:
        Strukturert personas-objekt med grad, utdanningsinstitusjon, tidligere arbeidsgivere og fagpublikasjoner.
    """
    res = query_employee_cv(ident=ident)
    if not res:
        return {"error": f"Ingen persona eller CV funnet for '{ident}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def get_condition_report(artwork_id: str) -> dict[str, Any]:
    """Hent verkskonservering og tilstandsrapport med luks-krav, fuktighetskrav og forsikringsverdi (for samlingsforvalter/kurator).

    Args:
        artwork_id: Kunstverkets ID (f.eks. 'AURA-2026-009') eller tittel ('Skrik').

    Returns:
        Tilstandsrapport med tilstandsgrad (1-4), maks lux, klimakrav, konserveringslogg og forsikringsverdi i NOK.
    """
    res = query_condition_report(artwork_id=artwork_id)
    if not res:
        return {"error": f"Ingen tilstandsrapport funnet for '{artwork_id}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def search_loans(
    exhibition_id: str | None = None,
    query: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i historiske og aktive kunstlån fra eksterne museer (Nasjonalmuseet, KODE, Lillehammer m.fl.).

    Args:
        exhibition_id: Valgfri utstillings-ID (f.eks. 'KP-EXH-2024-001').
        query: Fritekst i tittel, kunstner eller utlånsinstitusjon.
        limit: Maksimalt antall utlån som returneres (standard 10).

    Returns:
        Liste over innlånte mesterverk med 3-lags formidlingstekst, forsikringsverdi og kurertransportkrav.
    """
    return query_loans(exhibition_id=exhibition_id, query=query, limit=limit)


@mcp.tool()
def get_exhibition_economy(exhibition_id: str) -> dict[str, Any]:
    """Hent fullstendig prosjektøkonomi og regnskap for en utstilling (budsjett, innleie, billettinntekter, netto resultat).

    Args:
        exhibition_id: Utstillings-ID (f.eks. 'KP-EXH-2024-001') eller tittel.

    Returns:
        Økonomisk sammendrag med budsjett, faktiske kostnader, billettinntekter, sponsorstøtte og avviksforklaring.
    """
    res = query_exhibition_economy(exhibition_id=exhibition_id)
    if not res:
        return {"error": f"Ingen økonomirapport funnet for '{exhibition_id}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def search_incidents(
    kategori: str | None = None,
    alvorlighetsgrad: str | None = None,
    sal_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Søk i museets operative avvikslogg (HMS, sikkerhetshendelser, klimasvingninger, teknisk feil og publikum).

    Args:
        kategori: Valgfri kategori ('HMS', 'SIKKERHET', 'KLIMA', 'TEKNISK', 'PUBLIKUM').
        alvorlighetsgrad: Valgfri alvorlighetsgrad ('GRØNN', 'GUL', 'RØD').
        sal_id: Filtrer på berørt sal (f.eks. 'SAL-A', 'MAG-1').
        limit: Maksimalt antall hendelser som returneres (standard 10).

    Returns:
        Liste over avvikshendelser med strakstiltak, ansvarlig leder og oppfølgingsstatus.
    """
    return query_incidents(kategori=kategori, alvorlighetsgrad=alvorlighetsgrad, sal_id=sal_id, limit=limit)


@mcp.tool()
def verify_supplier_brreg(orgnr_or_name: str) -> dict[str, Any]:
    """Verifiser en leverandør mot autoritative Enhetsregister-data fra Brønnøysundregistrene (Brreg).

    Args:
        orgnr_or_name: Organisasjonsnummer (f.eks. '912876543') eller firmanavn (f.eks. 'Securitas AS').

    Returns:
        Fullt selskapsregister med org.form, MVA-status, konkursstatus, antall ansatte og aksjekapital.
    """
    res = query_supplier_brreg(orgnr_or_name=orgnr_or_name)
    if not res:
        return {"error": f"Ingen registrert enhet funnet i Brreg for '{orgnr_or_name}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def calculate_shift_cost(
    lonnstrinn: int,
    timer: float = 7.5,
    er_kveld: bool = False,
    er_helg: bool = False,
    er_helligdag: bool = False,
) -> dict[str, Any]:
    """Beregn lønnskostnad for et skift basert på Virke Landsoverenskomst for museer (lønnstrinn 20–65).

    Args:
        lonnstrinn: Virke lønnstrinn (20 til 65).
        timer: Antall arbeidstimer for skiftet (standard 7.5).
        er_kveld: Sann hvis skiftet avvikles etter kl. 17:00 (kveldstillegg).
        er_helg: Sann hvis skiftet er lagt til lørdag eller søndag (helgetillegg).
        er_helligdag: Sann hvis skiftet er på en rød dag (133% helligdagstillegg).

    Returns:
        Strukturert lønnsberegning med ordinær timesats, tillegg og total personalkostnad.
    """
    tariff = query_tariff_pay(lonnstrinn=lonnstrinn)
    if not tariff:
        return {"error": f"Ugyldig Virke-lønnstrinn: {lonnstrinn} (må være mellom 20 og 65)", "code": "INVALID_STEP"}

    if er_helligdag:
        effective_rate = tariff["timesats_helligdag"]
        applied_type = "Helligdag (133% overtid)"
    elif er_helg:
        effective_rate = tariff["timesats_helg"]
        applied_type = "Helgetillegg (+75 kr/t)"
    elif er_kveld:
        effective_rate = tariff["timesats_kveld"]
        applied_type = "Kveldstillegg (+56 kr/t etter kl 17)"
    else:
        effective_rate = tariff["timesats_ordinar"]
        applied_type = "Ordinær dagtid"

    total_cost = round(effective_rate * timer, 2)
    return {
        "lonnstrinn": lonnstrinn,
        "rolle": tariff["tittel_eksempel"],
        "timer": timer,
        "sats_anvendt": effective_rate,
        "tilleggstype": applied_type,
        "total_kostnad_nok": total_cost,
        "tariff_kilde": "Virke Landsoverenskomst for museer",
    }


# --- HR, HMS & Kvalitetsverktøy (integrert) ---
@mcp.tool()
def count_documented_skill(code: str, as_of: str = "2026-11-07") -> dict:
    """Fortell nøyaktig hvor mange aktive ansatte som har dokumentert og gyldig kompetansebevis."""
    return count_skill(code, as_of)


@mcp.tool()
def propose_kiosk_staffing(
    work_date: str = "2026-11-07",
    start: str = "10:00",
    end: str = "16:00",
    need: int = 5,
) -> dict:
    """Få eksplisitte harde krav, reproduserbar relevansscore og full evidens for bemanningskandidater."""
    return candidates(work_date, start, end, need)


@mcp.tool()
def lookup_hr_hms_quality_rules(
    domain: str | None = None,
    topic: str | None = None,
    as_of: str = "2026-11-07",
) -> list[dict]:
    """Søk i strukturerte museumsprosedyrer på tvers av HR, HMS og KVALITET."""
    return find_rules(domain, topic, as_of)


@mcp.tool()
def get_competence_catalog() -> list[dict]:
    """Vis komplett katalog over alle definerte ferdigheter, krav og utløpsregler."""
    return list_skills()


@mcp.tool()
def get_staff_member(person_id: str, as_of: str = "2026-11-07") -> dict:
    """Hent komplett ansattkort med dokumenterte kompetanser og tilgjengelighet."""
    res = get_person(person_id, as_of=as_of)
    if res is None:
        return {"error": "PERSON_NOT_FOUND", "person_id": person_id}
    return res


@mcp.tool()
def evaluate_kiosk_proposal(
    suggested_ids: list[str],
    work_date: str = "2026-11-07",
    need: int = 5,
) -> dict:
    """Evaluer et foreslått bemanningsforslag deterministisk mot sikkerhetskrav og kognitive KI-feller (L01-L03)."""
    return evaluate_staffing_proposal(suggested_ids, work_date=work_date, need=need)


# --- Kategori C: HR, HMS, Arbeidsmiljø & Arbeidstid ---
@mcp.tool()
def audit_shift_compliance(
    ansatt_id: str,
    dato: str,
    start: str = "08:00",
    end: str = "16:00",
) -> dict[str, Any]:
    """Evaluer et planlagt skift deterministisk mot Arbeidsmiljøloven kap. 10 (§ 10-8 hviletid og § 10-4 arbeidstid).

    Args:
        ansatt_id: Ansatt-ID (f.eks. 'KP-ANS-001' eller 'E101').
        dato: Dato for skiftet (ISO-format YYYY-MM-DD).
        start: Starttidspunkt (f.eks. '08:00' eller '15:30').
        end: Sluttidspunkt (f.eks. '16:00' eller '23:00').

    Returns:
        Strukturert revisjonsrapport med status (APPROVED_AML / REJECTED_AML_VIOLATION), hviletimer og eventuelle lovbrudd.
    """
    return audit_shift_aml_compliance(ansatt_id=ansatt_id, dato=dato, start=start, end=end)


@mcp.tool()
def check_cleaning_supplier_approval(orgnr: str) -> dict[str, Any]:
    """Sjekk om en renholdsleverandør er offentlig godkjent i Arbeidstilsynets Renholdsregister.

    Args:
        orgnr: Organisasjonsnummer eller navn (f.eks. '982345678' for ISS Facility Services AS).

    Returns:
        Godkjenningsstatus, utløpsdato og krav om gyldige HMS-kort.
    """
    res = query_cleaning_registry(orgnr=orgnr)
    if not res:
        return {"error": f"Ingen renholdsleverandør funnet med orgnr/navn '{orgnr}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def get_job_profile_styrk(kode_or_stilling: str) -> dict[str, Any]:
    """Slå opp offisiell SSB STYRK-08 yrkeskode, utdanningskrav og minste Virke-lønnstrinn for en stilling.

    Args:
        kode_or_stilling: 4- eller 6-sifret STYRK-kode (f.eks. '2651.01') eller stillingstittel (f.eks. 'Kurator', 'Salvert', 'Konservator').

    Returns:
        Yrkesprofil med STYRK-kode, formelle utdanningskrav, ansvarsbeskrivelse og minste lønnstrinn.
    """
    res = query_styrk_job_code(code_or_title=kode_or_stilling)
    if not res:
        return {"error": f"Ingen STYRK-08 yrkeskode funnet for '{kode_or_stilling}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def get_calendar_holiday_info(dato: str) -> dict[str, Any]:
    """Sjekk om en gitt dato er offentlig høytidsdag (med 133% helligdagstillegg) eller skoleferie.

    Args:
        dato: Dato i ISO-format (YYYY-MM-DD), f.eks. '2024-05-17' eller '2025-04-18'.

    Returns:
        Kalenderinformasjon med høytidsnavn, overtidssatsfaktor (f.eks. 2.33) og ferieukestatus.
    """
    rows = query_holidays(date_str=dato, limit=1)
    if not rows:
        return {
            "dato": dato,
            "er_offentlig_hoytid": False,
            "navn": "Ordinær virkedag",
            "tillegg_faktor": 1.0,
            "skoleferie_type": None,
        }
    return rows[0]


@mcp.tool()
def get_ergonomic_rotation_rules(sal_or_station_id: str) -> dict[str, Any]:
    """Hent STAMI ergonomiske retningslinjer, maksimal ståtid og påbudt rotasjonsstasjon for et salareal.

    Args:
        sal_or_station_id: Stasjons-ID (f.eks. 'STASJON-SAL-D') eller salbetegnelse ('SAL-D', 'SAL-A', 'SKRANKE').

    Returns:
        Ergonomiske grenser med underlagstype, maksimal sammenhengende ståtid og anbefalt rotasjonsrekkefølge.
    """
    res = query_station_ergonomics(station_id=sal_or_station_id)
    if not res:
        return {"error": f"Ingen ergonomiske data funnet for '{sal_or_station_id}'", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def get_sickness_absence_statistics(year: int, quarter: int) -> dict[str, Any]:
    """Hent offisiell SSB sykefraværsstatistikk (tabell 12441) og anbefalt vikarbuffer for kultursektoren.

    Args:
        year: Årstall (2010–2026).
        quarter: Kvartal (1, 2, 3 eller 4).

    Returns:
        Sykefraværsrate i prosent (egenmeldt/legemeldt) og anbefalt vikarreservefaktor for vaktplanlegging.
    """
    res = query_quarterly_absence(year=year, quarter=quarter)
    if not res:
        return {"error": f"Ingen sykefraværsstatistikk funnet for {year}-Q{quarter}", "code": "NOT_FOUND"}
    return res


@mcp.tool()
def lookup_handbook(
    query: str | None = None,
    handbok: str | None = None,
    role: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Søk og slå opp autoritative regler i museets fire virksomhetshåndbøker (Personal, HMS, Drift, Ledelse).

    Args:
        query: Søkeord eller problemstilling (f.eks. 'egenmelding', 'hviletid', 'brann', 'løft', 'haccp', 'varsling').
        handbok: Valgfri håndbok ('PERSONAL', 'HMS_SIKKERHET', 'DRIFT_KVALITET', 'LEDER_BEREDSKAP').
        role: Målgruppe eller rollefilter (f.eks. 'vert', 'leder', 'kafé', 'montør').
        limit: Maksimalt antall oppslagspunkter som returneres (1–20, standard 5).

    Returns:
        Relevante håndbokpunkter med kapittel, tittel, juridisk hjemmel, innhold og målgruppe.
    """
    return query_handbook(query=query, handbok=handbok, role=role, limit=limit)


@mcp.tool()
def search_hms_guidance(
    query: str | None = None,
    topic: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Søk i 344 autoritative nasjonale HMS- og arbeidsmiljøveiledningspunkter (Arbeidstilsynet/BHT).

    Args:
        query: Fritekst-søkeord (f.eks. 'ergonomi', 'vernerunde', 'ulykke', 'psykososialt', 'støy').
        topic: Tema- eller kategorifilter (f.eks. 'Lederansvar', 'Risikovurdering', 'Lovverk').
        limit: Maksimalt antall veiledningspunkter som returneres (1–50, standard 5).

    Returns:
        Liste med strukturerte oppslag som inneholder id, tema, sporsmal, kort_svar og detaljert_veiledning.
    """
    return find_hms_guidance(query=query, topic=topic, limit=limit)


if __name__ == "__main__":
    mcp.run()


