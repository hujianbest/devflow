"""Tests for domain-knowledge-library/domain-knowledge-maintain/scripts/kb.py.

Runnable with either `python3 -m unittest` or pytest.
"""

import datetime as dt
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "domain-knowledge-library" / "domain-knowledge-maintain" / "scripts" / "kb.py"


def load_kb():
    spec = importlib.util.spec_from_file_location("kb", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kb = load_kb()

RULE_STABLE = """---
type: Business Rule
title: 已发货订单取消规则
description: 描述订单发货后的取消限制和例外。
tags: [order, cancellation]
context: order-fulfillment
view: as-is
owner: team:order-platform
sources:
  - id: cancel-service
    resource: git+https://example/order.git@abc123#src/CancelService.java
    role: implementation
verified:
  - by: human:order-domain-owner
    at: 2026-08-19T17:00:00Z
status: stable
stale_after: {stale_after}
---

# 定义
Observed  已发货订单原则上不能直接取消。见 [overview](../overview.md)。
"""

CONTEXT_DRAFT = """---
type: Bounded Context
title: 订单履约
description: 订单从支付完成到签收的履约上下文。
context: order-fulfillment
view: as-is
owner: team:order-platform
sources:
  - id: repo
    resource: git+https://example/order.git@abc123
    role: implementation
generated:
  by: domain-kb-agent/test
  at: 2026-09-03T00:00:00Z
status: draft
---

# 边界
Inferred  按命名聚类推断。
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class BundleCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.bundle = self.tmp / "bundle"
        (self.bundle / "knowledge").mkdir(parents=True)
        kb.run_init(self.bundle, "demo")
        self.ctx = self.bundle / "knowledge" / "domains" / "order-fulfillment"
        write(self.ctx / "overview.md", CONTEXT_DRAFT)
        write(self.ctx / "rules" / "shipped-order-cancel.md", RULE_STABLE.format(stale_after="2099-01-01"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def validate(self, **kwargs):
        return kb.run_validate(self.bundle, **kwargs)


class TestFrontmatterParser(unittest.TestCase):
    def test_parses_nested_lists_and_maps(self):
        fm = kb.parse_yaml_subset(
            "type: Business Rule\ntags: [a, b]\napplies_to:\n  systems: [x]\n"
            "sources:\n  - id: s\n    resource: git+https://e/r.git@1#f\n    role: implementation\n"
            "verified:\n  - by: human:owner\n    at: 2026-01-01T00:00:00Z\nstatus: stable\n"
        )
        self.assertEqual(fm["type"], "Business Rule")
        self.assertEqual(fm["tags"], ["a", "b"])
        self.assertEqual(fm["applies_to"]["systems"], ["x"])
        self.assertEqual(fm["sources"][0]["role"], "implementation")
        self.assertEqual(fm["sources"][0]["resource"], "git+https://e/r.git@1#f")
        self.assertEqual(fm["verified"][0]["by"], "human:owner")

    def test_rejects_unterminated_frontmatter(self):
        with self.assertRaises(kb.ParseError):
            kb.split_frontmatter("---\ntype: X\n")


class TestValidate(BundleCase):
    def test_valid_bundle_has_no_errors(self):
        errors, warnings, concepts = self.validate()
        self.assertEqual(errors, [])
        self.assertEqual(len(concepts), 2)

    def test_missing_required_field_is_error(self):
        write(self.ctx / "rules" / "broken.md", CONTEXT_DRAFT.replace("owner: team:order-platform\n", ""))
        errors, _, _ = self.validate()
        self.assertTrue(any("missing required field `owner`" in e for e in errors))

    def test_stable_business_type_requires_human_verifier(self):
        text = RULE_STABLE.format(stale_after="2099-01-01").replace("human:order-domain-owner", "tool:tree-sitter")
        write(self.ctx / "rules" / "shipped-order-cancel.md", text)
        errors, _, _ = self.validate()
        self.assertTrue(any("requires a `human:` verifier" in e for e in errors))

    def test_generated_without_verified_cannot_be_stable(self):
        write(self.ctx / "overview.md", CONTEXT_DRAFT.replace("status: draft", "status: stable"))
        errors, _, _ = self.validate()
        self.assertTrue(any("stable requires non-empty `verified`" in e for e in errors))

    def test_detail_type_requires_expanded_by(self):
        endpoint = CONTEXT_DRAFT.replace("type: Bounded Context", "type: API Endpoint").replace("context: order-fulfillment", "context: system:order-core")
        write(self.bundle / "knowledge" / "systems" / "order-core" / "interfaces" / "post-cancel.md", endpoint)
        errors, _, _ = self.validate()
        self.assertTrue(any("requires `expanded_by`" in e for e in errors))
        write(
            self.bundle / "knowledge" / "systems" / "order-core" / "interfaces" / "post-cancel.md",
            endpoint.replace("status: draft", "status: draft\nexpanded_by: domain-knowledge-expand"),
        )
        errors, _, _ = self.validate()
        self.assertFalse(any("expanded_by" in e for e in errors))

    def test_git_source_must_pin_revision(self):
        write(self.ctx / "overview.md", CONTEXT_DRAFT.replace("order.git@abc123", "order.git"))
        errors, _, _ = self.validate()
        self.assertTrue(any("pin a revision" in e for e in errors))

    def test_broken_link_and_bad_filename(self):
        write(self.ctx / "rules" / "Bad_Name.md", CONTEXT_DRAFT.replace("[overview](../overview.md)", "[x](../missing.md)"))
        errors, _, _ = self.validate()
        self.assertTrue(any("kebab-case" in e for e in errors))

    def test_stale_after_past_is_warning_not_error(self):
        write(self.ctx / "rules" / "shipped-order-cancel.md", RULE_STABLE.format(stale_after="2000-01-01"))
        errors, warnings, _ = self.validate()
        self.assertEqual(errors, [])
        self.assertTrue(any("past stale_after" in w for w in warnings))
        report = kb.run_stale(self.bundle)
        self.assertEqual(len(report["stale"]), 1)
        self.assertEqual(report["by_status"]["stable"], 1)

    def test_supersession_cycle_detected(self):
        a = CONTEXT_DRAFT.replace("status: draft", "status: deprecated\nsuperseded_by: domains/order-fulfillment/rules/b.md")
        b = CONTEXT_DRAFT.replace("status: draft", "status: deprecated\nsuperseded_by: domains/order-fulfillment/rules/a.md")
        write(self.ctx / "rules" / "a.md", a)
        write(self.ctx / "rules" / "b.md", b)
        errors, _, _ = self.validate()
        self.assertTrue(any("superseded_by cycle" in e for e in errors))


class TestIndex(BundleCase):
    def test_index_generated_and_checked(self):
        kb.run_index(self.bundle)
        root_index = (self.bundle / "knowledge" / "index.md").read_text(encoding="utf-8")
        self.assertIn("domains/order-fulfillment/rules/shipped-order-cancel.md", root_index)
        self.assertIn("draft 1 · stable 1", root_index)
        self.assertTrue((self.ctx / "index.md").is_file())
        errors, _, _ = self.validate(check_index=True)
        self.assertEqual(errors, [])
        write(self.ctx / "rules" / "another.md", RULE_STABLE.format(stale_after="2099-01-01"))
        errors, _, _ = self.validate(check_index=True)
        self.assertTrue(any("out of date" in e for e in errors))

    def test_generated_index_is_not_validated_as_concept(self):
        kb.run_index(self.bundle)
        errors, _, concepts = self.validate()
        self.assertEqual(errors, [])
        self.assertNotIn("index.md", " ".join(concepts))


class TestProposals(BundleCase):
    def write_proposal(self, name: str, kind: str, body: str = "Observed  something\n", concepts="[domains/order-fulfillment/overview.md]"):
        return write(
            self.bundle / ".kb" / "proposals" / name,
            f"---\nkind: {kind}\nconcepts: {concepts}\ncontext: order-fulfillment\ntask: t\n"
            "sources:\n  - resource: git+https://e/r.git@1#f\n    role: implementation\n"
            "submitted_by: agent:test\nsubmitted_at: 2026-09-03T00:00:00Z\n---\n\n## 发现\n" + body,
        )

    def test_valid_proposal_and_queue(self):
        self.write_proposal("2026-09-03-a.md", "refine")
        self.write_proposal("2026-09-03-b.md", "route-error")
        items, errors = kb.run_proposals(self.bundle, queue=True)
        self.assertEqual(errors, [])
        self.assertEqual(len(items), 2)
        queued = {i["file"] for i in items if i["queued"]}
        self.assertEqual(queued, {"2026-09-03-b.md"})
        self.assertTrue((self.bundle / ".kb" / "review-queue" / "2026-09-03-b.md").is_file())

    def test_invalid_kind_missing_concepts_and_unmarked_claims(self):
        self.write_proposal("2026-09-03-c.md", "opinion", body="just text\n", concepts="[]")
        _, errors = kb.run_proposals(self.bundle)
        joined = " ".join(errors)
        self.assertIn("invalid kind", joined)
        self.assertIn("must list affected concepts", joined)
        self.assertIn("Observed/Derived/Confirmed/Inferred", joined)

    def test_unknown_concept_is_error(self):
        self.write_proposal("2026-09-03-d.md", "stale", concepts="[domains/nope.md]")
        _, errors = kb.run_proposals(self.bundle)
        self.assertTrue(any("concept not found" in e for e in errors))


class TestMaintenance(BundleCase):
    def test_lock_unlock_and_audit(self):
        kb.run_lock(self.bundle, "ingest", "tester")
        self.assertEqual(kb.read_lock(self.bundle)["holder"], "tester")
        kb.run_index(self.bundle)
        report, ok = kb.run_audit(self.bundle)
        self.assertTrue(ok)
        text = report.read_text(encoding="utf-8")
        self.assertIn("Maintenance lock: held by tester", text)
        self.assertIn("Concepts: 2", text)
        self.assertTrue(kb.run_unlock(self.bundle))
        self.assertFalse(kb.run_unlock(self.bundle))
        log = (self.bundle / "knowledge" / "log.md").read_text(encoding="utf-8")
        self.assertIn("audit |", log)

    def test_init_scaffolds_control_plane(self):
        for relative in (".kb/config.yaml", ".kb/proposals", ".kb/review-queue", ".kb/.sessions", "AGENTS.md", "knowledge/index.md", "knowledge/log.md"):
            self.assertTrue((self.bundle / relative).exists(), relative)
        self.assertIn("expand:", (self.bundle / ".kb" / "config.yaml").read_text(encoding="utf-8"))

    def test_inventory_finds_build_roots_and_contracts(self):
        repo = self.tmp / "repo"
        write(repo / "pom.xml", "<project/>")
        write(repo / "api" / "openapi.yaml", "openapi: 3.0.0")
        write(repo / "src" / "main" / "java" / "Application.java", "class Application {}")
        write(repo / "db" / "migrations" / "V1__init.sql", "create table t(id int);")
        write(repo / "node_modules" / "x" / "index.js", "ignored")
        result = kb.run_inventory(repo, self.bundle, name="demo-repo")
        self.assertIn("pom.xml", result["build_roots"])
        self.assertIn("api/openapi.yaml", result["contracts"])
        self.assertIn("db/migrations", result["migrations"])
        self.assertEqual(result["languages"].get("java"), 1)
        self.assertNotIn("javascript", result["languages"])
        self.assertTrue((self.bundle / ".kb" / "inventory" / "demo-repo.json").is_file())

    def test_find_bundle_root_via_pointer(self):
        project = self.tmp / "project"
        project.mkdir()
        (project / ".domain-kb").write_text("../bundle\n", encoding="utf-8")
        self.assertEqual(kb.find_bundle_root(project), self.bundle.resolve())


if __name__ == "__main__":
    unittest.main()
