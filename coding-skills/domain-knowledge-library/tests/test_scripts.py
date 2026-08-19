from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


def run_script(name: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def concept(status: str = "draft", verified: str = "") -> str:
    return f"""---
type: Business Rule
title: Cancellation rule
description: Current cancellation behavior.
context: orders
view: as-is
sensitivity: internal
sources:
  - id: code-v1
    resource: git+https://example/repo.git@abc#src/order.py
    role: implementation
generated:
  by: domain-knowledge-library/test
  at: 2026-08-19T00:00:00Z
{verified}status: {status}
stale_after: 2026-08-20
---

# Rule

Paid orders can be cancelled.[^code-v1]

[^code-v1]: Fixed source
"""


class ScriptTests(unittest.TestCase):
    def test_hash_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.txt"
            source.write_text("stable\n", encoding="utf-8")
            first = json.loads(run_script("compute_source_hash.py", str(source)).stdout)
            second = json.loads(run_script("compute_source_hash.py", str(source)).stdout)
            self.assertEqual(first["digest"], second["digest"])
            self.assertEqual(first["file_count"], 1)

    def test_inventory_is_read_only_and_reports_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "src").mkdir()
            (repo / "src" / "app.py").write_text(
                "raise RuntimeError('must not execute')\n", encoding="utf-8"
            )
            result = json.loads(run_script("inventory_repository.py", str(repo)).stdout)
            self.assertEqual(result["summary"]["languages"], {"Python": 1})
            self.assertIn("runtime calls", result["limitations"]["does_not_prove"])

    def test_validate_requires_human_for_stable_business_concept(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "rule.md").write_text(concept(status="stable"), encoding="utf-8")
            result = run_script("validate_okf.py", str(root), "--json", check=False)
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "stable-business-unverified",
                {finding["code"] for finding in payload["findings"]},
            )

            (root / "rule.md").write_text(
                concept(
                    status="stable",
                    verified="verified:\n  - by: human:owner\n    at: 2026-08-19T01:00:00Z\n",
                ),
                encoding="utf-8",
            )
            valid = run_script("validate_okf.py", str(root), "--json")
            self.assertTrue(json.loads(valid.stdout)["valid"])

    def test_indexes_links_staleness_and_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rules = root / "domains" / "orders" / "rules"
            rules.mkdir(parents=True)
            target = rules / "cancel.md"
            target.write_text(concept(), encoding="utf-8")

            run_script("rebuild_indexes.py", str(root))
            run_script("rebuild_indexes.py", str(root), "--check")
            run_script("check_links.py", str(root))

            stale = run_script(
                "detect_stale.py", str(root), "--as-of", "2026-08-20", "--json"
            )
            self.assertEqual(len(json.loads(stale.stdout)["results"]), 1)

            trace = run_script("trace_sources.py", str(target))
            trace_payload = json.loads(trace.stdout)
            self.assertEqual(trace_payload["sources"][0]["id"], "code-v1")
            self.assertTrue(trace_payload["footnotes"][0]["matches_source"])


if __name__ == "__main__":
    unittest.main()
