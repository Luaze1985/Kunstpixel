# Slik leverer du Colab-dataene, steg for steg

*Bruk denne når databasen er ferdig i Colab. Hvorfor merkingen ser slik ut, står i [`merkeplan_colab_data.md`](merkeplan_colab_data.md).*

## Huskeliste

1. Lagre til Disk, ikke bare til Colab.
2. Kjør hjelpecellen. Den lister alle tabeller og foreslår merking.
3. Rett forslaget der det er feil, og kjør merkecellen.
4. Sjekk at tre filer ligger i mappen på Disk.
5. Skriv en kort `LESMEG.md`.
6. Send meg meldingen nederst.

Regn med 30–60 minutter når du har mange tabeller. Mesteparten av tiden går til steg 3.

---

## Steg 1. Koble Colab til Disk

Lim inn øverst i notatboken og kjør:

```python
from google.colab import drive
drive.mount("/content/drive")
import os
MAPPE = "/content/drive/MyDrive/Kunstpixel/05_data/innkommende/2026-10-27_stor_database"   # bytt dato og navn
os.makedirs(MAPPE, exist_ok=True)
DB = f"{MAPPE}/kunstpixel_stor.db"
```

Skriv databasen til `DB`. Alt som bare ligger i `/content`, forsvinner når økten stopper. Det var det som skjedde i morges.

**Har du flere databaser?** Gi hver sin mappe og lever én om gangen.

## Steg 2. Hjelpecellen: få oversikt over alle tabellene

Når du har mange tabeller, skal du ikke skrive merkingen for hånd. Denne cellen leser databasen og skriver ut et ferdig forslag du kan kopiere:

```python
import sqlite3, re
con = sqlite3.connect(DB)
FOLSOM = {  # rekkefølgen teller: første treff vinner
    "fnr": r"fnr|fodselsnummer|personnr", "fodselsdato": r"fodsels(dato|aar)|birth",
    "fagforening": r"fagforening|union", "helse": r"helse|diagnose|sykdom|art9|bht",
    "okonomi": r"skatt|formue|inntekt", "lonn": r"lonn|salary",
    "familie": r"sivilstand|barn|paarorende|partner", "adresse": r"adresse|gate|postnr|postnummer",
    "navn": r"(^|_)(navn|name|fornavn|etternavn)($|_)", "epost": r"(^|_)e?-?post($|_)|mail",
    "telefon": r"tlf|telefon|mobil|phone", "lokasjon": r"lokasjon|posisjon|gps|pendler",
    "fritekst": r"fritekst|beskrivelse|kommentar|notat",
}
TUNGE = {"helse", "fagforening", "okonomi", "familie"}
PERSON_ID = r"ansatt_id|person_id"
tabeller = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name not like '\\_%' escape '\\' and name != 'sqlite_sequence' order by name")]
print("TABELLER = {")
kolonner = []
for t in tabeller:
    n = con.execute(f'select count(*) from "{t}"').fetchone()[0]
    typer, navn = set(), [r[1] for r in con.execute(f'pragma table_info("{t}")')]
    for k in navn:
        for typ, mønster in FOLSOM.items():
            if re.search(mønster, k.lower()):
                typer.add(typ); kolonner.append((t, k, typ, "saerlig_kategori" if typ in TUNGE else "personopplysning")); break
    knyttet = any(re.search(PERSON_ID, k.lower()) for k in navn)
    if typer & TUNGE:
        forslag = ("saerlig_kategori", "undervisning", "museumsdirektor")
    elif typer or knyttet:
        forslag = ("personopplysning", "assistent", "museumsdirektor,driftsansvarlig")
    else:
        forslag = ("intern", "assistent", "alle")
    merk = sorted(typer) + (["knyttet til person"] if knyttet else []) + (["SJEKK: sykefravær er helse"] if re.search("fravaer|syk", t) else [])
    print(f'    "{t}": {forslag},   # {n} rader' + (f", {', '.join(merk)}" if merk else ""))
print("}\n\nKOLONNER = [")
for k in kolonner:
    print(f"    {k},")
print("]")
con.close()
```

Den endrer ingenting i databasen, den bare skriver ut.

## Steg 3. Gå gjennom forslaget og kjør merkecellen

1. Kopier utskriften inn i merkecellen fra [`merkeplan_colab_data.md`](merkeplan_colab_data.md), der det står `TABELLER = {…}` og `KOLONNER = […]`. Bytt `DB`-linjen i merkecellen med din egen sti fra steg 1.
2. Gå gjennom linje for linje. Hjelpecellen gjetter ut fra kolonnenavn, så den kan ta feil begge veier:
   - **Kolonner den ikke fant:** en kolonne som heter `info` eller `x1`, men inneholder helse, må du legge til selv.
   - **Kolonner den fant feil:** `beskrivelse` om en vakt er ikke følsom, så slett den linjen fra `KOLONNER`.
   - **Sykefravær:** fravær knyttet til en ansatt er helseopplysning. Hjelpecellen skriver `SJEKK` ved slike tabeller. Bestem selv om tabellen skal brukes av assistenten med streng tilgang, eller bare i undervisning.
   - **Adresser:** merkecellen bytter ut e-post, telefon og fødselsnummer, men ikke adresser. Fjern gatenavn i Colab før du merker, og behold bare bydel og postnummer.
   - **Tilgang:** bruk bare `museumsdirektor`, `samlingsforvalter`, `kurator`, `formidler`, `museumsvert`, `driftsansvarlig`, `kvalitetsvokter` eller `alle`.
