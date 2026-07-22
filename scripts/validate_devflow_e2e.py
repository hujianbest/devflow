#!/usr/bin/env python3
"""Validate DevFlow lifecycle eval definitions and grade an agent run."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = ROOT / "skills" / "using-devflow" / "evals" / "e2e.json"
INTERACTIONS_PATH = (
    ROOT
    / "skills"
    / "using-devflow"
    / "evals"
    / "fixtures"
    / "devflow-lifecycle"
    / "interactions.json"
)
REQUIRED_SCENARIO_FIELDS = {
    "id",
    "name",
    "changeId",
    "topic",
    "componentRoot",
    "componentMode",
    "executionMode",
    "profile",
    "prompt",
    "oracle",
    "expected",
}
REQUIRED_CHANGE_FILES = {
    "change.json",
    "srs.md",
    "delta-spec.md",
    "delta-design.md",
    "tasks.md",
    "traceability.md",
    "closeout.md",
}
REQUIRED_ARTIFACT_KEYS = {
    "canonicalSpec",
    "canonicalDesign",
    "srs",
    "deltaSpec",
    "deltaDesign",
    "tasks",
    "traceability",
    "reviews",
    "closeout",
}
REQUIRED_GATES = {
    "baselinePreflight",
    "r1",
    "r2",
    "r3",
    "canonicalSync",
    "closeout",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_suite(eval_path: Path = EVAL_PATH) -> dict[str, Any]:
    data = read_json(eval_path)
    if not isinstance(data, dict):
        raise ValueError(f"{eval_path}: root must be an object")
    return data


def scenarios_by_id(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = suite.get("scenarios")
    if not isinstance(scenarios, list):
        return {}
    return {
        item["id"]: item
        for item in scenarios
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def validate_definitions(
    eval_path: Path = EVAL_PATH,
    interactions_path: Path = INTERACTIONS_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        suite = load_suite(eval_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    if suite.get("schemaVersion") != "1.0":
        errors.append(f"{eval_path}: schemaVersion must be 1.0")
    if suite.get("skill") != "using-devflow":
        errors.append(f"{eval_path}: skill must be using-devflow")

    scenarios = suite.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 2:
        errors.append(f"{eval_path}: exactly two scenarios are required")
        scenarios = []

    seen_ids: set[str] = set()
    for index, scenario in enumerate(scenarios):
        label = f"{eval_path}: scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_SCENARIO_FIELDS - scenario.keys()
        if missing:
            errors.append(f"{label} missing fields: {sorted(missing)}")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
        elif scenario_id in seen_ids:
            errors.append(f"{label}.id duplicates {scenario_id}")
        else:
            seen_ids.add(scenario_id)
        if scenario.get("componentMode") not in {"existing", "new"}:
            errors.append(f"{label}.componentMode must be existing or new")
        if scenario.get("executionMode") not in {"attended", "unattended"}:
            errors.append(f"{label}.executionMode must be attended or unattended")
        if not isinstance(scenario.get("prompt"), str) or not scenario["prompt"].strip():
            errors.append(f"{label}.prompt must be non-empty")
        expected = scenario.get("expected")
        if not isinstance(expected, list) or not expected:
            errors.append(f"{label}.expected must be a non-empty list")
        profile = scenario.get("profile")
        if not isinstance(profile, dict):
            errors.append(f"{label}.profile must be an object")
        else:
            for field in (
                "name",
                "risk",
                "reasons",
                "requiredEvidence",
                "requiredReviewers",
            ):
                if not profile.get(field):
                    errors.append(f"{label}.profile.{field} must be non-empty")
        oracle = scenario.get("oracle")
        if isinstance(oracle, str) and not (eval_path.parent / oracle).is_file():
            errors.append(f"{label}.oracle does not exist: {oracle}")

    fixture = suite.get("fixture")
    fixture_root = eval_path.parent / fixture if isinstance(fixture, str) else None
    if fixture_root is None or not fixture_root.is_dir():
        errors.append(f"{eval_path}: fixture directory does not exist")
    else:
        notifications = fixture_root / "components" / "notifications"
        if not notifications.is_dir():
            errors.append(f"{fixture_root}: existing notifications component is missing")
        if (notifications / "specs").exists():
            errors.append(f"{notifications}: existing fixture must not contain canonical specs")
        if (fixture_root / "components" / "rate_limiter").exists():
            errors.append(f"{fixture_root}: new rate_limiter component must be absent")

    try:
        interactions = read_json(interactions_path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    else:
        scripted = interactions.get("scenarios", {})
        if not isinstance(scripted, dict) or set(scripted) != seen_ids:
            errors.append(
                f"{interactions_path}: interaction scenarios must exactly match eval IDs"
            )
        else:
            for scenario_id, checkpoints in scripted.items():
                if not isinstance(checkpoints, list) or not checkpoints:
                    errors.append(
                        f"{interactions_path}: {scenario_id} needs scripted checkpoints"
                    )
                    continue
                names = {
                    item.get("checkpoint")
                    for item in checkpoints
                    if isinstance(item, dict)
                }
                expected_names = {"final-canonical-and-archive-confirmation"}
                if scenario_id.startswith("existing-"):
                    expected_names.add("baseline-init-confirmation")
                if names != expected_names:
                    errors.append(
                        f"{interactions_path}: {scenario_id} checkpoints are {sorted(names)}"
                    )
                for item in checkpoints:
                    if not isinstance(item, dict):
                        continue
                    if not item.get("deliverOnlyAfter") or not item.get("response"):
                        errors.append(
                            f"{interactions_path}: {scenario_id} checkpoint is incomplete"
                        )

    return errors


def add_result(
    results: list[dict[str, Any]], text: str, passed: bool, evidence: str
) -> None:
    results.append({"text": text, "passed": bool(passed), "evidence": evidence})


def run_command(command: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def run_oracle(
    scenario: dict[str, Any], eval_path: Path, repo: Path
) -> tuple[bool, str]:
    oracle = (eval_path.parent / scenario["oracle"]).resolve()
    try:
        completed = run_command([sys.executable, str(oracle), str(repo)], cwd=repo)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"oracle could not run: {exc}"
    output = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    evidence = f"exit={completed.returncode}"
    if output:
        evidence = f"{evidence}; {output[-3000:]}"
    return completed.returncode == 0, evidence


def git_changed_paths(repo: Path, seed_revision: str) -> tuple[list[str], str]:
    try:
        completed = run_command(
            ["git", "diff", "--name-only", seed_revision, "--"], cwd=repo
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"git diff could not run: {exc}"
    paths = [line.strip().replace("\\", "/") for line in completed.stdout.splitlines()]
    return [path for path in paths if path], completed.stderr.strip()


def find_change_root(
    component_root: Path, change_id: str, topic: str
) -> tuple[Path | None, list[Path], Path]:
    active = component_root / "specs" / "changes" / f"{change_id}-{topic}"
    archive_parent = component_root / "specs" / "archive"
    archives = (
        sorted(archive_parent.glob(f"????-??-??-{change_id}-{topic}"))
        if archive_parent.is_dir()
        else []
    )
    if len(archives) == 1:
        return archives[0], archives, active
    if active.is_dir():
        return active, archives, active
    return None, archives, active


def text_has_frontmatter_value(text: str, key: str, value: str) -> bool:
    pattern = rf"(?m)^\s*{re.escape(key)}\s*:\s*[\"']?{re.escape(value)}[\"']?\s*$"
    return re.search(pattern, text) is not None


def no_unresolved_placeholders(paths: list[Path]) -> tuple[bool, str]:
    offenders: list[str] = []
    patterns = (
        re.compile(r"TBD\("),
        re.compile(r"<(?:change|component|revision|topic|path|date)[^>]*>", re.I),
    )
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in patterns):
            offenders.append(path.name)
    return not offenders, f"placeholder files: {offenders or 'none'}"


def grade_run(
    scenario_id: str,
    repo: Path,
    run_dir: Path,
    seed_revision: str,
    eval_path: Path = EVAL_PATH,
) -> dict[str, Any]:
    suite = load_suite(eval_path)
    scenario = scenarios_by_id(suite).get(scenario_id)
    if scenario is None:
        raise ValueError(f"unknown scenario: {scenario_id}")

    repo = repo.resolve()
    run_dir = run_dir.resolve()
    component = repo / Path(scenario["componentRoot"])
    results: list[dict[str, Any]] = []

    oracle_passed, oracle_evidence = run_oracle(scenario, eval_path, repo)
    add_result(
        results,
        "Functional acceptance oracle passes",
        oracle_passed,
        oracle_evidence,
    )

    changed_paths, git_error = git_changed_paths(repo, seed_revision)
    component_prefix = scenario["componentRoot"].rstrip("/") + "/"
    scope_ok = bool(changed_paths) and all(
        path == scenario["componentRoot"] or path.startswith(component_prefix)
        for path in changed_paths
    )
    add_result(
        results,
        "All implementation and delivery changes stay inside the declared component",
        scope_ok,
        f"changed={changed_paths}; git_error={git_error or 'none'}",
    )

    change_root, archives, active = find_change_root(
        component, scenario["changeId"], scenario["topic"]
    )
    archive_ok = (
        len(archives) == 1
        and change_root == archives[0]
        and not active.exists()
    )
    add_result(
        results,
        "The complete AR is archived once and no active copy remains",
        archive_ok,
        f"archives={[str(path.relative_to(repo)) for path in archives]}; "
        f"active_exists={active.exists()}",
    )

    manifest: dict[str, Any] = {}
    if change_root is not None and (change_root / "change.json").is_file():
        try:
            manifest = read_json(change_root / "change.json")
        except (OSError, json.JSONDecodeError) as exc:
            manifest_error = str(exc)
        else:
            manifest_error = ""
    else:
        manifest_error = "change.json not found"

    identity_ok = bool(manifest) and all(
        (
            manifest.get("changeId") == scenario["changeId"],
            manifest.get("topic") == scenario["topic"],
            manifest.get("componentRoot") == scenario["componentRoot"],
            manifest.get("componentMode") == scenario["componentMode"],
            manifest.get("executionMode") == scenario["executionMode"],
            manifest.get("baseRevision") == seed_revision,
        )
    )
    identity = {
        key: manifest.get(key)
        for key in (
            "changeId",
            "topic",
            "componentRoot",
            "componentMode",
            "executionMode",
            "baseRevision",
        )
    }
    add_result(
        results,
        "change.json preserves scenario identity and the immutable seed revision",
        identity_ok,
        f"manifest_error={manifest_error or 'none'}; identity={identity}",
    )

    topology_ok = change_root is not None and all(
        (change_root / relative).is_file() for relative in REQUIRED_CHANGE_FILES
    )
    topology_ok = topology_ok and (change_root / "reviews").is_dir()
    add_result(
        results,
        "The archived change contains the complete fixed artifact topology",
        topology_ok,
        f"change_root={change_root}; required={sorted(REQUIRED_CHANGE_FILES)}",
    )

    artifacts = manifest.get("artifacts", {}) if isinstance(manifest, dict) else {}
    gates = manifest.get("gates", {}) if isinstance(manifest, dict) else {}
    artifact_keys_ok = isinstance(artifacts, dict) and REQUIRED_ARTIFACT_KEYS <= set(
        artifacts
    )
    change_artifacts_ok = artifact_keys_ok and all(
        node.get("status") == "archived"
        for key, node in artifacts.items()
        if isinstance(node, dict) and node.get("scope") == "change"
    )
    canonical_artifacts_ok = artifact_keys_ok and all(
        isinstance(artifacts.get(key), dict)
        and artifacts[key].get("status") == "baseline-ready"
        for key in ("canonicalSpec", "canonicalDesign")
    )
    gates_ok = isinstance(gates, dict) and REQUIRED_GATES <= set(gates) and all(
        isinstance(gates.get(key), dict) and gates[key].get("status") == "passed"
        for key in REQUIRED_GATES
    )
    archive_state = manifest.get("archive", {}) if isinstance(manifest, dict) else {}
    state_ok = (
        change_artifacts_ok
        and canonical_artifacts_ok
        and gates_ok
        and isinstance(archive_state, dict)
        and archive_state.get("status") == "archived"
    )
    add_result(
        results,
        "Artifact, gate, and archive states match the completed filesystem state",
        state_ok,
        f"artifact_keys_ok={artifact_keys_ok}; change_artifacts_ok={change_artifacts_ok}; "
        f"canonical_artifacts_ok={canonical_artifacts_ok}; gates_ok={gates_ok}; "
        f"archive_status={archive_state.get('status') if isinstance(archive_state, dict) else None}",
    )

    reviews = change_root / "reviews" if change_root else Path()
    review_names = (
        sorted(path.name for path in reviews.glob("*.md")) if reviews.is_dir() else []
    )
    required_review_prefixes = (
        "r1-review-",
        "r2-review-",
        "r3-review-",
        "canonical-sync-review-",
    )
    reviews_ok = all(
        any(name.startswith(prefix) for name in review_names)
        for prefix in required_review_prefixes
    )
    review_gate_links_ok = bool(gates) and all(
        isinstance(gates.get(key), dict) and bool(gates[key].get("reviewRecords"))
        for key in ("r1", "r2", "r3", "canonicalSync")
    )
    add_result(
        results,
        "Independent R1, R2, R3, and canonical-sync reviews are persisted and linked",
        reviews_ok and review_gate_links_ok,
        f"reviews={review_names}; gate_links={review_gate_links_ok}",
    )

    tasks_path = change_root / "tasks.md" if change_root else Path()
    trace_path = change_root / "traceability.md" if change_root else Path()
    r3_paths = list(reviews.glob("r3-review-*.md")) if reviews.is_dir() else []
    tasks_text = (
        tasks_path.read_text(encoding="utf-8", errors="replace")
        if tasks_path.is_file()
        else ""
    )
    trace_text = (
        trace_path.read_text(encoding="utf-8", errors="replace")
        if trace_path.is_file()
        else ""
    )
    r3_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in r3_paths
    )
    tdd_ok = all(token in tasks_text.upper() for token in ("RED", "GREEN", "REFACTOR"))
    tdd_ok = tdd_ok and "done" in tasks_text.lower()
    trace_ok = bool(trace_text) and "TBD(" not in trace_text and "Evidence" in trace_text
    mutation_ok = "mutation" in r3_text.lower()
    add_result(
        results,
        "TDD, final-suite, mutation, and end-to-end traceability evidence are complete",
        tdd_ok and trace_ok and mutation_ok,
        f"tdd_tokens={tdd_ok}; trace_complete={trace_ok}; mutation_recorded={mutation_ok}",
    )

    canonical_paths = [component / "specs" / "spec.md", component / "specs" / "design.md"]
    canonical_texts = [
        path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        for path in canonical_paths
    ]
    canonical_ok = all(canonical_texts) and all(
        text_has_frontmatter_value(text, "baselineStatus", "baseline-ready")
        and text_has_frontmatter_value(text, "baselineRevision", seed_revision)
        and text_has_frontmatter_value(
            text, "baselineChange", f"{scenario['changeId']}-{scenario['topic']}"
        )
        and text_has_frontmatter_value(text, "provenanceMethod", "canonical-sync")
        and "passed" in text
        and "confirmed" in text
        for text in canonical_texts
    )
    add_result(
        results,
        "Canonical spec and design are confirmed baseline-ready canonical-sync results",
        canonical_ok,
        f"canonical_files={[path.is_file() for path in canonical_paths]}",
    )

    artifact_paths = (
        [path for path in change_root.rglob("*") if path.is_file()]
        if change_root is not None
        else []
    )
    placeholder_ok, placeholder_evidence = no_unresolved_placeholders(
        artifact_paths + canonical_paths
    )
    add_result(
        results,
        "No stage-owned TBD or template placeholder remains",
        placeholder_ok and bool(artifact_paths),
        placeholder_evidence,
    )

    checkpoints = run_dir / "checkpoints"
    if scenario["componentMode"] == "existing":
        baseline_reviews = [
            name for name in review_names if name.startswith("baseline-init-review-")
        ]
        baseline_gate = gates.get("baselinePreflight", {}) if gates else {}
        baseline_linked = isinstance(baseline_gate, dict) and any(
            "baseline-init-review-" in str(item)
            for item in baseline_gate.get("reviewRecords", [])
        )
        init_diff_path = checkpoints / "baseline-init.diff"
        init_diff = (
            init_diff_path.read_text(encoding="utf-8", errors="replace")
            if init_diff_path.is_file()
            else ""
        )
        changed_in_checkpoint = re.findall(r"(?m)^\+\+\+ b/(.+)$", init_diff)
        init_scope_ok = bool(init_diff) and all(
            path.startswith(f"{scenario['componentRoot']}/specs/")
            for path in changed_in_checkpoint
            if path != "/dev/null"
        )
        route_ok = bool(baseline_reviews) and baseline_linked and init_scope_ok
        route_evidence = (
            f"baseline_reviews={baseline_reviews}; linked={baseline_linked}; "
            f"checkpoint_paths={changed_in_checkpoint}; checkpoint_exists={init_diff_path.is_file()}"
        )
        route_text = (
            "Existing mode is proven to run reviewed init before feature work without "
            "changing implementation files"
        )
    else:
        baseline_reviews = [
            name for name in review_names if name.startswith("baseline-init-review-")
        ]
        delta_spec = (
            (change_root / "delta-spec.md").read_text(encoding="utf-8", errors="replace")
            if change_root and (change_root / "delta-spec.md").is_file()
            else ""
        )
        delta_design = (
            (change_root / "delta-design.md").read_text(
                encoding="utf-8", errors="replace"
            )
            if change_root and (change_root / "delta-design.md").is_file()
            else ""
        )
        pre_sync_tree_path = checkpoints / "pre-sync-tree.txt"
        pre_sync_tree = (
            pre_sync_tree_path.read_text(encoding="utf-8", errors="replace")
            if pre_sync_tree_path.is_file()
            else ""
        )
        canonical_absent_pre_sync = (
            pre_sync_tree_path.is_file()
            and f"{scenario['componentRoot']}/specs/spec.md" not in pre_sync_tree
            and f"{scenario['componentRoot']}/specs/design.md" not in pre_sync_tree
        )
        empty_added = all(
            "EMPTY" in text and "ADDED" in text for text in (delta_spec, delta_design)
        )
        route_ok = (
            not baseline_reviews
            and empty_added
            and canonical_absent_pre_sync
            and all("devflow-init" not in text for text in canonical_texts)
        )
        route_evidence = (
            f"baseline_reviews={baseline_reviews}; empty_added={empty_added}; "
            f"pre_sync_checkpoint={pre_sync_tree_path.is_file()}; "
            f"canonical_absent_pre_sync={canonical_absent_pre_sync}"
        )
        route_text = (
            "New mode is proven to skip init, use EMPTY ADDED deltas, and defer first "
            "canonical documents until sync"
        )
    add_result(results, route_text, route_ok, route_evidence)

    passed = sum(1 for result in results if result["passed"])
    grading = {
        "expectations": results,
        "summary": {
            "passed": passed,
            "failed": len(results) - passed,
            "total": len(results),
            "pass_rate": passed / len(results) if results else 0.0,
        },
    }
    return grading


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-definitions",
        action="store_true",
        help="validate only the committed eval definitions and fixture",
    )
    parser.add_argument("--scenario", help="scenario ID to grade")
    parser.add_argument("--repo", type=Path, help="completed evaluation repository")
    parser.add_argument("--run-dir", type=Path, help="configuration run directory")
    parser.add_argument(
        "--seed-revision",
        help="immutable revision recorded when the sandbox was created",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="grading JSON path; defaults to <run-dir>/grading.json",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return non-zero when any run expectation fails",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    definition_errors = validate_definitions()
    if definition_errors:
        for error in definition_errors:
            print(error, file=sys.stderr)
        return 1
    if args.check_definitions or not args.scenario:
        print("DevFlow E2E definitions passed")
        return 0

    if args.repo is None or args.run_dir is None or not args.seed_revision:
        print(
            "--scenario requires --repo, --run-dir, and --seed-revision",
            file=sys.stderr,
        )
        return 2

    try:
        grading = grade_run(
            args.scenario, args.repo, args.run_dir, args.seed_revision
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = args.output or args.run_dir / "grading.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(grading, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = grading["summary"]
    print(
        f"{args.scenario}: {summary['passed']}/{summary['total']} "
        f"({summary['pass_rate']:.0%})"
    )
    return 1 if args.strict and summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
