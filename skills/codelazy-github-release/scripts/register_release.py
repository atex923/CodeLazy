from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def repository_name(value):
    value = re.sub(r"^(https?://github.com/|git@github.com:|ssh://git@github.com/)", "", value.strip())
    value = value.removesuffix(".git").strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Expected a GitHub owner/repo")
    return value


def filename_key(value):
    basename = str(value or "").replace("\\", "/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.(pyw?|swift|app|exe)$", "", basename, flags=re.IGNORECASE)
    return re.split(r"[_\- ]*[vV]\d+\.\d+\.\d+(?=$|[_\- .])", stem, maxsplit=1)[0].strip().casefold()


def register(database, repo, name, version, category, filename="", published_at=None, commit=""):
    database = Path(database)
    repo = repository_name(repo)
    parts = re.fullmatch(r"[vV]?(\d+)\.(\d+)\.(\d+)", version)
    if not parts:
        raise ValueError("Version must have three numeric segments")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    published_at = published_at or now
    timestamp = datetime.fromisoformat(published_at)
    if timestamp.tzinfo is None:
        raise ValueError("Publication time needs a timezone")
    if category not in ("iOS", "macOS", "PY", "其他"):
        raise ValueError("Invalid category")
    data = json.loads(database.read_text(encoding="utf-8-sig"))
    records = data["records"]
    if not isinstance(records, list) or not isinstance(data.get("deleted"), dict):
        raise ValueError("Invalid CodeLazy database")
    key = filename_key(filename)
    matches = [r for r in records if key and filename_key(r.get("filename")) == key]
    if any(r.get("github_repo") and repository_name(r["github_repo"]).casefold() != repo.casefold()
           for r in matches):
        raise ValueError("Filename belongs to another repository; database was not changed")
    if not matches:
        matches = [r for r in records if r.get("github_repo")
                   and repository_name(r["github_repo"]).casefold() == repo.casefold()]
    if not matches:
        matches = [r for r in records if not r.get("github_repo") and (
            str(r.get("name", "")).casefold() == name.casefold()
        )]
    if len(matches) > 1:
        raise ValueError("Ambiguous project match; database was not changed")
    record = matches[0] if matches else {
        "id": str(uuid.uuid4()), "item": str(len(records) + 1), "name": name,
        "initial_name": name, "created_at": now, "created_date": timestamp.date().isoformat(),
        "notes": "", "description": "", "category": category,
    }
    if not matches:
        records.append(record)
    if record.get("published_at") and len(record["published_at"]) > 10:
        previous = datetime.fromisoformat(record["published_at"])
        if previous.tzinfo and previous > timestamp:
            raise ValueError("Publication is older than the existing registration")
    record.update(github_repo=repo, version=[int(p) for p in parts.groups()],
                  published_version="V" + ".".join(parts.groups()), published_at=published_at,
                  updated_at=now, last_method="Codex", published_commit=commit)
    if filename:
        record["filename"] = filename
    data["updated_at"] = now
    backup = database.with_name(database.name + ".backup_" + uuid.uuid4().hex + ".json")
    shutil.copy2(database, backup)
    descriptor, temporary = tempfile.mkstemp(prefix=database.name + ".", dir=database.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, database)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"id": record["id"], "repo": repo, "version": record["published_version"],
            "database": str(database), "backup": str(backup)}


def main():
    parser = argparse.ArgumentParser()
    for option in ("database", "repo", "name", "version", "category"):
        parser.add_argument("--" + option, required=True)
    for option in ("filename", "published-at", "commit"):
        parser.add_argument("--" + option, default=None)
    args = vars(parser.parse_args())
    print(json.dumps(register(**args), ensure_ascii=False))


if __name__ == "__main__":
    main()
