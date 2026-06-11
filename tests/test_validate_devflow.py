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


def test_repository_passes_validation():
    validator = load_validator()

    errors = validator.run_all(ROOT)

    assert errors == [], "\n".join(errors)
