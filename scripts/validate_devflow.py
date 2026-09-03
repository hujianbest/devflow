"""Lightweight repository checks for DevFlow architecture boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT_NAME = "skills"

EXPECTED_SKILLS = {
    "using-devflow",
    "devflow-init",
    "devflow-specify",
    "devflow-design",
    "devflow-tdd",
    "devflow-clean-code",
    "writing-readable-doc",
    "devflow-review",
    "devflow-ship",
    "devflow-fix",
    "devflow-learn",
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
    "devflow-learn.md",
}

REQUIRED_CONTRACT_TOKENS = {
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
    "skills/devflow-fix/SKILL.md": ("specs/changes/", "tasks.md"),
    "skills/devflow-learn/SKILL.md": (
        "docs/learnings/",
        "change.json.archive.status",
        "learning-schema.json",
        "validate_learning.py",
        "sensitivity: restricted",
    ),
    "skills/using-devflow/SKILL.md": (
        "specs/changes/",
        "change.json",
        "componentMode",
        "devflow-init",
        "docs/learnings/",
    ),
    "skills/devflow-ship/SKILL.md": (
        "specs/archive/",
        "closeout.md",
        "canonical",
        "devflow-learn",
    ),
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
    for sub in (SKILLS_ROOT_NAME, "commands", "agents"):
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
    for skill in root.glob(f"{SKILLS_ROOT_NAME}/*/SKILL.md"):
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
    skills_root = root / SKILLS_ROOT_NAME
    if not skills_root.exists():
        return [f"{skills_root}: skills directory is missing"]

    present = {p.name for p in skills_root.iterdir() if p.is_dir()}
    for missing in sorted(EXPECTED_SKILLS - present):
        errors.append(f"{SKILLS_ROOT_NAME}/{missing}: expected skill is missing")
    for legacy in sorted(present & LEGACY_SKILL_NAMES):
        errors.append(f"{SKILLS_ROOT_NAME}/{legacy}: legacy skill should be removed")
    for name in sorted(present):
        if name.endswith("-coding-standards") and not CODING_STANDARDS_NAME.match(name):
            errors.append(
                f"{SKILLS_ROOT_NAME}/{name}: must follow the <language>-coding-standards naming convention"
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


SKILL_FILE_PATH_RE = re.compile(
    r"(?:coding-skills|skills|domain-knowledge-library)/[A-Za-z0-9_-]+/SKILL\.md"
)


def _installed_skill_names(root: Path) -> set[str]:
    names: set[str] = set()
    for base in (root / SKILLS_ROOT_NAME, root / DOMAIN_KNOWLEDGE_ROOT_NAME):
        if base.exists():
            names.update(
                path.name for path in base.iterdir() if (path / "SKILL.md").is_file()
            )
    return names


def validate_skill_loading_by_name(root: Path = ROOT) -> list[str]:
    """技能、命令与 agent 只能用技能名加载技能，不写技能的仓库路径或跨技能相对路径。

    技能安装到运行时的 skills root 后，仓库路径全部失效；跨技能相对路径还会让技能
    无法独立安装。引用别的技能里的文件时写「技能名 + 该技能内的相对文件名」。
    """
    errors: list[str] = []
    names = _installed_skill_names(root)
    targets: list[Path] = []
    for sub in (SKILLS_ROOT_NAME, "commands", "agents", DOMAIN_KNOWLEDGE_ROOT_NAME):
        base = root / sub
        if base.exists():
            targets.extend(base.rglob("*.md"))

    for path in sorted(targets):
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = SKILL_FILE_PATH_RE.search(text)
        if match:
            errors.append(f"{path}: 用仓库路径 {match.group(0)} 加载技能，应改为技能名")
        for name in sorted(names):
            if f"../{name}/" in text:
                errors.append(
                    f"{path}: 用跨技能相对路径 ../{name}/ 引用，应改为「{name} 的 <文件名>」"
                )
    return errors


def validate_repository_skill_paths(root: Path = ROOT) -> list[str]:
    """活动指令必须使用 skills/ 源码根，不能引用已废弃的 coding-skills/ 根。"""
    errors: list[str] = []
    paths = list(iter_active_markdown_files(root))
    domain_root = root / DOMAIN_KNOWLEDGE_ROOT_NAME
    if domain_root.exists():
        paths.extend(domain_root.rglob("*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "coding-skills/" in text:
            errors.append(f"{path}: 仍引用已废弃的仓库 coding-skills/ 根")
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

    component_path = root / SKILLS_ROOT_NAME / "devflow-specify/references/component-spec-template.md"
    if component_path.exists():
        text = component_path.read_text(encoding="utf-8", errors="ignore")
        ordered = ("## 1. 目的", "## 2. 需求", "#### 场景", "## 3. 来源追溯")
        positions = [text.find(token) for token in ordered]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append(f"{component_path}: Purpose/Requirements/Scenario/Provenance order is invalid")

    delta_path = root / SKILLS_ROOT_NAME / "devflow-specify/references/delta-spec-template.md"
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
    active_paths.extend(root.glob(f"{SKILLS_ROOT_NAME}/*/evals/*.json"))
    for path in active_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for hit in find_legacy_references(text):
            errors.append(f"{path}: legacy reference remains: {hit}")
    return errors


def validate_no_skill_design_doc_references(root: Path = ROOT) -> list[str]:
    """Packaged skills must stay deployable without the repo-level docs/ tree."""
    errors: list[str] = []
    docs_root = root / "docs"
    if not docs_root.exists():
        return errors

    design_doc_paths = sorted(
        path.relative_to(root).as_posix()
        for path in docs_root.rglob("*")
        if path.is_file()
    )
    for skills_root in (root / SKILLS_ROOT_NAME, root / "domain-knowledge-library"):
        if not skills_root.exists():
            continue
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
    for path in root.glob(f"{SKILLS_ROOT_NAME}/*/evals/*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        scenarios = data.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(f"{path}: missing non-empty scenarios list")
    return errors


def validate_learning_skill(root: Path = ROOT) -> list[str]:
    """校验 devflow-learn 的打包结构与 schema 核心约束。"""
    errors: list[str] = []
    skill_root = root / SKILLS_ROOT_NAME / "devflow-learn"
    required_paths = (
        "SKILL.md",
        "references/learning-contract.md",
        "references/learning-schema.json",
        "references/learning-templates.md",
        "references/learning-review-rubric.md",
        "references/learning-refresh-protocol.md",
        "scripts/validate_learning.py",
        "evals/evals.json",
    )
    for relative in required_paths:
        path = skill_root / relative
        if not path.is_file():
            errors.append(f"{path}: devflow-learn 必需文件缺失")

    schema_path = skill_root / "references" / "learning-schema.json"
    if not schema_path.is_file():
        return errors
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{schema_path}: learning schema 不是有效 JSON：{exc}")
        return errors

    if schema.get("additionalProperties") is not False:
        errors.append(f"{schema_path}: learning schema 必须拒绝未声明字段")
    if schema.get("properties", {}).get("schemaVersion", {}).get("const") != "1.1":
        errors.append(f"{schema_path}: learning schemaVersion 必须是 1.1")
    expected_mapping = {
        "problem-solution": "problem-solutions",
        "design-decision": "design-decisions",
        "engineering-practice": "engineering-practices",
    }
    if schema.get("categoryMapping") != expected_mapping:
        errors.append(f"{schema_path}: learning 类型与目录映射不完整")
    required = set(schema.get("required", []))
    for field in (
        "learningId",
        "learningType",
        "component",
        "componentRoot",
        "status",
        "sensitivity",
        "sourceChanges",
        "sourceArchives",
        "tags",
    ):
        if field not in required:
            errors.append(f"{schema_path}: 缺少必需字段 `{field}`")
    properties = schema.get("properties", {})
    for field in ("relatedLearnings", "supersededBy", "statusReason"):
        if field not in properties:
            errors.append(f"{schema_path}: 缺少维护字段 `{field}`")

    validator_path = skill_root / "scripts" / "validate_learning.py"
    if validator_path.is_file():
        validator_text = validator_path.read_text(encoding="utf-8", errors="ignore")
        for token in (
            "lookup",
            "validate-store",
            "discoverability",
            "refresh-audit",
            "refresh-plan-check",
            "CLAIM_RE",
        ):
            if token not in validator_text:
                errors.append(f"{validator_path}: 缺少 learning 运行契约 `{token}`")
    return errors


DOMAIN_KNOWLEDGE_ROOT_NAME = "domain-knowledge-library"
DOMAIN_KNOWLEDGE_SKILLS = {
    "using-domain-knowledge",
    "domain-knowledge-maintain",
    "domain-knowledge-expand",
}
DOMAIN_KNOWLEDGE_REQUIRED_PATHS = (
    "README.md",
    "domain-knowledge-maintain/references/bundle-contract.md",
    "domain-knowledge-maintain/references/bootstrap-workflow.md",
    "domain-knowledge-maintain/references/ingest-workflow.md",
    "domain-knowledge-maintain/references/sync-workflow.md",
    "domain-knowledge-maintain/references/review-workflow.md",
    "domain-knowledge-maintain/references/audit-workflow.md",
    "domain-knowledge-maintain/references/templates.md",
    "domain-knowledge-maintain/scripts/kb.py",
    "using-domain-knowledge/references/consume-protocol.md",
    "using-domain-knowledge/references/capture-protocol.md",
    "using-domain-knowledge/references/proposal-template.md",
    "domain-knowledge-expand/references/expand-workflow.md",
    "hooks/hooks.json",
    "hooks/install.sh",
    "hooks/kb_common.py",
    "hooks/kb_session_start.py",
    "hooks/kb_read_guard.py",
    "hooks/kb_write_guard.py",
    "hooks/kb_shell_guard.py",
    "hooks/kb_capture_prompt.py",
)
DOMAIN_KNOWLEDGE_COMMANDS = {
    "domain-knowledge.md",
    "domain-knowledge-capture.md",
    "domain-knowledge-maintain.md",
    "domain-knowledge-expand.md",
}
DOMAIN_KNOWLEDGE_HOOK_EVENTS = {"sessionStart", "postToolUse", "preToolUse", "beforeShellExecution", "stop"}


def validate_domain_knowledge_collection(root: Path = ROOT) -> list[str]:
    """domain-knowledge-library 是独立集合：三技能、hooks、命令与 reviewer 必须齐全且自洽。"""
    errors: list[str] = []
    base = root / DOMAIN_KNOWLEDGE_ROOT_NAME
    if not base.exists():
        return [f"{base}: domain knowledge collection is missing"]

    for relative in DOMAIN_KNOWLEDGE_REQUIRED_PATHS:
        if not (base / relative).is_file():
            errors.append(f"{base / relative}: domain knowledge collection file is missing")

    for name in sorted(DOMAIN_KNOWLEDGE_SKILLS):
        skill = base / name / "SKILL.md"
        if not skill.is_file():
            errors.append(f"{skill}: expected skill is missing")
            continue
        text = skill.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            errors.append(f"{skill}: missing YAML frontmatter")
            continue
        end = text.find("\n---", 4)
        frontmatter = text[4:end] if end != -1 else ""
        name_match = re.search(r"^name:\s*([A-Za-z0-9_-]+)\s*$", frontmatter, re.MULTILINE)
        if not name_match or name_match.group(1) != name:
            errors.append(f"{skill}: name must equal directory {name}")
        if "\ndescription:" not in f"\n{frontmatter}":
            errors.append(f"{skill}: missing description")
        evals = base / name / "evals" / "evals.json"
        if not evals.is_file():
            errors.append(f"{evals}: missing evals")
        else:
            try:
                data = json.loads(evals.read_text(encoding="utf-8"))
                if not isinstance(data.get("scenarios"), list) or not data["scenarios"]:
                    errors.append(f"{evals}: missing non-empty scenarios list")
            except json.JSONDecodeError as exc:
                errors.append(f"{evals}: invalid JSON: {exc}")

    commands_root = root / "commands"
    present = {p.name for p in commands_root.glob("domain-knowledge*.md")} if commands_root.exists() else set()
    for missing in sorted(DOMAIN_KNOWLEDGE_COMMANDS - present):
        errors.append(f"commands/{missing}: expected command is missing")
    for command in sorted(present):
        text = (commands_root / command).read_text(encoding="utf-8", errors="ignore")
        if not any(f"`{name}`" in text for name in DOMAIN_KNOWLEDGE_SKILLS):
            errors.append(
                f"commands/{command}: 必须按技能名加载 {DOMAIN_KNOWLEDGE_ROOT_NAME} 中的技能"
            )

    reviewer = root / "agents" / "domain-knowledge-reviewer.md"
    if not reviewer.is_file():
        errors.append(f"{reviewer}: domain knowledge reviewer agent is missing")

    hooks_json = base / "hooks" / "hooks.json"
    if hooks_json.is_file():
        try:
            hooks = json.loads(hooks_json.read_text(encoding="utf-8"))
            events = set((hooks.get("hooks") or {}).keys())
            for missing in sorted(DOMAIN_KNOWLEDGE_HOOK_EVENTS - events):
                errors.append(f"{hooks_json}: missing hook event {missing}")
            for event, entries in (hooks.get("hooks") or {}).items():
                for entry in entries:
                    command = str(entry.get("command", ""))
                    script = command.split()[-1] if command else ""
                    if not script.startswith(".cursor/hooks/domain-kb/"):
                        errors.append(f"{hooks_json}: {event} command must live under .cursor/hooks/domain-kb/")
                    elif not (base / "hooks" / Path(script).name).is_file():
                        errors.append(f"{hooks_json}: {event} references missing script {Path(script).name}")
        except json.JSONDecodeError as exc:
            errors.append(f"{hooks_json}: invalid JSON: {exc}")

    contract = base / "domain-knowledge-maintain" / "references" / "bundle-contract.md"
    if contract.is_file():
        text = contract.read_text(encoding="utf-8", errors="ignore")
        for token in ("draft", "stable", "deprecated", "expanded_by", "sources", "verified", ".kb/proposals/", "maintenance.lock"):
            if token not in text:
                errors.append(f"{contract}: missing bundle contract token {token}")

    kb_script = base / "domain-knowledge-maintain" / "scripts" / "kb.py"
    if kb_script.is_file():
        text = kb_script.read_text(encoding="utf-8", errors="ignore")
        for token in ("validate", "index", "stale", "proposals", "inventory", "audit", "lock", "unlock", "init", "expanded_by"):
            if token not in text:
                errors.append(f"{kb_script}: missing kb.py subcommand or gate `{token}`")
    return errors


def run_all(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_domain_knowledge_collection(root))
    errors.extend(validate_markdown_links(root))
    errors.extend(validate_skill_frontmatter(root))
    errors.extend(validate_agent_frontmatter(root))
    errors.extend(validate_skill_set(root))
    errors.extend(validate_command_set(root))
    errors.extend(validate_repository_skill_paths(root))
    errors.extend(validate_skill_loading_by_name(root))
    errors.extend(validate_delivery_contract(root))
    errors.extend(validate_spec_template_shape(root))
    errors.extend(validate_no_legacy_references(root))
    errors.extend(validate_no_skill_design_doc_references(root))
    errors.extend(validate_eval_json(root))
    errors.extend(validate_learning_skill(root))
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
