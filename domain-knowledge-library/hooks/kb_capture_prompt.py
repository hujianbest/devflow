#!/usr/bin/env python3
"""stop: if this conversation read knowledge/ but wrote no proposal, ask once
whether anything needs to be written back (capture loop ③)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import emit, find_bundle_root, load_session, lock_held, project_dir, read_input, save_session  # noqa: E402


def main() -> None:
    payload = read_input()
    if payload.get("status") != "completed" or int(payload.get("loop_count") or 0) > 0:
        emit({})
        return
    bundle = find_bundle_root(project_dir(payload))
    if bundle is None or lock_held(bundle):
        emit({})
        return
    conversation_id = payload.get("conversation_id") or "unknown"
    state = load_session(bundle, conversation_id)
    if not state.get("reads") or state.get("proposals") or state.get("prompted"):
        emit({})
        return
    state["prompted"] = True
    save_session(bundle, conversation_id, state)
    reads = state["reads"][:8]
    more = f" 等 {len(state['reads'])} 条" if len(state["reads"]) > 8 else ""
    emit(
        {
            "followup_message": (
                "回写检查（领域知识 ③ capture）：本次任务读过以下 Concept 但没有写提案："
                + "、".join(f"`{r}`" for r in reads)
                + more
                + "。请按 using-domain-knowledge 的回写协议判断：是否发现了 Concept 与真源矛盾、index 路由错误、任务依赖但 Bundle 缺失的规则、会影响后续任务的设计取舍、或已被推翻的 stable？"
                "有则写入 `.kb/proposals/<YYYY-MM-DD>-<slug>.md`（不要改 knowledge/）；没有则回答“无需回写”并结束。"
            )
        }
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"[kb_capture_prompt] {exc}\n")
        emit({})
