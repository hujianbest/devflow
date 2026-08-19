#!/usr/bin/env python3
"""Validate the domain-knowledge-library OKF profile without external packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BUSINESS_TYPES = {
    "Bounded Context",
    "Ubiquitous Term",
    "Business Capability",
    "Business Process",
    "Business Rule",
    "Domain Event",
    "Context Relationship",
}
VALID_STATUS = {"draft", "stable", "deprecated"}
VALID_VIEW = {"as-is", "to-be", "historical"}
RESERVED = {"index.md", "log.md"}


@dataclass
class Concept:
    path: Path
    frontmatter: str
    body: str

    def scalar(self, key: str) -> str | None:
        match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", self.frontmatter)
        if not match:
            return None
        value = match.group(1).strip().strip("\"'")
        return value or None


def parse_concept(path: Path) -> tuple[Concept | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"cannot read UTF-8 markdown: {exc}"
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter"
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, "unclosed YAML frontmatter"
    return Concept(path, text[4:end], text[end + 5 :]), None


def source_blocks(frontmatter: str) -> list[str]:
    match = re.search(
        r"(?m)^sources:[ \t]*\n(?P<body>(?:^[ \t]+[^\n]*(?:\n|$))*)",
        frontmatter,
    )
    if not match:
        return []
    body = match.group("body")
    starts = [item.start() for item in re.finditer(r"(?m)^  -\s+", body)]
    if not starts:
        return []
    starts.append(len(body))
    return [body[starts[index] : starts[index + 1]] for index in range(len(starts) - 1)]


def validate_concept(concept: Concept, root: Path) -> list[dict]:
    relative = concept.path.relative_to(root).as_posix()
    findings: list[dict] = []

    def error(code: str, message: str) -> None:
        findings.append({"level": "error", "code": code, "path": relative, "message": message})

    def warning(code: str, message: str) -> None:
        findings.append({"level": "warning", "code": code, "path": relative, "message": message})

    concept_type = concept.scalar("type")
    status = concept.scalar("status")
    view = concept.scalar("view")
    sensitivity = concept.scalar("sensitivity")
    if not concept_type:
        error("missing-type", "frontmatter requires a non-empty type")
    if not concept.scalar("title"):
        warning("missing-title", "title is recommended")
    if not concept.scalar("description"):
        warning("missing-description", "description is recommended")
    if not concept.scalar("generated"):
        # A nested generated mapping has an empty scalar in the lightweight parser.
        if not re.search(r"(?m)^generated:\s*(?:\{|\n)", concept.frontmatter):
            error("missing-generated", "generated metadata is required by this profile")
    if status not in VALID_STATUS:
        error("invalid-status", f"status must be one of {sorted(VALID_STATUS)}")
    if view is not None and view not in VALID_VIEW:
        error("invalid-view", f"view must be one of {sorted(VALID_VIEW)}")
    if sensitivity == "restricted":
        error("restricted-published", "restricted content cannot be published in the bundle")
    if status == "stable" and concept_type in BUSINESS_TYPES:
        if not re.search(r"(?m)^\s*-\s*\{?\s*by:\s*human:", concept.frontmatter) and not re.search(
            r"(?m)^verified:\s*\{[^}]*by:\s*human:", concept.frontmatter
        ):
            error("stable-business-unverified", "stable business concepts require a human verifier")

    ids: list[str] = []
    for block in source_blocks(concept.frontmatter):
        source_id = re.search(r"(?m)^  -\s+id:\s*(\S+)", block)
        resource = re.search(r"(?m)^\s+resource:\s*(\S.+?)\s*$", block)
        if source_id:
            ids.append(source_id.group(1).strip("\"'"))
        else:
            error("source-missing-id", "each source requires a stable id")
        if not resource:
            error("source-missing-resource", "each source requires a resource")
    if len(ids) != len(set(ids)):
        error("duplicate-source-id", "source ids must be unique inside a concept")

    footnote_uses = set(re.findall(r"\[\^([A-Za-z0-9_.-]+)\]", concept.body))
    footnote_defs = set(re.findall(r"(?m)^\[\^([A-Za-z0-9_.-]+)\]:", concept.body))
    undefined = footnote_uses - footnote_defs
    if undefined:
        error("undefined-footnote", f"undefined footnotes: {sorted(undefined)}")
    source_like = {item for item in footnote_uses if item in set(ids)}
    missing_source_defs = source_like - footnote_defs
    if missing_source_defs:
        error("source-footnote-missing", f"source footnotes lack definitions: {sorted(missing_source_defs)}")

    resource = concept.scalar("resource")
    if resource and resource in {relative, "/" + relative}:
        error("self-resource", "concept resource cannot point to itself")
    return findings


def validate(root: Path) -> dict:
    findings: list[dict] = []
    concepts = 0
    for path in sorted(root.rglob("*.md")):
        if path.name in RESERVED:
            continue
        concepts += 1
        concept, parse_error = parse_concept(path)
        if parse_error:
            findings.append(
                {
                    "level": "error",
                    "code": "invalid-concept",
                    "path": path.relative_to(root).as_posix(),
                    "message": parse_error,
                }
            )
            continue
        findings.extend(validate_concept(concept, root))
    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    return {
        "concepts": concepts,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
        "valid": errors == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("knowledge_root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.knowledge_root.resolve()
    if not root.is_dir():
        parser.error(f"knowledge root is not a directory: {root}")
    result = validate(root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for finding in result["findings"]:
            print(f"{finding['level'].upper()} {finding['path']} [{finding['code']}]: {finding['message']}")
        print(
            f"concepts={result['concepts']} errors={result['errors']} "
            f"warnings={result['warnings']} valid={str(result['valid']).lower()}"
        )
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
