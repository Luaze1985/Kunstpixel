"""H5: import av innlimte chat-svar. Du limer inn hele svaret, tekst rundt og alt. Importen finner YAML-en."""

import copy

import pytest

from src.kunstpixel.core.intern import leveranse as L
from src.kunstpixel.core.intern.leveranse_kjoring import MAKS_SVAR, del_svar, importer_svar
from tests import kontroller_leveranse as cli
from tests.test_leveranse import Teller, dump, fyll

FENCE = "```"


def blokk(kode, d=None):
    return f"{FENCE}yaml\n{dump(d if d is not None else fyll(L.skjelett(kode), Teller()))}{FENCE}"


def chat(*koder):
    return "Selvfølgelig! Her er filene du ba om:\n\n" + "\n\n".join(f"### {L.FILER[k]}\n{blokk(k)}" for k in koder) + "\n\nSkal jeg endre noe mer?"


def kontroller(mappe, kode):
    return [f for f in L.kontroller_tekst(kode, (mappe / L.FILER[kode]).read_text(encoding="utf-8")) if f.alvor == "FEIL"]


# ---------- del_svar ----------


def test_single_file_with_chatter_around_it_is_found_by_its_top_level_field():
    deler, adv = del_svar(chat("A"))
    assert list(deler) == ["A"] and adv == []
    assert "Selvfølgelig" not in deler["A"] and "```" not in deler["A"] and "Skal jeg" not in deler["A"]


def test_all_files_in_one_reply_are_split_correctly_regardless_of_order():
    deler, adv = del_svar(chat("E", "C", "A", "F", "D", "B"))
    assert sorted(deler) == sorted(L.FILER) and adv == []


def test_history_text_file_is_recognised_by_its_top_level_field():
    assert list(del_svar(chat("F"))[0]) == ["F"]


def test_file_is_identified_by_content_not_by_the_heading_the_model_wrote():
    tekst = f"### feilnavn.yaml\n{blokk('C')}"
    assert list(del_svar(tekst)[0]) == ["C"]


def test_raw_yaml_without_fences_is_found_by_its_top_level_field():
    deler, _ = del_svar(dump(fyll(L.skjelett("B"), Teller())))
    assert list(deler) == ["B"]


def test_block_without_known_field_needs_an_explicit_file_code():
    tekst = f"{FENCE}yaml\nnoe: annet\n{FENCE}"
    deler, adv = del_svar(tekst)
    assert deler == {} and "kunne ikke avgjøre" in adv[0]
    deler, adv = del_svar(tekst, "A")
    assert list(deler) == ["A"] and adv == []


def test_requested_file_wins_and_other_blocks_are_skipped_with_a_warning():
    deler, adv = del_svar(chat("A", "B"), "B")
    assert list(deler) == ["B"] and any("myndighetskontakter.yaml" in a and "hoppet over" in a for a in adv)


def test_same_file_twice_keeps_the_last_one_and_warns():
    ny = copy.deepcopy(fyll(L.skjelett("A"), Teller()))
    ny["myndigheter"][0]["hva_de_vil"] = "Rutinen er skrevet om og gjelder nå på en litt annen måte."
    deler, adv = del_svar(f"{blokk('A')}\n\nHer er en rettet versjon:\n\n{blokk('A', ny)}")
    assert "skrevet om" in deler["A"] and any("flere ganger" in a for a in adv)


@pytest.mark.parametrize("tekst", ["", "   \n", None, 42, []])
def test_empty_or_non_text_reply_gives_nothing_and_a_warning(tekst):
    deler, adv = del_svar(tekst)
    assert deler == {} and adv


def test_huge_reply_is_refused():
    deler, adv = del_svar("a" * (MAKS_SVAR + 1))
    assert deler == {} and "importeres ikke" in adv[0]


def test_chat_text_with_other_code_blocks_does_not_confuse_the_split():
    tekst = f"Forklaring:\n{FENCE}python\nprint('hei')\n{FENCE}\n\n{chat('A')}"
    deler, adv = del_svar(tekst)
    assert list(deler) == ["A"] and len(adv) == 1  # python-blokken hoppes over


# ---------- importer_svar ----------


def test_import_writes_only_known_file_names_inside_the_target_folder(tmp_path):
    tekst = "### ../../ond.yaml\n" + blokk("A") + "\n### /etc/passwd\n" + blokk("B")
    skrevet, _ = importer_svar(tekst, tmp_path / "ut")
    assert skrevet == ["A", "B"]
    assert {p.name for p in (tmp_path / "ut").iterdir()} == {L.FILER["A"], L.FILER["B"]}
    assert not (tmp_path / "ond.yaml").exists()


def test_imported_reference_files_pass_the_control(tmp_path):
    importer_svar(chat(*L.FILER), tmp_path)
    assert L.kontroller_mappe(tmp_path).ok


def test_reimport_overwrites_the_staging_file_so_a_corrected_answer_replaces_the_bad_one(tmp_path):
    dårlig = copy.deepcopy(fyll(L.skjelett("A"), Teller()))
    dårlig["myndigheter"][0]["hva_de_vil"] = "Ring Kari på 22 33 44 55 for å avtale tid."
    importer_svar(f"{blokk('A', dårlig)}", tmp_path)
    assert kontroller(tmp_path, "A")
    importer_svar(chat("A"), tmp_path)
    assert kontroller(tmp_path, "A") == []


def test_lowercase_file_code_is_accepted(tmp_path):
    skrevet, _ = importer_svar(f"{FENCE}\nnoe: annet\n{FENCE}", tmp_path, "c")
    assert skrevet == ["C"]


# ---------- Kommandolinjen ----------


