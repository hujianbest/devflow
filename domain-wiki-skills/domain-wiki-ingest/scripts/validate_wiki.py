#!/usr/bin/env python3
"""Validate domain wiki mechanical contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RESERVED_NAMES = {
    "index.md",
    "log.md",
    "instructions.md",
    ".last-update.json",
}
RESERVED_DIRS = {".discovery", "raw"}
LOG_PREFIX = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] \S+ \| .+$")
STATUS_VALUES = {"interrupted", "complete"}
COMMAND_VALUES = {"init", "update", "ingest"}
FRONT_MATTER = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
MERMAID_FENCE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
END_NODE = re.compile(r"(?:^|[\s;])end(?:\[|\(|\{|>)", re.MULTILINE)
UNESCAPED_ANGLE = re.compile(r"(?:\[[^\]]*<(?![-\s.])[^ \]]*\]|\"[^\"]*<(?![-\s.])[^\"]*\")")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", required=True, help="Path to wiki/")
    return parser.parse_args()


def error(message: str, errors: list[str]) -> None:
    errors.append(message)


def load_front_matter(text: str) -> dict[str, object] | None:
    match = FRONT_MATTER.match(text)
    if match is None:
        return None
    data: dict[str, object] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def validate_metadata(wiki_root: Path, errors: list[str]) -> None:
    path = wiki_root / ".last-update.json"
    if not path.is_file():
        error("missing .last-update.json", errors)
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f".last-update.json is not valid JSON: {exc}", errors)
        return
    if not isinstance(payload, dict):
        error(".last-update.json must be an object", errors)
        return
    status = payload.get("status")
    command = payload.get("command")
    if status not in STATUS_VALUES:
        error(f"status must be one of {sorted(STATUS_VALUES)}", errors)
    if command not in COMMAND_VALUES:
        error(f"command must be one of {sorted(COMMAND_VALUES)}", errors)
    if "updatedAt" not in payload:
        error("missing updatedAt", errors)


def validate_log(wiki_root: Path, errors: list[str]) -> None:
    path = wiki_root / "log.md"
    if not path.is_file():
        error("missing log.md", errors)
        return
    headings = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("## [")
    ]
    if not headings:
        error("log.md has no operation entries", errors)
        return
    for heading in headings:
        if LOG_PREFIX.match(heading) is None:
            error(f"log entry must match '## [YYYY-MM-DD] op | title': {heading}", errors)


def iter_concept_pages(wiki_root: Path) -> list[Path]:
    pages: list[Path] = []
    for path in wiki_root.rglob("*.md"):
        relative = path.relative_to(wiki_root)
        if any(part in RESERVED_DIRS for part in relative.parts):
            continue
        if path.name.lower() in RESERVED_NAMES:
            continue
        pages.append(path)
    return pages


def validate_concepts(wiki_root: Path, errors: list[str]) -> None:
    for path in iter_concept_pages(wiki_root):
        text = path.read_text(encoding="utf-8")
        matter = load_front_matter(text)
        rel = path.relative_to(wiki_root).as_posix()
        if matter is None:
            error(f"{rel}: missing YAML front matter", errors)
            continue
        if not matter.get("type"):
            error(f"{rel}: front matter type is required", errors)


def validate_mermaid(wiki_root: Path, errors: list[str]) -> None:
    for path in wiki_root.rglob("*.md"):
        relative = path.relative_to(wiki_root)
        if any(part in RESERVED_DIRS for part in relative.parts):
            continue
        rel = relative.as_posix()
        text = path.read_text(encoding="utf-8")
        for index, block in enumerate(MERMAID_FENCE.findall(text), start=1):
            if not block.strip():
                error(f"{rel}: mermaid block {index} is empty", errors)
            if END_NODE.search(block):
                error(f"{rel}: mermaid block {index} uses reserved node id 'end'", errors)
            if UNESCAPED_ANGLE.search(block):
                error(f"{rel}: mermaid block {index} has unescaped <> in a label", errors)


def main() -> int:
    args = parse_args()
    wiki_root = Path(args.wiki_root).resolve()
    errors: list[str] = []
    if not wiki_root.is_dir():
        print(f"wiki root does not exist: {wiki_root}", file=sys.stderr)
        return 2
    validate_metadata(wiki_root, errors)
    validate_log(wiki_root, errors)
    validate_concepts(wiki_root, errors)
    validate_mermaid(wiki_root, errors)
    if errors:
        print("wiki validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1
    print("wiki validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
