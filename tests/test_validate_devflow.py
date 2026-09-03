import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_devflow.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_devflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_skill(root: Path, name: str):
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test\n---\n# {name}\n", encoding="utf-8"
    )


def test_markdown_link_checker_reports_missing_relative_links(tmp_path):
    validator = load_validator()
    doc = tmp_path / "doc.md"
    doc.write_text("[missing](missing.md)\n", encoding="utf-8")

    result = validator.validate_markdown_links(tmp_path)

    assert str(doc) in result[0]
    assert "missing.md" in result[0]


def test_frontmatter_name_must_match_directory(tmp_path):
    validator = load_validator()
    skill_dir = tmp_path / "skills" / "devflow-tdd"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: wrong-name\ndescription: test\n---\n", encoding="utf-8"
    )

    result = validator.validate_skill_frontmatter(tmp_path)

    assert any("does not match directory" in error for error in result)


def test_expected_skill_set_is_enforced(tmp_path):
    validator = load_validator()
    for name in validator.EXPECTED_SKILLS - {"devflow-tdd"}:
        write_skill(tmp_path, name)

    result = validator.validate_skill_set(tmp_path)

    assert any("devflow-tdd" in error and "missing" in error for error in result)


def test_expected_command_set_is_enforced(tmp_path):
    validator = load_validator()
    commands = tmp_path / "commands"
    commands.mkdir()
    for name in validator.EXPECTED_COMMANDS - {"devflow-init.md"}:
        (commands / name).write_text("# command\n", encoding="utf-8")

    result = validator.validate_command_set(tmp_path)

    assert any("devflow-init.md" in error and "missing" in error for error in result)


def test_活动指令不能引用已废弃的_coding_skills_根(tmp_path):
    validator = load_validator()
    commands = tmp_path / "commands"
    commands.mkdir()
    (commands / "devflow.md").write_text(
        "读取 `coding-skills/using-devflow/SKILL.md`。\n", encoding="utf-8"
    )
    (commands / "devflow-specify.md").write_text(
        "读取 `skills/devflow-specify/SKILL.md`。\n", encoding="utf-8"
    )

    result = validator.validate_repository_skill_paths(tmp_path)

    assert any("devflow.md" in error and "已废弃" in error for error in result)
    assert not any("devflow-specify.md" in error for error in result)


def test_废弃根检查覆盖命令之外的活动指令(tmp_path):
    validator = load_validator()
    skill = tmp_path / "skills" / "using-devflow" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("同步顺序见 `coding-skills/devflow-ship/SKILL.md`。\n", encoding="utf-8")
    domain_readme = tmp_path / "domain-knowledge-library" / "README.md"
    domain_readme.parent.mkdir(parents=True)
    domain_readme.write_text("集合独立于 `coding-skills/`。\n", encoding="utf-8")

    result = validator.validate_repository_skill_paths(tmp_path)

    assert any("using-devflow" in error and "已废弃" in error for error in result)
    assert any("domain-knowledge-library" in error for error in result)


def test_命令不能用仓库路径加载技能(tmp_path):
    validator = load_validator()
    write_skill(tmp_path, "using-devflow")
    commands = tmp_path / "commands"
    commands.mkdir()
    (commands / "devflow.md").write_text(
        "1. 读取 `skills/using-devflow/SKILL.md` 及其直接 references。\n", encoding="utf-8"
    )

    result = validator.validate_skill_loading_by_name(tmp_path)

    assert any("devflow.md" in error and "应改为技能名" in error for error in result)


def test_技能之间不能用跨技能相对路径引用(tmp_path):
    validator = load_validator()
    write_skill(tmp_path, "devflow-tdd")
    write_skill(tmp_path, "devflow-specify")
    (tmp_path / "skills" / "devflow-specify" / "SKILL.md").write_text(
        "---\nname: devflow-specify\ndescription: test\n---\n"
        "使用 `../devflow-tdd/references/tasks-template.md` 建立骨架。\n",
        encoding="utf-8",
    )

    result = validator.validate_skill_loading_by_name(tmp_path)

    assert any("../devflow-tdd/" in error for error in result)


def test_用技能名引用其他技能的文件时通过(tmp_path):
    validator = load_validator()
    write_skill(tmp_path, "devflow-tdd")
    write_skill(tmp_path, "devflow-specify")
    (tmp_path / "skills" / "devflow-specify" / "SKILL.md").write_text(
        "---\nname: devflow-specify\ndescription: test\n---\n"
        "加载 `devflow-tdd` 技能，使用它的 `references/tasks-template.md` 建立骨架。\n",
        encoding="utf-8",
    )

    assert validator.validate_skill_loading_by_name(tmp_path) == []


def test_两个_skill_root_下技能重名会被拒绝(tmp_path):
    validator = load_validator()
    write_skill(tmp_path, "using-domain-knowledge")
    duplicate = tmp_path / "domain-knowledge-library" / "using-domain-knowledge"
    duplicate.mkdir(parents=True)
    (duplicate / "SKILL.md").write_text(
        "---\nname: using-domain-knowledge\ndescription: test\n---\n", encoding="utf-8"
    )

    result = validator.validate_skill_name_uniqueness(tmp_path)

    assert any("按名加载会产生歧义" in error for error in result)


def test_delivery_contract_requires_canonical_tokens(tmp_path):
    validator = load_validator()
    for relative_path, tokens in validator.REQUIRED_CONTRACT_TOKENS.items():
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(tokens), encoding="utf-8")

    using_devflow = tmp_path / "skills" / "using-devflow" / "SKILL.md"
    using_devflow.write_text("specs/changes/\nchange.json\ndevflow-init\n", encoding="utf-8")

    result = validator.validate_delivery_contract(tmp_path)

    assert any("using-devflow" in error and "componentMode" in error for error in result)


