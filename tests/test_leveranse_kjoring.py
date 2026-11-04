"""H5: den styrte løkken mot en annen modell, og Colab-pakken. Ingen ekte modell, ingen nettverk."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

from src.kunstpixel.core.intern import leveranse as L
from src.kunstpixel.core.intern.leveranse_bestilling import PAKKEFILER, skriv_colab_pakke
from src.kunstpixel.core.intern.leveranse_kjoring import MAKS_KALL, MAKS_RUNDER, hent_yaml, kjor
from tests.test_leveranse import Teller, dump, fyll

ROOT = Path(__file__).resolve().parent.parent
PAKKE = ROOT / "01_inbox" / "h5_colab"


def fil_i(prompt: str) -> str:
    """Hvilken fil bestillingen gjelder."""
    for k, f in L.FILER.items():
        if f"### {f}" in prompt.split("## Skjelettene")[-1]:
            return k
    raise AssertionError("fant ingen fil i bestillingen")


class Modell:
    """Skriptet modell. `svar` får (kode, prompt, runde) og returnerer tekst."""

    def __init__(self, svar):
        self.svar = svar
        self.prompter: list[str] = []
        self.runder: dict[str, int] = {}

    def __call__(self, prompt: str) -> str:
        k = fil_i(prompt)
        self.runder[k] = self.runder.get(k, 0) + 1
        self.prompter.append(prompt)
        return self.svar(k, prompt, self.runder[k])


def perfekt(k, prompt, runde):
    return dump(fyll(L.skjelett(k), Teller()))


def rolig(_):
    pass


# ---------- Løkken ----------


def test_perfect_model_passes_every_file_in_one_round_with_one_call_each(tmp_path):
    m = Modell(perfekt)
    res = kjor(m, tmp_path / "ut", logg=rolig)
    assert all(r["ok"] and r["runder"] == 1 and r["feil"] == 0 for r in res.values())
    assert len(m.prompter) == len(L.FILER)
    assert L.kontroller_mappe(tmp_path / "ut").ok


def test_model_only_ever_sees_the_order_for_one_file_at_a_time(tmp_path):
    m = Modell(perfekt)
    kjor(m, tmp_path / "ut", logg=rolig)
    for p in m.prompter:
        assert sum(p.split("## Skjelettene")[-1].count(f"### {f}") for f in L.FILER.values()) == 1
        assert len(p) < 16_000
        for forbidden in ("05_data", "C:\\", "G:\\", "sk-ant", "ANTHROPIC", "museum.db", "Lars"):
            assert forbidden not in p


def test_model_that_fails_first_is_given_its_own_answer_and_the_exact_errors(tmp_path):
    def svar(k, prompt, runde):
        return L.skjelett_tekst(k) if runde == 1 else perfekt(k, prompt, runde)

    m = Modell(svar)
    res = kjor(m, tmp_path / "ut", koder=["A"], logg=rolig)
    assert res["A"] == {"ok": True, "runder": 2, "feil": 0, "stopp": None}
    runde2 = m.prompter[1]
    assert "## Din forrige leveranse" in runde2 and "## Feil som må rettes" in runde2
    assert "TODO_FYLL (1 setning" in runde2.split("## Din forrige leveranse")[1].split("## Feil")[0]  # forrige svar er med
    assert "myndigheter[0].hva_de_vil [PLASSHOLDER]" in runde2 and "Ikke endre faste felt" in runde2
    assert len(m.prompter[0]) < len(runde2)


def test_model_that_never_fixes_gets_exactly_three_rounds_and_is_reported_as_failed(tmp_path):
    m = Modell(lambda k, p, r: L.skjelett_tekst(k))
    res = kjor(m, tmp_path / "ut", koder=["B"], logg=rolig)
    assert res["B"]["ok"] is False and res["B"]["runder"] == MAKS_RUNDER == 3
    assert res["B"]["stopp"] == "maks runder uten å bestå" and len(m.prompter) == 3
    assert not L.kontroller_mappe(tmp_path / "ut").ok


def test_hard_call_cap_stops_the_run_and_never_exceeds_the_cap(tmp_path):
    m = Modell(perfekt)
    res = kjor(m, tmp_path / "ut", maks_kall=3, logg=rolig)
    assert len(m.prompter) == 3
    assert [res[k]["ok"] for k in "ABC"] == [True] * 3
    assert res["D"]["stopp"] == res["E"]["stopp"] == "kallgrense"


def test_default_cap_covers_five_files_with_three_rounds_each():
    assert MAKS_KALL == 20 and 5 * MAKS_RUNDER <= 20 + 5


def test_call_cap_is_shared_across_files_when_the_model_keeps_failing(tmp_path):
    m = Modell(lambda k, p, r: L.skjelett_tekst(k))
    res = kjor(m, tmp_path / "ut", maks_kall=4, logg=rolig)
    assert len(m.prompter) == 4 and res["A"]["runder"] == 3 and res["B"]["runder"] == 1
    assert res["C"]["stopp"] == "kallgrense"


def test_model_error_stops_only_that_file_and_counts_as_a_call(tmp_path):
    def svar(k, prompt, runde):
        if k == "B":
            raise ConnectionError("nett nede med hemmelig sti C:/x")
        return perfekt(k, prompt, runde)

    m = Modell(svar)
    logg: list[str] = []
    res = kjor(m, tmp_path / "ut", logg=logg.append)
    assert res["B"]["stopp"] == "modellfeil: ConnectionError" and res["B"]["ok"] is False
    assert all(res[k]["ok"] for k in "ACDEF")
    assert not any("hemmelig" in l for l in logg)  # feilmeldingen fra modellen logges ikke
    assert len(m.prompter) == len(L.FILER)


@pytest.mark.parametrize("svar", [None, 42, [], {"a": 1}, "", "   "])
def test_non_text_or_empty_answers_are_treated_as_failures_and_retried(tmp_path, svar):
    m = Modell(lambda k, p, r: svar if r == 1 else perfekt(k, p, r))
    res = kjor(m, tmp_path / "ut", koder=["A"], logg=rolig)
    assert res["A"]["ok"] and res["A"]["runder"] == 2


def test_chatty_answer_with_fenced_yaml_is_accepted(tmp_path):
    m = Modell(lambda k, p, r: "Selvfølgelig! Her er filen:\n\n```yaml\n" + perfekt(k, p, r) + "```\n\nSkal jeg endre noe mer?")
    res = kjor(m, tmp_path / "ut", koder=["A"], logg=rolig)
    assert res["A"]["ok"]
    assert "```" not in (tmp_path / "ut" / L.FILER["A"]).read_text(encoding="utf-8")


def test_hent_yaml_variants():
    assert hent_yaml("```yaml\na: 1\n```") == "a: 1\n"
    assert hent_yaml("tekst\n```\na: 1\n```\nmer") == "a: 1\n"
    assert hent_yaml("a: 1") == "a: 1\n"
    assert hent_yaml("```yml\na: 1\n```\n```yaml\nb: 2\n```") == "a: 1\n"  # første blokk
    assert hent_yaml(None) == ""  # ikke-tekst gir tomt svar, som kontrollen avviser som TOM


def test_runs_write_only_inside_the_output_folder(tmp_path):
    ut = tmp_path / "ut"
    before = {p for p in ROOT.joinpath("05_data", "governance").iterdir()}
    kjor(Modell(perfekt), ut, logg=rolig)
    assert {p.name for p in ut.iterdir()} == set(L.FILER.values())
    assert {p for p in ROOT.joinpath("05_data", "governance").iterdir()} == before


def test_log_lines_report_round_and_error_counts_without_content(tmp_path):
    logg: list[str] = []
    kjor(Modell(lambda k, p, r: L.skjelett_tekst(k) if r == 1 else perfekt(k, p, r)), tmp_path / "ut", koder=["C"], logg=logg.append)
    assert logg[0].startswith("rapporteringskalender.yaml: runde 1, ") and " feil" in logg[0]
    assert logg[1].startswith("rapporteringskalender.yaml: runde 2, 0 feil")
    assert logg[-1] == "Modellkall brukt: 2 av 20"
    assert not any("TODO_FYLL" in l for l in logg)


def test_second_round_prompt_does_not_grow_without_bound(tmp_path):
    m = Modell(lambda k, p, r: L.skjelett_tekst(k))
    kjor(m, tmp_path / "ut", koder=["D"], logg=rolig)
    assert len(m.prompter[2]) < 3 * len(m.prompter[0])  # forrige svar er med, men ikke hele historikken


# ---------- Colab-pakken ----------


def test_committed_package_matches_the_source_files_byte_for_byte():
    kilde = ROOT / "src" / "kunstpixel" / "core" / "intern"
    for navn in PAKKEFILER:
        assert (PAKKE / navn).read_bytes() == (kilde / navn).read_bytes(), f"{navn} er utdatert. Kjør --lag-colab-pakke"


def test_checksums_file_is_correct():
    linjer = (PAKKE / "SJEKKSUM.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(linjer) == 3
    for l in linjer:
        h, navn = l.split("  ")
        assert hashlib.sha256((PAKKE / navn).read_bytes()).hexdigest() == h


def test_package_is_regenerated_identically(tmp_path):
    skriv_colab_pakke(tmp_path)
    for navn in (*PAKKEFILER, "SJEKKSUM.txt"):
        assert (tmp_path / navn).read_bytes() == (PAKKE / navn).read_bytes()


def test_package_works_standalone_without_the_repository_on_the_path():
    """Kjører pakken slik Colab gjør: bare de tre filene i en mappe, og ingen tilgang til prosjektet."""
    kode = (
        "import sys; sys.path.insert(0, '.')\n"
        "try:\n"
        "    import src.kunstpixel\n"
        "    print('REPO_SYNLIG')\n"
        "except ImportError:\n"
        "    pass\n"
        "import leveranse as L, leveranse_bestilling as B, leveranse_kjoring as K\n"
        "assert B.bestilling_for(['A']).count('myndighetskontakter.yaml') >= 1\n"
        "feil = [f for f in L.kontroller_tekst('A', L.skjelett_tekst('A')) if f.alvor == 'FEIL']\n"
        "assert feil\n"
        "def modell(prompt): return ''\n"
        "import tempfile, pathlib\n"
        "res = K.kjor(modell, pathlib.Path(tempfile.mkdtemp()), koder=['A'], logg=lambda s: None)\n"
        "assert res['A']['ok'] is False and res['A']['runder'] == 3\n"
        "print('OK', L.summer()['totalt'])\n"
    )
    r = subprocess.run([sys.executable, "-c", kode], cwd=PAKKE, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "REPO_SYNLIG" not in r.stdout and "OK 287" in r.stdout


def test_package_contains_no_machine_specific_paths_or_secrets():
    for navn in PAKKEFILER:
        tekst = (PAKKE / navn).read_text(encoding="utf-8")
        assert not re.search(r"[A-Z]:\\|/Users/|larse|sk-ant-", tekst), navn