3. Kjør merkecellen. Stopper den med «Disse tabellene mangler merking», har du glemt en tabell. Legg den til og kjør på nytt.

**Er du usikker på en tabell?** Sett den til `("saerlig_kategori", "undervisning", "museumsdirektor")`. Det er det strengeste valget, og det er lett å åpne opp senere. Det motsatte er vanskelig.

## Steg 4. Sjekk at filene ligger på Disk

Åpne Utforsker på PC-en og gå til `G:\Min disk\Kunstpixel\05_data\innkommende\2026-10-27_stor_database\`. Der skal du finne:

| Fil | Hva den er |
|---|---|
| `kunstpixel_stor.db` | Databasen |
| `kunstpixel_stor.MANIFEST.json` | Radantall og sjekksum per tabell |
| `LESMEG.md` | Notatet ditt (steg 5) |

Det kan ta noen minutter før Google Disk har synket store filer. Vent til filstørrelsen står stille.

Mappen `innkommende` kommer ikke inn i git. Dataene blir der til de er kontrollert.

## Steg 5. Skriv `LESMEG.md` (5 minutter)

Lag filen i samme mappe og fyll inn malen. Svar kort, og stikkord holder.

```markdown
# Levering: <navn>, <dato>

## Hva er dette
- Hva databasen skal vise (1–2 setninger):
- Hvilke år den dekker:
- Hvor mange ansatte og vakter, omtrent:

## Hvordan den ble laget
- Notatbok (navn på Disk):
- Frø (seed), så den kan lages på nytt:
- Er noe skrevet av en språkmodell (fritekst)? Hvilke kolonner:

## Forhold til det vi har
- Skal den erstatte noe i museum.db, legges ved siden av, eller være et eget case?
- Tabeller som overlapper med museum.db:

## Grensecase
- Hvilke tabeller er ment for undervisning (personvern, OSINT, helse)?
- Hva skal caset vise?

## Ting jeg er usikker på
-
```

## Steg 6. Send meg denne meldingen

Kopier og lim inn i en ny samtale med meg i Kunstpixel-mappen. Bytt ut det som står i `< >`:

```text
Ny levering fra Colab ligger i 05_data/innkommende/<mappenavn>/.
Les LESMEG.md først. Les databasen bare med mode=ro, og ikke endre noe.
1. Kontroller merkingen mot merkeplan_colab_data.md og manifestet.
2. Sammenlign med museum.db v4: overlapp, avvik og hva som er nytt.
3. Gi meg en rapport i klarspråk: KLAR eller liste med feil.
Ta beslutningene med meg én om gangen før du skriver byggeskript.
```

## Hvordan vi tar diskusjonen

Vi tar det i fire runder. Hver runde slutter med en beslutning, slik at ingenting blir hengende.

| Runde | Hva vi snakker om | Hvem bestemmer | Typisk tid |
|---|---|---|---|
| 1. Rapport | Jeg viser hva som er i databasen, hva som feiler kontrollen og hva som overlapper med `museum.db`. | Ingen beslutning, bare forståelse | 15 min |
| 2. Rettinger | Feil i merkingen rettes i Colab, ikke av meg, og leveres på nytt. Maks tre runder, som for H5. | Du | Varierer |
| 3. Plass og tilgang | Én spørsmål om gangen: hvilke tabeller blir fasit, hva erstattes, hvem får se hva. | Du, og medgründeren din for tilgang | 30 min |
| 4. Bygg | Jeg skriver byggeskript og tester. **Du** bygger `museum.db` og kjører statusporten. | Du godkjenner diffen | 30 min |

**Med medgründeren din** bør dere være enige om tre ting før runde 3:
1. Hvem i det tenkte museet skal se lønn, fravær og helse? Det setter `tilgang`.
2. Hva skal grensecaset lære bort? For eksempel at koblinger av «harmløse» data avslører mye. Det avgjør hvilke tabeller som blir undervisning.
3. Skal undervisningscaset noen gang vises til en ekstern modell? Min anbefaling er nei, bare regelbasert visning og avslagstester.

**Mellom rundene:** del gjerne opp hvis du har mange tabeller. Lever HR- og vakttabellene først, siden de er det assistenten trenger. Lever grensecaset til slutt.

## Hvis noe går galt

| Det som skjer | Hva du gjør |
|---|---|
| Colab sier `AssertionError: … mangler merking` | Legg til tabellen i `TABELLER`, og kjør på nytt. |
| Filen dukker ikke opp på PC-en | Vent på synk. Sjekk i nettleseren på drive.google.com at den ligger der. |
| Databasen er over 2 GB | Si fra i meldingen, så deler vi den opp. |
| Du ombestemmer deg om merkingen | Kjør merkecellen på nytt. Den sletter og lager merketabellene på nytt hver gang. |
