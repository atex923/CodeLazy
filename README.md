# CodeLazy V0.1.11 / 程式創作室

CodeLazy 是給個人開發者使用的程式開發資料管理工具，用 PySide6 製作成 Windows 桌面程式，集中記錄每個小工具的名稱、檔名、初開發名稱、建立日期、最新版號、修改方式、說明與備註。

## 主要特色

- macOS 玻璃感無邊框介面，視窗標題置中，視窗控制鈕位於右側。
- 開發項目自動連號；刪除或同步後會重新整理項次。
- 左側清單可拖曳項目改變項次位置，移位後會重新編號並同步輸出。
- 版號以 `V0.1.9` 這類三段式格式管理，每段可用 `+ / -` 調整。
- 管理版號第一碼按 `+` 時，第二碼從 `1` 開始、第三碼歸 `0`；第二碼按 `+` 時，第三碼歸 `0`。
- 儲存後鎖定基本資料與說明，鎖定文字仍保持黑色方便閱讀，並保留最新版號、修改方式、備註可快速更新。
- 左側清單支援搜尋項次、名稱、檔名、初開發名稱、說明與備註。
- 本機資料以 UTF-8 JSON 儲存在程式旁的 `CodeLazy_data.json`。
- 另存 `CodeLazy_sync.txt` 作為跨電腦同步交換檔，內容為 JSON。
- 同步時依每筆 UUID 與 `updated_at` 合併，較新的資料與刪除狀態優先。
- 資料檔損壞時會自動改名備份，再建立新的空資料庫。
- 會記住最後一次選取的同步紀錄檔位置，並支援拖曳 `.txt` / `.json` 同步檔載入。
- `同步` 右側的 `+` 可自選其他同步紀錄檔；後續儲存會回寫至該檔案。
- `CODELAZY_SYNC_FOLDER` 環境變數可覆寫預設同步資料夾，方便不同磁碟代號或測試環境使用。

## 快速啟動

1. 安裝 Python 3.13。
2. 雙擊 `啟動_CodeLazy.bat`。
3. 若缺少 PySide6，批次檔會自動執行 `pip install -r requirements.txt`。

## 建立單一 EXE

雙擊 `Nuitka_單一EXE打包.bat`，成功後會產生：

```text
Nuitka_Output\CodeLazy_V0.1.11.exe
```

## 同步路徑

Windows 預設同步輸出：

```text
Y:\我的雲端硬碟\12.Codex\CodeLazy_sync.txt
```

若雲端硬碟代號或資料夾不同，可先設定：

```bat
set CODELAZY_SYNC_FOLDER=D:\GoogleDrive\我的雲端硬碟\12.Codex
```

## 倉庫規則

GitHub root 只保留目前最新版 V0.1.11 的程式與文件。舊版完整來源收在 `history/Vx.y.z/`，索引見 `history/README.md`。

使用者資料檔 `CodeLazy_data.json`、同步檔 `CodeLazy_sync.txt` 與本機設定檔 `CodeLazy_settings.json` 不納入公開倉庫。
