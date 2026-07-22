"""Lightweight repository checks for DevFlow architecture boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SKILLS = {
    "using-devflow",
    "devflow-init",
    "devflow-specify",
    "devflow-design",
    "devflow-tdd",
    "devflow-clean-code",
    "devflow-review",
    "devflow-ship",
    "devflow-fix",
    "c-coding-standards",
    "cpp-coding-standards",
    "java-coding-standards",
    "python-coding-standards",
    "coding-standards-creator",
    "embedded-development",
    "automotive-development",
    "frontend-development",
    "backend-development",
}

EXPECTED_COMMANDS = {
    "devflow.md",
    "devflow-init.md",
    "devflow-specify.md",
    "devflow-design.md",
    "devflow-build.md",
    "devflow-review.md",
    "devflow-ship.md",
    "devflow-fix.md",
}

REQUIRED_CONTRACT_TOKENS = {
    "skills/using-devflow/SKILL.md": (
        "specs/changes/",
        "change.json",
        "componentMode",
        "devflow-init",
    ),
    "skills/devflow-init/SKILL.md": (
        "澄清而不臆造",
        "baseline-ready",
        "specs/spec.md",
        "specs/design.md",
    ),
    "skills/devflow-specify/SKILL.md": ("srs.md", "delta-spec.md", "change.json"),
    "skills/devflow-specify/references/component-spec-template.md": (
        "## 1. 目的",
        "## 2. 需求",
        "### SPEC-FR-001",
        "#### 场景",
        "### SPEC-NFR-001",
        "#### 质量属性场景",
        "### SPEC-CON-001",
        "#### 验证场景",
        "## 3. 来源追溯",
        "## 4. 未知项",
        "## 5. 修订与确认",
    ),
    "skills/devflow-specify/references/delta-spec-template.md": (
        "## 组件目的变更",
        "## ADDED 需求",
        "## MODIFIED 需求",
        "## REMOVED 需求",
        "## RENAMED 需求",
        "RENAMED → REMOVED → MODIFIED → ADDED",
        "同一规格 ID 不得同时出现在互斥分区",
        "完整需求块",
        "删除原因",
        "## 无规格变化",
    ),
    "skills/devflow-fix/references/fix-template.md": (
        "## MODIFIED 需求",
        "## 无规格变化（仅缺陷恢复适用）",
        "manifest: change.json",
    ),
    "skills/devflow-design/SKILL.md": ("delta-design.md", "specs/design.md"),
    "skills/devflow-tdd/SKILL.md": ("tasks.md", "change.json"),
    "skills/devflow-review/SKILL.md": ("reviews/", "canonical"),
    "skills/devflow-ship/SKILL.md": ("specs/archive/", "closeout.md", "canonical"),
    "skills/devflow-fix/SKILL.md": ("specs/changes/", "tasks.md"),
    "INTRODUCTION.md": ("devflow-init", "delta-spec.md", "tasks.md", "canonical sync"),
    "docs/devflow-core-architecture.md": (
        "specs/changes/",
        "change.json",
        "devflow-init",
        "Canonical Sync",
    ),
    "docs/guides/opencode-setup.md": (
        "reviews/r1-review-*.md",
        "reviews/r2-review-*.md",
        "reviews/r3-review-*.md",
        "devflow-init",
    ),
}

# Language standards follow the `<language>-coding-standards` naming convention and
# are generated/maintained via coding-standards-creator. New language skills (e.g.
# java-coding-standards) are valid without being listed here; add them to
# EXPECTED_SKILLS once adopted, to guard against accidental deletion.
CODING_STANDARDS_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-coding-standards$")

# Active instructions must use only the current skill and lifecycle contract.
LEGACY_SKILL_NAMES = {
    "devflow-router",
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
    "devflow-clean-design",
    "devflow-design-craft",
    "devflow-coding-craft",
    "devflow-test-craft",
    "automotive-embedded-development",
}

LEGACY_MECHANISM_PHRASES = [
    "Next Action Or Recommended Skill",
    "next_action_or_recommended_skill",
    "Workflow Profile",
    "Execution Mode",
    "Implementer Context Pack",
    "canonical node",
    "canonical 节点",
    "features/",
    "docs/ar-specs/",
    "docs/ar-designs/",
    "component-design-draft.md",
    "plan.md",
    "promotion",
]

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def iter_markdown_files(root: Path):
    ignored_parts = {".git", "__pycache__", ".cursor", ".idea"}
    for path in root.rglob("*.md"):
        if ignored_parts.intersection(path.parts):
            continue
        yield path


def iter_active_markdown_files(root: Path):
    """Active instructions and user docs, excluding explicit history / changelog."""
    for sub in ("skills", "commands", "agents"):
        base = root / sub
        if base.exists():
            yield from (p for p in base.rglob("*.md"))
    for name in ("README.md", "README.zh-CN.md", "INTRODUCTION.md"):
        path = root / name
        if path.exists():
            yield path
    guides = root / "docs" / "guides"
    if guides.exists():
        yield from guides.rglob("*.md")
    core_architecture = root / "docs" / "devflow-core-architecture.md"
    if core_architecture.exists():
        yield core_architecture


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


def validate_agent_frontmatter(root: Path = ROOT) -> list[str]:
    """Agent files under agents/ must carry OpenCode-discoverable frontmatter."""
    errors: list[str] = []
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return [f"{agents_dir}: agents directory is missing"]
    for agent in agents_dir.glob("*.md"):
        text = agent.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            errors.append(f"{agent}: missing YAML frontmatter (OpenCode requires description + mode)")
            continue
        end = text.find("\n---", 4)
        if end == -1:
            errors.append(f"{agent}: unterminated YAML frontmatter")
            continue
        frontmatter = text[4:end]
        if "\ndescription:" not in f"\n{frontmatter}":
            errors.append(f"{agent}: missing description (required for OpenCode task tool dispatch)")
        if "\nmode:" not in f"\n{frontmatter}":
            errors.append(f"{agent}: missing mode (subagent agents need mode: subagent)")
    return errors


def validate_skill_set(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    skills_root = root / "skills"
    if not skills_root.exists():
        return [f"{skills_root}: skills directory is missing"]

    present = {p.name for p in skills_root.iterdir() if p.is_dir()}
    for missing in sorted(EXPECTED_SKILLS - present):
        errors.append(f"skills/{missing}: expected skill is missing")
    for legacy in sorted(present & LEGACY_SKILL_NAMES):
        errors.append(f"skills/{legacy}: legacy skill should be removed")
    for name in sorted(present):
        if name.endswith("-coding-standards") and not CODING_STANDARDS_NAME.match(name):
            errors.append(
                f"skills/{name}: must follow the <language>-coding-standards naming convention"
            )
    return errors


def validate_command_set(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    commands_root = root / "commands"
    if not commands_root.exists():
        return [f"{commands_root}: commands directory is missing"]

    present = {p.name for p in commands_root.glob("devflow*.md")}
    for missing in sorted(EXPECTED_COMMANDS - present):
        errors.append(f"commands/{missing}: expected command is missing")
    return errors


def validate_delivery_contract(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative_path, tokens in REQUIRED_CONTRACT_TOKENS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"{path}: delivery contract file is missing")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in tokens:
            if token not in text:
                errors.append(f"{path}: missing delivery contract token {token}")
    return errors


def validate_spec_template_shape(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    component_path = root / "skills/devflow-specify/references/component-spec-template.md"
    if component_path.exists():
        text = component_path.read_text(encoding="utf-8", errors="ignore")
        ordered = ("## 1. 目的", "## 2. 需求", "#### 场景", "## 3. 来源追溯")
        positions = [text.find(token) for token in ordered]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append(f"{component_path}: Purpose/Requirements/Scenario/Provenance order is invalid")

    delta_path = root / "skills/devflow-specify/references/delta-spec-template.md"
    if delta_path.exists():
        text = delta_path.read_text(encoding="utf-8", errors="ignore")
        headings = (
            "## 组件目的变更",
            "## ADDED 需求",
            "## MODIFIED 需求",
            "## REMOVED 需求",
            "## RENAMED 需求",
            "## 无规格变化",
        )
        for heading in headings:
            if text.count(heading) != 1:
                errors.append(f"{delta_path}: expected exactly one heading {heading}")
        if "`new` 必填" not in text:
            errors.append(f"{delta_path}: new component Purpose must be mandatory")
        if "RENAMED → REMOVED → MODIFIED → ADDED" not in text:
            errors.append(f"{delta_path}: deterministic operation order is missing")

    return errors


def find_legacy_references(text: str) -> list[str]:
    found: list[str] = []
    for name in sorted(LEGACY_SKILL_NAMES):
        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", text):
            found.append(name)
    for phrase in LEGACY_MECHANISM_PHRASES:
        if phrase in text:
            found.append(phrase)
    return found


def validate_no_legacy_references(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    active_paths = list(iter_active_markdown_files(root))
    active_paths.extend(root.glob("skills/*/evals/*.json"))
    for path in active_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for hit in find_legacy_references(text):
            errors.append(f"{path}: legacy reference remains: {hit}")
    return errors


def validate_no_skill_design_doc_references(root: Path = ROOT) -> list[str]:
    """Packaged skills must stay deployable without the repo-level docs/ tree."""
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
    for skill_doc in skills_root.rglob("*.md"):
        text = skill_doc.read_text(encoding="utf-8", errors="ignore")
        for design_doc_path in design_doc_paths:
            if design_doc_path in text:
                errors.append(
                    f"{skill_doc}: packaged skill references non-deployed design doc {design_doc_path}"
                )
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


def run_all(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_markdown_links(root))
    errors.extend(validate_skill_frontmatter(root))
    errors.extend(validate_agent_frontmatter(root))
    errors.extend(validate_skill_set(root))
    errors.extend(validate_command_set(root))
    errors.extend(validate_delivery_contract(root))
    errors.extend(validate_spec_template_shape(root))
    errors.extend(validate_no_legacy_references(root))
    errors.extend(validate_no_skill_design_doc_references(root))
    errors.extend(validate_eval_json(root))
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
