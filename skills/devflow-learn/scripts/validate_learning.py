#!/usr/bin/env python3
"""校验 DevFlow learning 的结构、来源、引用和敏感信息。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
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
    return errors


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
        if manifest.get("archive", {}).get("status") != "archived":
            errors.append(f"source change 尚未归档：`{raw_archive}`")
        gates = manifest.get("gates", {})
        for gate in required_gates:
            gate_data = gates.get(gate, {})
            if gate_data.get("status") != "passed":
                errors.append(f"source change 的 `{gate}` gate 未通过：`{raw_archive}`")
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

    missing = source_changes - found_changes
    extra = found_changes - source_changes
    if missing:
        errors.append(f"`sourceChanges` 缺少可验证 archive：{', '.join(sorted(missing))}")
    if extra:
        errors.append(f"`sourceArchives` 包含未声明 change：{', '.join(sorted(extra))}")
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
    return [f"`canonicalRefs` 中的 `{ref}` 未在当前 canonical 中找到" for ref in refs if ref not in canonical_text]


def validate_related(repo_root: Path, data: dict[str, Any], learning_path: Path) -> list[str]:
    errors: list[str] = []
    related = data.get("relatedLearnings", [])
    if not related:
        return errors
    store = repo_root / "docs" / "learnings"
    for learning_id in related:
        matches = [path for path in store.glob(f"*/*{learning_id}.md") if path.resolve() != learning_path.resolve()]
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


def validate_body(body: str, body_start: int, learning_path: Path) -> list[str]:
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

    for target in MARKDOWN_LINK_RE.findall(body):
        if "://" in target or target.startswith(("#", "mailto:")):
            continue
        bare = target.split("#", 1)[0]
        if bare and not (learning_path.parent / bare).resolve().exists():
            errors.append(f"相对链接无法解析：`{target}`")
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
    errors.extend(validate_sources(repo_root, data))
    errors.extend(validate_canonical_refs(repo_root, data))
    errors.extend(validate_related(repo_root, data, learning_path))
    errors.extend(validate_unique_id(repo_root, data, learning_path))
    errors.extend(validate_body(body, body_start, learning_path))
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验 DevFlow learning")
    parser.add_argument("learning_path", type=Path, help="待校验的 learning Markdown")
    parser.add_argument("--repo-root", type=Path, required=True, help="Git 仓库根目录")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    errors = validate(args.learning_path, args.repo_root)
    if errors:
        print(f"DevFlow learning 校验失败：{args.learning_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"DevFlow learning 校验通过：{args.learning_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
