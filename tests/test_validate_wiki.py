import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "domain-wiki-skills"
    / "domain-wiki-lint"
    / "scripts"
    / "validate_wiki.py"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_wiki", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_wiki(tmp_path: Path, *, status="complete", concept_ok=True) -> Path:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "log.md").write_text(
        "# Log\n\n## [2026-08-14] init | Wiki initialized\n",
        encoding="utf-8",
    )
    (wiki / ".last-update.json").write_text(
        json.dumps(
            {
                "updatedAt": "2026-08-14T00:00:00Z",
                "command": "init",
                "gitHead": "abc123",
                "status": status,
                "language": "zh",
            }
        ),
        encoding="utf-8",
    )
    body = (
        "---\ntype: Concept\ntitle: Auth\n---\n\n# Auth\n"
        if concept_ok
        else "# Auth\n\nmissing front matter\n"
    )
    (wiki / "quickstart.md").write_text(body, encoding="utf-8")
    return wiki


def test_valid_wiki_passes(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path)
    errors: list[str] = []
    module.validate_metadata(wiki, errors)
    module.validate_log(wiki, errors)
    module.validate_concepts(wiki, errors)
    assert errors == []


def test_invalid_status_is_rejected(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path, status="draft")
    errors: list[str] = []
    module.validate_metadata(wiki, errors)
    assert any("status" in item for item in errors)


def test_concept_requires_type(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path, concept_ok=False)
    errors: list[str] = []
    module.validate_concepts(wiki, errors)
    assert any("front matter" in item or "type" in item for item in errors)


def test_valid_mermaid_passes(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path)
    page = wiki / "flow.md"
    page.write_text(
        "---\ntype: Concept\ntitle: Flow\n---\n\n# Flow\n\n"
        "```mermaid\nflowchart LR\n  start[Start] --> finish[Finish]\n```\n",
        encoding="utf-8",
    )
    errors: list[str] = []
    module.validate_mermaid(wiki, errors)
    assert errors == []


def test_mermaid_end_node_is_rejected(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path)
    (wiki / "flow.md").write_text(
        "---\ntype: Concept\ntitle: Flow\n---\n\n# Flow\n\n"
        "```mermaid\nflowchart LR\n  end[Done]\n```\n",
        encoding="utf-8",
    )
    errors: list[str] = []
    module.validate_mermaid(wiki, errors)
    assert any("end" in item for item in errors)


def test_mermaid_unescaped_angle_is_rejected(tmp_path):
    module = load_validator()
    wiki = write_wiki(tmp_path)
    (wiki / "flow.md").write_text(
        "---\ntype: Concept\ntitle: Flow\n---\n\n# Flow\n\n"
        "```mermaid\nflowchart LR\n  n[User <Admin>]\n```\n",
        encoding="utf-8",
    )
    errors: list[str] = []
    module.validate_mermaid(wiki, errors)
    assert any("<>" in item for item in errors)
