---
name: codelazy-github-release
description: After a user-authorized successful GitHub publication, register or update the project version, category, repository and publication time in the user's CodeLazy database.
---

# CodeLazy GitHub Release Registration

When the user requests 發佈, 發布, publication or pushing a project to GitHub, complete the authorized publication and verify the remote commit first. Then register that successful publication in CodeLazy. A failed or unverified push must not be recorded as successful.

Use scripts/register_release.py. Select the database explicitly using CODELAZY_DATABASE or the active CodeLazy program's CodeLazy_data.json. The established local program lives at /Users/atex1/Documents/Codex/2026-08-12/atex923-guppypdflazytool-git-codex-text-link-4/work/CodeLazy_repo. Do not select old delivery databases or create an empty database in place of a missing user database.

Obtain owner/repo from git remote get-url origin and the release version from the project's authoritative version metadata. Supply the actual successful publication time with a timezone. Classify native iOS projects as iOS, native macOS projects as macOS, Python programs as PY, and other projects as 其他. For mixed platforms use the actual target of this publication.

Example:

```sh
python3 scripts/register_release.py --database /absolute/path/CodeLazy_data.json --repo owner/repo --name Project --version V1.2.0 --category PY --filename Project_V1.2.0.py --published-at 2026-10-04T12:00:00+08:00 --commit REMOTE_COMMIT
```

The helper matches the repository first, then an unbound exact project name or filename stem. Ambiguous matches stop without writing. It preserves notes and existing fields, backs up the database, records version and publication metadata, and writes atomically. Existing repository classifications are retained.

CodeLazy V0.2.0 or later monitors its active database every second and refreshes external changes automatically. It preserves unsaved edits and defers the display refresh until they are saved or discarded; saving merges the latest publication fields. After registration, read back the record and report the database path. If CodeLazy is open, allow its automatic refresh to display the new data. Older builds require saving and closing before registration; installing source does not upgrade an already-running process. Registration is part of publication authorization; it does not authorize cloud uploads of the user's database.
