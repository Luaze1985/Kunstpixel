"""Genererer bestillingen til den andre språkmodellen fra de samme tabellene som kontrollen bruker.

Bestillingen skrives på nytt fra koden, så den kan aldri komme ut av takt med kontrollen.
"""

from __future__ import annotations

from pathlib import Path

try:  # i repoet
    from src.kunstpixel.core.intern.leveranse import FILER, KILDER_TILLATT, NAVN, PLASSHOLDER, ROLLER_TILLATT, skjelett_tekst
except ImportError:  # i Colab-pakken, der filene ligger side om side
    from leveranse import FILER, KILDER_TILLATT, NAVN, PLASSHOLDER, ROLLER_TILLATT, skjelett_tekst  # type: ignore[no-redef]

KJERNE = f"""# Bestilling: syntetisk fyll for et kunstmuseum

## Oppdraget
Du skal skrive **fritekst** i ferdige YAML-skjelett. Dataene er trenings- og demodata for en intern assistent
hos et fiktivt museum (Kunstpixel). De handler om to ting museet bruker tid på: **kontakt med myndigheter** og
**rapportering**. Alt er oppdiktet. Ingenting er ekte, og ingenting skal ligne på ekte personer eller saker.

Historikkfilen (`historikk_tekst.yaml`) har ett år per oppføring, fra 2010 til 2026. Temaet og nøkkeltallene for hvert år
står ferdig. Skriv `hendelse` og `laerdom` slik at de passer til temaet og tallene for akkurat det året, for eksempel
lavt besøk og stengte perioder når temaet er pandemi. Ikke skriv tall eller årstall i teksten. Tekstene må være ulike fra
år til år, og tonen skal være nøktern og konkret.

## Slik jobber du
1. Du får ett eller flere skjelett. Alle faste felt er allerede fylt ut: id-er, navn, roller, tall, valg og strukturen.
2. Du skriver bare der det står `{PLASSHOLDER}`. Teksten i parentesen forteller hva som skal stå der.
3. Erstatt HELE verdien, inkludert `{PLASSHOLDER}` og parentesen. Verdien skal bare inneholde den ferdige teksten.
4. Der det står `{PLASSHOLDER}_KILDER`: skriv en liste med verdier fra listen i parentesen, og ingen andre.
5. Der det står `{PLASSHOLDER}_LISTE`: skriv en liste med 2 eller 3 korte regler.
6. Lever hele filen på nytt. Ikke utelat noe, ikke legg til felt, ikke endre rekkefølge.

## Skriveregler (kontrolleres automatisk, brudd gir feil)
- Norsk bokmål. Korte, konkrete setninger som beskriver, ikke setninger som snakker til leseren.
- **Ingen tall i fritekst.** Ikke sifre, ikke datoer, ikke frister, ikke prosent, ikke beløp, ikke antall. Tall er allerede satt i de faste feltene.
- **Ingen personnavn i fritekst.** Bruk roller, og bare disse: {', '.join(ROLLER_TILLATT)}. Feltene `kontaktperson`, `intern_eier_navn` og e-postfeltene er oppdiktede og ferdig utfylt av koden. Ikke endre dem, og ikke gjenta navnene i fritekst.
- **Ingen kontaktdetaljer i fritekst:** ingen e-post, telefonnummer, adresser eller lenker.
- **Ingen paragrafer og ingen sitater fra lover eller forskrifter.** Du kan beskrive hva en myndighet vanligvis ber om, uten å vise til lovtekst.
- Ingen emoji, ingen overskrifter, ingen markdown i verdiene, ingen kodegjerder rundt filen.
- Hver tekst skal være **unik**. Ikke kopier setninger mellom felt eller oppføringer.
- Hver tekst skal være mellom 20 og 160 tegn, med mindre skjelettet sier noe annet.
- Ikke skriv som en chat-assistent. Ingen «Her er», «Selvfølgelig» eller forklaringer før eller etter filen.
- Ikke finn på nye myndigheter, roller, frister eller rapporter.

## Eksempler
Bra:
- `hva_de_vil`: Dokumentert internkontroll og oversikt over hvordan avvik følges opp.
- `utloser`: Varslet tilsyn, uvarslet besøk eller klage fra en gjest.
- `begrunnelse`: Rapporten bygger på data som allerede finnes og kan settes sammen uten skjønn.

Dårlig, og hvorfor:
- «Frist: 30 dager etter besøket.» (tall)
- «Ta kontakt med Kari på kari@eksempel.no.» (personnavn og e-post)
- «I henhold til § 5 skal virksomheten...» (paragraf)
- «Selvfølgelig! Her er teksten du ba om.» (chat-snakk)

## Selvsjekk før du leverer
- Står det noen `{PLASSHOLDER}` igjen? Da er du ikke ferdig.
- Finnes det sifre i noen av tekstene dine? Fjern dem.
- Er to tekster like eller nesten like? Skriv om en av dem.
- Har du endret en id, et navn, en rolle eller et tall? Endre det tilbake.
- Er filen ren YAML uten tekst rundt?

## Hva skjer etterpå
En kontroll sammenligner leveransen din med skjelettet og sender deg en liste over feil. Du retter og leverer hele filene på nytt.
Det tas høyst tre runder. Deretter vurderer et menneske resultatet. Ingenting tas i bruk uten menneskelig godkjenning.

## Levering
Lever hver fil som en egen blokk, merket med filnavnet:

### filnavn.yaml
```yaml
...
```
"""


def bestilling_for(koder: list[str]) -> str:
    deler = [KJERNE, "## Skjelettene\n"]
    for k in koder:
        deler.append(f"### {FILER[k]}  ({NAVN[k]})\n```yaml\n{skjelett_tekst(k)}```\n")
    return "\n".join(deler)


PAKKEFILER = ("leveranse.py", "leveranse_bestilling.py", "leveranse_kjoring.py")


def skriv_colab_pakke(mappe: Path) -> list[Path]:
    """Kopierer de tre filene uendret til en mappe, med sjekksum, så de kan lastes opp i Colab."""
    import hashlib

    kilde = Path(__file__).resolve().parent
    mappe.mkdir(parents=True, exist_ok=True)
    ut: list[Path] = []
    sjekksummer: list[str] = []
    for navn in PAKKEFILER:
        data = (kilde / navn).read_bytes()
        (mappe / navn).write_bytes(data)
        sjekksummer.append(f"{hashlib.sha256(data).hexdigest()}  {navn}")
        ut.append(mappe / navn)
    (mappe / "SJEKKSUM.txt").write_text("\n".join(sjekksummer) + "\n", encoding="utf-8")
    ut.append(mappe / "SJEKKSUM.txt")
    return ut


def skriv_bestillinger(mappe: Path) -> list[Path]:
    mappe.mkdir(parents=True, exist_ok=True)
    ut: list[Path] = []
    p = mappe / "komplett.md"
    p.write_text(bestilling_for(list(FILER)), encoding="utf-8")
    ut.append(p)
    for k in FILER:
        p = mappe / f"fil_{k}_{FILER[k].removesuffix('.yaml')}.md"
        p.write_text(bestilling_for([k]), encoding="utf-8")
        ut.append(p)
    return ut


assert KILDER_TILLATT  # brukes av skjelettene