def skriv_svar(tmp_path, tekst, navn="svar.txt"):
    p = tmp_path / navn
    p.write_text(tekst, encoding="utf-8")
    return p


def test_cli_import_of_a_good_answer_reports_ok_and_exit_zero(tmp_path, capsys):
    svar = skriv_svar(tmp_path, chat("A"))
    assert cli.main(["--importer", str(svar), "--til", str(tmp_path / "lev")]) == 0
    ut = capsys.readouterr().out
    assert "myndighetskontakter.yaml" in ut and "OK" in ut and "LIM DETTE" not in ut


def test_cli_import_of_a_bad_answer_prints_the_correction_list_for_that_file_only(tmp_path, capsys):
    dårlig = copy.deepcopy(fyll(L.skjelett("C"), Teller()))
    dårlig["rapporter"][2]["timer_per_gang"] = 37
    svar = skriv_svar(tmp_path, chat("A") + "\n\n" + f"### rapporteringskalender.yaml\n{blokk('C', dårlig)}")
    assert cli.main(["--importer", str(svar), "--til", str(tmp_path / "lev")]) == 1
    ut = capsys.readouterr().out
    assert "LIM DETTE TILBAKE TIL MODELLEN (rapporteringskalender.yaml)" in ut
    assert "rapporter[2].timer_per_gang [FAST_FELT_ENDRET]" in ut and "Skal være 36" in ut
    assert ut.count("LIM DETTE") == 1  # ren fil A gir ingen retteliste


def test_cli_import_exit_codes_for_missing_file_and_nothing_found(tmp_path, capsys):
    assert cli.main(["--importer", str(tmp_path / "finnes-ikke.txt")]) == 2
    tom = skriv_svar(tmp_path, "Jeg kan dessverre ikke hjelpe med dette.")
    assert cli.main(["--importer", str(tom), "--til", str(tmp_path / "lev")]) == 2
    assert "Ingen filer ble importert" in capsys.readouterr().out
    assert not (tmp_path / "lev").exists() or not list((tmp_path / "lev").iterdir())


def test_cli_import_with_explicit_file_code_for_answer_without_fences(tmp_path, capsys):
    svar = skriv_svar(tmp_path, dump(fyll(L.skjelett("D"), Teller())))
    assert cli.main(["--importer", str(svar), "--fil", "D", "--til", str(tmp_path / "lev")]) == 0
    assert (tmp_path / "lev" / L.FILER["D"]).is_file()


def test_cli_default_staging_folder_is_the_inbox_delivery_folder():
    assert cli.STANDARD_LEVERANSE.as_posix().endswith("01_inbox/h5_leveranse")
    assert not any((cli.STANDARD_LEVERANSE / f).exists() for f in L.FILER.values())  # tomt før du leverer


def test_full_flow_import_then_install_into_a_scratch_data_folder(tmp_path, capsys):
    svar = skriv_svar(tmp_path, chat(*L.FILER))
    lev, mal = tmp_path / "lev", tmp_path / "data"
    assert cli.main(["--importer", str(svar), "--til", str(lev)]) == 0
    assert cli.main([str(lev)]) == 0
    assert cli.main([str(lev), "--installer", ",".join(L.FILER), "--mal", str(mal), "--yes"]) == 0
    assert {p.name for p in mal.iterdir()} == set(L.FILER.values())


# ---------- Kodeblokk-leseren ----------


def test_fence_reader_handles_languages_unterminated_blocks_and_odd_tags():
    from src.kunstpixel.core.intern.leveranse_kjoring import hent_yaml, kodeblokker, yaml_blokker

    tekst = f"{FENCE}python\nprint(1)\n{FENCE}\ntekst\n{FENCE}YAML title\na: 1\n{FENCE}\n{FENCE}\nb: 2\n{FENCE}\n{FENCE}json\n{{}}\n{FENCE}"
    assert [s for s, _ in kodeblokker(tekst)] == ["python", "yaml title", "", "json"]
    assert yaml_blokker(tekst) == ["b: 2"]  # «yaml title» regnes ikke som ren yaml, men blokk uten språk gjør det
    assert hent_yaml(f"{FENCE}python\nx=1\n{FENCE}\n{FENCE}yaml\na: 1\n{FENCE}") == "a: 1\n"
    assert kodeblokker(f"{FENCE}yaml\na: 1\nb: 2") == [("yaml", "a: 1\nb: 2")]  # ulukket blokk tas med
    assert kodeblokker("ingen blokker her") == [] and kodeblokker("") == []


def test_python_block_before_the_yaml_never_hides_the_yaml():
    tekst = f"Først en forklaring:\n{FENCE}python\nprint('hei')\n{FENCE}\n\nHer er filen:\n{blokk('A')}"
    deler, _ = del_svar(tekst)
    assert list(deler) == ["A"]


# ---------- Kopiering av prompt ----------


def test_copy_command_picks_the_right_order_file_and_never_touches_the_clipboard_in_tests(monkeypatch, capsys):
    kopiert = []
    monkeypatch.setattr(cli, "kopier_til_utklippstavle", lambda fil: kopiert.append(fil.name) or True)
    assert cli.main(["--kopier", "a"]) == 0
    assert cli.main(["--kopier", "ALLE"]) == 0
    assert kopiert == ["fil_A_myndighetskontakter.md", "komplett.md"]
    assert "Lim den inn i modellen" in capsys.readouterr().out


def test_copy_command_rejects_unknown_codes_and_reports_clipboard_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli, "kopier_til_utklippstavle", lambda fil: False)
    assert cli.main(["--kopier", "Z"]) == 2
    assert cli.main(["--kopier", "B"]) == 0
    assert "Kunne ikke kopiere automatisk" in capsys.readouterr().out
