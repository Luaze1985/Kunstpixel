"""H5: bestilling og kontroll av syntetisk fyll fra en annen språkmodell.

Referanseleveransen under er TESTDATA laget av testen selv for å bevise at kontrollen ikke er for streng.
Den er ikke innholdet som skal brukes. Det skriver den andre modellen.
"""

import copy
import re
from pathlib import Path

import pytest
import yaml

from src.kunstpixel.core.intern import leveranse as L
from src.kunstpixel.core.intern.data import DEFAULT_SOURCES, ROLLER, InternData, SourceSpec
from src.kunstpixel.core.intern.leveranse_bestilling import bestilling_for, skriv_bestillinger
from tests import kontroller_leveranse as cli

ROOT = Path(__file__).resolve().parent.parent
BESTILLING = ROOT / "01_inbox" / "h5_bestilling"

SUBJ = ["Rutinen", "Oppgaven", "Dokumentet", "Prosessen", "Rapporten", "Avtalen", "Oversikten"]
VERB = ["beskriver", "samler", "forklarer", "følger", "dekker", "sikrer", "ordner"]
OBJ = ["arbeidet", "saksgangen", "oppfølgingen", "dokumentasjonen", "kontakten", "ansvaret", "oversikten", "kontrollen", "planleggingen", "leveransen", "innsynet"]
END = ["slik at alle forstår hva som gjelder", "uten at noe blir liggende", "på en måte som kan følges opp", "i hverdagen på museet", "så ingen må lete etter svar",
       "før noe sendes videre", "med tydelig eier", "uten unødvendig omvei", "så arbeidet går jevnt", "og gjør det lett å kontrollere", "slik at tiden brukes riktig", "med kort og tydelig språk", "uten tvil om hvem som gjør hva"]  # fmt: skip


class Teller:
    def __init__(self):
        self.n = 0

    def neste(self) -> str:
        n = self.n
        self.n += 1
        return f"{SUBJ[n % 7]} {VERB[(n // 7) % 7]} {OBJ[(n // 49) % 11]} {END[(n // 539) % 13]}."


def fyll(skel, teller=None):
    """Bygger en gyldig referanseleveranse ut fra skjelettet."""
    teller = teller or Teller()
    if isinstance(skel, str) and skel.startswith(L.PLASSHOLDER):
        if skel.startswith(f"{L.PLASSHOLDER}_KILDER"):
            return ["manuell"] if "1 eller 2" in skel else ["driftslogg", "hendelser"]
        if skel.startswith(f"{L.PLASSHOLDER}_LISTE"):
            return [teller.neste(), teller.neste()]
        return teller.neste()
    if isinstance(skel, dict):
        return {k: fyll(v, teller) for k, v in skel.items()}
    if isinstance(skel, list):
        return [fyll(v, teller) for v in skel]
    return skel


def dump(d) -> str:
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=1000)


@pytest.fixture
def ref():
    """Referanseleveranse som dict per filkode."""
    t = Teller()
    return {k: fyll(L.skjelett(k), t) for k in L.FILER}


@pytest.fixture
def leveranse(tmp_path, ref):
    for k, f in L.FILER.items():
        (tmp_path / f).write_text(dump(ref[k]), encoding="utf-8")
    return tmp_path


def koder(funn):
    return {f.kode for f in funn if f.alvor == "FEIL"}


# ---------- Tabellene henger sammen ----------


def test_tables_sums_and_ids_are_consistent():
    s = L.summer()
    assert s == {"myndighetskontakt": 112, "rapportering": 175, "totalt": 287}
    assert [r[0] for r in L.RAPPORTER] == [f"RP-{i:02d}" for i in range(1, 13)]
    assert [m[0] for m in L.MYNDIGHETER] == [f"MK-{i:02d}" for i in range(1, 9)]
    assert [o[0] for o in L.MYNDIGHETSOPPGAVER] == [f"AO-{i:02d}" for i in range(1, 8)]
    assert len({m[1] for m in L.MYNDIGHETER}) == 8


