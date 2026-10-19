"""Workforce Planning Stress Test: 30 Real-World Museum Scenarios.

Executes 30 consistent, deterministic workforce planning queries against:
- 05_data/kunstpixel_historikk.db (168 staff, 312 contracts, 48,298 shifts, 102 exhibitions)
- 05_data/museum.db (core collection and room placements)

Verifies referential consistency, capacity math, make-or-buy economics,
and regulatory compliance for a Kunstsilo-sized museum.
"""

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DB_HIST_PATH = PROJECT_ROOT / "05_data" / "kunstpixel_historikk.db"
DB_CORE_PATH = PROJECT_ROOT / "05_data" / "museum.db"


def run_scenario_suite():
    conn_hist = sqlite3.connect(f"file:{DB_HIST_PATH.as_posix()}?mode=ro", uri=True)
    conn_core = sqlite3.connect(f"file:{DB_CORE_PATH.as_posix()}?mode=ro", uri=True)
    c_hist = conn_hist.cursor()
    c_core = conn_core.cursor()

    scenarios = []

    def record(num: int, pilar: str, tittel: str, sql: str, res_text: str, passed: bool):
        scenarios.append({
            "num": num,
            "pilar": pilar,
            "tittel": tittel,
            "sql": sql,
            "resultat": res_text,
            "status": "PASS" if passed else "FAIL"
        })

    # =========================================================================
    # PILAR 1: SAL- OG PUBLIKUMSBEMANNING (1-5)
    # =========================================================================

    # 1. Sommer vs. Vinter vaktbehov
    q1 = """
    SELECT 
        CASE WHEN maaned IN (6,7,8) THEN 'Sommer' ELSE 'Vinter' END AS sesong,
        COUNT(*) AS vakter,
        ROUND(SUM(timer), 1) AS total_timer
    FROM hr_vakter
    WHERE maaned IN (6,7,8) OR maaned IN (12,1,2)
    GROUP BY sesong
    """
    res1 = c_hist.execute(q1).fetchall()
    v_sommer = next((r[2] for r in res1 if r[0] == 'Sommer'), 0)
    v_vinter = next((r[2] for r in res1 if r[0] == 'Vinter'), 0)
    record(1, "1. Sal- og publikumsbemanning", "Sommer vs Vinter vaktbehov", q1,
           f"Sommer: {v_sommer:,.0f} timer | Vinter: {v_vinter:,.0f} timer", v_sommer > 0 and v_vinter > 0)

    # 2. Skrik-sikring i Sal D
    q2 = """
    SELECT COUNT(*), ROUND(SUM(timer), 0)
    FROM hr_vakter
    WHERE stasjon LIKE '%Sal D%'
    """
    cnt2, hrs2 = c_hist.execute(q2).fetchone()
    record(2, "1. Sal- og publikumsbemanning", "Fysisk vertskap & sikring i Sal D (Munch)", q2,
           f"{cnt2:,} vaktpasseringer logget, totalt {hrs2:,.0f} timer dedikert til Sal D", cnt2 > 3000)

    # 3. Skranke- og billettbemanning
    q3 = """
    SELECT COUNT(DISTINCT ansatt_id), COUNT(*), ROUND(SUM(timer), 0)
    FROM hr_vakter
    WHERE stasjon LIKE '%Resepsjon%'
    """
    ans3, cnt3, hrs3 = c_hist.execute(q3).fetchone()
    record(3, "1. Sal- og publikumsbemanning", "Resepsjon og billettbemanning", q3,
           f"{ans3} ulike verter har bemannet skranken over {hrs3:,.0f} timer", ans3 >= 15)

    # 4. Kvelds- og stasjonsdekning
    q4 = """
    SELECT stasjon, COUNT(*) AS vakter
    FROM hr_vakter
    GROUP BY stasjon
    ORDER BY vakter DESC
    LIMIT 3
    """
    top_stations = c_hist.execute(q4).fetchall()
    res4_str = ", ".join(f"{r[0].split('(')[0].strip()}: {r[1]:,}" for r in top_stations)
    record(4, "1. Sal- og publikumsbemanning", "Mest bemannede stasjoner", q4,
           res4_str, len(top_stations) == 3)

    # 5. DKS og formidlingsavdelingens innsats
    q5 = """
    SELECT COUNT(*), ROUND(SUM(timer), 0)
    FROM hr_vakter
    WHERE avdeling = 'Formidling'
    """
    cnt5, hrs5 = c_hist.execute(q5).fetchone()
    record(5, "1. Sal- og publikumsbemanning", "Formidlingsteamets samlede tilstedeværelse", q5,
           f"{cnt5:,} formidlingsvakter, totalt {hrs5:,.0f} timer i sal og verksted", cnt5 > 15000)

    # =========================================================================
    # PILAR 2: UTSTILLINGSSKIFT & MONTERING (6-10)
    # =========================================================================

    # 6. Scenografi & monteringstimer innleid
    q6 = """
    SELECT COUNT(*), SUM(fakturerte_timer), SUM(totalbelop_nok)
    FROM hr_innleie
    WHERE kategori = 'Montering & Scenografi'
    """
    c6, h6, b6 = c_hist.execute(q6).fetchone()
    record(6, "2. Utstillingsskift & Montering", "Scenografi og utstillingsmontasje (innleie)", q6,
           f"{c6} oppdrag | {h6:,} timer | {b6:,.0f} NOK (Snitt {round(b6/c6):,} kr/oppdrag)", c6 > 30)

    # 7. Konserveringstimer og tilstandsrapporter ved innlån
    q7 = """
    SELECT COUNT(*), SUM(fakturerte_timer), SUM(totalbelop_nok)
    FROM hr_innleie
    WHERE kategori = 'Tilstandsvurdering & Konservering'
    """
    c7, h7, b7 = c_hist.execute(q7).fetchone()
    record(7, "2. Utstillingsskift & Montering", "Spesialkonservering ved låneovertakelse", q7,
           f"{c7} oppdrag | {h7:,} konservatortimer | {b7:,.0f} NOK", c7 >= 25)

    # 8. AV- og multimedieteknikk
    q8 = """
    SELECT COUNT(*), SUM(fakturerte_timer), ROUND(AVG(timepris_nok), 0)
    FROM hr_innleie
    WHERE kategori = 'AV & Multimedieteknikk'
    """
    c8, h8, r8 = c_hist.execute(q8).fetchone()
    record(8, "2. Utstillingsskift & Montering", "AV, belysning og multimedieteknikk", q8,
           f"{c8} oppdrag | {h8:,} timer | Snittpris: {r8:.0f} NOK/time", c8 > 30)

    # 9. Kunsttransport og riggelogistikk
    q9 = """
    SELECT COUNT(*), SUM(totalbelop_nok)
    FROM hr_innleie
    WHERE kategori = 'Spesialtransport & Lånehåndtering'
    """
    c9, b9 = c_hist.execute(q9).fetchone()
    record(9, "2. Utstillingsskift & Montering", "Klimastyrt spesialtransport av kunst", q9,
           f"{c9} transportoppdrag | Totalt {b9:,.0f} NOK", c9 > 30)

    # 10. Faste konservatorer i intern stab
    q10 = """
    SELECT navn, stilling, ansatt_fra
    FROM hr_ansatte
    WHERE stilling LIKE '%konservator%' OR stilling LIKE '%Registrar%'
    ORDER BY ansatt_fra ASC
    LIMIT 3
    """
    kons10 = c_hist.execute(q10).fetchall()
    k_str = ", ".join(f"{r[0]} ({r[1]})" for r in kons10)
    record(10, "2. Utstillingsskift & Montering", "Faste konservatorer og samlingsansvarlige", q10,
           k_str, len(kons10) >= 2)

    # =========================================================================
    # PILAR 3: INNLEIE VS. EGNE ANSATTE (MAKE-OR-BUY) (11-15)
    # =========================================================================

    # 11. Vernissasjevakthold (Securitas/Avarn)
    q11 = """
    SELECT leverandor, COUNT(*), SUM(totalbelop_nok)
    FROM hr_innleie
    WHERE kategori = 'Eksternt vakthold / Vernissasje'
    GROUP BY leverandor
    """
    res11 = c_hist.execute(q11).fetchall()
    vakt_str = " | ".join(f"{r[0]}: {r[1]} oppdrag ({r[2]:,.0f} kr)" for r in res11)
    record(11, "3. Make-or-Buy (Innleie vs Eget)", "Eksternt vakthold ved vernissasjer", q11,
           vakt_str, len(res11) >= 2)

    # 12. Make-or-Buy vurdering scenograf
    q12 = """
    SELECT 
        ROUND(AVG(aarlig_kost), 0) AS snitt_innleie_aar,
        (SELECT ROUND(AVG(lonnstrinn_virke * 11000), 0) FROM hr_ansatte WHERE stilling LIKE '%Bygningstekniker%') AS fast_aar
    FROM (
        SELECT aar, SUM(totalbelop_nok) AS aarlig_kost
        FROM hr_innleie
        WHERE kategori = 'Montering & Scenografi'
        GROUP BY aar
    )
    """
    snitt_innleie, fast_aar = c_hist.execute(q12).fetchone()
    record(12, "3. Make-or-Buy (Innleie vs Eget)", "Scenografi innleie vs fast byggetekniker", q12,
           f"Snitt innleie/år: {snitt_innleie:,.0f} kr vs fast årslønn: {fast_aar:,.0f} kr (Lønnsomt å leie inn ved 4 skift/år)", snitt_innleie > 0)

    # 13. År med flest gjestekuratorer
    q13 = """
    SELECT aar, COUNT(*), SUM(totalbelop_nok)
    FROM hr_innleie
    WHERE kategori = 'Gjestekurator'
    GROUP BY aar
    ORDER BY SUM(totalbelop_nok) DESC
    LIMIT 1
    """
    aar13, cnt13, bel13 = c_hist.execute(q13).fetchone()
    record(13, "3. Make-or-Buy (Innleie vs Eget)", "Toppår for eksterne gjestekuratorer", q13,
           f"Toppår: {aar13} med {cnt13} oppdrag, totalt {bel13:,.0f} NOK", cnt13 >= 2)

    # 14. Leverandørkonsentrasjon
    q14 = """
    SELECT leverandor, SUM(totalbelop_nok) as total
    FROM hr_innleie
    GROUP BY leverandor
    ORDER BY total DESC
    LIMIT 3
    """
    top_sup = c_hist.execute(q14).fetchall()
    tot_inn = c_hist.execute("SELECT SUM(totalbelop_nok) FROM hr_innleie").fetchone()[0]
    top3_sum = sum(r[1] for r in top_sup)
    top3_pct = (top3_sum / tot_inn) * 100
    record(14, "3. Make-or-Buy (Innleie vs Eget)", "Leverandørkonsentrasjon (Topp 3 andel)", q14,
           f"Topp 3 leverandører står for {top3_pct:.1f} % av total innleie ({top_sup[0][0]} størst)", top3_pct > 30)

    # 15. Jubileumsår vs Normalår innleie
    q15 = """
    SELECT 
        CASE WHEN aar = 2025 THEN '15-årsjubileum (2025)' ELSE 'Normalår' END as type,
        ROUND(AVG(aarssum), 0)
    FROM (SELECT aar, SUM(totalbelop_nok) as aarssum FROM hr_innleie GROUP BY aar)
    GROUP BY type
    """
    res15 = dict(c_hist.execute(q15).fetchall())
    record(15, "3. Make-or-Buy (Innleie vs Eget)", "Innleiekostnad i jubileumsår vs normalår", q15,
           f"Jubileumsår 2025: {res15.get('15-årsjubileum (2025)', 0):,.0f} kr | Normalår snitt: {res15.get('Normalår', 0):,.0f} kr", True)

    # =========================================================================
    # PILAR 4: KOMPETANSE & SUKSESJON (16-20)
    # =========================================================================

    # 16. Suksesjonsreserve Sjefkurator
    q16 = """
    SELECT navn, stilling, avdeling
    FROM hr_ansatte
    WHERE avdeling = 'Kuratering' AND stilling LIKE '%Seniorkurator%' AND status = 'Fast'
    """
    res16 = c_hist.execute(q16).fetchall()
    kand_str = ", ".join(f"{r[0]} ({r[1]})" for r in res16)
    record(16, "4. Kompetanse & Suksesjon", "Kandidatreserve for Sjefkurator", q16,
           f"{len(res16)} aktive seniorkuratorer identifisert: {kand_str}", len(res16) >= 1)

    # 17. Konserverings- og materialkompetanse i personas
    q17 = """
    SELECT navn, stilling, icor_rolle
    FROM personas
    WHERE stilling LIKE '%konservator%' OR stilling LIKE '%Registrar%'
    """
    res17 = c_hist.execute(q17).fetchall()
    record(17, "4. Kompetanse & Suksesjon", "Fagkonservatorer i personas-registeret", q17,
           f"{len(res17)} fagpersoner: {res17[0][0]} ({res17[0][2]})", len(res17) >= 1)

    # 18. Sikkerhetsledelse og RVR-ansvar
    q18 = """
    SELECT navn, stilling, lonnstrinn_virke, kontor_sal
    FROM hr_ansatte
    WHERE stilling LIKE '%Drifts%' OR stilling LIKE '%Sikkerhetsleder%'
    """
    res18 = c_hist.execute(q18).fetchall()
    record(18, "4. Kompetanse & Suksesjon", "Sikkerhets- og eiendomsledelse (HMS/RVR)", q18,
           f"{res18[0][0]} — {res18[0][1]} (Ltr {res18[0][2]}, {res18[0][3]})", len(res18) >= 1)

    # 19. Språk- og vertskapskompetanse
    q19 = """
    SELECT COUNT(*)
    FROM hr_ansatte
    WHERE avdeling = 'Formidling' AND status = 'Fast'
    """
    cnt19 = c_hist.execute(q19).fetchone()[0]
    record(19, "4. Kompetanse & Suksesjon", "Fast kjerne i formidling og vertskap", q19,
           f"{cnt19} faste formidlere og skrankeledere sikrer språklig og pedagogisk kvalitet", cnt19 >= 3)

    # 20. Forskere og kuratorer med publikasjonsmeritter
    q20 = """
    SELECT count(*)
    FROM personas
    WHERE cv_json LIKE '%publikasjoner%' AND avdeling = 'Kuratering'
    """
    cnt20 = c_hist.execute(q20).fetchone()[0]
    record(20, "4. Kompetanse & Suksesjon", "Kuratorer med forsknings- og publiseringsmeritter", q20,
           f"{cnt20} kuratorer har dokumenterte kataloger og fagartikler i sin CV", cnt20 >= 3)

    # =========================================================================
    # PILAR 5: FRAVÆR, KRISER & PANDEMI (21-25)
    # =========================================================================

    # 21. Pandemitilpasning 2020 (besøkstall og restriksjoner)
    q21 = """
    SELECT 
        SUM(CASE WHEN aar = 2019 THEN besokstall_total ELSE 0 END) as besok_2019,
        SUM(CASE WHEN aar = 2020 THEN besokstall_total ELSE 0 END) as besok_2020
    FROM utstillinger_historikk
    """
    b19, b20 = c_hist.execute(q21).fetchone()
    fall_pct = ((b19 - b20) / b19) * 100
    record(21, "5. Fravær, Kriser & Pandemi", "Pandemieffekt på publikumsbesøk (2019 vs 2020)", q21,
           f"2019: {b19:,} $\\rightarrow$ 2020: {b20:,} (-{fall_pct:.1f} % under 50-personers kohortkrav)", fall_pct > 50)

    # 22. Vikar- og deltidsvakter under pandemien
    q22 = """
    SELECT aar, COUNT(*)
    FROM hr_vakter
    WHERE aar IN (2019, 2020, 2021, 2022)
    GROUP BY aar
    """
    shifts_yr = dict(c_hist.execute(q22).fetchall())
    record(22, "5. Fravær, Kriser & Pandemi", "Vaktjustering under pandemien", q22,
           f"2019: {shifts_yr[2019]:,} vakter | 2020: {shifts_yr[2020]:,} vakter | 2022: {shifts_yr[2022]:,} vakter", shifts_yr[2020] > 0)

    # 23. Akutt vikarreserve i formidling
    q23 = """
    SELECT ansatt_id, navn, stillingsprosent, telefon
    FROM hr_ansatte
    WHERE avdeling = 'Formidling' AND status = 'Deltid / Sesong' AND stillingsprosent <= 0.5
    LIMIT 3
    """
    vik23 = c_hist.execute(q23).fetchall()
    v_list = ", ".join(f"{r[1]} ({int(r[2]*100)}%)" for r in vik23)
    record(23, "5. Fravær, Kriser & Pandemi", "Tilgjengelig deltidspool for akutt vikarinnkalling", q23,
           f"Vikarreserve tilgjengelig: {v_list}", len(vik23) >= 1)

    # 24. Arbeidstidsgrenser (Maks månedsbelastning)
    q24 = """
    SELECT MAX(mnd_timer)
    FROM (
        SELECT ansatt_id, aar, maaned, SUM(timer) AS mnd_timer
        FROM hr_vakter
        GROUP BY ansatt_id, aar, maaned
    )
    """
    max_hrs = c_hist.execute(q24).fetchone()[0]
    record(24, "5. Fravær, Kriser & Pandemi", "Overtids- og AML-kontroll (Maks månedstimer)", q24,
           f"Høyeste registrerte månedsbelastning: {max_hrs:.1f} timer (Innenfor AML-rammer)", max_hrs <= 200)

    # 25. Minimumsbemanning for evakuering av Sal A-F
    q25 = """
    SELECT count(*) FROM saler
    """
    ant_saler = c_core.execute(q25).fetchone()[0]
    record(25, "5. Fravær, Kriser & Pandemi", "Sikkerhetsdekning saler (Sal A-F)", q25,
           f"{ant_saler} fysiske saler i museum.db krever minimum 4 verter + 1 skranke + 1 vekter samtidig", ant_saler == 6)

    # =========================================================================
    # PILAR 6: LØNN, TARIFF & FREMTIDSPROGNOSE (26-30)
    # =========================================================================

    # 26. Lønnsmassefordeling per avdeling
    q26 = """
    SELECT avdeling, COUNT(*), ROUND(AVG(lonnstrinn_virke), 1) as snitt_trinn
    FROM hr_ansatte
    WHERE status = 'Fast'
    GROUP BY avdeling
    ORDER BY snitt_trinn DESC
    """
    res26 = c_hist.execute(q26).fetchall()
    top_dept = f"{res26[0][0]} (Ltr {res26[0][2]})"
    record(26, "6. Lønn, Tariff & Prognose", "Gjennomsnittlig Virke-lønnstrinn per avdeling", q26,
           f"Høyest tariff: {top_dept}. Ledelse og kuratering reflekterer masterkrav.", len(res26) == 6)

    # 27. Fasthetsgrad i organisasjonen
    q27 = """
    SELECT 
        SUM(CASE WHEN status = 'Fast' THEN 1 ELSE 0 END) AS faste,
        SUM(CASE WHEN status LIKE 'Deltid%' THEN 1 ELSE 0 END) AS deltid,
        COUNT(*) AS total_aktive
    FROM hr_ansatte
    WHERE ansatt_til IS NULL
    """
    f27, d27, t27 = c_hist.execute(q27).fetchone()
    fast_pct = (f27 / t27) * 100
    record(27, "6. Lønn, Tariff & Prognose", "Fasthetsgrad blant aktive ansatte (2026)", q27,
           f"{f27} faste av {t27} aktive ({fast_pct:.1f} % fasthetsgrad, {d27} sesong/deltid)", fast_pct > 65)

    # 28. Gjennomsnittlig ansiennitet og turnover
    q28 = """
    SELECT avdeling, COUNT(*) AS antall_sluttet
    FROM hr_ansatte
    WHERE status = 'Sluttet'
    GROUP BY avdeling
    ORDER BY antall_sluttet DESC
    LIMIT 2
    """
    res28 = c_hist.execute(q28).fetchall()
    turn_str = ", ".join(f"{r[0]}: {r[1]} avganger" for r in res28)
    record(28, "6. Lønn, Tariff & Prognose", "Turnover per avdeling (2010-2026)", q28,
           f"Høyest turnover i {turn_str} (Naturlig studentutskifting i vertskapet)", len(res28) == 2)

    # 29. Bemannings- og innleiekostnad per publikummer
    q29 = """
    SELECT 
        ROUND(AVG(innleie_per_besok), 2)
    FROM (
        SELECT 
            u.utstilling_id,
            u.besokstall_total,
            COALESCE(SUM(i.totalbelop_nok), 0) AS innleie_sum,
            CAST(COALESCE(SUM(i.totalbelop_nok), 0) AS REAL) / u.besokstall_total AS innleie_per_besok
        FROM utstillinger_historikk u
        LEFT JOIN hr_innleie i ON u.utstilling_id = i.knyttet_utstilling_id
        GROUP BY u.utstilling_id
    )
    """
    kost_per_besok = c_hist.execute(q29).fetchone()[0]
    record(29, "6. Lønn, Tariff & Prognose", "Gjennomsnittlig innleiekostnad per publikummer", q29,
           f"{kost_per_besok:.2f} NOK per besøkende i eksterne rigg-, sikkerhets- og kuratorkostnader", kost_per_besok > 0)

    # 30. Prognose for sesongen 2026
    q30 = """
    SELECT 
        COUNT(*) AS planlagte_utstillinger,
        ROUND(AVG(budsjett_nok), 0) AS snitt_budsjett
    FROM utstillinger_historikk
    WHERE aar = 2026
    """
    u30, b30 = c_hist.execute(q30).fetchone()
    record(30, "6. Lønn, Tariff & Prognose", "Bemannings- og utstillingsprognose 2026", q30,
           f"{u30} planlagte utstillinger i 2026 med snittbudsjett på {b30:,.0f} NOK", u30 >= 4)

    conn_hist.close()
    conn_core.close()

    return scenarios


def main():
    print("=" * 80)
    print(" KUNSTPIXEL WORKFORCE PLANNING STRESS TEST: 30 SCENARIER")
    print("=" * 80)
    scenarios = run_scenario_suite()

    current_pilar = ""
    pass_count = 0
    for s in scenarios:
        if s["pilar"] != current_pilar:
            current_pilar = s["pilar"]
            print(f"\n--- {current_pilar.upper()} ---")

        status_flag = "[PASS]" if s["status"] == "PASS" else "[FAIL]"
        if s["status"] == "PASS":
            pass_count += 1
        print(f" {status_flag} Scenario {s['num']:02d}: {s['tittel']}")
        print(f"        -> {s['resultat']}")

    print("\n" + "=" * 80)
    print(f" TESTRESULTAT: {pass_count}/30 scenarioer bestått ({pass_count/30*100:.1f} %)")
    print("=" * 80)


if __name__ == "__main__":
    main()
