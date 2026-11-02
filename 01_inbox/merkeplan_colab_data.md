# Merkeplan: slik merkes Colab-dataene før de kommer inn

*Skrevet 2026-10-27. Gjelder den store databasen du lager i Colab, og enhver senere database. Den er ikke levert ennå.*

## Kort fortalt

- **Du merker dataene i Colab**, mens du lager dem. Den som lager dataene vet best hva de er.
- **Du kontrollerer merkingen i VS Code** på din egen maskin med et fast skript. Det gir samme svar hver gang. Fungerer kontrollen, er databasen klar for meg.
- Merkingen er to små tabeller inne i selve databasen: én rad per tabell og én rad per følsom kolonne. Da følger merkingen alltid med filen.
- Tabeller med helse, fagforening, skatt eller formue blir **bare undervisningscase**. Assistenten svarer aldri fra dem.

## Hvorfor dette er nødvendig

Assistenten er fail-closed: alt den ikke vet sikkert er syntetisk, behandler den som `ekte`. Ekte data får ingen modell se, fordi lokal modell er på vent. En umerket database er derfor trygg, men ubrukelig for assistenten. Merkingen gjør dataene brukbare uten at sikkerheten svekkes.

## Hvor gjøres hva

| Steg | Hvor | Hvem |
|---|---|---|
| 1. Lag dataene | Colab | Du |
| 2. Merk tabeller og følsomme kolonner, og nøytraliser kontaktdata | Colab, i siste celle | Du (koden står under) |
| 3. Lagre `.db` og `MANIFEST.json` til **Disk**, ikke bare til `/content` | Colab | Du |
| 4. Kjør kontrollen | VS Code-terminalen | Du |
| 5. Les databasen med `mode=ro`, skriv rapport, byggeskript og tester | Repoet | Meg |
| 6. Bygg `museum.db` og kjør statusporten | VS Code | Du |

**Hvorfor ikke merke i VS Code?** Da må noen gjette i ettertid hva hver kolonne betyr. I Colab vet du det mens du lager den.

**Hvorfor kontrollere i VS Code?** Colab-modellen endret faste felt i morges. Kontrollen må kjøres et sted der modellen ikke kan endre den.

## Merkingen: to tabeller i databasen

### `_datamerking`, én rad per tabell

| Felt | Lovlige verdier | Eksempel |
|---|---|---|
| `tabell` | navnet på tabellen | `hr_vakter` |
| `klassifisering` | `syntetisk` eller `ekte` (eksakt, med små bokstaver) | `syntetisk` |
| `sensitivitet` | `aapen`, `intern`, `personopplysning`, `saerlig_kategori` | `personopplysning` |
| `formaal` | `assistent`, `undervisning`, `statistikk` | `assistent` |
| `tilgang` | roller skilt med komma, eller `alle` | `museumsdirektor,driftsansvarlig` |
| `generator` | hva som laget den | `colab_vaktgenerator` |
| `fro` | tilfeldighetsfrøet, så samme data kan lages igjen | `20261027` |
| `laget` | dato | `2026-10-27` |

### `_kolonnemerking`, én rad per kolonne som kan si noe om en person

| Felt | Lovlige verdier |
|---|---|
| `tabell`, `kolonne` | navn |
| `type` | `navn`, `epost`, `telefon`, `fnr`, `adresse`, `fodselsdato`, `helse`, `fagforening`, `okonomi` (skatt, formue, inntekt), `lonn`, `familie`, `lokasjon`, `fritekst` |
| `sensitivitet` | som over |

### Fem regler som kontrollen håndhever

1. Hver tabell har nøyaktig én rad i `_datamerking`.
2. En tabell med en kolonne av typen `helse`, `fagforening`, `okonomi` (skatt, formue) eller `familie` er `saerlig_kategori` med formål `undervisning`. Den kan aldri ha `assistent`.
3. E-post slutter på `.example.test`.
4. Telefon er enten tom eller på formen `SYNT-TLF-0001`. Ingen tall som ligner ekte numre.
5. Fødselsnummer består **aldri** kontrollsifferet (mod 11). Adresser har bare bydel og postnummer, ingen gatenavn.

Kolonner uten rad i `_kolonnemerking` regnes som harmløse. Kontrollen ser derfor også etter kolonnenavn som `navn`, `epost`, `telefon`, `fnr`, `adresse`, `helse`, `skatt` og `formue` som mangler merking.

### Rollene

`museumsdirektor`, `samlingsforvalter`, `kurator`, `formidler`, `museumsvert`, `driftsansvarlig` og `kvalitetsvokter`. Det er de samme som i den interne assistenten. Andre roller gir feil.

## Colab-cellen: lim inn som siste celle

