#!/usr/bin/env python3
"""preToolUse (Write / StrReplace / Edit / Delete): protect the Bundle.

- knowledge/**        : only writable while .kb/maintenance.lock is held
- .kb/proposals/**    : always writable by task agents, but secrets / PII are denied
- other .kb/**        : only writable while the lock is held
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (  # noqa: E402
    emit,
    find_bundle_root,
    find_secrets,
    is_under,
    load_session,
    lock_held,
    project_dir,
    read_input,
    resolve_path,
    save_session,
    tool_path,
)

ALLOW = {"permission": "allow"}


def deny(user: str, agent: str) -> dict:
    return {"permission": "deny", "user_message": user, "agent_message": agent}


def written_text(tool_input: dict) -> str:
    parts = []
    for key in ("contents", "content", "new_string", "text"):
        value = tool_input.get(key)
        if isinstance(value, str):
            parts.append(value)
    return "\n".join(parts)


def main() -> None:
    payload = read_input()
    tool_input = payload.get("tool_input") or {}
    raw = tool_path(tool_input)
    if not raw:
        emit(ALLOW)
        return
    bundle = find_bundle_root(project_dir(payload))
    if bundle is None:
        emit(ALLOW)
        return
    target = resolve_path(raw, payload)
    knowledge = bundle / "knowledge"
    control = bundle / ".kb"
    lock = lock_held(bundle)

    if is_under(target, knowledge):
        if lock:
            emit(ALLOW)
            return
        emit(
            deny(
                "领域知识 Bundle 的 knowledge/ 只能由维护流程写入。",
                "你正在直接修改 knowledge/，但没有维护锁。任务 Agent 不改 knowledge/：把这个发现写成提案到 "
                ".kb/proposals/<YYYY-MM-DD>-<slug>.md（kind: conflict | refine | new | route-error | stale，见 using-domain-knowledge）。"
                "如果你确实在执行 domain-knowledge-maintain / expand，先运行 `kb.py lock <mode>`。",
            )
        )
        return

    if is_under(target, control):
        if is_under(target, control / ".sessions"):
            emit(ALLOW)
            return
        if is_under(target, control / "proposals"):
            hits = find_secrets(written_text(tool_input))
            if hits:
                emit(
                    deny(
                        "提案中包含疑似密钥或个人信息，已拦截。",
                        f"提案不得包含密钥、token、连接串、邮箱等（命中：{', '.join(hits)}）。删除后重写；只保留结论、证据锚点与来源。",
                    )
                )
                return
            conversation_id = payload.get("conversation_id") or "unknown"
            state = load_session(bundle, conversation_id)
            rel = target.resolve().relative_to(control.resolve()).as_posix()
            if rel not in state["proposals"]:
                state["proposals"].append(rel)
                save_session(bundle, conversation_id, state)
            emit(ALLOW)
            return
        if lock:
            emit(ALLOW)
            return
        emit(
            deny(
                ".kb/ 控制面只能由维护流程写入（提案除外）。",
                "任务 Agent 只能写 .kb/proposals/。冲突记录、审核队列、来源登记由 domain-knowledge-maintain 在持有维护锁时写入。",
            )
        )
        return

    emit(ALLOW)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"[kb_write_guard] {exc}\n")
        emit(ALLOW)
