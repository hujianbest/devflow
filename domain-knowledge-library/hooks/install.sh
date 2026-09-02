#!/usr/bin/env bash
# Install Domain Knowledge hooks into the current repository's .cursor/.
#
# Usage: bash <devflow>/domain-knowledge-library/hooks/install.sh [target-repo]
#
# Copies kb_*.py into .cursor/hooks/domain-kb/ and merges hooks.json entries
# into .cursor/hooks.json without touching unrelated hooks.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$(pwd)}"
HOOK_DIR="$TARGET/.cursor/hooks/domain-kb"
HOOKS_JSON="$TARGET/.cursor/hooks.json"

command -v python3 >/dev/null 2>&1 || { echo "python3 is required by the hooks" >&2; exit 1; }

mkdir -p "$HOOK_DIR"
cp "$SRC_DIR"/kb_*.py "$HOOK_DIR"/
chmod +x "$HOOK_DIR"/kb_*.py

python3 - "$SRC_DIR/hooks.json" "$HOOKS_JSON" <<'PY'
import json, sys
from pathlib import Path

src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
dst_path = Path(sys.argv[2])
dst = {"version": 1, "hooks": {}}
if dst_path.is_file():
    try:
        dst = json.loads(dst_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        sys.exit(f"{dst_path} is not valid JSON; fix or remove it first")
dst.setdefault("version", 1)
hooks = dst.setdefault("hooks", {})
for event, entries in src["hooks"].items():
    existing = hooks.setdefault(event, [])
    existing[:] = [e for e in existing if "domain-kb/" not in str(e.get("command", ""))]
    existing.extend(entries)
dst_path.parent.mkdir(parents=True, exist_ok=True)
dst_path.write_text(json.dumps(dst, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"merged domain-kb hooks into {dst_path}")
PY

if [ ! -f "$TARGET/.domain-kb" ] && [ ! -d "$TARGET/domain-kb" ] && [ ! -f "$TARGET/knowledge/index.md" ]; then
  cat <<EOF
hooks installed, but no Bundle was found under $TARGET.
Point them at one with either:
  echo "../path/to/bundle" > $TARGET/.domain-kb
  export DOMAIN_KB_ROOT=/abs/path/to/bundle
or create one: python3 <devflow>/domain-knowledge-library/domain-knowledge-maintain/scripts/kb.py init $TARGET/domain-kb
EOF
fi

echo "done. Cursor reloads hooks.json automatically; check the Hooks output channel if nothing fires."
