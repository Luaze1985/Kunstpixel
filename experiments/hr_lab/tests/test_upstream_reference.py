"""Kun strukturell kontroll av det isolerte, innhentede kodeutvalget."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UpstreamReferenceTests(unittest.TestCase):
    def test_all_declared_files_exist(self):
        manifest = json.loads((ROOT / "SOURCE_LOCK.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "reference_only_do_not_import")
        self.assertEqual(len(manifest["files"]), 13)
        for item in manifest["files"]:
            p = (ROOT / item["local_path"]).resolve()
            self.assertTrue(p.is_relative_to((ROOT / "upstream").resolve()))
            self.assertTrue(p.is_file(), item["local_path"])
            self.assertGreater(p.stat().st_size, 100)
            self.assertIn("/blob/", item["upstream_url"])
            self.assertIn(manifest["repositories"][item["origin"]]["commit"], item["upstream_url"])

    def test_each_upstream_has_its_license(self):
        for relative in ("upstream/frappe/license.txt", "upstream/mint/LICENSE", "upstream/onyx/LICENSE"):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_no_museum_db_in_lab(self):
        self.assertFalse((ROOT / "museum.db").exists())
        self.assertFalse((ROOT / "hr_lab.sqlite").exists())

if __name__ == "__main__":
    unittest.main()
