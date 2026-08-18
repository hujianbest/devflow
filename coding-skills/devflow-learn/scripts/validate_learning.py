#!/usr/bin/env python3
"""校验 DevFlow learning 的结构、来源、引用和敏感信息。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_DIR / "references" / "learning-schema.json"
KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*):(?:\s*(.*))?$")
ARRAY_ITEM_RE = re.compile(r"^  -(?:\s+(.*))?$")

SECRET_PATTERNS = {
    "私钥": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "认证头": re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|basic)\s+\S+"),
    "凭证赋值": re.compile(
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"']?[^<\s\"']{8,}"
    ),
    "连接串": re.compile(r"(?i)\b(?:postgres|mysql|mongodb(?:\+srv)?|redis)://[^@\s]+:[^@\s]+@"),
}
PII_PATTERNS = {
    "邮箱地址": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "内部 URL": re.compile(
        r"https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|"
        r"172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|[^/\s]+\.internal)\b",
        re.IGNORECASE,
    ),
}
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|Documents and Settings|home)[\\/]"),
    re.compile(r"(?<![\w.])/(?:Users|home)/[^/\s]+/"),
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TBD|TODO|FIXME)\b"),
    re.compile(r"\{\{[^}\n]+\}\}"),
    re.compile(r"<(?:replace|placeholder|component|topic|path|name|date)[^>\n]*>", re.IGNORECASE),
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
CLAIM_RE = re.compile(
    r"<!--\s*claim:\s*(CLM-[0-9]+);\s*kind:\s*(historical|current|guidance);"
    r"\s*evidence:\s*([A-Z0-9,-]+)\s*-->"
)
EVIDENCE_RE = re.compile(
    r"^\s*-\s*(EV-[0-9]+)\s*\|\s*"
    r"(archive|current-canonical|current-code|current-test)\s*\|\s*`([^`\n]+)`\s*$",
    re.MULTILINE,
)
SHA_RE = re.compile(r"\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
REQUIRED_HEADINGS = {
    "problem-solution": ("## 问题", "## 根因", "## 已验证方案", "## 适用范围", "## 证据"),
    "design-decision": ("## 背景与约束", "## 决策", "## 理由与后果", "## 适用范围", "## 证据"),
    "engineering-practice": ("## 触发信号", "## 做法", "## 原因", "## 适用范围", "## 证据"),
}
STORE_LIMIT = 500
CANDIDATE_LIMIT = 20
RESULT_LIMIT = 5
EVIDENCE_LIMIT = 12
PACK_BYTE_LIMIT = 64 * 1024


class FrontmatterError(ValueError):
    """Frontmatter 不符合 DevFlow learning 的受限 YAML 子集。"""


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def parse_scalar(raw: str, line_number: int) -> str:
    value = raw.strip()
    if not value:
        raise FrontmatterError(f"第 {line_number} 行：标量值不能为空")
    if value.startswith("["):
        raise FrontmatterError(f"第 {line_number} 行：数组必须使用 block 形式，禁止 flow array")
    if value.startswith(("{", "|", ">", "&", "*", "!", "@", "`")):
        raise FrontmatterError(f"第 {line_number} 行：不支持该 YAML 结构或未加引号的指示符")
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(f"第 {line_number} 行：双引号字符串无效：{exc.msg}") from exc
        if not isinstance(parsed, str):
            raise FrontmatterError(f"第 {line_number} 行：只允许字符串标量")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise FrontmatterError(f"第 {line_number} 行：单引号字符串未闭合")
        return value[1:-1].replace("''", "'")
    if " #" in value or ": " in value:
        raise FrontmatterError(f"第 {line_number} 行：值包含 YAML 歧义标点，必须加引号")
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("文件必须以独立的 `---` frontmatter 分隔行开始")

    end_index = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end_index is None:
        raise FrontmatterError("frontmatter 缺少结束分隔行 `---`")

    data: dict[str, Any] = {}
    current_array: str | None = None
    for index, line in enumerate(lines[1:end_index], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        item = ARRAY_ITEM_RE.match(line)
        if item:
            if current_array is None:
                raise FrontmatterError(f"第 {index} 行：数组项前没有数组字段")
            raw_item = item.group(1)
            if raw_item is None:
                raise FrontmatterError(f"第 {index} 行：数组项不能为空")
            data[current_array].append(parse_scalar(raw_item, index))
            continue

        if line.startswith((" ", "\t")):
            raise FrontmatterError(f"第 {index} 行：只允许两个空格缩进的字符串数组项")

        match = KEY_RE.match(line)
        if not match:
            raise FrontmatterError(f"第 {index} 行：不是有效的顶层 `key: value`")
        key, raw_value = match.groups()
        if key in data:
            raise FrontmatterError(f"第 {index} 行：字段 `{key}` 重复")

        if not raw_value:
            data[key] = []
            current_array = key
        else:
            data[key] = parse_scalar(raw_value, index)
            current_array = None

    body_start = end_index + 2
    body = "\n".join(lines[end_index + 1 :])
    return data, body, body_start


def validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(schema["required"])
    properties = schema["properties"]

    for key in sorted(required - data.keys()):
        errors.append(f"缺少必需字段 `{key}`")
    for key in sorted(data.keys() - properties.keys()):
        errors.append(f"不允许的字段 `{key}`")

    for key, value in data.items():
        rules = properties.get(key)
        if not rules:
            continue
        if "const" in rules and value != rules["const"]:
            errors.append(f"`{key}` 必须是 `{rules['const']}`")
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"`{key}` 必须是 {', '.join(rules['enum'])} 之一")

        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"`{key}` 必须是字符串")
            continue
        if expected_type == "array" and not isinstance(value, list):
            errors.append(f"`{key}` 必须是 block array")
            continue

        if isinstance(value, str):
            if len(value) < rules.get("minLength", 0):
                errors.append(f"`{key}` 长度不足")
            if len(value) > rules.get("maxLength", sys.maxsize):
                errors.append(f"`{key}` 长度超过限制")
            pattern = rules.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                errors.append(f"`{key}` 的值 `{value}` 不符合格式")

        if isinstance(value, list):
            if len(value) < rules.get("minItems", 0):
                errors.append(f"`{key}` 至少需要 {rules['minItems']} 项")
            if len(value) > rules.get("maxItems", sys.maxsize):
                errors.append(f"`{key}` 最多允许 {rules['maxItems']} 项")
            if rules.get("uniqueItems") and len(value) != len(set(value)):
                errors.append(f"`{key}` 包含重复项")
            item_rules = rules.get("items", {})
            for item in value:
                if not isinstance(item, str):
                    errors.append(f"`{key}` 的数组项必须是字符串")
                    continue
                pattern = item_rules.get("pattern")
                if pattern and not re.fullmatch(pattern, item):
                    errors.append(f"`{key}` 的数组项 `{item}` 不符合格式")
                if len(item) < item_rules.get("minLength", 0):
                    errors.append(f"`{key}` 的数组项不能为空")
                if len(item) > item_rules.get("maxLength", sys.maxsize):
                    errors.append(f"`{key}` 的数组项 `{item}` 长度超过限制")

    learning_id = data.get("learningId")
    related = data.get("relatedLearnings", [])
    superseded_by = data.get("supersededBy", [])
    if learning_id in related:
        errors.append("`relatedLearnings` 禁止自引用")
    if learning_id in superseded_by:
        errors.append("`supersededBy` 禁止自引用")
    if data.get("status") == "superseded" and not superseded_by:
        errors.append("`status: superseded` 时必须提供 `supersededBy`")
    if data.get("status") != "superseded" and superseded_by:
        errors.append("只有 `status: superseded` 才能提供 `supersededBy`")
    if data.get("status") in {"stale", "superseded"} and not data.get("statusReason"):
        errors.append("`stale` 或 `superseded` 必须提供 `statusReason`")
    return errors


def resolve_repo_path(repo_root: Path, raw_path: str) -> Path | None:
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None
    return resolved


def validate_location(
    learning_path: Path, repo_root: Path, data: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    try:
        relative = learning_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return ["learning 文件不在指定仓库内"]

    if data.get("learningId") and learning_path.stem != data["learningId"]:
        errors.append("文件名必须与 `learningId` 完全一致")

    expected_category = schema["categoryMapping"].get(data.get("learningType"))
    if expected_category and relative.parent.as_posix() != f"docs/learnings/{expected_category}":
        errors.append(
            f"`learningType: {data.get('learningType')}` 必须位于 "
            f"`docs/learnings/{expected_category}/`"
        )
    return errors


def validate_dates(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    parsed: dict[str, date] = {}
    for key in ("capturedAt", "lastVerifiedAt"):
        value = data.get(key)
        if not isinstance(value, str):
            continue
        try:
            parsed[key] = date.fromisoformat(value)
        except ValueError:
            errors.append(f"`{key}` 不是有效日期：{value}")
    if parsed.get("lastVerifiedAt") and parsed.get("capturedAt"):
        if parsed["lastVerifiedAt"] < parsed["capturedAt"]:
            errors.append("`lastVerifiedAt` 不能早于 `capturedAt`")
    today = date.today()
    for key, value in parsed.items():
        if value > today:
            errors.append(f"`{key}` 不能是未来日期")
    return errors


def resolve_record_path(archive: Path, repo_root: Path, raw: str) -> Path | None:
    locator = raw.split("::", 1)[0].split("#", 1)[0].strip("` ")
    if not locator or not ("/" in locator or Path(locator).suffix):
        return None
    archive_candidate = (archive / locator).resolve()
    if archive_candidate.exists():
        return archive_candidate
    return resolve_repo_path(repo_root, locator)


def validate_sources(repo_root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source_changes = set(data.get("sourceChanges", []))
    found_changes: set[str] = set()
    required_gates = ("r1", "r2", "r3", "canonicalSync", "closeout")

    for raw_archive in data.get("sourceArchives", []):
        archive = resolve_repo_path(repo_root, raw_archive)
        if archive is None:
            errors.append(f"source archive 不是安全的仓库相对路径：`{raw_archive}`")
            continue
        manifest_path = archive / "change.json"
        if not manifest_path.is_file():
            errors.append(f"source archive 缺少 `change.json`：`{raw_archive}`")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"无法解析 `{raw_archive}/change.json`：{exc}")
            continue

        change_id = manifest.get("changeId")
        topic = manifest.get("topic")
        change_identity = f"{change_id}-{topic}" if change_id and topic else ""
        if change_identity:
            found_changes.add(change_identity)
            if not archive.name.endswith(f"-{change_identity}"):
                errors.append(f"archive 目录名与 change 身份不一致：`{raw_archive}`")
        if manifest.get("archive", {}).get("status") != "archived":
            errors.append(f"source change 尚未归档：`{raw_archive}`")
        archive_state = manifest.get("archive", {})
        expected_targets = {raw_archive}
        component_root = data.get("componentRoot")
        if isinstance(component_root, str) and component_root != ".":
            prefix = component_root.rstrip("/") + "/"
            if raw_archive.startswith(prefix):
                expected_targets.add(raw_archive[len(prefix) :])
        if archive_state.get("target") not in expected_targets:
            errors.append(f"archive target 与真实路径不一致：`{raw_archive}`")
        if not archive_state.get("confirmedBy"):
            errors.append(f"source archive 缺少确认人：`{raw_archive}`")
        archived_at = archive_state.get("archivedAt")
        if not archived_at:
            errors.append(f"source archive 缺少归档时间：`{raw_archive}`")
        else:
            try:
                archived_date = datetime.fromisoformat(str(archived_at).replace("Z", "+00:00")).date()
                captured_at = data.get("capturedAt")
                if isinstance(captured_at, str) and date.fromisoformat(captured_at) < archived_date:
                    errors.append(f"`capturedAt` 早于 source archive 归档时间：`{raw_archive}`")
            except ValueError:
                errors.append(f"source archive 的 `archivedAt` 无效：`{raw_archive}`")

        required_artifacts = (
            "srs.md",
            "delta-spec.md",
            "delta-design.md",
            "tasks.md",
            "traceability.md",
            "reviews",
            "closeout.md",
        )
        for artifact in required_artifacts:
            if not (archive / artifact).exists():
                errors.append(f"source archive 缺少必需工件 `{artifact}`：`{raw_archive}`")
        artifact_contract = {
            "srs": "srs.md",
            "deltaSpec": "delta-spec.md",
            "deltaDesign": "delta-design.md",
            "tasks": "tasks.md",
            "traceability": "traceability.md",
            "reviews": "reviews/",
            "closeout": "closeout.md",
        }
        manifest_artifacts = manifest.get("artifacts", {})
        for key, expected_path in artifact_contract.items():
            artifact_data = manifest_artifacts.get(key, {})
            if artifact_data.get("path") != expected_path:
                errors.append(f"source change 的 artifact `{key}` 路径无效：`{raw_archive}`")
            if artifact_data.get("status") != "archived":
                errors.append(f"source change 的 artifact `{key}` 未标为 archived：`{raw_archive}`")

        gates = manifest.get("gates", {})
        for gate in required_gates:
            gate_data = gates.get(gate, {})
            if gate_data.get("status") != "passed":
                errors.append(f"source change 的 `{gate}` gate 未通过：`{raw_archive}`")
            evidence = gate_data.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"source change 的 `{gate}` gate 缺少 evidence：`{raw_archive}`")
            else:
                resolved_any = False
                for item in evidence:
                    raw_item = str(item)
                    resolved_evidence = resolve_record_path(archive, repo_root, raw_item)
                    if resolved_evidence is not None and resolved_evidence.exists():
                        resolved_any = True
                    if ("/" in raw_item or re.search(r"\.(?:md|json|txt)(?:#|::|$)", raw_item)) and (
                        resolved_evidence is None or not resolved_evidence.exists()
                    ):
                        errors.append(
                            f"source change 的 `{gate}` evidence 无法解析：`{raw_item}`"
                        )
                if not resolved_any:
                    errors.append(f"source change 的 `{gate}` gate 没有可定位 evidence：`{raw_archive}`")
                if gate == "closeout" and not any(
                    resolve_record_path(archive, repo_root, str(item))
                    == (archive / "closeout.md").resolve()
                    for item in evidence
                ):
                    errors.append(f"source change 的 closeout evidence 未指向 `closeout.md`：`{raw_archive}`")
            review_records = gate_data.get("reviewRecords")
            if gate != "closeout":
                if not isinstance(review_records, list) or not review_records:
                    errors.append(f"source change 的 `{gate}` gate 缺少 review record：`{raw_archive}`")
                else:
                    for record in review_records:
                        resolved_record = resolve_record_path(archive, repo_root, str(record))
                        if resolved_record is None or not resolved_record.is_file():
                            errors.append(
                                f"source change 的 `{gate}` review record 无法解析：`{record}`"
                            )
            elif review_records not in ([], None):
                errors.append(f"source change 的 closeout reviewRecords 必须为空：`{raw_archive}`")
        for gate in ("canonicalSync", "closeout"):
            if gates.get(gate, {}).get("humanConfirmation") != "confirmed":
                errors.append(f"source change 的 `{gate}` 缺少人工确认：`{raw_archive}`")
        closeout_path = archive / "closeout.md"
        if not closeout_path.is_file():
            errors.append(f"source archive 缺少 `closeout.md`：`{raw_archive}`")
        else:
            closeout = closeout_path.read_text(encoding="utf-8", errors="ignore")
            if any(pattern.search(closeout) for pattern in PLACEHOLDER_PATTERNS):
                errors.append(f"source archive 的 `closeout.md` 仍有占位符：`{raw_archive}`")
        if data.get("component") != manifest.get("component"):
            errors.append(f"`component` 与 `{raw_archive}/change.json` 不一致")
        manifest_root = manifest.get("componentRoot")
        if data.get("componentRoot") != manifest_root:
            errors.append(f"`componentRoot` 与 `{raw_archive}/change.json` 不一致")
        root = repo_root if manifest_root == "." else resolve_repo_path(repo_root, str(manifest_root))
        if root is not None and archive.parent.resolve() != (root / "specs" / "archive").resolve():
            errors.append(f"source archive 不在声明组件的 `specs/archive/`：`{raw_archive}`")
        if root is not None and change_identity:
            active_change = root / "specs" / "changes" / change_identity
            if active_change.exists():
                errors.append(f"source change 仍同时存在于活动目录：`{active_change}`")

    missing = source_changes - found_changes
    extra = found_changes - source_changes
    if missing:
        errors.append(f"`sourceChanges` 缺少可验证 archive：{', '.join(sorted(missing))}")
    if extra:
        errors.append(f"`sourceArchives` 包含未声明 change：{', '.join(sorted(extra))}")
    if len(data.get("sourceArchives", [])) != len(data.get("sourceChanges", [])):
        errors.append("`sourceChanges` 与 `sourceArchives` 必须一一对应")
    return errors


def validate_canonical_refs(repo_root: Path, data: dict[str, Any]) -> list[str]:
    refs = data.get("canonicalRefs", [])
    if not refs:
        return []
    component_root = data.get("componentRoot")
    if not isinstance(component_root, str):
        return []
    root = repo_root if component_root == "." else resolve_repo_path(repo_root, component_root)
    if root is None:
        return ["`componentRoot` 不是安全的仓库相对路径"]
    canonical_text = ""
    for name in ("spec.md", "design.md"):
        path = root / "specs" / name
        if path.is_file():
            canonical_text += path.read_text(encoding="utf-8", errors="ignore")
    return [
        f"`canonicalRefs` 中的 `{ref}` 未在当前 canonical 中找到"
        for ref in refs
        if not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(ref)}(?![A-Za-z0-9_-])", canonical_text)
    ]


def validate_related(repo_root: Path, data: dict[str, Any], learning_path: Path) -> list[str]:
    errors: list[str] = []
    related = list(data.get("relatedLearnings", [])) + list(data.get("supersededBy", []))
    store = repo_root / "docs" / "learnings"
    for learning_id in related:
        matches = [
            path
            for path in store.glob("*/*.md")
            if path.stem == learning_id and path.resolve() != learning_path.resolve()
        ]
        if not any(path.stem == learning_id for path in matches):
            errors.append(f"related learning 不存在：`{learning_id}`")
    return errors


def validate_unique_id(repo_root: Path, data: dict[str, Any], learning_path: Path) -> list[str]:
    learning_id = data.get("learningId")
    if not isinstance(learning_id, str):
        return []
    matches = [
        path
        for path in (repo_root / "docs" / "learnings").glob(f"*/*.md")
        if path.stem == learning_id and path.resolve() != learning_path.resolve()
    ]
    return [f"`learningId` 重复，已存在：`{path.relative_to(repo_root).as_posix()}`" for path in matches]


def resolve_locator(repo_root: Path, raw_locator: str) -> tuple[Path | None, str | None]:
    if "::" not in raw_locator:
        return None, None
    raw_path, anchor = raw_locator.split("::", 1)
    if not anchor.strip():
        return None, None
    return resolve_repo_path(repo_root, raw_path.strip()), anchor.strip()


def validate_claims(body: str, repo_root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    claims: dict[str, tuple[str, list[str]]] = {}
    evidence: dict[str, tuple[str, str]] = {}

    for match in CLAIM_RE.finditer(body):
        claim_id, kind, raw_refs = match.groups()
        refs = [item for item in raw_refs.split(",") if item]
        if claim_id in claims:
            errors.append(f"claim ID 重复：`{claim_id}`")
        claims[claim_id] = (kind, refs)
    for match in EVIDENCE_RE.finditer(body):
        evidence_id, kind, locator = match.groups()
        if evidence_id in evidence:
            errors.append(f"evidence ID 重复：`{evidence_id}`")
        evidence[evidence_id] = (kind, locator)

    if not claims:
        errors.append("正文至少需要一个 `<!-- claim: ... -->` 声明")
    if not evidence:
        errors.append("`## 证据` 至少需要一条结构化 evidence")

    source_archives = [str(item).rstrip("/") + "/" for item in data.get("sourceArchives", [])]
    for evidence_id, (kind, locator) in evidence.items():
        path, anchor = resolve_locator(repo_root, locator)
        raw_path = locator.split("::", 1)[0]
        if path is None or anchor is None:
            errors.append(f"`{evidence_id}` locator 必须是安全的 `repo/path::anchor`")
            continue
        if kind == "archive" and not any(raw_path.startswith(prefix) for prefix in source_archives):
            errors.append(f"`{evidence_id}` 的 archive locator 不在 `sourceArchives` 内")
        if kind != "archive" and any(raw_path.startswith(prefix) for prefix in source_archives):
            errors.append(f"`{evidence_id}` 的 current locator 不能指向 source archive")
        if kind == "current-canonical" and not raw_path.endswith(("specs/spec.md", "specs/design.md")):
            errors.append(f"`{evidence_id}` 的 current-canonical 必须指向当前 spec/design")
        if path is None or not path.is_file():
            errors.append(f"`{evidence_id}` locator 文件不存在：`{raw_path}`")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        count = text.count(anchor)
        if count == 0:
            errors.append(f"`{evidence_id}` anchor 不存在：`{anchor}`")
        elif count > 1:
            errors.append(f"`{evidence_id}` anchor 不唯一：`{anchor}`")

    referenced: set[str] = set()
    for claim_id, (kind, refs) in claims.items():
        if not refs:
            errors.append(f"`{claim_id}` 至少需要一个 evidence")
            continue
        missing = [ref for ref in refs if ref not in evidence]
        for ref in missing:
            errors.append(f"`{claim_id}` 引用了不存在的 evidence：`{ref}`")
        resolved = [evidence[ref][0] for ref in refs if ref in evidence]
        referenced.update(ref for ref in refs if ref in evidence)
        if kind == "historical" and any(item != "archive" for item in resolved):
            errors.append(f"`{claim_id}` historical claim 只能引用 archive evidence")
        if kind == "current" and resolved and not any(item.startswith("current-") for item in resolved):
            errors.append(f"`{claim_id}` current claim 至少需要一项 current evidence")

    for evidence_id in sorted(evidence.keys() - referenced):
        errors.append(f"evidence 未被任何 claim 使用：`{evidence_id}`")
    return errors


def validate_body(
    body: str,
    body_start: int,
    learning_path: Path,
    repo_root: Path,
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    def line_for(match: re.Match[str]) -> int:
        return body_start + body.count("\n", 0, match.start())

    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(body):
            errors.append(f"第 {line_for(match)} 行存在未清理占位符：`{match.group(0)}`")
    for label, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(body):
            errors.append(f"第 {line_for(match)} 行疑似包含{label}，禁止写入 learning")
    for label, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(body):
            errors.append(f"第 {line_for(match)} 行疑似包含{label}，请脱敏或确认仓库策略")
    for pattern in ABSOLUTE_PATH_PATTERNS:
        for match in pattern.finditer(body):
            errors.append(f"第 {line_for(match)} 行包含机器绝对路径：`{match.group(0)}`")
    for match in SHA_RE.finditer(body):
        errors.append(f"第 {line_for(match)} 行包含不稳定的 commit SHA：`{match.group(0)}`")

    for target in MARKDOWN_LINK_RE.findall(body):
        if "://" in target or target.startswith(("#", "mailto:")):
            continue
        bare = target.split("#", 1)[0]
        if bare and not (learning_path.parent / bare).resolve().exists():
            errors.append(f"相对链接无法解析：`{target}`")
    for heading in REQUIRED_HEADINGS.get(data.get("learningType"), ()):
        if heading not in body:
            errors.append(f"正文缺少必需章节 `{heading}`")

    evidence_locators = {match.group(3) for match in EVIDENCE_RE.finditer(body)}
    for match in BACKTICK_RE.finditer(body):
        raw_token = match.group(1)
        if raw_token in evidence_locators:
            continue
        token = raw_token.split("::", 1)[0].split("#", 1)[0]
        if (
            "/" not in token
            or token.startswith(("http://", "https://", "/", "~"))
            or any(char in token for char in "<>{}*$")
            or "path/to" in token
        ):
            continue
        path = resolve_repo_path(repo_root, token)
        if path is not None and path.exists():
            continue
        line_start = body.rfind("\n", 0, match.start()) + 1
        line_end = body.find("\n", match.end())
        line = body[line_start : line_end if line_end >= 0 else len(body)]
        if re.search(r"历史|已删除|移除|重命名|pre-fix|removed|renamed", line, re.IGNORECASE):
            continue
        errors.append(f"第 {line_for(match)} 行引用的仓库路径不存在：`{token}`")

    errors.extend(validate_claims(body, repo_root, data))
    return errors


def validate_metadata_sensitivity(data: dict[str, Any]) -> list[str]:
    text = json.dumps(data, ensure_ascii=False)
    errors: list[str] = []
    for label, pattern in {**SECRET_PATTERNS, **PII_PATTERNS}.items():
        if pattern.search(text):
            errors.append(f"frontmatter 疑似包含{label}，请移除或脱敏")
    for pattern in ABSOLUTE_PATH_PATTERNS:
        if pattern.search(text):
            errors.append("frontmatter 包含机器绝对路径")
    return errors


def validate(learning_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    if not learning_path.is_file():
        return [f"learning 文件不存在：{learning_path}"]
    if not repo_root.is_dir():
        return [f"仓库根不存在：{repo_root}"]

    schema = load_schema()
    try:
        text = learning_path.read_text(encoding="utf-8")
        data, body, body_start = parse_frontmatter(text)
    except (OSError, UnicodeDecodeError, FrontmatterError) as exc:
        return [str(exc)]

    errors.extend(validate_schema(data, schema))
    errors.extend(validate_location(learning_path, repo_root, data, schema))
    errors.extend(validate_dates(data))
    if data.get("sensitivity") == "restricted":
        errors.append("`sensitivity: restricted` 的内容禁止写入仓库 learning store")
    errors.extend(validate_metadata_sensitivity(data))
    errors.extend(validate_sources(repo_root, data))
    errors.extend(validate_canonical_refs(repo_root, data))
    errors.extend(validate_related(repo_root, data, learning_path))
    errors.extend(validate_unique_id(repo_root, data, learning_path))
    errors.extend(validate_body(body, body_start, learning_path, repo_root, data))
    return errors


def iter_learning_paths(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "docs" / "learnings").glob("*/*.md"))


def read_learning(path: Path) -> tuple[dict[str, Any], str]:
    data, body, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    return data, body


def validate_store(repo_root: Path) -> list[str]:
    errors: list[str] = []
    store = repo_root / "docs" / "learnings"
    paths = iter_learning_paths(repo_root)
    if len(paths) > STORE_LIMIT:
        return [f"learning 数量超过 {STORE_LIMIT}，store 校验被截断"]
    if paths:
        if not (store / "README.md").is_file():
            errors.append("learning store 缺少 `docs/learnings/README.md`")
        for category in ("problem-solutions", "design-decisions", "engineering-practices"):
            if not (store / category).is_dir():
                errors.append(f"learning store 缺少固定目录 `{category}/`")

    by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in paths:
        for error in validate(path, repo_root):
            errors.append(f"{path.relative_to(repo_root).as_posix()}: {error}")
        try:
            data, _ = read_learning(path)
        except (OSError, FrontmatterError, UnicodeDecodeError) as exc:
            errors.append(f"{path.relative_to(repo_root).as_posix()}: {exc}")
            continue
        learning_id = data.get("learningId")
        if isinstance(learning_id, str):
            if learning_id in by_id:
                errors.append(f"learning ID 重复：`{learning_id}`")
            by_id[learning_id] = (path, data)

    for learning_id, (_, data) in by_id.items():
        for related in data.get("relatedLearnings", []):
            target = by_id.get(related)
            if target and learning_id not in target[1].get("relatedLearnings", []):
                errors.append(f"related 关系必须双向：`{learning_id}` ↔ `{related}`")

    graph = {
        learning_id: [target for target in data.get("supersededBy", []) if target in by_id]
        for learning_id, (_, data) in by_id.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node: str) -> None:
        if node in visiting:
            errors.append(f"supersession 存在环：`{node}`")
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, []):
            walk(target)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        walk(node)
    return errors


def result_envelope(mode: str, status: str, result: Any, reason_codes: list[str] | None = None) -> dict[str, Any]:
    return {
        "contractVersion": "1",
        "mode": mode,
        "status": status,
        "terminal": True,
        "reasonCodes": reason_codes or [],
        "writeSet": [],
        "result": result,
    }


def query_terms(raw: str) -> list[str]:
    return sorted(set(re.findall(r"[A-Za-z0-9_.-]+|[\u4e00-\u9fff]{2,}", raw.lower())))


def lookup_learnings(
    repo_root: Path,
    query: str,
    component: str | None = None,
    component_root: str | None = None,
    learning_type: str | None = None,
) -> dict[str, Any]:
    paths = iter_learning_paths(repo_root)
    if len(paths) > STORE_LIMIT:
        return result_envelope(
            "lookup",
            "truncated",
            {"matches": [], "scanned": STORE_LIMIT},
            ["store-limit"],
        )

    terms = query_terms(query)
    records: list[tuple[Path, dict[str, Any], str]] = []
    for path in paths:
        try:
            data, body = read_learning(path)
        except (OSError, FrontmatterError, UnicodeDecodeError):
            continue
        records.append((path, data, body))

    def metadata_score(data: dict[str, Any]) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []
        if component and data.get("component") == component:
            score += 5
            reasons.append("component")
        if component_root and data.get("componentRoot") == component_root:
            score += 5
            reasons.append("componentRoot")
        if learning_type and data.get("learningType") == learning_type:
            score += 3
            reasons.append("learningType")
        metadata = json.dumps(data, ensure_ascii=False).lower()
        for term in terms:
            if term in metadata:
                score += 2
                reasons.append(f"metadata:{term}")
        return score, reasons

    active: list[tuple[int, Path, dict[str, Any], str, list[str]]] = []
    diagnostic: list[dict[str, str]] = []
    for path, data, body in records:
        score, reasons = metadata_score(data)
        if data.get("status") != "active":
            if score > 0:
                diagnostic.append(
                    {
                        "learningId": str(data.get("learningId", path.stem)),
                        "status": str(data.get("status")),
                        "reason": "元数据命中但不能作为当前指导",
                    }
                )
            continue
        if score > 0:
            active.append((score, path, data, body, reasons))

    if len(active) < 3 and terms:
        known_paths = {item[1] for item in active}
        for path, data, body in records:
            if data.get("status") != "active" or path in known_paths:
                continue
            body_lower = body.lower()
            hits = [term for term in terms if term in body_lower]
            if hits:
                active.append((len(hits), path, data, body, [f"body:{term}" for term in hits]))

    status = "completed"
    reasons: list[str] = []
    if len(active) > CANDIDATE_LIMIT:
        status = "truncated"
        reasons.append("candidate-limit")
    active.sort(key=lambda item: (-item[0], str(item[2].get("learningId", item[1].stem))))
    selected = active[:RESULT_LIMIT]
    selected_ids = {str(item[2].get("learningId", item[1].stem)) for item in selected}
    by_id = {
        str(data.get("learningId", path.stem)): (path, data, body)
        for path, data, body in records
    }
    for parent in list(selected):
        if len(selected) >= RESULT_LIMIT:
            break
        parent_id = str(parent[2].get("learningId", parent[1].stem))
        for related_id in parent[2].get("relatedLearnings", [])[:8]:
            related = by_id.get(related_id)
            if (
                related is None
                or related_id in selected_ids
                or related[1].get("status") != "active"
            ):
                continue
            selected.append(
                (
                    max(parent[0] - 1, 0),
                    related[0],
                    related[1],
                    related[2],
                    [f"related:{parent_id}"],
                )
            )
            selected_ids.add(related_id)
            if len(selected) >= RESULT_LIMIT:
                break
    matches = [
        {
            "learningId": item[2].get("learningId", item[1].stem),
            "path": item[1].relative_to(repo_root).as_posix(),
            "score": item[0],
            "matchedBy": item[4],
            "learningType": item[2].get("learningType"),
            "component": item[2].get("component"),
        }
        for item in selected
    ]
    if not matches and status == "completed":
        status = "no-op"
        reasons.append("no-match")
    return result_envelope(
        "lookup",
        status,
        {"matches": matches, "diagnostic": diagnostic[:RESULT_LIMIT], "scanned": len(records)},
        reasons,
    )


def build_evidence_pack(learning_path: Path, repo_root: Path) -> dict[str, Any]:
    try:
        data, body = read_learning(learning_path)
    except (OSError, FrontmatterError, UnicodeDecodeError) as exc:
        return result_envelope("pack", "invalid", {"errors": [str(exc)]}, ["invalid-learning"])
    items: list[dict[str, Any]] = []
    total_bytes = 0
    for match in list(EVIDENCE_RE.finditer(body))[:EVIDENCE_LIMIT]:
        evidence_id, kind, locator = match.groups()
        path, anchor = resolve_locator(repo_root, locator)
        if path is None or anchor is None or not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        indexes = [index for index, line in enumerate(lines) if anchor in line]
        if len(indexes) != 1:
            continue
        index = indexes[0]
        excerpt = "\n".join(lines[max(0, index - 2) : min(len(lines), index + 3)])
        encoded = excerpt.encode("utf-8")
        if total_bytes + len(encoded) > PACK_BYTE_LIMIT:
            return result_envelope(
                "pack",
                "truncated",
                {"items": items, "bytes": total_bytes},
                ["pack-byte-limit"],
            )
        if any(pattern.search(excerpt) for pattern in (*SECRET_PATTERNS.values(), *PII_PATTERNS.values())):
            return result_envelope(
                "pack",
                "blocked",
                {"evidenceId": evidence_id},
                ["sensitive-evidence"],
            )
        total_bytes += len(encoded)
        items.append(
            {
                "evidenceId": evidence_id,
                "kind": kind,
                "locator": locator,
                "excerpt": excerpt,
            }
        )
    status = "completed" if items else "no-op"
    return result_envelope(
        "pack",
        status,
        {"learningId": data.get("learningId"), "items": items, "bytes": total_bytes},
        [] if items else ["no-resolvable-evidence"],
    )


def check_discoverability(repo_root: Path) -> dict[str, Any]:
    instruction_files = [
        path
        for path in (
            repo_root / "AGENTS.md",
            repo_root / "CLAUDE.md",
            repo_root / "README.md",
            repo_root / "README.zh-CN.md",
        )
        if path.is_file()
    ]
    discovered_by: list[str] = []
    for path in instruction_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "docs/learnings/" in text or "devflow-learn" in text:
            discovered_by.append(path.relative_to(repo_root).as_posix())
    status = "completed" if discovered_by else "no-op"
    reasons = [] if discovered_by else ["discoverability-gap"]
    return result_envelope(
        "discoverability",
        status,
        {
            "discoveredBy": discovered_by,
            "recommendation": (
                None
                if discovered_by
                else "在显式初始化或配置流程中加入 docs/learnings/ 的用途和检索时机；capture 不自动修改指令文件。"
            ),
        },
        reasons,
    )


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def store_digest(paths: list[Path], repo_root: Path) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(repo_root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def audit_refresh(repo_root: Path) -> dict[str, Any]:
    paths = iter_learning_paths(repo_root)
    if len(paths) > STORE_LIMIT:
        return result_envelope(
            "refresh-audit",
            "truncated",
            {"actions": [], "scanned": STORE_LIMIT},
            ["store-limit"],
        )
    actions: list[dict[str, Any]] = []
    write_set: list[str] = []
    for path in paths:
        relative = path.relative_to(repo_root).as_posix()
        try:
            data, _ = read_learning(path)
            errors = validate(path, repo_root)
        except (OSError, FrontmatterError, UnicodeDecodeError) as exc:
            data = {}
            errors = [str(exc)]
        action = "keep"
        if data.get("schemaVersion") != "1.1":
            action = "manual-rewrite-required"
        elif any("related" in error for error in errors):
            action = "repair-related"
        elif any(
            token in error
            for error in errors
            for token in ("locator 文件不存在", "anchor 不存在", "current claim")
        ):
            action = "mark-stale"
        elif errors:
            action = "manual-rewrite-required"
        if action != "keep":
            write_set.append(relative)
        actions.append(
            {
                "path": relative,
                "learningId": data.get("learningId", path.stem),
                "action": action,
                "beforeDigest": file_digest(path),
                "reasons": errors,
            }
        )
    plan: dict[str, Any] = {
        "storeDigest": store_digest(paths, repo_root),
        "actions": actions,
        "writeSet": sorted(write_set),
    }
    plan["planId"] = hashlib.sha256(
        json.dumps(plan, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    envelope = result_envelope("refresh-audit", "completed", plan)
    envelope["writeSet"] = plan["writeSet"]
    return envelope


def verify_refresh_plan(repo_root: Path, plan_path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return result_envelope("refresh-plan-check", "invalid", {"errors": [str(exc)]})
    current_paths = iter_learning_paths(repo_root)
    errors: list[str] = []
    if plan.get("storeDigest") != store_digest(current_paths, repo_root):
        errors.append("store digest 已变化，必须重新审计")
    declared_write_set = set(plan.get("writeSet", []))
    for action in plan.get("actions", []):
        relative = action.get("path")
        if not isinstance(relative, str):
            errors.append("plan action 缺少 path")
            continue
        path = resolve_repo_path(repo_root, relative)
        if path is None or not path.is_file():
            errors.append(f"plan 文件不存在：`{relative}`")
            continue
        if action.get("beforeDigest") != file_digest(path):
            errors.append(f"before digest 已变化：`{relative}`")
        if action.get("action") != "keep" and relative not in declared_write_set:
            errors.append(f"非 keep action 未进入 writeSet：`{relative}`")
    status = "completed" if not errors else "blocked"
    return result_envelope("refresh-plan-check", status, {"errors": errors}, [] if not errors else ["plan-drift"])


def parse_args(argv: list[str]) -> argparse.Namespace:
    commands = {
        "validate",
        "validate-store",
        "lookup",
        "pack",
        "discoverability",
        "refresh-audit",
        "refresh-plan-check",
    }
    if argv and argv[0] not in commands and not argv[0].startswith("-"):
        argv = ["validate", *argv]
    parser = argparse.ArgumentParser(description="校验和检索 DevFlow learning")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="校验单份 learning")
    validate_parser.add_argument("learning_path", type=Path)
    validate_parser.add_argument("--repo-root", type=Path, required=True)
    validate_parser.add_argument("--format", choices=("text", "json"), default="text")

    store_parser = subparsers.add_parser("validate-store", help="校验整个 learning store")
    store_parser.add_argument("--repo-root", type=Path, required=True)
    store_parser.add_argument("--format", choices=("text", "json"), default="text")

    lookup_parser = subparsers.add_parser("lookup", help="有界检索 active learning")
    lookup_parser.add_argument("--repo-root", type=Path, required=True)
    lookup_parser.add_argument("--query", required=True)
    lookup_parser.add_argument("--component")
    lookup_parser.add_argument("--component-root")
    lookup_parser.add_argument("--learning-type")

    pack_parser = subparsers.add_parser("pack", help="构造窄 evidence pack")
    pack_parser.add_argument("learning_path", type=Path)
    pack_parser.add_argument("--repo-root", type=Path, required=True)

    discoverability_parser = subparsers.add_parser(
        "discoverability", help="只读检查普通 Agent 和人能否发现 learning store"
    )
    discoverability_parser.add_argument("--repo-root", type=Path, required=True)

    audit_parser = subparsers.add_parser("refresh-audit", help="只读审计 learning store")
    audit_parser.add_argument("--repo-root", type=Path, required=True)

    plan_parser = subparsers.add_parser("refresh-plan-check", help="检查 refresh plan 是否仍可应用")
    plan_parser.add_argument("--repo-root", type=Path, required=True)
    plan_parser.add_argument("--plan", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "validate":
        errors = validate(args.learning_path, args.repo_root)
        if args.format == "json":
            print(
                json.dumps(
                    result_envelope(
                        "validate",
                        "completed" if not errors else "invalid",
                        {"errors": errors},
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif errors:
            print(f"DevFlow learning 校验失败：{args.learning_path}", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        else:
            print(f"DevFlow learning 校验通过：{args.learning_path}")
        return 0 if not errors else 1
    if args.command == "validate-store":
        errors = validate_store(args.repo_root)
        if args.format == "json":
            print(
                json.dumps(
                    result_envelope(
                        "validate-store",
                        "completed" if not errors else "invalid",
                        {"errors": errors},
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for error in errors:
                print(error, file=sys.stderr)
            if not errors:
                print("DevFlow learning store 校验通过")
        return 0 if not errors else 1
    if args.command == "lookup":
        result = lookup_learnings(
            args.repo_root,
            args.query,
            args.component,
            args.component_root,
            args.learning_type,
        )
    elif args.command == "pack":
        result = build_evidence_pack(args.learning_path, args.repo_root)
    elif args.command == "discoverability":
        result = check_discoverability(args.repo_root)
    elif args.command == "refresh-audit":
        result = audit_refresh(args.repo_root)
    else:
        result = verify_refresh_plan(args.repo_root, args.plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"completed", "no-op", "truncated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
