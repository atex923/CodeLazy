import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from test_codelazy_data import app


class DatabaseRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = app.QApplication.instance() or app.QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.folder_patch = patch.object(app, "app_folder", return_value=Path(self.folder.name))
        self.folder_patch.start()
        self.window = app.MainWindow()
        self.window.store.upsert({
            "id": "demo", "item": "1", "name": "Demo", "version": [0, 1, 0],
            "updated_at": "2026-10-03T00:00:00+00:00", "notes": "",
        })
        self.window.store.save_local()
        self.window.refresh_external_database()
        self.window.load_record("demo")

    def tearDown(self):
        self.window.dirty = False
        self.window.close()
        self.folder_patch.stop()
        self.folder.cleanup()

    def external_update(self):
        path = self.window.store.local_path
        data = json.loads(path.read_text())
        data["records"][0].update(
            version=[0, 2, 0], github_repo="user/demo",
            published_version="V0.2.0", published_at="2026-10-04T12:00:00+08:00",
            updated_at="2099-01-01T00:00:00+00:00",
        )
        path.write_text(json.dumps(data))

    def test_clean_form_refreshes_external_publication(self):
        self.external_update()
        self.window.refresh_external_database()
        self.assertEqual(self.window.github_edit.text(), "user/demo")
        self.assertEqual(self.window.version_edit.value(), [0, 2, 0])
        self.assertEqual(self.window.current_id, "demo")

    def test_edit_filename_save_and_reload_across_timezones(self):
        path = self.window.store.local_path
        data = json.loads(path.read_text())
        data["records"][0].update(filename="Old.py", updated_at="2026-10-04T14:00:00+08:00")
        path.write_text(json.dumps(data))
        self.window.refresh_external_database()
        self.window.load_record("demo")
        self.window.toggle_full_edit()
        self.window.file_edit.setText("Changed.py")
        with patch.object(app, "utc_now", return_value="2026-10-04T06:01:00.000001+00:00"), \
             patch.object(self.window, "export_current_sync", return_value=(True, "test")):
            self.window.save_record()
        self.assertEqual(self.window.file_edit.text(), "Changed.py")
        saved = json.loads(path.read_text())
        self.assertEqual(saved["records"][0]["filename"], "Changed.py")
        reopened = app.DataStore(path)
        reopened.load()
        self.assertEqual(reopened.record_by_id("demo")["filename"], "Changed.py")

    def test_dirty_form_preserves_note_and_latest_publication(self):
        self.window.note_edit.setPlainText("New note")
        self.external_update()
        self.window.refresh_external_database()
        self.assertEqual(self.window.note_edit.toPlainText(), "New note")
        self.window.store.merge(json.loads(self.window.store.local_path.read_text()))
        record = self.window.form_record()
        self.assertEqual(record["notes"], "New note")
        self.assertEqual(record["github_repo"], "user/demo")
        self.assertEqual(record["version"], [0, 2, 0])
        self.assertEqual(record["published_at"], "2026-10-04T12:00:00+08:00")
