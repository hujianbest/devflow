#!/usr/bin/env python3
"""beforeShellExecution (matcher: knowledge/|\\.kb/): ask before shell commands
that look like they write into the Bundle without the maintenance lock."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import emit, find_bundle_root, lock_held, project_dir, read_input  # noqa: E402

WRITE_HINT = re.compile(r"(^|[;&|]\s*|\s)(rm|mv|cp|tee|truncate|install|sed\s+-i|perl\s+-i)\s|>{1,2}\s*\S*(knowledge/|\.kb/)")
TRUSTED = re.compile(r"\bkb\.py\b")
PROPOSALS = re.compile(r"\.kb/proposals/")


def main() -> None:
    payload = read_input()
    command = payload.get("command") or ""
    if not command or TRUSTED.search(command):
        emit({"permission": "allow"})
        return
    bundle = find_bundle_root(project_dir(payload))
    if bundle is None or lock_held(bundle):
        emit({"permission": "allow"})
        return
    if not WRITE_HINT.search(command):
        emit({"permission": "allow"})
        return
    if PROPOSALS.search(command) and "knowledge/" not in command:
        emit({"permission": "allow"})
        return
    emit(
        {
            "permission": "ask",
            "user_message": "这条命令可能在没有维护锁的情况下写入领域知识 Bundle。",
            "agent_message": "knowledge/ 与 .kb/（提案除外）只能由 domain-knowledge-maintain / expand 在持有维护锁时写入。"
            "任务中的发现请用文件工具写到 .kb/proposals/。若确在维护，先运行 `kb.py lock <mode>`。",
        }
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"[kb_shell_guard] {exc}\n")
        emit({"permission": "allow"})
