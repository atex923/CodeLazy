from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APP_NAME = "程式創作室"
APP_VERSION = "V0.1.4"
DATA_FILE_NAME = "CodeLazy_data.json"
SYNC_FILE_NAME = "CodeLazy_sync.txt"
SYNC_FOLDER = Path(r"Y:\我的雲端硬碟\12.Codex")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def app_folder() -> Path:
    """Return a writable folder beside the program/executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


try:
    from PySide6.QtCore import QDate, QEvent, QPoint, QRect, Qt, Signal
    from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
    from PySide6.QtWidgets import (
        QApplication,
        QCalendarWidget,
        QComboBox,
        QDateEdit,
        QFileDialog,
        QFrame,
        QGraphicsDropShadowEffect,
        QGridLayout,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSizeGrip,
        QSizePolicy,
        QSpacerItem,
        QStackedWidget,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    # .pyw has no console, so show an actionable graphical message.
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            APP_NAME,
            "尚未安裝 PySide6。\n\n請開啟命令提示字元執行：\n"
            "python -m pip install PySide6",
        )
        root.destroy()
    except Exception:
        pass
    raise SystemExit(1)


STYLE_SHEET = """
QWidget {
    color: #23302b;
    font-family: "Microsoft JhengHei UI", "PingFang TC", sans-serif;
    font-size: 13px;
}
#glassWindow {
    background-color: rgba(241, 246, 242, 236);
    border: 1px solid rgba(255, 255, 255, 210);
    border-radius: 18px;
}
#titleBar {
    background-color: rgba(255, 255, 255, 74);
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
    border-bottom: 1px solid rgba(96, 119, 108, 38);
}
#appTitle { font-size: 15px; font-weight: 700; color: #34463e; }
#versionText { color: #7b8b83; font-size: 11px; }
#sidebar {
    background-color: rgba(224, 234, 228, 158);
    border: 1px solid rgba(255,255,255,160);
    border-radius: 14px;
}
#editorCard {
    background-color: rgba(255, 255, 255, 166);
    border: 1px solid rgba(255, 255, 255, 220);
    border-radius: 14px;
}
QLineEdit, QDateEdit, QComboBox, QTextEdit {
    background-color: rgba(255,255,255,205);
    border: 1px solid rgba(89, 116, 103, 55);
    border-radius: 8px;
    padding: 7px 9px;
    selection-background-color: #7fa693;
}
QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #719884;
}
QLineEdit:disabled, QDateEdit:disabled, QComboBox:disabled, QTextEdit:disabled {
    color: #77817c;
    background-color: rgba(231,235,232,150);
}
QPushButton {
    background-color: rgba(255,255,255,178);
    border: 1px solid rgba(75, 103, 90, 50);
    border-radius: 9px;
    padding: 7px 13px;
}
QPushButton:hover { background-color: rgba(255,255,255,235); border-color: #84a393; }
QPushButton:pressed { background-color: rgba(205,220,211,220); }
QPushButton#primaryButton {
    background-color: #678c79;
    color: white;
    border: none;
    font-weight: 700;
    padding: 9px 18px;
}
QPushButton#primaryButton:hover { background-color: #567b68; }
QPushButton#dangerButton { color: #b94a48; }
QPushButton#trafficButton { border: none; padding: 0px; border-radius: 7px; min-width: 14px; max-width: 14px; min-height: 14px; max-height: 14px; }
QPushButton#stepButton { padding: 0px; min-width: 21px; max-width: 21px; min-height: 16px; max-height: 16px; border-radius: 5px; font-size: 11px; font-weight: 700; }
QLabel#fieldLabel { color: #586a61; font-size: 12px; font-weight: 600; }
QLabel#sectionTitle { font-size: 17px; font-weight: 800; color: #30443a; }
QLabel#versionNumber {
    background-color: rgba(255,255,255,210);
    border: 1px solid rgba(89,116,103,55);
    border-radius: 8px;
    min-width: 38px;
    padding: 8px 5px;
    font-size: 16px;
    font-weight: 800;
}
QTableWidget {
    background-color: transparent;
    alternate-background-color: rgba(255,255,255,86);
    border: none;
    gridline-color: rgba(89,116,103,25);
    selection-background-color: rgba(112,151,131,145);
    selection-color: #17251e;
}
QHeaderView::section {
    background-color: rgba(255,255,255,130);
    border: none;
    border-bottom: 1px solid rgba(89,116,103,50);
    padding: 7px;
    color: #596c62;
    font-weight: 700;
}
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: rgba(91,118,105,90); border-radius: 5px; min-height: 25px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QCalendarWidget QWidget { background-color: #f8fbf9; }
QCalendarWidget QToolButton { color: #263a30; background: transparent; border: none; }
"""


class DataStore:
    def __init__(self, local_path: Path):
        self.local_path = local_path
        self.data: dict[str, Any] = self.empty_data()

    @staticmethod
    def empty_data() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "app_version": APP_VERSION,
            "updated_at": utc_now(),
            "records": [],
            "deleted": {},
        }

    def load(self) -> tuple[bool, str]:
        if not self.local_path.exists():
            return True, ""
        try:
            raw = json.loads(self.local_path.read_text(encoding="utf-8-sig"))
            self.data = self.normalize(raw)
            self.reindex_items()
            return True, ""
        except Exception as exc:
            backup = self.local_path.with_suffix(
                f".broken_{datetime.now():%Y%m%d_%H%M%S}.json"
            )
            try:
                self.local_path.replace(backup)
                detail = f"原檔已改名備份為：\n{backup.name}"
            except Exception:
                detail = "無法自動備份損壞的資料檔。"
            self.data = self.empty_data()
            return False, f"本機資料檔讀取失敗：{exc}\n\n{detail}"

    @staticmethod
    def normalize(raw: Any) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError("資料格式不是物件")
        output = DataStore.empty_data()
        records = raw.get("records", [])
        deleted = raw.get("deleted", {})
        if not isinstance(records, list) or not isinstance(deleted, dict):
            raise ValueError("records 或 deleted 格式錯誤")
        cleaned = []
        for item in records:
            if not isinstance(item, dict):
                continue
            record = dict(item)
            record.pop("title", None)
            record.setdefault("id", str(uuid.uuid4()))
            record.setdefault("updated_at", raw.get("updated_at", utc_now()))
            record.setdefault("version", [0, 1, 0])
            if not isinstance(record["version"], list) or len(record["version"]) != 3:
                record["version"] = [0, 1, 0]
            cleaned.append(record)
        output.update(
            schema_version=1,
            app_version=APP_VERSION,
            updated_at=str(raw.get("updated_at", utc_now())),
            records=cleaned,
            deleted={str(k): str(v) for k, v in deleted.items()},
        )
        return output

    def save_local(self) -> None:
        self.data["app_version"] = APP_VERSION
        self.data["updated_at"] = utc_now()
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.local_path.with_suffix(".tmp")
        text = json.dumps(self.data, ensure_ascii=False, indent=2)
        temp_path.write_text(text, encoding="utf-8")
        os.replace(temp_path, self.local_path)

    def export_sync(self, folder: Path = SYNC_FOLDER) -> tuple[bool, str]:
        if os.name != "nt" and folder == SYNC_FOLDER:
            return False, "指定的 Y: 雲端硬碟路徑僅能在 Windows 使用。"
        try:
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / SYNC_FILE_NAME
            temp = target.with_suffix(".tmp")
            temp.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temp, target)
            return True, str(target)
        except Exception as exc:
            return False, str(exc)

    def record_by_id(self, record_id: str) -> dict[str, Any] | None:
        return next((r for r in self.data["records"] if r.get("id") == record_id), None)

    @staticmethod
    def _item_sort_key(record: dict[str, Any]) -> tuple[int, str, str]:
        try:
            item_number = int(str(record.get("item", "")).strip())
        except (TypeError, ValueError):
            item_number = 10**9
        return item_number, str(record.get("created_at", "")), str(record.get("id", ""))

    def reindex_items(self) -> None:
        """Keep item numbers automatic, unique, and continuous from 1."""
        ordered = sorted(self.data["records"], key=self._item_sort_key)
        for index, record in enumerate(ordered, start=1):
            record["item"] = str(index)
        self.data["records"] = ordered

    def next_item(self) -> str:
        return str(len(self.data["records"]) + 1)

    def upsert(self, record: dict[str, Any]) -> None:
        current = self.record_by_id(record["id"])
        if current is None:
            self.data["records"].append(record)
        else:
            current.clear()
            current.update(record)
        self.data["deleted"].pop(record["id"], None)
        self.reindex_items()

    def delete(self, record_id: str) -> None:
        self.data["records"] = [
            r for r in self.data["records"] if r.get("id") != record_id
        ]
        self.data["deleted"][record_id] = utc_now()
        self.reindex_items()

    @staticmethod
    def _newer(left: str, right: str) -> bool:
        return str(left) > str(right)

    def merge(self, incoming_raw: Any) -> tuple[int, int, int]:
        incoming = self.normalize(incoming_raw)
        local_records = {r["id"]: r for r in self.data["records"]}
        remote_records = {r["id"]: r for r in incoming["records"]}
        local_deleted = dict(self.data["deleted"])
        remote_deleted = dict(incoming["deleted"])
        changed, added, removed = 0, 0, 0

        all_ids = set(local_records) | set(remote_records) | set(local_deleted) | set(remote_deleted)
        merged_records: dict[str, dict[str, Any]] = {}
        merged_deleted: dict[str, str] = {}

        for record_id in all_ids:
            candidates: list[tuple[str, str, Any]] = []
            if record_id in local_records:
                candidates.append((local_records[record_id].get("updated_at", ""), "record", local_records[record_id]))
            if record_id in remote_records:
                candidates.append((remote_records[record_id].get("updated_at", ""), "record", remote_records[record_id]))
            if record_id in local_deleted:
                candidates.append((local_deleted[record_id], "deleted", local_deleted[record_id]))
            if record_id in remote_deleted:
                candidates.append((remote_deleted[record_id], "deleted", remote_deleted[record_id]))
            newest = max(candidates, key=lambda item: item[0])
            if newest[1] == "deleted":
                merged_deleted[record_id] = newest[0]
                if record_id in local_records:
                    removed += 1
            else:
                merged_records[record_id] = dict(newest[2])
                if record_id not in local_records:
                    added += 1
                elif newest[2] is remote_records.get(record_id) and newest[2] != local_records[record_id]:
                    changed += 1

        self.data["records"] = list(merged_records.values())
        self.data["deleted"] = merged_deleted
        self.reindex_items()
        self.data["updated_at"] = utc_now()
        return added, changed, removed


class TodayCalendarDateEdit(QDateEdit):
    """Calendar always opens on today, while preserving the stored date."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy/MM/dd")
        self.setDate(QDate.currentDate())
        self.calendarWidget().installEventFilter(self)

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if watched is self.calendarWidget() and event.type() == QEvent.Type.Show:
            today = QDate.currentDate()
            self.calendarWidget().setCurrentPage(today.year(), today.month())
        return super().eventFilter(watched, event)


class VersionSegment(QWidget):
    changed = Signal()

    def __init__(self, value: int = 0, parent: QWidget | None = None):
        super().__init__(parent)
        self._value = max(0, min(99, int(value)))
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self.number = QLabel(str(self._value))
        self.number.setObjectName("versionNumber")
        self.number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls = QVBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(2)
        self.plus = QPushButton("+")
        self.minus = QPushButton("−")
        for button in (self.plus, self.minus):
            button.setObjectName("stepButton")
        self.plus.clicked.connect(lambda: self.adjust(1))
        self.minus.clicked.connect(lambda: self.adjust(-1))
        controls.addWidget(self.plus)
        controls.addWidget(self.minus)
        row.addWidget(self.number)
        row.addLayout(controls)

    def adjust(self, amount: int) -> None:
        new_value = max(0, min(99, self._value + amount))
        if new_value != self._value:
            self._value = new_value
            self.number.setText(str(self._value))
            self.changed.emit()

    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        self._value = max(0, min(99, int(value)))
        self.number.setText(str(self._value))

    def setEditorEnabled(self, enabled: bool) -> None:
        self.plus.setEnabled(enabled)
        self.minus.setEnabled(enabled)


class VersionEditor(QWidget):
    changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(7)
        prefix = QLabel("V")
        prefix.setStyleSheet("font-size: 18px; font-weight: 800; color: #3f564a;")
        row.addWidget(prefix)
        self.segments = [VersionSegment(0), VersionSegment(1), VersionSegment(0)]
        for index, segment in enumerate(self.segments):
            segment.changed.connect(self.changed)
            row.addWidget(segment)
            if index < 2:
                dot = QLabel(".")
                dot.setStyleSheet("font-size: 20px; font-weight: 800;")
                row.addWidget(dot)
        row.addStretch(1)

    def value(self) -> list[int]:
        return [part.value() for part in self.segments]

    def setValue(self, value: list[int]) -> None:
        safe = value if isinstance(value, list) and len(value) == 3 else [0, 1, 0]
        for segment, number in zip(self.segments, safe):
            segment.setValue(number)

    def setEditorEnabled(self, enabled: bool) -> None:
        for segment in self.segments:
            segment.setEditorEnabled(enabled)

    def text(self) -> str:
        return "V" + ".".join(str(number) for number in self.value())


class TitleBar(QFrame):
    def __init__(self, window: "MainWindow"):
        super().__init__(window)
        self.window = window
        self.drag_offset: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(54)
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 0, 18, 0)
        row.setSpacing(9)

        close_button = self.traffic("#ff5f57", "關閉")
        min_button = self.traffic("#ffbd2e", "最小化")
        max_button = self.traffic("#28c840", "最大化／還原")
        close_button.clicked.connect(window.close)
        min_button.clicked.connect(window.showMinimized)
        max_button.clicked.connect(window.toggle_maximized)
        row.addWidget(close_button)
        row.addWidget(min_button)
        row.addWidget(max_button)
        row.addStretch(1)
        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        row.addWidget(title)
        version = QLabel(APP_VERSION)
        version.setObjectName("versionText")
        row.addWidget(version)
        row.addStretch(1)
        balance = QWidget()
        balance.setFixedWidth(60)
        row.addWidget(balance)

    @staticmethod
    def traffic(color: str, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("trafficButton")
        button.setStyleSheet(f"QPushButton#trafficButton {{ background-color: {color}; }}")
        button.setToolTip(tooltip)
        return button

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if self.window.isMaximized():
                self.window.showNormal()
                self.drag_offset = QPoint(self.window.width() // 2, 25)
            self.window.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window.toggle_maximized()


class GlassBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)
        painter.fillPath(path, QColor(239, 245, 241, 238))
        painter.setPen(QPen(QColor(255, 255, 255, 210), 1))
        painter.drawPath(path)
        super().paintEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.store = DataStore(app_folder() / DATA_FILE_NAME)
        self.current_id: str | None = None
        self.full_edit = False
        self.dirty = False
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(1020, 660)
        self.resize(1240, 760)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        root = GlassBackground()
        root.setObjectName("glassWindow")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(TitleBar(self))

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 14, 18, 18)
        content_layout.setSpacing(12)
        content_layout.addLayout(self.build_toolbar())
        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(self.build_sidebar(), 5)
        body.addWidget(self.build_editor(), 4)
        content_layout.addLayout(body, 1)
        outer.addWidget(content, 1)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 7)
        shadow.setColor(QColor(35, 55, 45, 95))
        root.setGraphicsEffect(shadow)

        ok, message = self.store.load()
        self.refresh_table()
        self.new_record()
        if not ok:
            QMessageBox.warning(self, "資料檔修復", message)

    def build_toolbar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self.new_button = QPushButton("＋ 新增")
        self.delete_button = QPushButton("刪除")
        self.delete_button.setObjectName("dangerButton")
        self.sync_button = QPushButton("同步")
        self.new_button.clicked.connect(self.new_record)
        self.delete_button.clicked.connect(self.delete_record)
        self.sync_button.clicked.connect(self.sync_from_file)
        row.addWidget(self.new_button)
        row.addWidget(self.delete_button)
        row.addWidget(self.sync_button)
        row.addStretch(1)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜尋項次、名稱、檔名或備註…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setFixedWidth(320)
        self.search_edit.textChanged.connect(self.refresh_table)
        row.addWidget(self.search_edit)
        return row

    def build_sidebar(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("sidebar")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(8)
        heading = QLabel("開發項目")
        heading.setObjectName("sectionTitle")
        self.count_label = QLabel("0 項")
        self.count_label.setObjectName("versionText")
        head = QHBoxLayout()
        head.addWidget(heading)
        head.addStretch(1)
        head.addWidget(self.count_label)
        layout.addLayout(head)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["項次", "名稱", "檔名", "最新版號", "修改方式", "更新時間"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.table_selection_changed)
        layout.addWidget(self.table, 1)
        return panel

    def build_editor(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("editorCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)
        title_row = QHBoxLayout()
        self.form_title = QLabel("新增程式")
        self.form_title.setObjectName("sectionTitle")
        self.edit_button = QPushButton("修改")
        self.edit_button.clicked.connect(self.toggle_full_edit)
        title_row.addWidget(self.form_title)
        title_row.addStretch(1)
        title_row.addWidget(self.edit_button)
        layout.addLayout(title_row)

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        self.item_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.file_edit = QLineEdit()
        self.initial_name_edit = QLineEdit()
        self.created_edit = TodayCalendarDateEdit()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["ChatGPT網頁", "Codex"])
        self.version_edit = VersionEditor()
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("說明程式用途、主要功能或操作方式…")
        self.description_edit.setFixedHeight(58)
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("記錄待辦、修改內容或開發注意事項…")
        self.note_edit.setMinimumHeight(120)
        self.note_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.add_field(form, 0, 0, "項次（自動）", self.item_edit)
        self.add_field(form, 0, 2, "名稱", self.name_edit)
        self.add_field(form, 1, 0, "檔名", self.file_edit)
        self.add_field(form, 1, 2, "初開發名稱", self.initial_name_edit)
        self.add_field(form, 2, 0, "建立時間", self.created_edit)
        self.add_field(form, 2, 2, "最後修改方式", self.method_combo)
        self.add_field(form, 3, 0, "最新版號", self.version_edit, span=3)
        self.add_field(form, 4, 0, "說明", self.description_edit, span=3)
        self.add_field(form, 5, 0, "備註", self.note_edit, span=3)
        form.setRowStretch(5, 1)
        layout.addLayout(form, 1)

        self.lock_hint = QLabel("項次由系統自動建立；儲存後基本資料與說明會鎖定，備註可直接更新；按「修改」可解鎖基本資料。")
        self.lock_hint.setWordWrap(True)
        self.lock_hint.setObjectName("versionText")
        layout.addWidget(self.lock_hint)
        footer = QHBoxLayout()
        self.status_label = QLabel("準備就緒")
        self.status_label.setObjectName("versionText")
        self.save_button = QPushButton("儲存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_record)
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.save_button)
        size_grip = QSizeGrip(panel)
        size_grip.setToolTip("拖曳調整視窗大小")
        footer.addWidget(size_grip, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(footer)

        for widget in (
            self.item_edit,
            self.name_edit,
            self.file_edit,
            self.initial_name_edit,
            self.created_edit,
            self.method_combo,
            self.description_edit,
            self.note_edit,
        ):
            if isinstance(widget, QTextEdit):
                widget.textChanged.connect(self.mark_dirty)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.mark_dirty)
            elif isinstance(widget, QDateEdit):
                widget.dateChanged.connect(self.mark_dirty)
            else:
                widget.textChanged.connect(self.mark_dirty)
        self.version_edit.changed.connect(self.mark_dirty)
        return panel

    @staticmethod
    def add_field(
        grid: QGridLayout,
        row: int,
        column: int,
        text: str,
        widget: QWidget,
        span: int = 1,
    ) -> None:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        grid.addWidget(label, row, column)
        grid.addWidget(widget, row, column + 1, 1, span)

    def mark_dirty(self, *_args) -> None:
        self.dirty = True
        self.status_label.setText("尚未儲存")

    def confirm_discard(self) -> bool:
        if not self.dirty:
            return True
        answer = QMessageBox.question(
            self,
            "尚未儲存",
            "目前有尚未儲存的內容，要放棄這些變更嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def set_base_fields_enabled(self, enabled: bool) -> None:
        for widget in (
            self.name_edit,
            self.file_edit,
            self.initial_name_edit,
            self.created_edit,
            self.description_edit,
        ):
            widget.setEnabled(enabled)
        self.item_edit.setEnabled(False)
        self.version_edit.setEditorEnabled(True)
        self.method_combo.setEnabled(True)
        self.note_edit.setEnabled(True)

    def clear_form(self) -> None:
        self.item_edit.setText(self.store.next_item())
        self.name_edit.clear()
        self.file_edit.clear()
        self.initial_name_edit.clear()
        self.created_edit.setDate(QDate.currentDate())
        self.version_edit.setValue([0, 1, 0])
        self.method_combo.setCurrentIndex(0)
        self.description_edit.clear()
        self.note_edit.clear()

    def new_record(self) -> None:
        if not self.confirm_discard():
            return
        self.current_id = None
        self.full_edit = True
        self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.blockSignals(False)
        self.clear_form()
        self.set_base_fields_enabled(True)
        self.form_title.setText("新增程式")
        self.edit_button.setVisible(False)
        self.status_label.setText("請輸入新程式資料")
        self.dirty = False
        self.name_edit.setFocus()

    def load_record(self, record_id: str) -> None:
        record = self.store.record_by_id(record_id)
        if record is None:
            return
        self.current_id = record_id
        self.full_edit = False
        self.item_edit.setText(str(record.get("item", "")))
        self.name_edit.setText(str(record.get("name", "")))
        self.file_edit.setText(str(record.get("filename", "")))
        self.initial_name_edit.setText(str(record.get("initial_name", "")))
        date = QDate.fromString(str(record.get("created_date", "")), "yyyy-MM-dd")
        self.created_edit.setDate(date if date.isValid() else QDate.currentDate())
        self.version_edit.setValue(record.get("version", [0, 1, 0]))
        method = str(record.get("last_method", "ChatGPT網頁"))
        self.method_combo.setCurrentIndex(max(0, self.method_combo.findText(method)))
        self.description_edit.setPlainText(str(record.get("description", "")))
        self.note_edit.setPlainText(str(record.get("notes", "")))
        self.set_base_fields_enabled(False)
        self.form_title.setText(record.get("name") or "程式資料")
        self.edit_button.setText("修改")
        self.edit_button.setVisible(True)
        self.status_label.setText("基本資料與說明已鎖定；最新版號、修改方式與備註可直接更新")
        self.dirty = False

    def table_selection_changed(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return
        record_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if record_id == self.current_id:
            return
        if not self.confirm_discard():
            self.select_row_by_id(self.current_id)
            return
        self.load_record(str(record_id))

    def select_row_by_id(self, record_id: str | None) -> None:
        if record_id is None:
            return
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == record_id:
                self.table.selectRow(row)
                break
        self.table.blockSignals(False)

    def toggle_full_edit(self) -> None:
        if self.current_id is None:
            return
        self.full_edit = not self.full_edit
        self.set_base_fields_enabled(self.full_edit)
        self.edit_button.setText("取消修改" if self.full_edit else "修改")
        if not self.full_edit:
            self.load_record(self.current_id)
        else:
            self.status_label.setText("基本資料已解鎖，可進行更正")

    def validate_form(self) -> str:
        if not self.name_edit.text().strip():
            return "請輸入名稱。"
        return ""

    def form_record(self) -> dict[str, Any]:
        old = self.store.record_by_id(self.current_id or "") or {}
        return {
            "id": self.current_id or str(uuid.uuid4()),
            "item": self.item_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "filename": self.file_edit.text().strip(),
            "initial_name": self.initial_name_edit.text().strip(),
            "created_date": self.created_edit.date().toString("yyyy-MM-dd"),
            "version": self.version_edit.value(),
            "last_method": self.method_combo.currentText(),
            "description": self.description_edit.toPlainText().strip(),
            "notes": self.note_edit.toPlainText().strip(),
            "created_at": old.get("created_at", utc_now()),
            "updated_at": utc_now(),
        }

    def save_record(self) -> None:
        error = self.validate_form()
        if error:
            QMessageBox.warning(self, "資料未完整", error)
            return
        record = self.form_record()
        self.current_id = record["id"]
        self.store.upsert(record)
        try:
            self.store.save_local()
        except Exception as exc:
            QMessageBox.critical(self, "儲存失敗", f"無法儲存本機資料：\n{exc}")
            return
        sync_ok, sync_detail = self.store.export_sync()
        self.refresh_table()
        self.select_row_by_id(self.current_id)
        self.load_record(self.current_id)
        if sync_ok:
            self.status_label.setText(f"已儲存並同步輸出：{SYNC_FILE_NAME}")
        else:
            self.status_label.setText("本機已儲存；雲端同步檔輸出失敗")
            QMessageBox.warning(
                self,
                "雲端同步未完成",
                "資料已安全儲存在本機，但無法另存同步文字檔。\n\n"
                f"目標：{SYNC_FOLDER / SYNC_FILE_NAME}\n"
                f"原因：{sync_detail}",
            )

    def delete_record(self) -> None:
        if self.current_id is None:
            QMessageBox.information(self, "刪除", "請先在左側選取要刪除的程式。")
            return
        record = self.store.record_by_id(self.current_id)
        if record is None:
            return
        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除「{record.get('name', '')}」嗎？\n刪除狀態也會寫入同步檔。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.store.delete(self.current_id)
        try:
            self.store.save_local()
        except Exception as exc:
            QMessageBox.critical(self, "刪除失敗", str(exc))
            return
        sync_ok, detail = self.store.export_sync()
        self.dirty = False
        self.refresh_table()
        self.new_record()
        if not sync_ok:
            QMessageBox.warning(self, "雲端同步未完成", f"本機已刪除，但同步檔輸出失敗：\n{detail}")

    def default_sync_path(self) -> Path:
        return SYNC_FOLDER / SYNC_FILE_NAME

    def sync_from_file(self) -> None:
        if not self.confirm_discard():
            return
        default_path = self.default_sync_path()
        if default_path.exists():
            chosen = str(default_path)
        else:
            chosen, _ = QFileDialog.getOpenFileName(
                self,
                "讀入 CodeLazy 同步文字檔",
                str(app_folder()),
                "CodeLazy 同步檔 (*.txt *.json);;所有檔案 (*.*)",
            )
        if not chosen:
            return
        try:
            incoming = json.loads(Path(chosen).read_text(encoding="utf-8-sig"))
            added, changed, removed = self.store.merge(incoming)
            self.store.save_local()
            sync_ok, detail = self.store.export_sync()
        except Exception as exc:
            QMessageBox.critical(self, "同步失敗", f"無法讀入同步檔：\n{exc}")
            return
        self.dirty = False
        self.refresh_table()
        self.new_record()
        summary = f"同步完成\n\n新增：{added} 項\n更新：{changed} 項\n刪除：{removed} 項"
        if not sync_ok:
            summary += f"\n\n合併資料已存到本機，但無法回寫雲端同步檔：\n{detail}"
        QMessageBox.information(self, "同步", summary)

    def refresh_table(self, *_args) -> None:
        query = self.search_edit.text().strip().casefold() if hasattr(self, "search_edit") else ""
        records = sorted(
            self.store.data["records"],
            key=self.store._item_sort_key,
        )
        if query:
            fields = ("item", "name", "filename", "initial_name", "description", "notes")
            records = [
                record
                for record in records
                if any(query in str(record.get(field, "")).casefold() for field in fields)
            ]
        self.table.blockSignals(True)
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            version = record.get("version", [0, 1, 0])
            values = [
                record.get("item", ""),
                record.get("name", ""),
                record.get("filename", ""),
                "V" + ".".join(str(x) for x in version),
                record.get("last_method", ""),
                str(record.get("updated_at", "")).replace("T", " ")[:16],
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, record["id"])
                if column == 3:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.table.setItem(row, column, item)
        self.table.blockSignals(False)
        self.count_label.setText(f"{len(records)} 項")

    def toggle_maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        if self.confirm_discard():
            event.accept()
        else:
            event.ignore()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
