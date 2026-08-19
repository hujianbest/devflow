#!/usr/bin/env python3
"""Extract a concept's provenance, trust, lifecycle, and footnote trace."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def scalar(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip("\"'") or None


def parse_sources(frontmatter: str) -> list[dict]:
    section = re.search(r"(?ms)^sources:[ \t]*\n(?P<body>(?:^[ \t]+.*\n?)*)", frontmatter)
    if not section:
        return []
    body = section.group("body")
    blocks = re.split(r"(?m)(?=^  -\s+)", body)
    sources: list[dict] = []
    for block in blocks:
        if not block.strip():
            continue
        item: dict[str, str] = {}
        first = re.search(r"(?m)^  -\s+([A-Za-z0-9_]+):\s*(.*?)\s*$", block)
        if first:
            item[first.group(1)] = first.group(2).strip().strip("\"'")
        for match in re.finditer(r"(?m)^\s{4}([A-Za-z0-9_]+):\s*(.*?)\s*$", block):
            item[match.group(1)] = match.group(2).strip().strip("\"'")
        sources.append(item)
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("concept", type=Path)
    args = parser.parse_args()
    path = args.concept.resolve()
    if not path.is_file():
        parser.error(f"concept is not a file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        parser.error("concept has invalid frontmatter")
    end = text.find("\n---\n", 4)
    metadata, body = text[4:end], text[end + 5 :]
    sources = parse_sources(metadata)
    source_ids = {item.get("id") for item in sources if item.get("id")}
    used_footnotes = sorted(set(re.findall(r"\[\^([A-Za-z0-9_.-]+)\]", body)))
    definitions = {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"(?m)^\[\^([A-Za-z0-9_.-]+)\]:\s*(.+)$", body)
    }
    human_verified = bool(
        re.search(r"(?m)^\s*-\s*\{?\s*by:\s*human:", metadata)
        or re.search(r"(?m)^verified:\s*\{[^}]*by:\s*human:", metadata)
    )
    output = {
        "concept": str(path),
        "type": scalar(metadata, "type"),
        "title": scalar(metadata, "title"),
        "status": scalar(metadata, "status") or "stable",
        "view": scalar(metadata, "view"),
        "owner": scalar(metadata, "owner"),
        "stale_after": scalar(metadata, "stale_after"),
        "human_verified": human_verified,
        "sources": sources,
        "footnotes": [
            {
                "id": footnote,
                "definition": definitions.get(footnote),
                "matches_source": footnote in source_ids,
            }
            for footnote in used_footnotes
        ],
        "untraceable_source_footnotes": sorted(
            footnote for footnote in used_footnotes if footnote not in source_ids
        ),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if output["untraceable_source_footnotes"] else 0


if __name__ == "__main__":
    sys.exit(main())
