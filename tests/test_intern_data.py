"""H2: datalaget for intern assistent. Lesere, kilde og sti, tilgang og feilformat."""

import shutil
from pathlib import Path

import pytest

from src.kunstpixel.core.datapolicy import EKTE, SYNTETISK
from src.kunstpixel.core.intern.data import (
    DEFAULT_SOURCES,
    LEDELSE,
    ROLLER,
    InternData,
    InternDataError,
    SourceSpec,
    fold,
    repo_root,
    role_id,
    tokens_match,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def data():
    return InternData()


def copy_layout(dest: Path) -> Path:
    """Kopier alle kildefiler til en ny base med samme mappestruktur."""
    for spec in DEFAULT_SOURCES:
        target = dest / spec.path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / spec.path, target)
    return dest


# ---------- Lesing ----------


def test_repo_root_is_project_root():
    assert repo_root() == ROOT


def test_every_source_loads_and_has_findings(data):
    by_source = {s.path: [f for f in data.findings if f.kilde == s.path] for s in DEFAULT_SOURCES}
    for path, findings in by_source.items():
        assert findings, f"Ingen funn fra {path}"


def test_every_finding_has_source_path_text_and_classification(data):
    for f in data.findings:
        assert (ROOT / f.kilde).is_file()
        assert f.sti.strip() and f.tekst.strip()
        assert f.klassifisering == SYNTETISK
        assert f.tema in {"hms", "ik_mat", "brann", "tilsyn", "rolle", "tiltak", "myndighet", "rapportering", "arbeidsoppgaver", "historikk"}


def test_myndighetskontakter_strips_person_names_and_emails(data):
    myn = [f for f in data.findings if f.kilde == "05_data/governance/myndighetskontakter.yaml"]
    assert myn
    for f in myn:
        assert ".example.test" not in f.tekst and "@" not in f.tekst
        assert "kontaktperson" not in f.tekst and "intern eier navn" not in f.tekst


def test_ergonomics_values_are_verbatim(data):
    f = next(f for f in data.findings if f.sti.endswith("ergonomi museumsverter"))
    assert "maks sammenhengende staing: 90 minutter" in f.tekst
    assert "Hver 2. time" in f.tekst


def test_calendar_list_gives_one_finding_per_month(data):
    months = [f for f in data.findings if f.tema == "tilsyn" and f.sti.startswith("revisjonskalender")]
    assert [f.sti.split(" › ")[-1] for f in months] == ["Januar", "Mars", "April", "Juni", "September", "November"]


def test_nested_lists_inherit_parent_context(data):
    skrik = next(f for f in data.findings if "AURA-2026-009" in f.sti)
    assert "Rødt klistremerke" in skrik.kontekst
    assert "tittel: Skrik" in skrik.tekst


def test_root_level_values_are_not_inherited_as_context(data):
    mars = next(f for f in data.findings if f.sti.endswith("Mars"))
    assert mars.kontekst == ""


def test_roster_has_a_contract_for_every_role(data):
    for rid in ROLLER:
        mine = [f for f in data.findings if f.rolle == rid]
        assert mine, rid
        labels = {f.sti.split(" › ")[-1] for f in mine if f.sti.startswith("Rollekontrakter")}
        assert {"Persona", "Input", "Control", "Output"} <= labels, (rid, labels)


def test_roster_keeps_nested_bullets_and_strips_markdown(data):
    ctrl = next(f for f in data.findings if f.rolle == "formidler" and f.sti.endswith("Control"))
    assert "50–90 ord" in ctrl.tekst
    assert "**" not in ctrl.tekst and "`" not in ctrl.tekst


def test_tool_access_table_keeps_wildcards(data):
    f = next(f for f in data.findings if f.sti == "Verktøytilganger › Driftsansvarlig")
    assert "calendar_*" in f.tekst


# ---------- Tilgang ----------


def test_leadership_only_source(data):
    tiltak = [f for f in data.findings if f.tema == "tiltak"]
    assert tiltak
    for rid in ROLLER:
        visible = data.for_role(rid, ("tiltak",))
        assert bool(visible) is (rid in LEDELSE), rid


@pytest.mark.parametrize("bad", [None, "", "admin", "Museumsvert; DROP", 5, ["museumsvert"], "museums vert"])
def test_unknown_role_sees_nothing(data, bad):
    assert data.for_role(bad) == []
    assert data.search("løft", bad) == []