```python
import sqlite3, hashlib, json, re, datetime, os

DB = "/content/drive/MyDrive/Kunstpixel/05_data/innkommende/kunstpixel_stor.db"   # Disk, ikke /content
FRO, GENERATOR, IDAG = 20261027, "colab_stor_database", datetime.date.today().isoformat()

# 1) Fyll inn én linje per tabell: (sensitivitet, formaal, tilgang)
TABELLER = {
    "hr_ansatte":  ("personopplysning", "assistent",    "museumsdirektor,driftsansvarlig"),
    "hr_vakter":   ("intern",           "assistent",    "alle"),
    # "ekstern_osint": ("saerlig_kategori", "undervisning", "museumsdirektor"),
}
# 2) Følsomme kolonner: (tabell, kolonne, type, sensitivitet)
KOLONNER = [
    ("hr_ansatte", "navn",    "navn",    "personopplysning"),
    ("hr_ansatte", "epost",   "epost",   "personopplysning"),
    ("hr_ansatte", "telefon", "telefon", "personopplysning"),
]

def ugyldig_fnr(fnr: str) -> str:
    """Beholder fødselsdatoen, men gjør kontrollsifferet feil med vilje."""
    d = [int(c) for c in re.sub(r"\D", "", fnr)][:9]
    k1 = 11 - sum(a * b for a, b in zip(d, [3, 7, 6, 1, 8, 9, 4, 5, 2])) % 11
    k1 = 0 if k1 == 11 else k1
    feil = (k1 + 1) % 10 if k1 < 10 else 0
    return "".join(map(str, d)) + f"{feil}0"

con = sqlite3.connect(DB)
alle = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name not like '\\_%' escape '\\' and name != 'sqlite_sequence'")]
mangler = sorted(set(alle) - set(TABELLER))
assert not mangler, f"Disse tabellene mangler merking: {mangler}"

for t, k, typ, _ in KOLONNER:
    rader = con.execute(f'select rowid, "{k}" from "{t}"').fetchall()
    for i, (rid, v) in enumerate(rader, 1):
        if v is None:
            continue
        if typ == "epost":
            ny = re.sub(r"@.*$", "@kunstpixel.example.test", v)
        elif typ == "telefon":
            ny = f"SYNT-TLF-{i:04d}"
        elif typ == "fnr":
            ny = ugyldig_fnr(v)
        else:
            continue
        con.execute(f'update "{t}" set "{k}"=? where rowid=?', (ny, rid))

con.execute("drop table if exists _datamerking"); con.execute("drop table if exists _kolonnemerking")
con.execute("create table _datamerking(tabell text primary key, klassifisering text, sensitivitet text, formaal text, tilgang text, generator text, fro integer, laget text)")
con.execute("create table _kolonnemerking(tabell text, kolonne text, type text, sensitivitet text, primary key(tabell, kolonne))")
for t, (s, f, tg) in TABELLER.items():
    con.execute("insert into _datamerking values (?,?,?,?,?,?,?,?)", (t, "syntetisk", s, f, tg, GENERATOR, FRO, IDAG))
con.executemany("insert into _kolonnemerking values (?,?,?,?)", KOLONNER)
con.commit()

# 3) Manifest med sjekksum per tabell
manifest = {"generator": GENERATOR, "fro": FRO, "laget": IDAG, "tabeller": {}}
for t in alle + ["_datamerking", "_kolonnemerking"]:
    rader = con.execute(f'select * from "{t}" order by 1').fetchall()
    manifest["tabeller"][t] = {"rader": len(rader), "sha256": hashlib.sha256(repr(rader).encode()).hexdigest()}
con.close()
with open(os.path.splitext(DB)[0] + ".MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("Merket", len(alle), "tabeller. Lagret på Disk:", DB)
```

Cellen stopper med feil hvis en tabell mangler merking. Det er meningen.

## Kontrollen i VS Code

Skriptet finnes ikke ennå. Jeg lager det når du sier fra. Det blir:

```powershell
py -3.13 scripts/kontroller_merking.py "05_data/innkommende/kunstpixel_stor.db"
```

Skriptet åpner databasen med `mode=ro`, sjekker de fem reglene og manifestet, og skriver svaret i klartekst: **KLAR** eller en liste med feil og hvor de står. Det kobles til samme sted som kvalitetssjekkene som kjører på lagring i VS Code, og til statusporten (P3) på `hr-konsolidering`.

## Etterpå: kobling til assistenten (min del)

1. Datapolicyen leser `klassifisering` fra `_datamerking`. Feltet `datakilde` (`syntetisk (archive_generator)`) beholdes bare som opprinnelse.
2. Verktøyene bruker `tilgang` som rollefilter, og bare tabeller med formål `assistent`.
3. Tabeller med `undervisning` blir avslagstester: assistenten skal nekte, og testene beviser det.
4. Det samme gjøres for `museum.db` v4 i neste bygg, slik at gamle og nye data merkes likt.

## Beslutninger du må ta

| Spørsmål | Min anbefaling |
|---|---|
| Merking per tabell eller per rad? | Per tabell, pluss per følsom kolonne. Per rad blir for tungt og gir ikke mer sikkerhet. |
| Hvor lagres den nye databasen? | `G:\Min disk\Kunstpixel\05_data\innkommende\`, utenfor git til den er kontrollert |
| Hvem setter `tilgang`? | Du, i Colab-cellen. Jeg foreslår verdier i rapporten. |
