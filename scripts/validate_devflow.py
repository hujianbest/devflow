"""Lightweight repository checks for DevFlow architecture boundaries."""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_NODES = {
    "devflow-router",
    "devflow-specify",
    "devflow-spec-review",
    "devflow-component-design",
    "devflow-component-design-review",
    "devflow-ar-design",
    "devflow-ar-design-review",
    "devflow-tdd-implementation",
    "devflow-test-review",
    "devflow-code-review",
    "devflow-completion-gate",
    "devflow-finalize",
    "devflow-problem-fix",
}

NON_CANONICAL_EXTENSION_SKILLS = {
    "using-devflow",
    "devflow-clean-design",
    "devflow-clean-code",
    "c-coding-standards",
    "cpp-coding-standards",
    "embedded-development",
    "automotive-development",
    "automotive-embedded-development",
    "devflow-design-craft",
    "devflow-coding-craft",
    "devflow-test-craft",
}

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RUNTIME_FIELD_PATTERN = re.compile(
    r"(?:Next Action Or Recommended Skill|next_action_or_recommended_skill|next_action|Current Stage|current_stage)\s*[:=]\s*`?([A-Za-z0-9_-]+)`?",
    re.IGNORECASE,
)


def iter_markdown_files(root: Path):
    ignored_parts = {".git", "__pycache__", ".cursor", ".idea"}
    for path in root.rglob("*.md"):
        if ignored_parts.intersection(path.parts):
            continue
        yield path