def test_role_id_normalisation():
    assert role_id("Museumsdirektør") == "museumsdirektor"
    assert role_id("  MUSEUMSVERT ") == "museumsvert"
    assert role_id("Kvalitetsvokter") == "kvalitetsvokter"
    assert role_id("Repoforvalter") is None  # byggeteam er ikke en brukerrolle


# ---------- Klassifisering ----------


def test_declared_classification_flows_to_findings():
    specs = tuple(SourceSpec(s.path, s.tema, EKTE if s.tema == "hms" else SYNTETISK, s.tilgang, s.kind) for s in DEFAULT_SOURCES)
    d = InternData(sources=specs)
    assert {f.klassifisering for f in d.findings if f.tema == "hms"} == {EKTE}
    assert {f.klassifisering for f in d.findings if f.tema == "ik_mat"} == {SYNTETISK}


def test_misspelled_classification_becomes_real():
    specs = tuple(SourceSpec(s.path, s.tema, "Syntetisk", s.tilgang, s.kind) for s in DEFAULT_SOURCES)
    assert {f.klassifisering for f in InternData(sources=specs).findings} == {EKTE}


# ---------- Feilformat ----------


def test_malformed_yaml_names_the_file(tmp_path):
    base = copy_layout(tmp_path)
    (base / "05_data/governance/hms_arbeidsmiljo.yaml").write_text("a: [unclosed\n  b: : :", encoding="utf-8")
    with pytest.raises(InternDataError, match="hms_arbeidsmiljo.yaml"):
        InternData(base=base)


def test_malformed_json_names_the_file(tmp_path):
    base = copy_layout(tmp_path)
    (base / "05_data/governance/tilsynskalender.json").write_text('{"a": ', encoding="utf-8")
    with pytest.raises(InternDataError, match="tilsynskalender.json"):
        InternData(base=base)


def test_missing_file_names_the_file(tmp_path):
    base = copy_layout(tmp_path)
    (base / "05_data/governance/ik_mat_kafe.yaml").unlink()
    with pytest.raises(InternDataError, match="ik_mat_kafe.yaml"):
        InternData(base=base)


def test_unknown_source_kind_is_rejected(tmp_path):
    base = copy_layout(tmp_path)
    spec = SourceSpec("05_data/governance/ik_mat_kafe.yaml", "ik_mat", SYNTETISK, frozenset(), "xml")
    with pytest.raises(InternDataError, match="Ukjent kildetype"):
        InternData(base=base, sources=(spec,))


def test_null_values_never_become_the_text_none(tmp_path):
    base = copy_layout(tmp_path)
    (base / "05_data/governance/ik_mat_kafe.yaml").write_text(
        "virksomhet:\n  navn: Kafeen\n  tomt:\nliste:\n  - a: 1\n    b:\n  - null\n", encoding="utf-8"
    )
    d = InternData(base=base)
    texts = [f.tekst for f in d.findings if f.tema == "ik_mat"]
    assert texts and all("None" not in t for t in texts)


def test_empty_yaml_gives_no_findings_not_a_crash(tmp_path):
    base = copy_layout(tmp_path)
    (base / "05_data/governance/ik_mat_kafe.yaml").write_text("", encoding="utf-8")
    d = InternData(base=base)
    assert not [f for f in d.findings if f.tema == "ik_mat"]


# ---------- Endring i kilden slår gjennom ----------


def test_changed_value_in_source_file_is_reflected(tmp_path):
    base = copy_layout(tmp_path)
    p = base / "05_data/governance/hms_arbeidsmiljo.yaml"
    p.write_text(p.read_text(encoding="utf-8").replace("90 minutter", "75 minutter"), encoding="utf-8")
    d = InternData(base=base)
    f = next(f for f in d.findings if f.sti.endswith("ergonomi museumsverter"))
    assert "75 minutter" in f.tekst and "90 minutter" not in f.tekst


# ---------- Søkehjelpere ----------


def test_fold_unifies_spellings():
    assert fold("løft") == fold("loft") == "loft"
    assert fold("Åpningstid") == fold("Apningstid")
    assert fold("høst") == fold("hoest")


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("vernerunde", "vernerunder", True),
        ("vernerunde", "verneutstyr", False),
        ("brann", "brannsikkerhet", True),
        ("museumsvertene", "museumsvert", True),
        ("kjoleskapet", "kjoleskap", True),
        ("loft", "lofte", False),  # for kort til å regnes som samme ord
        ("temperatur", "temperatur", True),
        ("24t", "24t", True),
        ("24t", "24", False),
    ],
)
def test_tokens_match(a, b, expected):
    assert tokens_match(a, b) is expected
