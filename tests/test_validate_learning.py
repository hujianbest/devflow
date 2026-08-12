import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "devflow-learn" / "scripts" / "validate_learning.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_learning", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_archive(repo: Path, *, status: str = "archived", gate_status: str = "passed") -> Path:
    archive = repo / "specs" / "archive" / "2026-08-11-AR001-timeout-fix"
    archive.mkdir(parents=True)
    gates = {
        name: {
            "status": gate_status,
            "evidence": [],
            "reviewRecords": [],
            "humanConfirmation": (
                "confirmed" if name in ("canonicalSync", "closeout") else "not-required"
            ),
        }
        for name in ("r1", "r2", "r3", "canonicalSync", "closeout")
    }
    manifest = {
        "changeId": "AR001",
        "topic": "timeout-fix",
        "component": "core",
        "componentRoot": ".",
        "gates": gates,
        "archive": {"status": status},
    }
    (archive / "change.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (archive / "closeout.md").write_text("# 收尾\n\n最终人工确认已记录。\n", encoding="utf-8")
    return archive


def create_learning(repo: Path, *, extra_frontmatter: str = "", body: str = "## 问题\n\n超时处理不完整。\n") -> Path:
    learning = (
        repo
        / "docs"
        / "learnings"
        / "problem-solutions"
        / "core-problem-solution-timeout.md"
    )
    learning.parent.mkdir(parents=True)
    learning.write_text(
        "\n".join(
            (
                "---",
                'schemaVersion: "1.0"',
                "documentType: devflow-learning",
                "learningId: core-problem-solution-timeout",
                "learningType: problem-solution",
                "component: core",
                "componentRoot: .",
                "status: active",
                "sensitivity: internal",
                "capturedAt: 2026-08-11",
                "lastVerifiedAt: 2026-08-11",
                "sourceChanges:",
                "  - AR001-timeout-fix",
                "sourceArchives:",
                "  - specs/archive/2026-08-11-AR001-timeout-fix",
                "tags:",
                "  - timeout",
                extra_frontmatter,
                "---",
                body,
            )
        ),
        encoding="utf-8",
    )
    return learning


def test_有效_learning_通过全部机械校验(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)

    assert validator.validate(learning, tmp_path) == []


def test_未归档或_gate_未通过时拒绝沉淀(tmp_path):
    validator = load_validator()
    create_archive(tmp_path, status="active", gate_status="pending")
    learning = create_learning(tmp_path)

    errors = validator.validate(learning, tmp_path)

    assert any("尚未归档" in error for error in errors)
    assert any("gate 未通过" in error for error in errors)


def test_未知字段和错误目录会被拒绝(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path, extra_frontmatter="unknownField: value")
    wrong_path = learning.parent.parent / "design-decisions" / learning.name
    wrong_path.parent.mkdir()
    learning.replace(wrong_path)

    errors = validator.validate(wrong_path, tmp_path)

    assert any("不允许的字段 `unknownField`" in error for error in errors)
    assert any("problem-solutions" in error for error in errors)


def test_敏感信息和机器绝对路径会被拒绝(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(
        tmp_path,
        body=(
            "## 证据\n\n"
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n"
            "日志来自 C:\\Users\\alice\\trace.log。\n"
        ),
    )

    errors = validator.validate(learning, tmp_path)

    assert any("认证头" in error for error in errors)
    assert any("机器绝对路径" in error for error in errors)


def test_restricted_内容禁止写入(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)
    text = learning.read_text(encoding="utf-8").replace(
        "sensitivity: internal", "sensitivity: restricted"
    )
    learning.write_text(text, encoding="utf-8")

    errors = validator.validate(learning, tmp_path)

    assert any("禁止写入" in error for error in errors)


def test_learning_id_在知识库中必须唯一(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)
    duplicate = (
        tmp_path
        / "docs"
        / "learnings"
        / "engineering-practices"
        / "core-problem-solution-timeout.md"
    )
    duplicate.parent.mkdir()
    duplicate.write_text(learning.read_text(encoding="utf-8"), encoding="utf-8")

    errors = validator.validate(learning, tmp_path)

    assert any("learningId" in error and "重复" in error for error in errors)


def test_frontmatter_拒绝_flow_array(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)
    text = learning.read_text(encoding="utf-8").replace(
        "tags:\n  - timeout", "tags: [timeout]"
    )
    learning.write_text(text, encoding="utf-8")

    errors = validator.validate(learning, tmp_path)

    assert any("flow array" in error for error in errors)
