"""Shared helpers for Domain Knowledge hooks.

Kept dependency-free and small: hooks run on every tool call, so they must be
fast and must never crash the agent loop (callers fail open).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

HIGH_RISK_TAGS = {"security", "payment", "permission", "release", "auth", "money", "refund"}
SESSION_TTL_SECONDS = 7 * 24 * 3600

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9\-_.=]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9\-_./+]{16,}"),
    re.compile(r"(?i)\b(jdbc|mongodb|postgres(ql)?|mysql|redis)://[^\s]*:[^\s]*@"),
]
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def read_input() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def project_dir(payload: dict) -> Path:
    roots = payload.get("workspace_roots") or []
    env = os.environ.get("CURSOR_PROJECT_DIR")
    for candidate in ([env] if env else []) + list(roots) + [payload.get("cwd"), os.getcwd()]:
        if candidate:
            return Path(candidate).resolve()
    return Path.cwd().resolve()


def find_bundle_root(start: Path) -> Path | None:
    env = os.environ.get("DOMAIN_KB_ROOT")
    if env and (Path(env) / "knowledge").is_dir():
        return Path(env).resolve()
    pointer = start / ".domain-kb"
    if pointer.is_file():
        try:
            target = (start / pointer.read_text(encoding="utf-8").strip()).resolve()
            if (target / "knowledge").is_dir():
                return target
        except OSError:
            pass
    for candidate in (start / "domain-kb", start):
        if (candidate / "knowledge" / "index.md").is_file() or (candidate / ".kb").is_dir():
            return candidate.resolve()
    return None


def lock_held(bundle: Path) -> dict | None:
    path = bundle / ".kb" / "maintenance.lock"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"holder": "unknown"}


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def tool_path(tool_input: dict) -> str | None:
    for key in ("path", "file_path", "target_file", "filePath"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def resolve_path(raw: str, payload: dict) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    base = payload.get("cwd") or os.environ.get("CURSOR_PROJECT_DIR") or os.getcwd()
    return (Path(base) / path).resolve()


# --------------------------------------------------------------------------- #
# Minimal frontmatter reader (top-level scalars, inline lists, block lists)
# --------------------------------------------------------------------------- #


def read_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    result: dict = {}
    current_list_key: str | None = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:
            match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s+(.*))?$", stripped)
            if not match:
                current_list_key = None
                continue
            key, value = match.group(1), (match.group(2) or "").strip()
            value = re.sub(r"\s#.*$", "", value) if '"' not in value and "'" not in value else value
            if value == "":
                result[key] = []
                current_list_key = key
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                result[key] = [v.strip().strip("\"'") for v in inner.split(",")] if inner else []
                current_list_key = None
            else:
                result[key] = value.strip("\"'")
                current_list_key = None
        elif current_list_key and stripped.startswith("- "):
            item = stripped[2:].strip()
            if re.match(r"^[A-Za-z0-9_.-]+:(\s|$)", item):
                # list of mappings (sources, verified): hooks only need the count
                result[current_list_key].append({})
            else:
                result[current_list_key].append(item.strip("\"'"))
    return result


def concept_notice(bundle: Path, path: Path, today: dt.date | None = None) -> str | None:
    """Build the reminder injected after a knowledge/ file is read."""
    today = today or dt.date.today()
    knowledge = bundle / "knowledge"
    rel = path.resolve().relative_to(knowledge.resolve()).as_posix()
    if path.name in ("index.md", "log.md"):
        return None
    fm = read_frontmatter(path)
    if not fm:
        return None
    notes = []
    status = fm.get("status")
    tags = {str(t).lower() for t in (fm.get("tags") or []) if not isinstance(t, dict)}
    high_risk = bool(tags & HIGH_RISK_TAGS)
    if status == "draft":
        line = f"`{rel}` 是 draft（未经人确认）。引用时必须写“未确认”并给出该路径。"
        if high_risk:
            line += " 它带高风险标签，只能当候选，不得写成可执行策略、落成代码或改配置。"
        notes.append(line)
    elif status == "deprecated":
        target = fm.get("superseded_by")
        line = f"`{rel}` 已 deprecated，不参与默认回答。"
        if target:
            line += f" 替代项：`{target}`。"
        notes.append(line)
    view = fm.get("view")
    if view == "to-be":
        notes.append(f"`{rel}` 是 view: to-be（目标态），不是现状；不要与 AS-IS 混答。")
    elif view == "historical":
        notes.append(f"`{rel}` 是 view: historical，只作背景。")
    stale_after = fm.get("stale_after")
    if stale_after:
        try:
            if dt.date.fromisoformat(str(stale_after)) < today:
                notes.append(f"`{rel}` 已过 stale_after {stale_after}，先回真源核对再引用。")
        except ValueError:
            pass
    if not notes:
        return None
    return "【领域知识提醒】" + " ".join(notes) + " 发现与真源矛盾或路由错误时，写提案到 .kb/proposals/，不要直接改 knowledge/。"


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #


def session_file(bundle: Path, conversation_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", conversation_id or "unknown")[:80]
    return bundle / ".kb" / ".sessions" / f"{safe}.json"


def load_session(bundle: Path, conversation_id: str) -> dict:
    path = session_file(bundle, conversation_id)
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"reads": [], "proposals": [], "prompted": False}


def save_session(bundle: Path, conversation_id: str, state: dict) -> None:
    path = session_file(bundle, conversation_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def prune_sessions(bundle: Path) -> None:
    folder = bundle / ".kb" / ".sessions"
    if not folder.is_dir():
        return
    cutoff = time.time() - SESSION_TTL_SECONDS
    for path in folder.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            continue


def find_secrets(text: str) -> list[str]:
    hits = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern[:40])
    if EMAIL_PATTERN.search(text):
        hits.append("email address")
    return hits
