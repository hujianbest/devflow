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


def test_markdown_link_checker_reports_missing_relative_links(tmp_path):
    validator = load_validator()
    doc = tmp_path / "doc.md"
    doc.write_text("[missing](missing.md)\n", encoding="utf-8")

    result = validator.validate_markdown_links(tmp_path)

    assert str(doc) in result[0]
    assert "missing.md" in result[0]


def test_old_craft_main_story_is_detected():
    validator = load_validator()

    result = validator.validate_no_old_craft_story(
        "DevFlow ships one public entry meta-skill, 13 canonical nodes, and 3 craft lenses."
    )

    assert result
