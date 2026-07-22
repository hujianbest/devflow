import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_devflow_e2e.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_devflow_e2e", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_e2e_definitions_are_valid():
    validator = load_validator()

    assert validator.validate_definitions() == []


def test_fixture_starts_with_only_the_existing_component():
    validator = load_validator()
    suite = validator.load_suite()
    fixture = validator.EVAL_PATH.parent / suite["fixture"]

    assert (fixture / "components" / "notifications").is_dir()
    assert not (fixture / "components" / "notifications" / "specs").exists()
    assert not (fixture / "components" / "rate_limiter").exists()


def test_existing_fixture_suite_is_green():
    validator = load_validator()
    suite = validator.load_suite()
    component = (
        validator.EVAL_PATH.parent
        / suite["fixture"]
        / "components"
        / "notifications"
    )

    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=component,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_duplicate_scenario_id_is_rejected(tmp_path):
    validator = load_validator()
    suite = validator.load_suite()
    suite["scenarios"][1]["id"] = suite["scenarios"][0]["id"]
    eval_path = tmp_path / "evals" / "e2e.json"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(json.dumps(suite), encoding="utf-8")

    errors = validator.validate_definitions(
        eval_path=eval_path,
        interactions_path=validator.INTERACTIONS_PATH,
    )

    assert any("duplicates" in error for error in errors)


def test_seed_run_fails_delivery_checks_without_agent_work(tmp_path):
    validator = load_validator()
    suite = validator.load_suite()
    fixture = validator.EVAL_PATH.parent / suite["fixture"]
    repo = tmp_path / "repo"
    shutil.copytree(fixture, repo)
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    grading = validator.grade_run(
        "existing-notifications-init-to-ship",
        repo,
        run_dir,
        "seed-revision",
    )

    assert grading["summary"]["failed"] > 0
    assert not next(
        item
        for item in grading["expectations"]
        if item["text"].startswith("Existing mode is proven")
    )["passed"]


def test_frontmatter_value_match_is_exact():
    validator = load_validator()
    text = "---\nbaselineStatus: baseline-ready\n---\n"

    assert validator.text_has_frontmatter_value(
        text, "baselineStatus", "baseline-ready"
    )
    assert not validator.text_has_frontmatter_value(text, "baselineStatus", "draft")
