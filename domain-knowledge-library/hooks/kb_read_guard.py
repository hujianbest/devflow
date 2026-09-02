#!/usr/bin/env python3
"""postToolUse (Read): remind about draft / deprecated / stale / to-be concepts
and record which knowledge files this conversation has read."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (  # noqa: E402
    concept_notice,
    emit,
    find_bundle_root,
    is_under,
    load_session,
    project_dir,
    read_input,
    resolve_path,
    save_session,
    tool_path,
)


def main() -> None:
    payload = read_input()
    raw = tool_path(payload.get("tool_input") or {})
    if not raw:
        emit({})
        return
    bundle = find_bundle_root(project_dir(payload))
    if bundle is None:
        emit({})
        return
    target = resolve_path(raw, payload)
    knowledge = bundle / "knowledge"
    control = bundle / ".kb"

    if is_under(target, knowledge):
        conversation_id = payload.get("conversation_id") or "unknown"
        state = load_session(bundle, conversation_id)
        rel = target.resolve().relative_to(knowledge.resolve()).as_posix()
        if rel not in state["reads"] and target.name not in ("index.md", "log.md"):
            state["reads"].append(rel)
            save_session(bundle, conversation_id, state)
        notice = concept_notice(bundle, target)
        emit({"additional_context": notice} if notice else {})
        return

    if is_under(target, control) and not is_under(target, control / ".sessions"):
        rel = target.resolve().relative_to(control.resolve()).as_posix()
        emit({"additional_context": f"【领域知识提醒】`.kb/{rel}` 是控制面材料（提案 / 冲突 / 队列 / 扫描结果），可以参考，不得当正式结论引用。"})
        return

    emit({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"[kb_read_guard] {exc}\n")
        emit({})
