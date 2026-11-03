"""Task 5: åpen MCP-server for kundedata (fase 1: ingen tilgangssperrer, men ingen skriving)."""

import asyncio
import sqlite3

import pytest

from src.kunstpixel.persondata.generer import bygg_database


@pytest.fixture(scope="module")
def srv(tmp_path_factory):
    d = tmp_path_factory.mktemp("mcp")
    bygg_database(d / "p.db", skala="test", csv_dir=None)
    mp = pytest.MonkeyPatch()
    mp.setenv("KUNSTPIXEL_PERSONDATA_DB", str(d / "p.db"))
    from src.kunstpixel.persondata import mcp_server
    yield mcp_server
    mp.undo()


def test_verktoyliste(srv):
    navn = {t.name for t in asyncio.run(srv.mcp.list_tools())}
    assert navn == {"list_tabeller", "beskriv_tabell", "sporring", "innsyn_kontakt", "gavekort_saldo"}


def test_alle_svar_er_merket_syntetisk(srv):
    kode = srv.sporring("SELECT kode FROM gavekort LIMIT 1")["rader"][0][0]
    svar = [
        srv.list_tabeller(), srv.beskriv_tabell("kontakter"), srv.sporring("SELECT 1"),
        srv.innsyn_kontakt("K000001"), srv.gavekort_saldo(kode),
    ]
    assert all(s["klassifisering"] == "syntetisk" for s in svar)


def test_list_tabeller(srv):
    tabeller = {t["tabell"]: t["antall"] for t in srv.list_tabeller()["tabeller"]}
    assert "kontakter" in tabeller and tabeller["kontakter"] > 0


def test_beskriv_tabell_ukjent(srv):
    with pytest.raises(ValueError):
        srv.beskriv_tabell("kontakter; DROP TABLE kontakter")


def test_sporring_kan_joine_ansatte(srv):
    sql = (
        "SELECT k.fornavn || ' ' || k.etternavn, a.navn FROM kontakter k "
        "JOIN museum.hr_ansatte a ON k.ansatt_id = a.ansatt_id LIMIT 5"
    )
    rader = srv.sporring(sql)["rader"]
    assert len(rader) == 5 and all(r[0] == r[1] for r in rader)


@pytest.mark.parametrize("sql", ["DELETE FROM kontakter", "SELECT 1; DROP TABLE kontakter", "UPDATE kontakter SET epost=NULL"])
def test_sporring_avviser_skriving(srv, sql):
    with pytest.raises(PermissionError):
        srv.sporring(sql)


def test_sporring_limit(srv):
    svar = srv.sporring("SELECT * FROM kontakter", limit=10)
    assert len(svar["rader"]) == 10 and svar["avkortet"] is True
    assert srv.sporring("SELECT * FROM kontakter", limit=99999)["rader"].__len__() <= 5000


@pytest.mark.parametrize("kid", ["K999999", "K1' OR '1'='1"])
def test_innsyn_ukjent_og_injeksjon(srv, kid):
    svar = srv.innsyn_kontakt(kid)
    assert svar["funnet"] is False


def test_innsyn_kjent_id_kun_egne_data(srv):
    kid = srv.sporring("SELECT kontakt_id FROM medlemskap WHERE type != 'ansatt' LIMIT 1")["rader"][0][0]
    svar = srv.innsyn_kontakt(kid)
    assert svar["funnet"] is True and svar["kontakt"]["kontakt_id"] == kid
    assert svar["medlemskap"] and all(m["kontakt_id"] == kid for m in svar["medlemskap"])
    assert all(p["kontakt_id"] == kid for p in svar["pameldinger"])


def test_gavekort_saldo_stemmer(srv):
    kode, gid, belop = srv.sporring("SELECT kode, gavekort_id, belop FROM gavekort LIMIT 1")["rader"][0]
    brukt = srv.sporring(f"SELECT COALESCE(SUM(belop), 0) FROM gavekort_bruk WHERE gavekort_id = {gid}")["rader"][0][0]
    svar = srv.gavekort_saldo(kode)
    assert svar["funnet"] is True and abs(svar["saldo"] - (belop - brukt)) < 1e-6


def test_gavekort_injeksjon(srv):
    assert srv.gavekort_saldo("GK' OR '1'='1")["funnet"] is False


def test_ingen_skriving_mulig(srv):
    with srv._koble() as conn, pytest.raises(sqlite3.OperationalError):
        conn.execute("INSERT INTO fordeler VALUES ('x', 'y', 'z')")
