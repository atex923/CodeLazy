---
name: codelazy-github-release
description: Update the user's CodeLazy 程式創作室 database when they say 更新程式創作室資料庫, or register project metadata after a user-authorized successful GitHub publication. Match filenames before the version suffix and preserve existing records.
---

# CodeLazy Studio Database Updates

## Explicit Command

The command 「更新程式創作室資料庫」 invokes this skill across projects. Update the current project's matching record in the selected database; if no current project can be identified, ask which project to update. This command authorizes the requested database update and its adjacent backup, not GitHub publication or release-folder synchronization. Editing the skill itself does not authorize a database mutation.

Read the project's authoritative filename, managed version, platform category and modification metadata. Match the filename before its version suffix using the rules below, irrespective of the display name. Preserve the original ID, display name, notes, description, ordering, classification and unrelated fields. Create and classify a record only when no matching record exists. Stop on ambiguous matches; never delete or merge duplicates automatically.

For an already verified successful publication, use scripts/register_release.py with the actual publication timestamp and commit. For a local-only project update, do not call that release helper: it sets publication fields. Instead use structured JSON editing with an adjacent backup and atomic replacement to update only the managed version, filename, known repository and modification metadata; retain existing publication fields. Never infer a publication time from the current time or an unrelated commit. If publication evidence is missing, leave publication fields unchanged and report that limitation.

Read back the target record and verify unrelated records and notes remain unchanged. Append a short correction entry to the project's Markdown maintenance log. Report a clickable absolute database path and the changed fields. When writing the mounted Drive file, distinguish successful local write from verified server synchronization.

## GitHub Publication

When the user requests 發佈, 發布, publication or pushing a project to GitHub, complete the authorized publication and verify the remote commit first. Then register that successful publication in CodeLazy. A failed or unverified push must not be recorded as successful.

Use scripts/register_release.py. Select a newly user-specified database first, then CODELAZY_DATABASE, then the user's explicitly selected database. Only fall back to the active program's database if none was explicitly selected. Do not select old delivery databases or create an empty database in place of a missing user database.

Obtain owner/repo from git remote get-url origin and the release version from the project's authoritative version metadata. Supply the actual successful publication time with a timezone. Classify native iOS projects as iOS, native macOS projects as macOS, Python programs as PY, and other projects as 其他. For mixed platforms use the actual target of this publication.

Example:

```sh
python3 scripts/register_release.py --database /absolute/path/CodeLazy_data.json --repo owner/repo --name Project --version V1.2.0 --category PY --filename Project_V1.2.0.py --published-at 2026-10-04T12:00:00+08:00 --commit REMOTE_COMMIT
```

Keep private database paths in the locally installed skill or CODELAZY_DATABASE, not in the public repository.

The helper matches filenames first using the name before the Vx.y.z version suffix, ignoring path and executable/source extension. CodeLazy, CodeLazy_V0.1.14.py and CodeLazy_V0.2.0.py identify the same project even when its display name differs. If no filename matches, fall back to repository, then an unbound exact display name. Ambiguous matches or filenames bound to another repository stop without writing. It preserves display names, notes and existing fields, backs up the database, records version and publication metadata, and writes atomically. Existing repository classifications are retained.

CodeLazy V0.2.0 or later monitors its active database every second and refreshes external changes automatically. It preserves unsaved edits and defers the display refresh until they are saved or discarded; saving merges the latest publication fields. After registration, read back the record and report the database path. If CodeLazy is open, allow its automatic refresh to display the new data. Older builds require saving and closing before registration; installing source does not upgrade an already-running process. Registration is part of publication authorization; it does not authorize cloud uploads of the user's database.
