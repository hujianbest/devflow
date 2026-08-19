#!/usr/bin/env python3
"""Create a deterministic, read-only repository inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

LANGUAGES = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".java": "Java",
    ".js": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scala": "Scala",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

BUILD_FILES = {
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "go.mod",
    "makefile",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}

LOCK_FILES = {
    "cargo.lock",
    "composer.lock",
    "go.sum",
    "gradle.lockfile",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value or None


def classify(relative: str, name: str) -> set[str]:
    lower_path = relative.lower()
    lower_name = name.lower()
    categories: set[str] = set()
    if lower_name in BUILD_FILES:
        categories.add("build")
    if lower_name in LOCK_FILES:
        categories.add("lock")
    if "codeowners" == lower_name:
        categories.add("ownership")
    if any(part in lower_path for part in ("/test/", "/tests/", "/spec/", "/specs/")):
        categories.add("test")
    if any(token in lower_path for token in ("migration", "migrations", "schema")):
        categories.add("data")
    if lower_name.endswith((".proto", ".graphql", ".gql")):
        categories.add("contract")
    if "openapi" in lower_name or "swagger" in lower_name or "asyncapi" in lower_name:
        categories.add("contract")
    if lower_name.startswith("dockerfile") or lower_name in {
        "docker-compose.yml",
        "docker-compose.yaml",
    }:
        categories.add("deployment")
    if any(token in lower_path for token in ("/helm/", "/k8s/", "/kubernetes/", "/terraform/")):
        categories.add("deployment")
    if lower_name.endswith((".md", ".mdx", ".rst", ".adoc")):
        categories.add("document")
    if "adr" in lower_path or "/decisions/" in lower_path:
        categories.add("decision")
    if lower_name.endswith((".env", ".ini", ".properties", ".toml", ".yaml", ".yml")):
        categories.add("configuration")
    return categories


def inventory(repo: Path, excludes: set[str], hash_limit: int) -> dict:
    files: list[dict] = []
    language_counts: Counter[str] = Counter()
    categories: dict[str, list[str]] = {}
    errors: list[dict] = []

    for root, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(d for d in dirnames if d not in excludes)
        for filename in sorted(filenames):
            path = Path(root) / filename
            relative = path.relative_to(repo).as_posix()
            try:
                stat = path.stat()
            except OSError as exc:
                errors.append({"path": relative, "error": str(exc)})
                continue
            suffix = path.suffix.lower()
            language = LANGUAGES.get(suffix)
            if language:
                language_counts[language] += 1
            file_entry = {
                "path": relative,
                "size": stat.st_size,
                "language": language,
                "categories": sorted(classify(relative, filename)),
            }
            if stat.st_size <= hash_limit:
                try:
                    file_entry["sha256"] = sha256(path)
                except OSError as exc:
                    errors.append({"path": relative, "error": str(exc)})
            files.append(file_entry)
            for category in file_entry["categories"]:
                categories.setdefault(category, []).append(relative)

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "path": str(repo.resolve()),
            "remote": git_value(repo, "config", "--get", "remote.origin.url"),
            "revision": git_value(repo, "rev-parse", "HEAD"),
            "branch": git_value(repo, "branch", "--show-current"),
            "dirty": bool(git_value(repo, "status", "--porcelain")),
        },
        "summary": {
            "file_count": len(files),
            "languages": dict(sorted(language_counts.items())),
            "category_counts": {key: len(value) for key, value in sorted(categories.items())},
        },
        "categories": {key: sorted(value) for key, value in sorted(categories.items())},
        "files": files,
        "limitations": {
            "method": "filesystem-and-filename-inventory",
            "does_not_prove": [
                "runtime calls",
                "business ownership",
                "bounded contexts",
                "contract conformance",
            ],
            "errors": errors,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--hash-limit", type=int, default=5 * 1024 * 1024)
    args = parser.parse_args()

    repo = args.repository.resolve()
    if not repo.is_dir():
        parser.error(f"repository is not a directory: {repo}")
    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    result = inventory(repo, excludes, args.hash_limit)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