def test_every_role_and_owner_is_in_the_allowed_vocabulary():
    for m in L.MYNDIGHETER:
        assert m[3] in L.ROLLER_TILLATT
    for r in L.RAPPORTER:
        assert r[7] in L.ROLLER_TILLATT
    for s in L.TILSYNSSTEG:
        assert s[2] in L.ROLLER_TILLATT
    for o in L.MYNDIGHETSOPPGAVER:
        assert o[3] in L.ROLLER_TILLATT
    assert {n.lower().replace("ø", "o") for n in L.ROLLER_TILLATT[:7]} == set(ROLLER)


def test_time_use_rows_match_the_report_calendar_exactly():
    e = L.skjelett("E")["oppgaver"]
    by_id = {r[0]: r for r in L.RAPPORTER}
    rapport_rader = [r for r in e if r["omrade"] == "Rapportering"]
    assert len(rapport_rader) == 12 and len(e) == 19
    for r in rapport_rader:
        rp = by_id[r["rapport_id"]]
        assert r["timer_per_ar"] == int(L.timer_per_ar(rp)) and r["oppgave"] == rp[1] and r["rolle"] == rp[7]
    assert sum(r["timer_per_ar"] for r in e if r["omrade"] == "Rapportering") == L.skjelett("E")["sum"]["rapportering"]
    assert sum(r["timer_per_ar"] for r in e if r["omrade"] == "Myndighetskontakt") == L.skjelett("E")["sum"]["myndighetskontakt"]


def test_every_external_report_needs_owner_approval_and_internal_ones_do_not():
    for r in L.RAPPORTER:
        assert (r[9] == "eier") is (r[3] == "ekstern"), r[0]
    for m in L.MALER:
        assert m[3] in ("eier", "ingen")
    assert {m[1]: m[3] for m in L.MALER}["Tilskuddsrapport"] == "eier"
    assert {m[1]: m[3] for m in L.MALER}["Svar til tilsyn"] == "eier"


def test_deadlines_match_the_existing_hms_file():
    hms = (ROOT / "05_data/governance/hms_arbeidsmiljo.yaml").read_text(encoding="utf-8")
    assert "14 dager" in hms and "24t" in hms
    assert L.AVVIK_FRISTER["gult_avvik_lukkes_innen"] == "14 dager"
    assert L.AVVIK_FRISTER["rodt_avvik_lukkes_innen"].startswith("24 ")


def test_authorities_match_the_existing_calendar_where_they_overlap():
    kal = (ROOT / "05_data/governance/tilsynskalender.json").read_text(encoding="utf-8")
    for navn in ("Arbeidstilsynet", "Mattilsynet", "Brann- og redningsetaten"):
        assert navn in kal and navn in {m[1] for m in L.MYNDIGHETER}


# ---------- Skjelettet ----------


@pytest.mark.parametrize("kode", list(L.FILER))
def test_raw_skeleton_is_rejected_because_nothing_is_filled_in(kode):
    funn = L.kontroller_tekst(kode, L.skjelett_tekst(kode))
    assert "PLASSHOLDER" in koder(funn) or "ANTALL" in koder(funn)
    assert len(koder(funn)) >= 1


@pytest.mark.parametrize("kode", list(L.FILER))
def test_skeleton_has_header_and_only_known_placeholder_kinds(kode):
    s = L.skjelett(kode)
    for k, v in L.HEADER.items():
        assert s[k] == v
    texts = re.findall(rf"{L.PLASSHOLDER}\w*", L.skjelett_tekst(kode))
    assert texts and set(texts) <= {L.PLASSHOLDER, f"{L.PLASSHOLDER}_KILDER", f"{L.PLASSHOLDER}_LISTE"}


def test_placeholder_counts_per_file():
    # D: 4 formål, 21 felt med beskrivelse og kilde, 4 regelsett
    n = {k: L.skjelett_tekst(k).count(L.PLASSHOLDER) for k in L.FILER}
    assert n == {"A": 24, "B": 12, "C": 24, "D": 4 + 21 * 2 + 4, "E": 19, "F": 34}


# ---------- Referanseleveransen består ----------


