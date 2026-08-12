import importlib.machinery
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "CodeLazy_V0.1.5.pyw"


def load_app():
    loader = importlib.machinery.SourceFileLoader("codelazy_app", str(APP_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


app = load_app()


class DataStoreTests(unittest.TestCase):
    def test_normalize_repairs_legacy_and_malformed_fields(self):
        data = app.DataStore.normalize(
            {
                "updated_at": "2026-08-12T00:00:00+00:00",
                "records": [
                    {
                        "id": "",
                        "title": "old field",
                        "name": "CodeLazy",
                        "version": ["2", 3, 150],
                    }
                ],
                "deleted": {"gone-id": None, "": "ignored"},
            }
        )

        self.assertEqual(data["app_version"], "V0.1.5")
        self.assertEqual(data["records"][0]["version"], [2, 3, 99])
        self.assertNotIn("title", data["records"][0])
        self.assertTrue(data["records"][0]["id"])
        self.assertIn("gone-id", data["deleted"])
        self.assertNotIn("", data["deleted"])

    def test_export_sync_uses_environment_folder_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get(app.SYNC_FOLDER_ENV)
            os.environ[app.SYNC_FOLDER_ENV] = tmp
            try:
                store = app.DataStore(Path(tmp) / app.DATA_FILE_NAME)
                store.data["records"].append(
                    {
                        "id": "one",
                        "item": "1",
                        "name": "Demo",
                        "updated_at": "2026-08-12T00:00:00+00:00",
                    }
                )

                ok, detail = store.export_sync()
                sync_path = Path(tmp) / app.SYNC_FILE_NAME

                self.assertTrue(ok, detail)
                self.assertEqual(Path(detail), sync_path)
                self.assertEqual(json.loads(sync_path.read_text(encoding="utf-8"))["records"][0]["id"], "one")
            finally:
                if previous is None:
                    os.environ.pop(app.SYNC_FOLDER_ENV, None)
                else:
                    os.environ[app.SYNC_FOLDER_ENV] = previous

    def test_merge_prefers_newer_remote_delete_and_reindexes_items(self):
        store = app.DataStore(Path("unused.json"))
        store.data["records"] = [
            {
                "id": "keep",
                "item": "9",
                "name": "Keep",
                "version": [0, 1, 0],
                "updated_at": "2026-08-12T00:00:00+00:00",
                "created_at": "2026-08-12T00:00:00+00:00",
            },
            {
                "id": "remove",
                "item": "1",
                "name": "Remove",
                "version": [0, 1, 0],
                "updated_at": "2026-08-12T00:00:00+00:00",
                "created_at": "2026-08-12T00:00:00+00:00",
            },
        ]

        added, changed, removed = store.merge(
            {
                "records": [
                    {
                        "id": "new",
                        "item": "4",
                        "name": "New",
                        "version": [0, 1, 0],
                        "updated_at": "2026-08-12T02:00:00+00:00",
                    }
                ],
                "deleted": {"remove": "2026-08-12T03:00:00+00:00"},
            }
        )

        self.assertEqual((added, changed, removed), (1, 0, 1))
        self.assertIsNone(store.record_by_id("remove"))
        self.assertEqual([record["item"] for record in store.data["records"]], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
