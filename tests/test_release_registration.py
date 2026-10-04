import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "skills/codelazy-github-release/scripts/register_release.py"
spec = importlib.util.spec_from_file_location("registration", script)
registration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)


class RegistrationTests(unittest.TestCase):
    def test_filename_without_version_updates_original_named_record(self):
        for filename in ("CodeLazy", "CodeLazy_V0.1.14.py", "CodeLazy_V0.1.14.pyw"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "data.json"
                path.write_text(json.dumps({"records": [{"id": "original", "name": "Studio",
                    "filename": filename, "notes": "Keep", "category": "PY"}], "deleted": {}}))
                registration.register(path, "atex923/CodeLazy", "CodeLazy", "V0.2.0", "PY",
                                      filename="CodeLazy_V0.2.0.py")
                records = json.loads(path.read_text())["records"]
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["id"], "original")
                self.assertEqual(records[0]["name"], "Studio")
                self.assertEqual(records[0]["notes"], "Keep")
                self.assertEqual(records[0]["version"], [0, 2, 0])

    def test_duplicate_filename_and_repository_conflict_do_not_write(self):
        for records in ([{"filename": "Demo_V0.1.0.py"}, {"filename": "Demo"}],
                        [{"filename": "Demo", "github_repo": "other/demo"}]):
            with self.subTest(records=records), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "data.json"
                original = json.dumps({"records": records, "deleted": {}})
                path.write_text(original)
                with self.assertRaises(ValueError):
                    registration.register(path, "user/demo", "Demo", "V0.2.0", "PY",
                                          filename="Demo_V0.2.0.py")
                self.assertEqual(path.read_text(), original)

    def test_register_update_preserves_notes_and_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "CodeLazy_data.json"
            path.write_text(json.dumps({"records": [], "deleted": {}}))
            result = registration.register(path, "https://github.com/user/demo.git", "Demo", "V0.2.0", "iOS")
            self.assertTrue(Path(result["backup"]).exists())
            data = json.loads(path.read_text())
            data["records"][0]["notes"] = "Keep notes"
            path.write_text(json.dumps(data))
            registration.register(path, "user/demo", "Demo", "V0.2.1", "PY")
            data = json.loads(path.read_text())
            self.assertEqual(len(data["records"]), 1)
            self.assertEqual(data["records"][0]["notes"], "Keep notes")
            self.assertEqual(data["records"][0]["category"], "iOS")
            self.assertEqual(data["records"][0]["version"], [0, 2, 1])

    def test_ambiguous_matches_do_not_change_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.json"
            original = json.dumps({"records": [{"name": "Demo"}, {"name": "Demo"}], "deleted": {}})
            path.write_text(original)
            with self.assertRaises(ValueError):
                registration.register(path, "user/demo", "Demo", "V0.2.0", "PY")
            self.assertEqual(path.read_text(), original)
