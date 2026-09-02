#!/usr/bin/env python3
"""sessionStart: inject the thin knowledge entry when a Bundle is present."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import emit, find_bundle_root, lock_held, project_dir, prune_sessions, read_input  # noqa: E402


def summary_line(bundle: Path) -> str:
    index = bundle / "knowledge" / "index.md"
    if index.is_file():
        for line in index.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("共 "):
                return line
    return "index 尚未生成；运行 `kb.py index`。"


def main() -> None:
    payload = read_input()
    root = project_dir(payload)
    bundle = find_bundle_root(root)
    if bundle is None:
        emit({})
        return
    prune_sessions(bundle)
    try:
        rel = bundle.relative_to(root).as_posix() or "."
    except ValueError:
        rel = str(bundle)
    lock = lock_held(bundle)
    lines = [
        "【领域知识 Bundle】",
        f"位置：`{rel}/knowledge/`（入口 `{rel}/knowledge/index.md`）。{summary_line(bundle)}",
        "读法：index（type / 一行摘要 / status / view / owner）→ 领域或系统 overview → 少量 Concept → 原文。Bundle 负责路由、约束、出处；函数实现、契约正文、配置值回真源。",
        "规则：`draft` 可用但必须写“未确认”并给路径；`deprecated` 不参与默认回答；`view: to-be` 是目标非现状；安全/资金/权限/发布规则的 draft 只能当候选；证据冲突、过期或不足时拒答或找 owner。",
        "写入：任务 Agent 不改 `knowledge/`。发现矛盾、路由错误、缺失规则、设计取舍、stable 被推翻时，写提案到 `.kb/proposals/<date>-<slug>.md`（见 using-domain-knowledge）。任务结束若读过知识却没写提案，会被追问一次；回答“无需回写”即可。",
    ]
    if lock:
        lines.append(f"当前维护锁由 {lock.get('holder')} 持有（{lock.get('mode')}）；本会话若是维护会话可直接写 knowledge/，否则请等待。")
    emit({"additional_context": "\n".join(lines)})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never break the session
        sys.stderr.write(f"[kb_session_start] {exc}\n")
        emit({})
