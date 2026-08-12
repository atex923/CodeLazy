import importlib.machinery
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "CodeLazy_V0.1.7.pyw"


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

        self.assertEqual(data["app_version"], "V0.1.7")
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

    def test_settings_remembers_last_sync_file_and_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / app.SETTINGS_FILE_NAME
            sync_path = Path(tmp) / "custom" / "sync.json"
            sync_path.parent.mkdir()

            settings = app.AppSettings(settings_path)
            settings.remember_sync_file(sync_path)

            loaded = app.AppSettings(settings_path)
            loaded.load()

            self.assertEqual(loaded.sync_file_path(), sync_path)
            self.assertEqual(loaded.dialog_folder(), sync_path.parent)

    def test_export_sync_file_writes_custom_file_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sync_path = Path(tmp) / "picked" / "CodeLazy_sync.json"
            store = app.DataStore(Path(tmp) / app.DATA_FILE_NAME)
            store.data["records"].append(
                {
                    "id": "custom",
                    "item": "1",
                    "name": "Custom",
                    "updated_at": "2026-08-12T00:00:00+00:00",
                }
            )

            ok, detail = store.export_sync_file(sync_path)

            self.assertTrue(ok, detail)
            self.assertEqual(Path(detail), sync_path)
            self.assertEqual(json.loads(sync_path.read_text(encoding="utf-8"))["records"][0]["id"], "custom")

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

    def test_move_record_reorders_items_and_updates_target(self):
        store = app.DataStore(Path("unused.json"))
        store.data["records"] = [
            {"id": "a", "item": "1", "name": "A", "updated_at": "2026-08-12T00:00:00+00:00"},
            {"id": "b", "item": "2", "name": "B", "updated_at": "2026-08-12T00:00:00+00:00"},
            {"id": "c", "item": "3", "name": "C", "updated_at": "2026-08-12T00:00:00+00:00"},
        ]

        moved = store.move_record("c", 0)

        self.assertTrue(moved)
        self.assertEqual([record["id"] for record in store.data["records"]], ["c", "a", "b"])
        self.assertEqual([record["item"] for record in store.data["records"]], ["1", "2", "3"])
        self.assertNotEqual(store.record_by_id("c")["updated_at"], "2026-08-12T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
