#!/usr/bin/env python3
"""Compute a stable SHA-256 for one source file or directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_directory(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        if ".git" in child.parts:
            continue
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hash_file(child).encode("ascii"))
        digest.update(b"\0")
        count += 1
    return digest.hexdigest(), count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.exists():
        parser.error(f"source does not exist: {source}")
    if source.is_file():
        digest, count, kind = hash_file(source), 1, "file"
    elif source.is_dir():
        digest, count, kind = *hash_directory(source), "directory"
    else:
        parser.error(f"unsupported source type: {source}")
    print(
        json.dumps(
            {
                "algorithm": "sha256",
                "digest": digest,
                "file_count": count,
                "kind": kind,
                "source": str(source),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
