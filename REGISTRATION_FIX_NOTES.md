# 2026-10-04 Publication registration correction

- Match the filename before its Vx.y.z suffix first, independent of display name.
- Ignore source/executable extension and path. Preserve existing record ID, name and notes.
- Stop without mutation on duplicate filename matches or conflicting repository binding.
- Use the user-selected CodeLazy_data_20260822_171517.json database in 12.Codex.
- Local skill correction only; no application version bump, GitHub publication or release-folder synchronization.
- Added tests for unversioned/versioned filenames, preserved metadata and conflicts.

## Explicit database update command

- Added 更新程式創作室資料庫 as a cross-project trigger in the installed skill description and instructions.
- The command updates database metadata only; it does not publish or synchronize release folders.
- Local-only updates preserve publication fields; actual publication timestamps require evidence.
- Preserve existing display names, notes and ordering; backup and read back every update.
- This skill update itself does not mutate the live database or bump the application version.

## Publication preparation

- User authorized GitHub publication of these skill corrections; application remains V0.2.0.
- Public skill omits private database paths; installed personal skill retains the selected database.
- README links the latest program, skill and maintenance notes. Release registration runs only after remote commit verification.
