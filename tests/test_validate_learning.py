import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "coding-skills" / "devflow-learn" / "scripts" / "validate_learning.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_learning", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_archive(repo: Path, *, status: str = "archived", gate_status: str = "passed") -> Path:
    archive = repo / "specs" / "archive" / "2026-08-11-AR001-timeout-fix"
    archive.mkdir(parents=True)
    (archive / "reviews").mkdir()
    for name in ("r1", "r2", "r3", "canonical-sync"):
        (archive / "reviews" / f"{name}.md").write_text(f"# {name}\n\nVerdict: pass\n", encoding="utf-8")
    artifact_content = {
        "srs.md": "# SRS\n\nREQ-001\n",
        "delta-spec.md": "# Delta Spec\n\nSPEC-001\n",
        "delta-design.md": "# Delta Design\n\nDEC-001\n",
        "tasks.md": "# Tasks\n\n## 症状\n\n请求超时。\n\n## 根因\n\n取消路径未清理计时器。\n",
        "traceability.md": "# Traceability\n\nTRACE-001\n",
        "closeout.md": "# 收尾\n\n最终人工确认已记录。\n",
    }
    for name, content in artifact_content.items():
        (archive / name).write_text(content, encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_timeout.py").write_text(
        "def test_timeout_regression():\n    assert True\n", encoding="utf-8"
    )

    review_names = {
        "r1": "r1.md",
        "r2": "r2.md",
        "r3": "r3.md",
        "canonicalSync": "canonical-sync.md",
    }
    evidence_names = {
        "r1": "srs.md::REQ-001",
        "r2": "delta-design.md::DEC-001",
        "r3": "tasks.md::## 根因",
        "canonicalSync": "traceability.md::TRACE-001",
        "closeout": "closeout.md::最终人工确认",
    }
    gates = {}
    for name in ("r1", "r2", "r3", "canonicalSync", "closeout"):
        gates[name] = {
            "status": gate_status,
            "evidence": [evidence_names[name]],
            "reviewRecords": [] if name == "closeout" else [f"reviews/{review_names[name]}"],
            "humanConfirmation": (
                "confirmed" if name in ("canonicalSync", "closeout") else "not-required"
            ),
        }
    manifest = {
        "changeId": "AR001",
        "topic": "timeout-fix",
        "component": "core",
        "componentRoot": ".",
        "artifacts": {
            "srs": {"path": "srs.md", "status": "archived"},
            "deltaSpec": {"path": "delta-spec.md", "status": "archived"},
            "deltaDesign": {"path": "delta-design.md", "status": "archived"},
            "tasks": {"path": "tasks.md", "status": "archived"},
            "traceability": {"path": "traceability.md", "status": "archived"},
            "reviews": {"path": "reviews/", "status": "archived"},
            "closeout": {"path": "closeout.md", "status": "archived"},
        },
        "gates": gates,
        "archive": {
            "status": status,
            "target": "specs/archive/2026-08-11-AR001-timeout-fix",
            "confirmedBy": "maintainer",
            "archivedAt": "2026-08-11T12:00:00Z",
        },
    }
    (archive / "change.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    return archive


VALID_BODY = """# 超时取消路径

## 问题

请求取消后计时器仍然存活。
<!-- claim: CLM-001; kind: historical; evidence: EV-001 -->

## 根因

取消路径没有清理计时器。
<!-- claim: CLM-002; kind: historical; evidence: EV-001 -->

## 已验证方案

取消请求时同步释放计时器。
<!-- claim: CLM-003; kind: guidance; evidence: EV-001,EV-002 -->

## 适用范围

适用于异步超时资源；不适用于无状态同步调用。

## 证据

- EV-001 | archive | `specs/archive/2026-08-11-AR001-timeout-fix/tasks.md::## 根因`
- EV-002 | current-test | `tests/test_timeout.py::def test_timeout_regression():`
"""


def create_learning(repo: Path, *, extra_frontmatter: str = "", body: str = VALID_BODY) -> Path:
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
                'schemaVersion: "1.1"',
                "documentType: devflow-learning",
                "learningId: core-problem-solution-timeout",
                "learningType: problem-solution",
                "component: core",
                "componentRoot: .",
                "status: active",
                "sensitivity: internal",
                "capturedAt: 2026-08-12",
                "lastVerifiedAt: 2026-08-12",
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


def test_current_claim_必须引用当前证据(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)
    text = learning.read_text(encoding="utf-8").replace(
        "kind: guidance; evidence: EV-001,EV-002",
        "kind: current; evidence: EV-001",
    )
    learning.write_text(text, encoding="utf-8")

    errors = validator.validate(learning, tmp_path)

    assert any("current claim 至少需要一项 current evidence" in error for error in errors)


def test_archive_target_和_review_record_必须真实(tmp_path):
    validator = load_validator()
    archive = create_archive(tmp_path)
    learning = create_learning(tmp_path)
    manifest_path = archive / "change.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["archive"]["target"] = "specs/archive/wrong"
    manifest["gates"]["r2"]["reviewRecords"] = ["reviews/missing.md"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    errors = validator.validate(learning, tmp_path)

    assert any("archive target" in error for error in errors)
    assert any("review record 无法解析" in error for error in errors)


def test_store_拒绝单向_related_关系(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    first = create_learning(tmp_path, extra_frontmatter="relatedLearnings:\n  - core-problem-solution-retry")
    second = first.parent / "core-problem-solution-retry.md"
    second.write_text(
        first.read_text(encoding="utf-8").replace(
            "learningId: core-problem-solution-timeout",
            "learningId: core-problem-solution-retry",
        ).replace("relatedLearnings:\n  - core-problem-solution-retry\n", ""),
        encoding="utf-8",
    )

    errors = validator.validate_store(tmp_path)

    assert any("related 关系必须双向" in error for error in errors)


def test_lookup_只返回_active_并给出命中原因(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    active = create_learning(tmp_path)
    stale = active.parent / "core-problem-solution-old-timeout.md"
    stale.write_text(
        active.read_text(encoding="utf-8")
        .replace(
            "learningId: core-problem-solution-timeout",
            "learningId: core-problem-solution-old-timeout",
        )
        .replace("status: active", "status: stale\nstatusReason: current-code-changed"),
        encoding="utf-8",
    )

    result = validator.lookup_learnings(tmp_path, "timeout", component="core")

    assert result["status"] == "completed"
    assert [item["learningId"] for item in result["result"]["matches"]] == [
        "core-problem-solution-timeout"
    ]
    assert result["result"]["matches"][0]["matchedBy"]
    assert result["result"]["diagnostic"][0]["status"] == "stale"


def test_evidence_pack_只提取_claim_锚点附近内容(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)

    result = validator.build_evidence_pack(learning, tmp_path)

    assert result["status"] == "completed"
    assert {item["evidenceId"] for item in result["result"]["items"]} == {"EV-001", "EV-002"}
    assert result["result"]["bytes"] < validator.PACK_BYTE_LIMIT


def test_refresh_audit_只读且_plan_可检测漂移(tmp_path):
    validator = load_validator()
    create_archive(tmp_path)
    learning = create_learning(tmp_path)
    before = learning.read_bytes()

    audit = validator.audit_refresh(tmp_path)

    assert audit["status"] == "completed"
    assert learning.read_bytes() == before
    plan = audit["result"]
    plan_path = tmp_path / "refresh-plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    assert validator.verify_refresh_plan(tmp_path, plan_path)["status"] == "completed"

    learning.write_text(learning.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    checked = validator.verify_refresh_plan(tmp_path, plan_path)

    assert checked["status"] == "blocked"
    assert any("digest" in error for error in checked["result"]["errors"])


def test_cli_validate_输出稳定_json_契约(tmp_path):
    create_archive(tmp_path)
    learning = create_learning(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "validate",
            str(learning),
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    result = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert result["contractVersion"] == "1"
    assert result["status"] == "completed"
    assert result["terminal"] is True


def test_cli_lookup_在_windows_utf8_路径下可执行(tmp_path):
    create_archive(tmp_path)
    create_learning(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "lookup",
            "--repo-root",
            str(tmp_path),
            "--query",
            "超时 timeout",
            "--component",
            "core",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    result = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert result["mode"] == "lookup"
    assert result["result"]["matches"][0]["learningId"] == "core-problem-solution-timeout"


def test_discoverability_只报告_gap_不修改文件(tmp_path):
    validator = load_validator()

    missing = validator.check_discoverability(tmp_path)

    assert missing["status"] == "no-op"
    assert "discoverability-gap" in missing["reasonCodes"]
    readme = tmp_path / "README.md"
    readme.write_text("开始前检索 `docs/learnings/`。\n", encoding="utf-8")
    before = readme.read_bytes()

    found = validator.check_discoverability(tmp_path)

    assert found["status"] == "completed"
    assert found["result"]["discoveredBy"] == ["README.md"]
    assert readme.read_bytes() == before