def test_reference_delivery_passes_with_no_errors_and_no_warnings(leveranse):
    r = L.kontroller_mappe(leveranse)
    assert r.ok, [(f.fil, f.sti, f.kode, f.melding) for f in r.feil]
    assert r.advarsler == [] and all(r.filer.values()) and len(r.filer) == len(L.FILER)
    assert L.retteliste(r) == ""


# ---------- Ett avvik om gangen ----------


def endre(ref, kode, fn):
    d = copy.deepcopy(ref[kode])
    fn(d)
    return L.kontroller_tekst(kode, dump(d))


MUT = [
    # (navn, filkode, endring, forventet kode)
    ("id endret", "A", lambda d: d["myndigheter"][0].update(id="MK-09"), "FAST_FELT_ENDRET"),
    ("myndighet endret", "A", lambda d: d["myndigheter"][1].update(myndighet="Politiet"), "FAST_FELT_ENDRET"),
    ("eier endret", "A", lambda d: d["myndigheter"][2].update(intern_eier="Kurator"), "FAST_FELT_ENDRET"),
    ("oppføring fjernet", "A", lambda d: d["myndigheter"].pop(), "ANTALL"),
    ("oppføring lagt til", "A", lambda d: d["myndigheter"].append(copy.deepcopy(d["myndigheter"][0])), "ANTALL"),
    ("ukjent felt", "A", lambda d: d["myndigheter"][0].update(telefon="aaa bbb ccc ddd eee"), "UKJENT_FELT"),
    ("felt mangler", "A", lambda d: d["myndigheter"][0].pop("hva_de_vil"), "MANGLER"),
    ("merknad endret", "A", lambda d: d["myndigheter"][0].update(merknad="ekte rettesnor"), "FAST_FELT_ENDRET"),
    ("header ekte", "A", lambda d: d.update(klassifisering="ekte"), "FAST_FELT_ENDRET"),
    ("header syntetisk false", "A", lambda d: d.update(syntetisk=False), "FAST_FELT_ENDRET"),
    ("header versjon som tekst", "A", lambda d: d.update(versjon="1"), "FAST_FELT_ENDRET"),
    ("header mangler", "A", lambda d: d.pop("syntetisk"), "MANGLER"),
    ("plassholder igjen", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="TODO_FYLL (1 setning): hva myndigheten ber om"), "PLASSHOLDER"),
    ("tall i tekst", "A", lambda d: d["myndigheter"][0].update(utloser="Svar må sendes innen 30 dager etter besøket."), "TALL_I_TEKST"),
    ("tall med bokstaver er lov i fritekst men ikke sifre", "A", lambda d: d["myndigheter"][0].update(utloser="Fristen er 2 uker etter varsel fra myndigheten."), "TALL_I_TEKST"),
    ("e-post", "A", lambda d: d["myndigheter"][0].update(dokumentasjon="Send dokumentene til kontakt@eksempel.no for gjennomgang."), "KONTAKTDETALJER"),
    ("lenke", "A", lambda d: d["myndigheter"][0].update(dokumentasjon="Se https://eksempel.no/regler for hele oversikten her."), "KONTAKTDETALJER"),
    ("telefon", "A", lambda d: d["myndigheter"][0].update(dokumentasjon="Ring oss på 22 33 44 55 for å avtale tid og sted."), "KONTAKTDETALJER"),
    ("paragraf", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Etter paragraf om internkontroll skal alt dokumenteres godt."), "PARAGRAF"),
    ("paragrafsymbol", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Kravet står i § om internkontroll og gjelder for alle."), "PARAGRAF"),
    ("personnavn", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Kari fra tilsynet ber om oversikt over alle avvik."), "PERSONNAVN"),
    ("ki-snakk", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Selvfølgelig! Her er teksten du ba om til feltet."), "KI_SNAKK"),
    ("emoji", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Oversikt over avvik og tiltak i hverdagen på museet 😀."), "EMOJI"),
    ("for kort", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="Kort tekst."), "FOR_KORT"),
    ("for lang", "A", lambda d: d["myndigheter"][0].update(hva_de_vil="ord " * 80), "FOR_LANG"),
    ("kopiert tekst", "A", lambda d: d["myndigheter"][1].update(hva_de_vil=d["myndigheter"][0]["hva_de_vil"]), "KOPIERT_TEKST"),
    ("kopiert tekst med store bokstaver", "A", lambda d: d["myndigheter"][1].update(hva_de_vil=d["myndigheter"][0]["hva_de_vil"].upper()), "KOPIERT_TEKST"),
    ("feil type på tekst", "A", lambda d: d["myndigheter"][0].update(hva_de_vil={"a": "b"}), "TYPE"),
    ("liste i stedet for tekst", "A", lambda d: d["myndigheter"][0].update(utloser=["en", "to"]), "TYPE"),
    ("avvikfrist endret", "B", lambda d: d["avvik_frister"].update(gult_avvik_lukkes_innen="30 dager"), "FAST_FELT_ENDRET"),
    ("steg byttet", "B", lambda d: d["steg"].reverse(), "FAST_FELT_ENDRET"),
    ("steg fjernet", "B", lambda d: d["steg"].pop(), "ANTALL"),
    ("ansvarlig endret", "B", lambda d: d["steg"][0].update(ansvarlig="Formidler"), "FAST_FELT_ENDRET"),
    ("timer endret", "C", lambda d: d["rapporter"][2].update(timer_per_gang=37), "FAST_FELT_ENDRET"),
    ("antall endret", "C", lambda d: d["rapporter"][0].update(antall_per_ar=11), "FAST_FELT_ENDRET"),
    ("godkjenning fjernet", "C", lambda d: d["rapporter"][2].update(godkjenning="ingen"), "FAST_FELT_ENDRET"),
    ("ekstern gjort intern", "C", lambda d: d["rapporter"][1].update(mottakertype="intern"), "FAST_FELT_ENDRET"),
    ("desimal som tekst", "C", lambda d: d["rapporter"][6].update(timer_per_gang="1,5"), "FAST_FELT_ENDRET"),
    ("desimal som heltall", "C", lambda d: d["rapporter"][6].update(timer_per_gang=2), "FAST_FELT_ENDRET"),
    ("tall som tekst", "C", lambda d: d["rapporter"][0].update(antall_per_ar="12"), "FAST_FELT_ENDRET"),
    ("ukjent kilde", "C", lambda d: d["rapporter"][0].update(kilder=["driftslogg", "magi"]), "UKJENT_KILDE"),
    ("for få kilder", "C", lambda d: d["rapporter"][0].update(kilder=["driftslogg"]), "ANTALL"),
    ("for mange kilder", "C", lambda d: d["rapporter"][0].update(kilder=["driftslogg", "hendelser", "regnskap", "innlån"]), "ANTALL"),
    ("samme kilde to ganger", "C", lambda d: d["rapporter"][0].update(kilder=["driftslogg", "driftslogg"]), "DUPLIKAT"),
    ("kilder som tekst", "C", lambda d: d["rapporter"][0].update(kilder="driftslogg, hendelser"), "TYPE"),
    ("mal-godkjenning endret", "D", lambda d: d["maler"][2].update(godkjenning="ingen"), "FAST_FELT_ENDRET"),
    ("mal-status endret", "D", lambda d: d["maler"][0].update(status_ved_opprettelse="Endelig"), "FAST_FELT_ENDRET"),
    ("felt fjernet", "D", lambda d: d["maler"][0]["felt"].pop(), "ANTALL"),
    ("felt omdøpt", "D", lambda d: d["maler"][0]["felt"][0].update(navn="Annet"), "FAST_FELT_ENDRET"),
    ("for mange regler", "D", lambda d: d["maler"][0].update(regler=[f"Regel nummer {'abc'[i]} som er unik og lang nok her." for i in range(3)] + ["Fjerde regel som er unik og lang nok her."]), "ANTALL"),
    ("for få regler", "D", lambda d: d["maler"][0].update(regler=["Bare en regel som er unik og lang nok her."]), "ANTALL"),
    ("regel med tall", "D", lambda d: d["maler"][0].update(regler=["Rapporten skal sendes innen 5 dager hver gang.", "Alt skal være ført inn før rapporten lages."]), "TALL_I_TEKST"),
    ("sum endret", "E", lambda d: d["sum"].update(totalt=288), "FAST_FELT_ENDRET"),
    ("timer endret E", "E", lambda d: d["oppgaver"][0].update(timer_per_ar=41), "FAST_FELT_ENDRET"),
    ("potensial endret", "E", lambda d: d["oppgaver"][3].update(automatiseringspotensial="Lav"), "FAST_FELT_ENDRET"),
    ("rapport-id endret", "E", lambda d: d["oppgaver"][8].update(rapport_id="RP-99"), "FAST_FELT_ENDRET"),
    ("rolle endret E", "E", lambda d: d["oppgaver"][0].update(rolle="Museumsvert"), "FAST_FELT_ENDRET"),
    ("oppgave fjernet E", "E", lambda d: d["oppgaver"].pop(0), "ANTALL"),
    ("toppnivå mangler", "E", lambda d: d.pop("oppgaver"), "MANGLER"),
]


@pytest.mark.parametrize("navn,kode,endring,forventet", MUT, ids=[m[0] for m in MUT])
def test_one_defect_at_a_time_is_caught(ref, navn, kode, endring, forventet):
    funn = endre(ref, kode, endring)
    assert forventet in koder(funn), (navn, [(f.kode, f.sti) for f in funn])


def test_every_mutation_leaves_the_untouched_files_passing(ref, tmp_path):
    for k, f in L.FILER.items():
        (tmp_path / f).write_text(dump(ref[k]), encoding="utf-8")
    d = copy.deepcopy(ref["A"])
    d["myndigheter"][0]["hva_de_vil"] = "Kari ringer 22 33 44 55."
    (tmp_path / L.FILER["A"]).write_text(dump(d), encoding="utf-8")
    r = L.kontroller_mappe(tmp_path)
    assert r.filer == {"A": False, "B": True, "C": True, "D": True, "E": True, "F": True}


def test_warning_for_unknown_capitalised_word_does_not_block(ref):
    d = copy.deepcopy(ref["A"])
    d["myndigheter"][0]["hva_de_vil"] = "Rutinen beskriver hvordan Zorbax følges opp på museet hver dag."
    funn = L.kontroller_tekst("A", dump(d))
    assert koder(funn) == set() and any(f.kode == "EGENNAVN" and f.alvor == "ADVARSEL" for f in funn)


def test_english_text_gives_a_warning(ref):
    d = copy.deepcopy(ref["A"])
    d["myndigheter"][0]["hva_de_vil"] = "The authority will have the documents from the museum and that must be done."
    assert any(f.kode == "ENGELSK" and f.alvor == "ADVARSEL" for f in L.kontroller_tekst("A", dump(d)))


# ---------- Format og sikkerhet ----------


def test_invalid_yaml_empty_and_wrong_top_level(ref):
    assert "UGYLDIG_YAML" in koder(L.kontroller_tekst("A", "a: [uferdig\n  b: : :"))
    assert "UGYLDIG_YAML" in koder(L.kontroller_tekst("A", "a:\n\tb: 1\n"))  # tabulator
    assert koder(L.kontroller_tekst("A", "")) == {"TOM"} == koder(L.kontroller_tekst("A", "  \n\n "))
    assert "STRUKTUR" in koder(L.kontroller_tekst("A", "- a\n- b\n"))
    assert "STRUKTUR" in koder(L.kontroller_tekst("A", "bare tekst"))


def test_code_fences_are_tolerated_with_a_warning_and_still_validated(ref):
    funn = L.kontroller_tekst("A", "```yaml\n" + dump(ref["A"]) + "```")
    assert koder(funn) == set() and any(f.kode == "KODEGJERDER" for f in funn)
    d = copy.deepcopy(ref["A"])
    d["myndigheter"][0]["hva_de_vil"] = "Kari ringer 22 33 44 55."
    assert "TALL_I_TEKST" in koder(L.kontroller_tekst("A", "```yaml\n" + dump(d) + "```"))


def test_bom_and_crlf_are_accepted(ref):
    tekst = "\ufeff" + dump(ref["A"]).replace("\n", "\r\n")
    assert koder(L.kontroller_tekst("A", tekst)) == set()


def test_python_tags_are_refused_and_never_executed(tmp_path):
    marker = tmp_path / "kjort.txt"
    tekst = f"x: !!python/object/apply:pathlib.Path.write_text [!!python/object/apply:pathlib.Path [\"{marker.as_posix()}\"], \"hei\"]\n"
    assert "UGYLDIG_YAML" in koder(L.kontroller_tekst("A", tekst))
    assert not marker.exists()


def test_billion_laughs_is_refused_quickly_without_building_it():
    import time

    lol = "a: &a [1,2,3,4,5,6,7,8,9]\n"
    prev = "a"
    for n in "bcdefghi":
        lol += f"{n}: &{n} [" + ",".join([f"*{prev}"] * 9) + "]\n"
        prev = n
    t = time.time()
    assert koder(L.kontroller_tekst("A", lol)) == {"ANKER"}
    assert time.time() - t < 2


def test_duplicate_keys_are_refused(ref):
    tekst = dump(ref["A"]).replace("versjon: 1", "versjon: 1\nversjon: 2")
    assert "DUPLIKAT_NOKKEL" in koder(L.kontroller_tekst("A", tekst))


def test_huge_file_is_refused_before_it_is_parsed():
    assert koder(L.kontroller_tekst("A", "a: " + "x" * (L.MAX_FILSTORRELSE + 10))) == {"FOR_STOR"}


def test_missing_and_unreadable_files_are_reported(tmp_path, ref):
    r = L.kontroller_mappe(tmp_path)
    assert not r.ok and {f.kode for f in r.feil} == {"MANGLER_FIL"} and len(r.feil) == len(L.FILER)
    (tmp_path / L.FILER["A"]).write_bytes(b"\xff\xfe\x00\x00 ikke utf-8 \x80")
    assert any(f.kode == "KAN_IKKE_LESES" for f in L.kontroller_mappe(tmp_path).feil)


def test_extra_files_in_the_folder_are_ignored(leveranse):
    (leveranse / "notater.txt").write_text("ignoreres", encoding="utf-8")
    assert L.kontroller_mappe(leveranse).ok


# ---------- Retteliste ----------


def test_retteliste_names_file_path_code_and_repeats_the_rules(leveranse, ref):
    d = copy.deepcopy(ref["C"])
    d["rapporter"][2]["timer_per_gang"] = 37
    d["rapporter"][0]["formal"] = "Kari ringer 22 33 44 55 om rapporten hver dag."
    (leveranse / L.FILER["C"]).write_text(dump(d), encoding="utf-8")
    liste = L.retteliste(L.kontroller_mappe(leveranse))
    assert "## rapporteringskalender.yaml" in liste
    assert "rapporter[2].timer_per_gang [FAST_FELT_ENDRET]" in liste and "Skal være 36" in liste
    assert "rapporter[0].formal" in liste and "PERSONNAVN" in liste
    assert "Ikke endre faste felt" in liste and "HELE filene" in liste
    assert "myndighetskontakter.yaml" not in liste  # ren fil nevnes ikke


def test_retteliste_is_capped_per_file_and_empty_when_ok(leveranse):
    assert L.retteliste(L.kontroller_mappe(leveranse)) == ""
    r = L.kontroller_mappe(leveranse.parent / "tom")
    assert len(L.retteliste(r).splitlines()) < 30


# ---------- Installering ----------


def test_install_copies_only_passing_files_after_explicit_request(leveranse, ref, tmp_path):
    d = copy.deepcopy(ref["B"])
    d["avvik_frister"]["gult_avvik_lukkes_innen"] = "30 dager"
    (leveranse / L.FILER["B"]).write_text(dump(d), encoding="utf-8")
    mal = tmp_path / "ut"
    ok, avvist = L.installer(leveranse, ["A", "B", "c"], mal)
    assert ok == ["A", "C"] and len(avvist) == 1 and "B" in avvist[0]
    assert {p.name for p in mal.iterdir()} == {L.FILER["A"], L.FILER["C"]}


def test_install_refuses_unknown_codes_and_never_overwrites_by_default(leveranse, tmp_path):
    mal = tmp_path / "ut"
    mal.mkdir()
    (mal / L.FILER["A"]).write_text("ORIGINAL", encoding="utf-8")
    ok, avvist = L.installer(leveranse, ["A", "Z"], mal)
    assert ok == [] and len(avvist) == 2
    assert (mal / L.FILER["A"]).read_text(encoding="utf-8") == "ORIGINAL"
    ok, _ = L.installer(leveranse, ["A"], mal, overskriv=True)
    assert ok == ["A"] and "myndigheter" in (mal / L.FILER["A"]).read_text(encoding="utf-8")


def test_installed_files_have_no_code_fences(leveranse, ref, tmp_path):
    (leveranse / L.FILER["A"]).write_text("```yaml\n" + dump(ref["A"]) + "```", encoding="utf-8")
    ok, _ = L.installer(leveranse, ["A"], tmp_path / "ut")
    assert ok == ["A"] and "```" not in (tmp_path / "ut" / L.FILER["A"]).read_text(encoding="utf-8")


def test_installed_files_load_in_the_existing_data_layer_without_code_changes(leveranse, tmp_path):
    """Beviser at leveransen kan tas i bruk uten å endre dataleseren: leses som vanlig YAML og kan søkes."""
    base = tmp_path / "base"
    for spec in DEFAULT_SOURCES:
        (base / spec.path).parent.mkdir(parents=True, exist_ok=True)
        (base / spec.path).write_bytes((ROOT / spec.path).read_bytes())
    L.installer(leveranse, list(L.FILER), base / "05_data" / "governance")
    ny = tuple(SourceSpec(f"05_data/governance/{L.FILER[k]}", t, "syntetisk", frozenset(ROLLER) if k != "E" else frozenset({"museumsdirektor", "driftsansvarlig", "kvalitetsvokter"}), "yaml")
               for k, t in (("A", "myndighet"), ("B", "myndighet"), ("C", "rapportering"), ("D", "rapportering"), ("E", "arbeidsoppgaver")))
    d = InternData(base=base, sources=DEFAULT_SOURCES + ny)
    assert any(f.tema == "myndighet" and "Mattilsynet" in f.tekst for f in d.findings)
    assert any(f.tema == "rapportering" and "Tilskuddsrapport" in f.tekst for f in d.findings)
    assert d.search("Tilskuddssøknad timer", "museumsvert", ("arbeidsoppgaver",)) == []  # fil E er ikke for ansatte
    assert d.search("Tilskuddssøknad timer", "museumsdirektor", ("arbeidsoppgaver",), bred=True)


# ---------- Kommandolinjen ----------


def test_cli_creates_orders_and_skeletons(tmp_path, capsys):
    assert cli.main(["--lag-bestilling", "--ut", str(tmp_path)]) == 0
    assert {p.name for p in tmp_path.iterdir()} >= {"komplett.md", "skjelett"}
    assert len(list((tmp_path / "skjelett").iterdir())) == len(L.FILER)


def test_cli_exit_codes_for_bad_good_and_missing(leveranse, tmp_path, capsys):
    assert cli.main([str(leveranse)]) == 0
    assert "Alt består" in capsys.readouterr().out
    assert cli.main([str(tmp_path / "finnes-ikke")]) == 2
    skel = tmp_path / "skel"
    L.skriv_skjelett(skel)
    assert cli.main([str(skel)]) == 1
    assert "RETTELISTE" in capsys.readouterr().out
    assert cli.main([]) == 2


def test_cli_writes_retteliste_to_file(tmp_path, capsys):
    skel = tmp_path / "skel"
    L.skriv_skjelett(skel)
    ut = tmp_path / "rett.md"
    assert cli.main([str(skel), "--retteliste", str(ut)]) == 1
    assert "myndighetskontakter.yaml" in ut.read_text(encoding="utf-8")


def test_cli_install_needs_yes_and_respects_target(leveranse, tmp_path, capsys):
    mal = tmp_path / "datamappe"
    assert cli.main([str(leveranse), "--installer", "A", "--mal", str(mal)]) == 2  # uten --yes
    assert not mal.exists()
    assert cli.main([str(leveranse), "--installer", "A,C", "--mal", str(mal), "--yes"]) == 0
    assert {p.name for p in mal.iterdir()} == {L.FILER["A"], L.FILER["C"]}
    assert cli.main([str(leveranse), "--installer", "A", "--mal", str(mal), "--yes"]) == 1  # finnes fra før


def test_cli_default_install_target_is_the_governance_folder_and_is_not_touched_by_tests(leveranse):
    assert cli.STANDARD_MAL == ROOT / "05_data" / "governance"
    assert all((cli.STANDARD_MAL / f).exists() for f in L.FILER.values())
    assert cli.main([str(leveranse), "--installer", "A", "--yes"]) == 1  # nekter å overskrive uten --overskriv


# ---------- Bestillingen ----------


def test_committed_orders_are_up_to_date_with_the_code(tmp_path):
    skriv_bestillinger(tmp_path)
    for p in tmp_path.iterdir():
        sammenligne = BESTILLING / p.name
        assert sammenligne.is_file(), f"{p.name} mangler i 01_inbox/h5_bestilling. Kjør --lag-bestilling"
        assert sammenligne.read_text(encoding="utf-8") == p.read_text(encoding="utf-8"), f"{p.name} er utdatert"


def test_committed_skeletons_match_the_code():
    for k, f in L.FILER.items():
        assert (BESTILLING / "skjelett" / f).read_text(encoding="utf-8") == L.skjelett_tekst(k)


def test_complete_order_contains_every_fixed_id_and_the_core_rules():
    tekst = bestilling_for(list(L.FILER))
    for ident in [m[0] for m in L.MYNDIGHETER] + [r[0] for r in L.RAPPORTER] + [m[0] for m in L.MALER] + [o[0] for o in L.MYNDIGHETSOPPGAVER]:
        assert ident in tekst
    for regel in ("Ingen tall i fritekst", "Ingen personnavn", "Ingen kontaktdetaljer", "Ingen paragrafer", "unik", "høyst tre runder", "menneskelig godkjenning"):
        assert regel in tekst
    assert tekst.count("```yaml") == len(L.FILER) + 1  # ett skjelett per fil og ett eksempel på leveringsformat


@pytest.mark.parametrize("kode", list(L.FILER))
def test_single_file_order_has_exactly_one_skeleton_and_fits_a_small_model(kode):
    tekst = bestilling_for([kode])
    assert tekst.count(f"### {L.FILER[kode]}") == 1 and sum(tekst.count(f"### {f}") for f in L.FILER.values() if f != L.FILER[kode]) == 0
    assert len(tekst) < 16_000


def test_orders_do_not_leak_real_data_or_keys():
    tekst = bestilling_for(list(L.FILER))
    import re

    assert "sk-ant-" not in tekst
    # e-post finnes bare som oppdiktede faste felt på det reserverte domenet .test, og er med i bestillingen
    adresser = [a.rstrip(".") for a in re.findall(r"[\w.+-]+@[\w.-]+", tekst) if a.rstrip(".") != "kari@eksempel.no"]  # «Dårlig»-eksemplet står i bestillingen med vilje
    assert adresser and all(a.endswith(".example.test") for a in adresser)
    assert {e for _, e in L.KONTAKTPERSONER.values()} | {e for _, e in L.INTERNE_PERSONER.values()} >= set(adresser)


def test_fixed_names_and_emails_pass_but_the_same_in_free_text_is_rejected():
    d = L.skjelett("A")
    assert all(m["kontaktperson"] and m["kontakt_epost"].endswith(".example.test") for m in d["myndigheter"])
    fylt = fyll(d, Teller())
    assert not [f for f in L.kontroller_tekst("A", dump(fylt)) if f.alvor == "FEIL"]
    fylt["myndigheter"][0]["hva_de_vil"] = f"Ta kontakt med {L.KONTAKTPERSONER['MK-01'][1]} om saken."
    assert any(f.kode == "KONTAKTDETALJER" for f in L.kontroller_tekst("A", dump(fylt)))
    fylt["myndigheter"][0]["kontaktperson"] = "Annen Person"
    assert any(f.kode == "FAST_FELT_ENDRET" for f in L.kontroller_tekst("A", dump(fylt)))
