import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_devflow.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_devflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extension_skills_are_not_canonical_next_actions():
    validator = load_validator()

    result = validator.validate_canonical_next_actions(
        "Next Action Or Recommended Skill = cpp-coding-standards"
    )

    assert any("cpp-coding-standards" in error for error in result)

    clean_result = validator.validate_canonical_next_actions(
        "Next Action Or Recommended Skill = devflow-clean-code"
    )

    assert any("devflow-clean-code" in error for error in clean_result)

    current_stage_result = validator.validate_canonical_next_actions(
        "Current Stage = devflow-clean-design"
    )

    assert any("devflow-clean-design" in error for error in current_stage_result)

    alias_result = validator.validate_canonical_next_actions(
        "next_action: embedded-development"
    )

    assert any("embedded-development" in error for error in alias_result)

    automotive_result = validator.validate_canonical_next_actions(
        "next_action: automotive-development"
    )

    assert any("automotive-development" in error for error in automotive_result)


def test_markdown_link_checker_reports_missing_relative_links(tmp_path):
    validator = load_validator()
    doc = tmp_path / "doc.md"
    doc.write_text("[missing](missing.md)\n", encoding="utf-8")

    result = validator.validate_markdown_links(tmp_path)

    assert str(doc) in result[0]
    assert "missing.md" in result[0]


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


def test_project_runtime_docs_paths_are_allowed_in_skills(tmp_path):
    validator = load_validator()
    skill = tmp_path / "skills" / "devflow-ar-design" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Read target project `docs/component-design.md` when present.\n", encoding="utf-8")

    result = validator.validate_no_skill_design_doc_references(tmp_path)

    assert result == []


def test_old_craft_main_story_is_detected():
    validator = load_validator()

    result = validator.validate_no_old_craft_story(
        "DevFlow ships one public entry meta-skill, 13 canonical nodes, and 3 craft lenses."
    )

    assert result


def test_old_craft_skill_file_is_rejected(tmp_path):
    validator = load_validator()
    old_skill = tmp_path / "skills" / "devflow-test-craft"
    old_skill.mkdir(parents=True)
    (old_skill / "SKILL.md").write_text("---\nname: devflow-test-craft\n---\n", encoding="utf-8")

    result = validator.validate_clean_layer_contract(tmp_path)

    assert any("legacy file should be removed" in error for error in result)

    mixed_domain = tmp_path / "skills" / "automotive-embedded-development"
    mixed_domain.mkdir(parents=True)
    (mixed_domain / "SKILL.md").write_text("---\nname: automotive-embedded-development\n---\n", encoding="utf-8")

    result = validator.validate_clean_layer_contract(tmp_path)

    assert any("automotive-embedded-development" in error for error in result)


def test_legacy_reference_file_is_rejected(tmp_path):
    validator = load_validator()
    legacy_file = tmp_path / "skills" / "devflow-code-review" / "references" / "team-code-review-checklist.md"
    legacy_file.parent.mkdir(parents=True)
    legacy_file.write_text("# legacy\n", encoding="utf-8")

    result = validator.validate_clean_layer_contract(tmp_path)

    assert any("team-code-review-checklist.md" in error for error in result)


def test_missing_split_domain_skills_are_rejected(tmp_path):
    validator = load_validator()
    (tmp_path / "skills" / "devflow-clean-design").mkdir(parents=True)
    (tmp_path / "skills" / "devflow-clean-design" / "SKILL.md").write_text(
        "---\nname: devflow-clean-design\ndescription: test\n---\n", encoding="utf-8"
    )
    (tmp_path / "skills" / "devflow-clean-code").mkdir(parents=True)
    (tmp_path / "skills" / "devflow-clean-code" / "SKILL.md").write_text(
        "---\nname: devflow-clean-code\ndescription: test\n---\n", encoding="utf-8"
    )

    result = validator.validate_clean_layer_contract(tmp_path)

    assert any("embedded-development" in error for error in result)
    assert any("automotive-development" in error for error in result)


def test_all_old_craft_names_are_detected_in_active_text():
    validator = load_validator()

    result = validator.validate_no_old_craft_story(
        "Use devflow-design-craft, devflow-coding-craft, and devflow-test-craft."
    )

    assert result

    mixed_domain_result = validator.validate_no_old_craft_story(
        "Use automotive-embedded-development."
    )

    assert mixed_domain_result
