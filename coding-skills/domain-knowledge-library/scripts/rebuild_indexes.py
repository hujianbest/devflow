#!/usr/bin/env python3
"""Generate or check deterministic OKF index.md files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def frontmatter_scalar(path: Path, key: str) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", text[4:end])
    if not match:
        return None
    return match.group(1).strip().strip("\"'") or None


def render_index(directory: Path, root: Path) -> str:
    title = "Knowledge Index" if directory == root else directory.name.replace("-", " ").title()
    lines: list[str] = []
    if directory == root:
        lines.extend(["---", 'okf_version: "0.2"', "---", ""])
    lines.extend([f"# {title}", ""])

    child_dirs = sorted(
        child for child in directory.iterdir() if child.is_dir() and any(child.rglob("*.md"))
    )
    concepts = sorted(
        child
        for child in directory.glob("*.md")
        if child.name not in {"index.md", "log.md"}
    )

    if child_dirs:
        lines.extend(["## Sections", ""])
        for child in child_dirs:
            description = f"{child.name.replace('-', ' ').title()} concepts."
            lines.append(f"- [{child.name}](./{child.name}/) - {description}")
        lines.append("")

    groups: dict[str, list[Path]] = {"stable": [], "draft": [], "deprecated": []}
    for concept in concepts:
        status = frontmatter_scalar(concept, "status") or "stable"
        groups.setdefault(status, []).append(concept)
    labels = {"stable": "Concepts", "draft": "Draft Concepts", "deprecated": "Deprecated Concepts"}
    for status in ("stable", "draft", "deprecated"):
        if not groups[status]:
            continue
        lines.extend([f"## {labels[status]}", ""])
        for concept in groups[status]:
            title_value = frontmatter_scalar(concept, "title") or concept.stem.replace("-", " ").title()
            description = frontmatter_scalar(concept, "description") or "No description."
            lines.append(f"- [{title_value}](./{concept.name}) - {description}")
        lines.append("")

    if not child_dirs and not concepts:
        lines.extend(["_No concepts published._", ""])
    return "\n".join(lines)


def index_directories(root: Path) -> list[Path]:
    directories = {root}
    for concept in root.rglob("*.md"):
        if ".kb" in concept.parts:
            continue
        current = concept.parent
        while current != root:
            directories.add(current)
            current = current.parent
    return sorted(directories, key=lambda path: (len(path.relative_to(root).parts), path.as_posix()), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("knowledge_root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.knowledge_root.resolve()
    if not root.is_dir():
        parser.error(f"knowledge root is not a directory: {root}")

    drift: list[str] = []
    updated: list[str] = []
    for directory in index_directories(root):
        expected = render_index(directory, root)
        target = directory / "index.md"
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == expected:
            continue
        relative = target.relative_to(root).as_posix()
        if args.check:
            drift.append(relative)
        else:
            target.write_text(expected, encoding="utf-8")
            updated.append(relative)

    if args.check:
        if drift:
            for path in drift:
                print(f"DRIFT {path}")
            return 1
        print("indexes are up to date")
        return 0
    for path in updated:
        print(f"UPDATED {path}")
    print(f"updated={len(updated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
