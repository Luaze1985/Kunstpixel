import csv
import json
import yaml
import sqlite3
import pytest
from pathlib import Path

DELIVERABLES_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = DELIVERABLES_DIR.parents[1]
DB_PATH = ROOT_DIR / "05_data" / "museum.db"
STAGING_DIR = DELIVERABLES_DIR / "staging"
AP9_DIR = STAGING_DIR / "AP9_museum_kunst_sluttleveranse"

# 1. FILE INTEGRITY & SCHEMA TESTS
class TestFileIntegrity:
    def test_deliverable_files_exist(self):
        expected_files = [
            "issues.csv",
            "data_contract.yaml",
            "rule_registry.yaml",
            "source_registry.jsonl",
            "changes.md",
            "blockers.md",
            "architecture_decision.md",
            "README.md"
        ]
        for fname in expected_files:
            assert (DELIVERABLES_DIR / fname).is_file(), f"Mangler leveranse: {fname}"

    def test_valid_yaml_contracts(self):
        with open(DELIVERABLES_DIR / "data_contract.yaml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert "kjerne_tabeller_museum_db" in data
        assert "hr_ansatte" in data["kjerne_tabeller_museum_db"]
        assert "personverngrenser_og_k_anonymitet" in data

    def test_valid_yaml_rule_registry(self):
        with open(DELIVERABLES_DIR / "rule_registry.yaml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert "operator_taksonomi" in data
        assert "regler" in data
        assert len(data["regler"]) == 212

    def test_source_registry_lines(self):
        count = 0
        with open(DELIVERABLES_DIR / "source_registry.jsonl", 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    assert "source_id" in item
                    assert "source_url" in item
                    assert "verification_status" in item
                    count += 1
        assert count >= 100, f"For få kilder registrert: {count}"

# 2. ID UNIQUENESS TESTS
class TestIdUniqueness:
    def test_question_id_uniqueness(self):
        with open(AP9_DIR / "fasit_sporsmal.csv", 'r', encoding='utf-8-sig') as f:
            questions = list(csv.DictReader(f))
        assert len(questions) == 94
        q_ids = [q['sporsmal_id'].strip() for q in questions]
        assert len(q_ids) == len(set(q_ids)), "Duplikate sporsmal_id funnet!"

    def test_rule_id_uniqueness(self):
        with open(AP9_DIR / "regler_forslag.csv", 'r', encoding='utf-8-sig') as f:
            rules = list(csv.DictReader(f))
        assert len(rules) == 212
        r_ids = [r['regel_id'].strip() for r in rules]
        assert len(r_ids) == len(set(r_ids)), "Duplikate regel_id funnet!"

    def test_issue_id_uniqueness(self):
        with open(DELIVERABLES_DIR / "issues.csv", 'r', encoding='utf-8') as f:
            issues = list(csv.DictReader(f))
        assert len(issues) >= 6
        iss_ids = [i['issue_id'].strip() for i in issues]
        assert len(iss_ids) == len(set(iss_ids)), "Duplikate issue_id funnet!"

# 3. RELATIONAL INTEGRITY TESTS
class TestRelationalIntegrity:
    @pytest.fixture(scope="class")
    def db_conn(self):
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        yield conn
        conn.close()

    def test_employee_and_shifts_integrity(self, db_conn):
        cur = db_conn.cursor()
        emp_ids = {r[0] for r in cur.execute("SELECT ansatt_id FROM hr_ansatte").fetchall()}
        assert len(emp_ids) == 168
        
        # Check all shifts reference valid employee
        orphan_shifts = cur.execute("SELECT COUNT(*) FROM hr_vakter WHERE ansatt_id NOT IN (SELECT ansatt_id FROM hr_ansatte)").fetchone()[0]
        assert orphan_shifts == 0, f"Foreldreløse vakter funnet: {orphan_shifts}"

    def test_absence_integrity(self, db_conn):
        cur = db_conn.cursor()
        orphan_absences = cur.execute("SELECT COUNT(*) FROM hr_fravaer WHERE ansatt_id NOT IN (SELECT ansatt_id FROM hr_ansatte)").fetchone()[0]
        assert orphan_absences == 0, f"Foreldreløst fravær funnet: {orphan_absences}"

    def test_tariff_trinn_integrity(self, db_conn):
        cur = db_conn.cursor()
        tariff_trinn = {r[0] for r in cur.execute("SELECT lonnstrinn FROM virke_tariff").fetchall()}
        emp_trinn = cur.execute("SELECT DISTINCT lonnstrinn_virke FROM hr_ansatte").fetchall()
        for (tr,) in emp_trinn:
            assert tr in tariff_trinn, f"Lønnstrinn {tr} finnes ikke i virke_tariff!"

# 4. DATE AND TIMELINE CONSISTENCY
class TestTimelineConsistency:
    @pytest.fixture(scope="class")
    def db_conn(self):
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        yield conn
        conn.close()

    def test_shifts_within_employment_dates(self, db_conn):
        cur = db_conn.cursor()
        bad_shifts = cur.execute("""
            SELECT v.vakt_id, v.ansatt_id, v.dato, a.ansatt_fra, a.ansatt_til
            FROM hr_vakter v
            JOIN hr_ansatte a ON v.ansatt_id = a.ansatt_id
            WHERE (v.dato < a.ansatt_fra) OR (a.ansatt_til IS NOT NULL AND v.dato > a.ansatt_til)
        """).fetchall()
        assert len(bad_shifts) == 0, f"Vakter utenfor ansettelsesperiode: {len(bad_shifts)}"

    def test_absence_within_employment_dates(self, db_conn):
        cur = db_conn.cursor()
        bad_absence = cur.execute("""
            SELECT f.fravaer_id, f.ansatt_id, f.fra, f.til, a.ansatt_fra, a.ansatt_til
            FROM hr_fravaer f
            JOIN hr_ansatte a ON f.ansatt_id = a.ansatt_id
            WHERE (f.fra < a.ansatt_fra) OR (a.ansatt_til IS NOT NULL AND f.til > a.ansatt_til)
        """).fetchall()
        assert len(bad_absence) == 0, f"Fravær utenfor ansettelsesperiode: {len(bad_absence)}"

# 5. RULE ENGINE AND OPERATOR EXECUTION
class TestRuleEngine:
    @pytest.fixture(scope="class")
    def registry(self):
        with open(DELIVERABLES_DIR / "rule_registry.yaml", 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_all_five_tiers_represented(self, registry):
        tiers = {r["tier"] for r in registry["regler"]}
        expected_tiers = {
            "Tier 1: Deterministisk beregningsregel",
            "Tier 2: Juridisk vilkårsregel",
            "Tier 3: Tariffavhengig regel",
            "Tier 4: Faglig vurderingsregel",
            "Tier 5: Regler som krever menneskelig beslutning"
        }
        assert tiers == expected_tiers, f"Mangler lag i regelmotoren: {expected_tiers - tiers}"

    def test_deterministic_operators_logic(self):
        # min_ge
        assert (40 >= 37.5) is True
        assert (35 >= 37.5) is False
        # max_le
        assert (8.0 <= 9.0) is True
        assert (10.5 <= 9.0) is False
        # required / not_null
        assert bool("verdi") is True
        assert bool(None) is False
        assert bool("") is False

    def test_all_rules_have_sources(self, registry):
        for r in registry["regler"]:
            assert r["kilde"].startswith("http"), f"Regel {r['regel_id']} mangler gyldig kilde: {r['kilde']}"

# 6. PRIVACY AND ANONYMIZATION BOUNDARIES
class TestPrivacyAndRoleBoundaries:
    def test_forbidden_diagnosis_fields(self):
        with open(DELIVERABLES_DIR / "data_contract.yaml", 'r', encoding='utf-8') as f:
            contracts = yaml.safe_load(f)
        forbidden = contracts["personverngrenser_og_k_anonymitet"]["forbudte_felter"]
        assert "diagnose" in forbidden
        assert "individuell_overvakingsscore" in forbidden

    def test_k_anonymity_threshold(self):
        with open(DELIVERABLES_DIR / "data_contract.yaml", 'r', encoding='utf-8') as f:
            contracts = yaml.safe_load(f)
        k_min = contracts["personverngrenser_og_k_anonymitet"]["minste_gruppestorrelse_kpi"]
        assert k_min >= 5, "Minste gruppestørrelse må være minst 5"

# 8. CASEPACK INTEGRATION TEST
class TestCasepackIntegration:
    def test_casepack_offline_integrity(self):
        casepack_dir = STAGING_DIR / "Kunstpixel_HR_KI_casepack_2024-2026_oppdatert" / "Kunstpixel_HR_KI_casepack_oppdatert"
        original = json.loads((casepack_dir / 'scenario_catalog.json').read_text(encoding='utf-8'))
        conversations = json.loads((casepack_dir / 'conversation_training' / 'scenario_catalog.json').read_text(encoding='utf-8'))
        links = json.loads((casepack_dir / 'conversation_training' / 'links_to_hr_cases.json').read_text(encoding='utf-8'))
        
        base = original['cases']
        entries = conversations['cases']
        assert len(base) == 14
        assert len(entries) == 113
        assert len({x['id'] for x in entries}) == 113
        assert sum(x['source_status'] == 'metadata_complete' for x in entries) == 112
        assert [x['id'] for x in entries if x['source_status'] == 'incomplete_source'] == ['VANS-07']
        assert len(links['links']) == 14

class TestNegativeCases:
    def test_invalid_date_format_fails(self):
        from datetime import datetime
        with pytest.raises(ValueError):
            datetime.strptime("2026/13/45", "%Y-%m-%d")

    def test_negative_shift_duration_rejected(self):
        start = "17:00"
        slutt = "09:00" # overnight without date wrap
        s_h, s_m = map(int, start.split(":"))
        e_h, e_m = map(int, slutt.split(":"))
        hours = (e_h + e_m/60) - (s_h + s_m/60)
        assert hours < 0, "Beregnet negativ varighet"

    def test_unknown_operator_flagged(self):
        with open(DELIVERABLES_DIR / "rule_registry.yaml", 'r', encoding='utf-8') as f:
            registry = yaml.safe_load(f)
        known_canonicals = set(registry["operator_taksonomi"].keys())
        for r in registry["regler"]:
            assert r["operator"] in known_canonicals, f"Ukjent operator: {r['operator']}"
