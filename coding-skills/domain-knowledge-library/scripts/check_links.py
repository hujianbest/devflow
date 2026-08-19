#!/usr/bin/env python3
"""Check internal Markdown links in an OKF bundle."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def without_fenced_code(text: str) -> str:
    lines: list[str] = []
    inside = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not inside:
                inside, fence = True, marker
            elif marker == fence:
                inside, fence = False, ""
            continue
        if not inside:
            lines.append(line)
    return "\n".join(lines)


def resolve_target(root: Path, source: Path, target: str) -> Path | None:
    target = target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "git+")):
        return None
    clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not clean:
        return None
    if clean.startswith("/"):
        resolved = root / clean.lstrip("/")
    else:
        resolved = source.parent / clean
    if resolved.is_dir():
        resolved = resolved / "index.md"
    return resolved.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("knowledge_root", type=Path)
    args = parser.parse_args()
    root = args.knowledge_root.resolve()
    if not root.is_dir():
        parser.error(f"knowledge root is not a directory: {root}")

    broken: list[tuple[str, str]] = []
    checked = 0
    for source in sorted(root.rglob("*.md")):
        try:
            text = without_fenced_code(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            broken.append((source.relative_to(root).as_posix(), f"unreadable: {exc}"))
            continue
        for match in LINK_RE.finditer(text):
            target_text = match.group(1)
            target = resolve_target(root, source, target_text)
            if target is None:
                continue
            checked += 1
            try:
                target.relative_to(root)
            except ValueError:
                broken.append((source.relative_to(root).as_posix(), f"escapes bundle: {target_text}"))
                continue
            if not target.exists():
                broken.append((source.relative_to(root).as_posix(), target_text))

    for source, target in broken:
        print(f"BROKEN {source} -> {target}")
    print(f"checked={checked} broken={len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
