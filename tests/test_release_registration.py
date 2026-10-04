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