def validate_markdown_links(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in LINK_PATTERN.findall(text):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            link_path = target.split("#", 1)[0]
            if not link_path:
                continue
            resolved = (path.parent / link_path).resolve()
            if not resolved.exists():
                errors.append(f"{path}: missing link target {target}")
    return errors


def validate_skill_frontmatter(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for skill in root.glob("skills/*/SKILL.md"):
        text = skill.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            errors.append(f"{skill}: missing YAML frontmatter")
            continue
        end = text.find("\n---", 4)
        if end == -1:
            errors.append(f"{skill}: unterminated YAML frontmatter")
            continue
        frontmatter = text[4:end]
        if "\nname:" not in f"\n{frontmatter}":
            errors.append(f"{skill}: missing name")
        if "\ndescription:" not in f"\n{frontmatter}":
            errors.append(f"{skill}: missing description")
        expected_name = skill.parent.name
        name_match = re.search(r"^name:\s*([A-Za-z0-9_-]+)\s*$", frontmatter, re.MULTILINE)
        if name_match and name_match.group(1) != expected_name:
            errors.append(f"{skill}: name {name_match.group(1)} does not match directory {expected_name}")
    return errors


def validate_no_skill_design_doc_references(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    docs_root = root / "docs"
    skills_root = root / "skills"
    if not docs_root.exists() or not skills_root.exists():
        return errors

    design_doc_paths = sorted(
        path.relative_to(root).as_posix()
        for path in docs_root.rglob("*")
        if path.is_file()
    )
    if not design_doc_paths:
        return errors

    for skill_doc in skills_root.rglob("*.md"):
        text = skill_doc.read_text(encoding="utf-8", errors="ignore")
        for design_doc_path in design_doc_paths:
            windows_path = design_doc_path.replace("/", "\\")
            if design_doc_path in text or windows_path in text:
                errors.append(
                    f"{skill_doc}: packaged skill references non-deployed design doc {design_doc_path}"
                )
    return errors


def validate_canonical_next_actions(text: str) -> list[str]:
    errors: list[str] = []
    for node in RUNTIME_FIELD_PATTERN.findall(text):
        if node in NON_CANONICAL_EXTENSION_SKILLS:
            errors.append(f"non-canonical next action: {node}")
        elif node.startswith("devflow-") and node not in CANONICAL_NODES:
            errors.append(f"unknown devflow next action: {node}")
    return errors


def validate_repository_next_actions(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for error in validate_canonical_next_actions(text):
            errors.append(f"{path}: {error}")
    return errors


def validate_no_old_craft_story(text: str) -> list[str]:
    old_story_patterns = [
        "3 craft lenses",
        "3 quality-craft lens skills",
        "3 个匠艺质量透镜",
        "craft quality lenses",
        "quality-craft lens",
        "devflow-design-craft",
        "devflow-coding-craft",
        "devflow-test-craft",
        "automotive-embedded-development",
    ]
    lowered = text.lower()
    return [pattern for pattern in old_story_patterns if pattern.lower() in lowered]


def validate_repository_old_craft_story(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    paths = [
        root / "README.md",
        root / "README.zh-CN.md",
        root / "skills" / "using-devflow" / "SKILL.md",
        root / "commands",
        root / "agents",
    ]
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(path.rglob("*.md"))
        else:
            files.append(path)
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in validate_no_old_craft_story(text):
            errors.append(f"{path}: old craft main story remains: {pattern}")
    return errors


def validate_eval_json(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in root.glob("skills/*/evals/*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        scenarios = data.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(f"{path}: missing non-empty scenarios list")
    return errors


def validate_clean_layer_contract(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    required_skills = [
        root / "skills" / "devflow-clean-design" / "SKILL.md",
        root / "skills" / "devflow-clean-code" / "SKILL.md",
        root / "skills" / "embedded-development" / "SKILL.md",
        root / "skills" / "automotive-development" / "SKILL.md",
    ]
    for path in required_skills:
        if not path.exists():
            errors.append(f"{path}: required clean-layer skill is missing")

    removed_skills = [
        root / "skills" / "devflow-test-craft" / "SKILL.md",
        root / "skills" / "devflow-design-craft" / "SKILL.md",
        root / "skills" / "devflow-coding-craft" / "SKILL.md",
        root / "skills" / "devflow-code-review" / "references" / "team-code-review-checklist.md",
        root / "skills" / "devflow-code-review" / "references" / "embedded-cpp-risk-checklist.md",
        root / "skills" / "devflow-problem-fix" / "references" / "devflow-progress-template.md",
        root / "skills" / "devflow-problem-fix" / "references" / "devflow-work-item-readme-template.md",
        root / "skills" / "automotive-embedded-development" / "SKILL.md",
    ]
    for path in removed_skills:
        if path.exists():
            errors.append(f"{path}: legacy file should be removed")

    core_docs = [
        root / "docs" / "devflow-core-architecture.md",
        root / "docs" / "devflow-internal-quality.md",
        root / "skills" / "using-devflow" / "SKILL.md",
    ]
    for path in core_docs:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for skill_name in ["devflow-clean-design", "devflow-clean-code"]:
            if skill_name not in text:
                errors.append(f"{path}: missing {skill_name} clean-layer reference")
    return errors


def validate_core_leakage(root: Path = ROOT) -> list[str]:
    """Catch stale core-level defaults that should live in extension skills."""
    errors: list[str] = []
    checked_paths = [
        root / "README.md",
        root / "README.zh-CN.md",
        root / "commands",
        root / "agents",
    ]
    checked_paths.extend(root.glob("skills/devflow-*/SKILL.md"))
    checked_paths.append(root / "skills" / "using-devflow" / "SKILL.md")
    checked_paths.append(root / "skills" / "devflow-ar-design" / "references" / "devflow-ar-design-template.md")

    files: list[Path] = []
    for path in checked_paths:
        if path.is_dir():
            files.extend(path.rglob("*.md"))
        else:
            files.append(path)

    stale_patterns = [
        "3 craft lenses",
        "3 个匠艺质量透镜",
        "quality-craft lens skills",
        "C / C++ 代码检视",
        "C/C++ code review",
        "DevFlow 面向 C/C++ 嵌入式",
        "embedded-risk",
        "MDC 场景设计、重构设计、测试设计、模板修订记录均为必填骨架",
        "devflow-test-craft",
        "devflow-design-craft",
        "devflow-coding-craft",
        "Legacy Example",
        "legacy example",
        "兼容说明",
        "旧团队代码检视清单",
        "team-code-review-checklist",
        "embedded-cpp-risk-checklist",
        "automotive-embedded-development",
    ]
    for path in files:
        if not path.exists():
            continue
        # Compatibility shim files intentionally mention old names.
        if path.parent.name in {"devflow-design-craft", "devflow-coding-craft", "devflow-test-craft"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in stale_patterns:
            if pattern in text:
                errors.append(f"{path}: stale core coupling phrase remains: {pattern}")
    return errors


def run_all(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_markdown_links(root))
    errors.extend(validate_skill_frontmatter(root))
    errors.extend(validate_repository_next_actions(root))
    errors.extend(validate_repository_old_craft_story(root))
    errors.extend(validate_eval_json(root))
    errors.extend(validate_clean_layer_contract(root))
    errors.extend(validate_no_skill_design_doc_references(root))
    errors.extend(validate_core_leakage(root))
    return errors


def main() -> int:
    errors = run_all(ROOT)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("DevFlow validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