def test_spec_template_shape_requires_new_component_purpose(tmp_path):
    validator = load_validator()
    references = tmp_path / "skills" / "devflow-specify" / "references"
    references.mkdir(parents=True)
    (references / "component-spec-template.md").write_text(
        "## 1. 目的\n## 2. 需求\n#### 场景\n## 3. 来源追溯\n",
        encoding="utf-8",
    )
    (references / "delta-spec-template.md").write_text(
        "\n".join(
            (
                "## 组件目的变更",
                "## ADDED 需求",
                "## MODIFIED 需求",
                "## REMOVED 需求",
                "## RENAMED 需求",
                "## 无规格变化",
                "RENAMED → REMOVED → MODIFIED → ADDED",
            )
        ),
        encoding="utf-8",
    )

    result = validator.validate_spec_template_shape(tmp_path)

    assert any("Purpose must be mandatory" in error for error in result)


def test_legacy_skill_directories_are_rejected(tmp_path):
    validator = load_validator()
    for name in validator.EXPECTED_SKILLS:
        write_skill(tmp_path, name)
    write_skill(tmp_path, "devflow-router")

    result = validator.validate_skill_set(tmp_path)

    assert any("devflow-router" in error and "removed" in error for error in result)


def test_new_language_coding_standards_is_accepted_by_convention(tmp_path):
    validator = load_validator()
    for name in validator.EXPECTED_SKILLS:
        write_skill(tmp_path, name)
    write_skill(tmp_path, "java-coding-standards")

    result = validator.validate_skill_set(tmp_path)

    assert result == []


def test_malformed_coding_standards_name_is_rejected(tmp_path):
    validator = load_validator()
    for name in validator.EXPECTED_SKILLS:
        write_skill(tmp_path, name)
    write_skill(tmp_path, "Java_Style-coding-standards")

    result = validator.validate_skill_set(tmp_path)

    assert any("naming convention" in error for error in result)


def test_legacy_references_are_detected_in_active_text():
    validator = load_validator()

    assert "devflow-tdd-implementation" in validator.find_legacy_references(
        "next step is devflow-tdd-implementation"
    )
    assert "Next Action Or Recommended Skill" in validator.find_legacy_references(
        "write Next Action Or Recommended Skill into progress.md"
    )
    assert "features/" in validator.find_legacy_references(
        "write current artifacts under features/AR123-demo"
    )
    assert "plan.md" in validator.find_legacy_references(
        "recover task state from plan.md"
    )
    # New skill names that contain no legacy tokens pass clean.
    assert validator.find_legacy_references("use devflow-tdd and devflow-design") == []


def test_packaged_skills_cannot_reference_repository_design_docs(tmp_path):
    validator = load_validator()
    design_doc = tmp_path / "docs" / "devflow-core-architecture.md"
    design_doc.parent.mkdir(parents=True)
    design_doc.write_text("# Architecture\n", encoding="utf-8")
    skill = tmp_path / "skills" / "using-devflow" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("See `docs/devflow-core-architecture.md`.\n", encoding="utf-8")

    result = validator.validate_no_skill_design_doc_references(tmp_path)

    assert any("docs/devflow-core-architecture.md" in error for error in result)


def test_agent_missing_frontmatter_is_caught(tmp_path):
    validator = load_validator()
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "bare.md").write_text("# Agent\nNo frontmatter.\n", encoding="utf-8")

    result = validator.validate_agent_frontmatter(tmp_path)

    assert any("missing YAML frontmatter" in e for e in result)


def test_agent_missing_description_is_caught(tmp_path):
    validator = load_validator()
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "nodesc.md").write_text(
        "---\nmode: subagent\n---\n# Agent\n", encoding="utf-8"
    )

    result = validator.validate_agent_frontmatter(tmp_path)

    assert any("missing description" in e for e in result)


def test_agent_valid_frontmatter_passes(tmp_path):
    validator = load_validator()
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "good.md").write_text(
        "---\ndescription: A good agent\nmode: subagent\npermission:\n  edit: deny\n---\n# Agent\n",
        encoding="utf-8",
    )

    result = validator.validate_agent_frontmatter(tmp_path)

    assert result == []


def test_devflow_learn_必需文件缺失时校验失败(tmp_path):
    validator = load_validator()
    skill = tmp_path / "skills" / "devflow-learn"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# 知识沉淀\n", encoding="utf-8")

    result = validator.validate_learning_skill(tmp_path)

    assert any("learning-schema.json" in error and "必需文件缺失" in error for error in result)
    assert any("validate_learning.py" in error and "必需文件缺失" in error for error in result)


def test_devflow_learn_schema_必须拒绝未知字段(tmp_path):
    validator = load_validator()
    skill = tmp_path / "skills" / "devflow-learn"
    for relative in (
        "SKILL.md",
        "references/learning-contract.md",
        "references/learning-templates.md",
        "references/learning-review-rubric.md",
        "references/learning-refresh-protocol.md",
        "scripts/validate_learning.py",
        "evals/evals.json",
    ):
        path = skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    schema_path = skill / "references" / "learning-schema.json"
    schema_path.write_text(
        '{"additionalProperties": true, "required": [], "categoryMapping": {}}\n',
        encoding="utf-8",
    )

    result = validator.validate_learning_skill(tmp_path)

    assert any("必须拒绝未声明字段" in error for error in result)
    assert any("类型与目录映射不完整" in error for error in result)


def test_repository_passes_validation():
    validator = load_validator()

    errors = validator.run_all(ROOT)

    assert errors == [], "\n".join(errors)
