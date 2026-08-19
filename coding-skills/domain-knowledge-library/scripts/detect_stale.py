#!/usr/bin/env python3
"""Report stale and deprecated concepts in an OKF bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


def scalar(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", frontmatter)
    return match.group(1).strip().strip("\"'") if match else None


def frontmatter(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return text[4:end] if end >= 0 else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("knowledge_root", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.knowledge_root.resolve()
    if not root.is_dir():
        parser.error(f"knowledge root is not a directory: {root}")

    results: list[dict] = []
    invalid: list[dict] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        metadata = frontmatter(path)
        if metadata is None:
            continue
        status = scalar(metadata, "status") or "stable"
        stale_text = scalar(metadata, "stale_after")
        stale = False
        if stale_text:
            try:
                stale = args.as_of >= date.fromisoformat(stale_text)
            except ValueError:
                invalid.append({"path": path.relative_to(root).as_posix(), "stale_after": stale_text})
        if stale or status == "deprecated":
            results.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "status": status,
                    "stale_after": stale_text,
                    "stale": stale,
                }
            )

    output = {"as_of": args.as_of.isoformat(), "results": results, "invalid_dates": invalid}
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for item in results:
            flags = ", ".join(flag for flag in ("stale" if item["stale"] else "", item["status"]) if flag)
            print(f"{flags.upper()} {item['path']} stale_after={item['stale_after'] or '-'}")
        for item in invalid:
            print(f"INVALID {item['path']} stale_after={item['stale_after']}")
        print(f"flagged={len(results)} invalid_dates={len(invalid)}")
    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(main())
