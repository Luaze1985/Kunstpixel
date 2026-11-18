"""Bygger Kunstprofil-appen for firmafesten.

Leser kunstnere og verk fra museum.db (kun lesing, via src.kunstpixel.core.db),
legger til quiz-spørsmålene under, og skriver:

  profiler.json            data appen bruker
  kunstprofil_artifact.html  siden uten <html>/<head>, klar til publisering
  index.html               samme side som vanlig HTML-fil (dobbeltklikk for å åpne)

Kjøres fra prosjektroten:
    py -3.13 02_deliverables/firmafest_kunstprofil/bygg_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
PROJECT_ROOT = HER.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.db import execute_read_query  # noqa: E402

# Festrollen er en lekende etikett, ikke et faktum om kunstneren.
# Nøkkel = kunstner-id i museum.db. Kunstnere uten verk i samlingen (Hans Gude)
# er ikke med: profilen skal peke på et verk deltakeren kan se.
FESTTYPE = {
    1: ("Festens historieforteller", "Du får hele rommet til å lytte. Noen går hjem med litt gåsehud."),
    2: ("Den som sier det alle tenker", "Du ser hvem som blir stående alene, og du går bort til dem."),
    3: ("Gjesten som får lyset riktig", "Du flytter lampene og lysene til alle plutselig ser bedre ut."),
    4: ("Han som blir stående ute i natten", "Du trenger ikke mange ord. Stillheten din er det folk husker."),
    5: ("Bålmakeren", "Der du står, blir det varmt og fargerikt. Resten av gjengen kommer etter."),
    6: ("Den som kjenner stemningen først", "Du merker når kvelden snur, og du sier det høyt."),
    7: ("Allsangleder og bordvert", "Du sørger for at alle har en plass og en tekst å synge."),
    9: ("Sommerkvelden selv", "Du får alle med ut på terrassen, uansett vær."),
    10: ("Festens tegner og talemann", "Du fanger folk akkurat slik de er, og alle ler gjenkjennende."),
    11: ("Den som får alt til å se lett ut", "Du er rolig, rask og sjelden våt på beina."),
    12: ("Den rolige glansen", "Du sier lite. Gull og sølv gjør resten."),
}

# [bakgrunn, hoved, aksent] til pikselportrettet
FARGER = {
    1: ["#14231f", "#3f7a64", "#d8e8a0"],
    2: ["#2a2a33", "#8a8f9a", "#d9b36a"],
    3: ["#1d3552", "#3f78b5", "#e8d9b0"],
    4: ["#0d1b3d", "#3a5fb0", "#e9eefc"],
    5: ["#2d1b4e", "#e0452f", "#ffc83d"],
    6: ["#5a1f1a", "#e8602c", "#2b4b8f"],
    7: ["#3b2a1e", "#a8442e", "#e8c98a"],
    9: ["#1f3b4d", "#4fb3b0", "#f6d38a"],
    10: ["#2c2a22", "#7a8a4a", "#d9cfa8"],
    11: ["#16324a", "#8fc9e0", "#f2f7fa"],
    12: ["#10141c", "#c9a54a", "#cfd5dc"],
}

# Hvert svar gir poeng til kunstner-id.
QUESTIONS = [
    {
        "tekst": "Du kommer inn døren på festen. Hva gjør du først?",
        "valg": [
            {"tekst": "Går rett inn til folkene midt i rommet", "poeng": {7: 2, 5: 2, 11: 1}},
            {"tekst": "Finner en plass ved siden av og ser på folk", "poeng": {2: 2, 10: 2, 6: 1}},
            {"tekst": "Går bort til vinduet og tar inn stemningen", "poeng": {4: 2, 12: 1, 3: 1}},
            {"tekst": "Begynner å fortelle en historie", "poeng": {1: 2, 5: 1, 9: 1}},
        ],
    },
    {
        "tekst": "Hvilken musikk setter du på?",
        "valg": [
            {"tekst": "Allsang og gamle favoritter", "poeng": {7: 2, 5: 1, 1: 1}},
            {"tekst": "Noe intenst og litt melankolsk", "poeng": {6: 2, 4: 1, 2: 1}},
            {"tekst": "Rolig jazz eller ambient", "poeng": {12: 1, 11: 2, 3: 1}},
            {"tekst": "Sommerhiten alle kan synge", "poeng": {9: 2, 10: 1, 5: 1}},
        ],
    },
    {
        "tekst": "Hva prater du helst om ved bordet?",
        "valg": [
            {"tekst": "Det som skjer i samfunnet", "poeng": {2: 2, 10: 1, 7: 1}},
            {"tekst": "Store spørsmål og følelser", "poeng": {6: 2, 4: 1, 12: 1}},
            {"tekst": "Små, gode detaljer fra hverdagen", "poeng": {3: 1, 11: 2, 9: 1}},
            {"tekst": "Rykter, eventyr og spøkelseshistorier", "poeng": {1: 2, 5: 1, 7: 1}},
        ],
    },
    {
        "tekst": "Hvilket lys vil du ha i lokalet?",
        "valg": [
            {"tekst": "Levende lys og bål", "poeng": {5: 2, 1: 1, 6: 1}},
            {"tekst": "Mykt og varmt lampelys", "poeng": {3: 2, 10: 1, 2: 1}},
            {"tekst": "Kaldt, blått skumringslys", "poeng": {4: 2, 11: 1, 12: 1}},
            {"tekst": "Sommerlys og åpne vinduer", "poeng": {9: 2, 7: 1, 11: 1}},
        ],
    },
    {
        "tekst": "Hvor er du etter midnatt?",
        "valg": [
            {"tekst": "På dansegulvet, full fart", "poeng": {5: 2, 6: 1, 7: 1}},
            {"tekst": "Ute under stjernene", "poeng": {4: 1, 12: 2, 9: 1}},
            {"tekst": "I en dyp samtale i sofaen", "poeng": {2: 1, 3: 2, 6: 1}},
            {"tekst": "Med en penn, tegner karikaturer av kollegene", "poeng": {10: 2, 11: 1, 1: 1}},
        ],
    },
    {
        "tekst": "Hvilke farger har festantrekket ditt?",
        "valg": [
            {"tekst": "Gull og sølv", "poeng": {12: 2, 11: 1, 7: 1}},
            {"tekst": "Sterke, kontrastfylte farger", "poeng": {5: 1, 6: 2, 1: 1}},
            {"tekst": "Dempede jordtoner og dyp blå", "poeng": {3: 2, 2: 1, 10: 1}},
            {"tekst": "Hvitt og lysblått", "poeng": {4: 1, 9: 2, 11: 1}},
        ],
    },
]


def finn_profil(svar: list[int], questions: list[dict] = QUESTIONS) -> int:
    """Returnerer kunstner-id for en liste med valgindekser (ett per spørsmål).

    Høyest sum vinner. Ved likt: den som fikk mest poeng av siste svar,
    deretter laveste kunstner-id. Samme regel står i index.html (JS).
    """
    sum_poeng: dict[int, int] = {}
    siste: dict[int, int] = {}
    for q, valgt in zip(questions, svar):
        poeng = q["valg"][valgt]["poeng"]
        for kid, p in poeng.items():
            sum_poeng[kid] = sum_poeng.get(kid, 0) + p
        siste = poeng
    return min(sum_poeng, key=lambda k: (-sum_poeng[k], -siste.get(k, 0), k))


def hent_artister() -> list[dict]:
    """Kunstnere som har minst ett verk, med verk som kan vises."""
    kunstnere = execute_read_query(
        "SELECT id, navn, fodt, dod, nasjonalitet, kunstretning, notable_teknikker "
        "FROM kunstnere ORDER BY id"
    )
    verk = execute_read_query(
        "SELECT v.id, v.tittel, v.kunstner_id, v.aar, v.teknikk, v.beskrivelse, v.status, "
        "s.navn AS sal_navn "
        "FROM verk v LEFT JOIN saler s ON s.id = v.sal_id ORDER BY v.id"
    )
    ut = []
    for k in kunstnere:
        egne = [v for v in verk if v["kunstner_id"] == k["id"]]
        if not egne:
            continue
        # Foretrekk et verk som er utstilt nå
        valgt = next((v for v in egne if v["status"] == "utstilt"), egne[0])
        festtype, festtekst = FESTTYPE[k["id"]]
        ut.append(
            {
                "id": k["id"],
                "navn": k["navn"],
                "fodt": k["fodt"],
                "dod": k["dod"],
                "nasjonalitet": k["nasjonalitet"],
                "kunstretning": k["kunstretning"],
                "teknikker": k["notable_teknikker"],
                "festtype": festtype,
                "festtekst": festtekst,
                "farger": FARGER[k["id"]],
                "verk": {
                    "id": valgt["id"],
                    "tittel": valgt["tittel"],
                    "aar": valgt["aar"],
                    "teknikk": valgt["teknikk"],
                    "beskrivelse": valgt["beskrivelse"],
                    "status": valgt["status"],
                    "sal": valgt["sal_navn"],
                },
            }
        )
    return ut


def bygg() -> None:
    data = {"artister": hent_artister(), "spoersmaal": QUESTIONS}
    json_tekst = json.dumps(data, ensure_ascii=False, indent=2)
    (HER / "profiler.json").write_text(json_tekst + "\n", encoding="utf-8")

    mal = (HER / "mal.html").read_text(encoding="utf-8")
    # </ i JSON kunne lukke <script>; ingen slik tekst finnes nå, men sikre likevel
    inline = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    fragment = mal.replace("/*PROFILER_JSON*/null", inline)
    (HER / "kunstprofil_artifact.html").write_text(fragment, encoding="utf-8")

    # Vanlig HTML-fil: samme innhold pakket inn så den åpnes riktig lokalt
    fullside = (
        '<!doctype html>\n<html lang="nb">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<style>html,body{height:100%;margin:0}</style>\n</head>\n<body>\n"
        + fragment
        + "\n</body>\n</html>\n"
    )
    (HER / "index.html").write_text(fullside, encoding="utf-8")
    print(f"Skrev {len(data['artister'])} profiler og {len(QUESTIONS)} spørsmål til {HER}")


if __name__ == "__main__":
    bygg()
