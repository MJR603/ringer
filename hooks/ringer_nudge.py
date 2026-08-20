#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NUDGE_TEXT = (
    "Ringer routing check: this looks like swarm-shaped work happening inline "
    "(model call/harness/edit loop outside a live Ringer run). Load the ringer "
    "skill and route it as a manifest — a single task is a one-task manifest. "
    "If the user explicitly asked for inline work, proceed."
)

PROVIDER_RE = re.compile(
    r"(api\.anthropic\.com|api\.openai\.com|openrouter\.ai|"
    r"generativelanguage\.googleapis|/v1/chat/completions|/v1/messages)",
    re.IGNORECASE,
)
# The keyword must appear in the script's own basename, not anywhere in its
# path. `\S*` used to span directories, so an ordinary command living under a
# directory like clean-my-ai-harness-mission-fit/ tripped the nudge on the word
# "harness" in a folder name (observed 2026-08-19). `[^/\s]*` cannot cross a
# path separator, so only the segment after the last slash is inspected.
HARNESS_RE = re.compile(
    r"\b(?:node|python3?|bun|deno)\s+"
    r"(?:\S*/)?"
    r"[^/\s]*"
    r"(?:simulat|probe|smoke|harness|persona|grader|eval)"
    r"[^/\s]*"
    r"\.(?:mjs|js|ts|py)\b",
    re.IGNORECASE,
)


def ringer_home() -> Path:
    value = os.environ.get("RINGER_HOME")
    if value and value.strip():
        return Path(value).expanduser()
    return Path.home() / ".ringer"


def pid_is_alive(pid: Any) -> bool:
    try:
        parsed = int(pid)
    except (TypeError, ValueError):
        return False
    if parsed <= 0:
        return False
    try:
        os.kill(parsed, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, sort_keys=True)
        fh.write("\n")
    os.replace(tmp_path, path)


def read_live_active_runs(home: Path) -> dict[str, dict[str, Any]]:
    path = home / "active-runs.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        return {}

    live: dict[str, dict[str, Any]] = {}
    changed = False
    for run_id, entry in raw.items():
        if not isinstance(entry, dict):
            changed = True
            continue
        if pid_is_alive(entry.get("pid")):
            live[str(run_id)] = entry
        else:
            changed = True

    if changed:
        write_json_atomic(path, live)
    return live


def safe_session_id(value: Any) -> str:
    text = str(value or "unknown-session")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return safe or "unknown-session"


def state_dir(home: Path) -> Path:
    return home / "nudge-state"


# How many qualifying occurrences pass between nudges. The first one always
# nudges; after that the hook stays quiet until the interval rolls over.
NUDGE_INTERVAL = 10


def marker_path(home: Path, session_id: Any, event: str) -> Path:
    key = f"{session_id}\0{event}".encode("utf-8", errors="replace")
    digest = hashlib.sha256(key).hexdigest()
    return state_dir(home) / f"{digest}.{event}.nudged"


def read_seen_count(path: Path) -> int:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    seen = raw.get("seen") if isinstance(raw, dict) else None
    return seen if isinstance(seen, int) and seen >= 0 else 0


def claim_dedupe_marker(home: Path, session_id: Any, event: str) -> bool:
    """Record one qualifying occurrence; report whether it should nudge.

    Previously this wrote a one-shot marker, so a nudge spent on a false
    positive silenced the hook for the rest of the session (measured: 18
    pre-bash nudges across 436 sessions). Now the count is kept and the hook
    speaks again once the interval rolls over, so a wasted nudge costs a
    cooldown rather than the whole session.
    """
    directory = state_dir(home)
    directory.mkdir(parents=True, exist_ok=True)
    marker = marker_path(home, session_id, event)

    seen = read_seen_count(marker) + 1
    should_nudge = (seen - 1) % NUDGE_INTERVAL == 0
    payload = {"seen": seen, "event": str(event), "last_seen": datetime.now(timezone.utc).isoformat()}
    if should_nudge:
        payload["last_nudged_at_seen"] = seen
    write_json_atomic(marker, payload)
    return should_nudge


def output_nudge(event_name: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": NUDGE_TEXT,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


def command_references_active_workdir(command: str, active_runs: dict[str, dict[str, Any]]) -> bool:
    for entry in active_runs.values():
        workdir = str(entry.get("workdir") or "").strip()
        if workdir and workdir in command:
            return True
    return False


def should_nudge_pre_bash(payload: dict[str, Any], home: Path) -> bool:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return False
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return False
    if "ringer.py" in command:
        return False
    if not (PROVIDER_RE.search(command) or HARNESS_RE.search(command)):
        return False

    active_runs = read_live_active_runs(home)
    if active_runs:
        return False
    if command_references_active_workdir(command, active_runs):
        return False
    return True


def post_edit_state_path(home: Path, session_id: Any) -> Path:
    return state_dir(home) / f"{safe_session_id(session_id)}.json"


def load_post_edit_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"count": 0, "file_paths": []}
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        return {"count": 0, "file_paths": []}
    count = raw.get("count")
    file_paths = raw.get("file_paths")
    if not isinstance(count, int):
        count = 0
    if not isinstance(file_paths, list):
        file_paths = []
    return {"count": count, "file_paths": [str(path) for path in file_paths]}


def record_post_edit(payload: dict[str, Any], home: Path) -> tuple[int, int]:
    path = post_edit_state_path(home, payload.get("session_id"))
    state = load_post_edit_state(path)
    count = int(state["count"]) + 1
    files = set(str(item) for item in state["file_paths"])

    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path")
        if isinstance(file_path, str) and file_path.strip():
            files.add(file_path)

    next_state = {"count": count, "file_paths": sorted(files)}
    write_json_atomic(path, next_state)
    return count, len(files)


def should_nudge_post_edit(payload: dict[str, Any], home: Path) -> bool:
    count, distinct_files = record_post_edit(payload, home)
    if count < 8 or distinct_files < 3:
        return False
    return not read_live_active_runs(home)


def load_stdin_payload() -> dict[str, Any] | None:
    text = sys.stdin.read()
    payload = json.loads(text)
    return payload if isinstance(payload, dict) else None


def run(argv: list[str]) -> int:
    if len(argv) != 2:
        return 0
    mode = argv[1]
    if mode not in {"pre-bash", "post-edit"}:
        return 0

    payload = load_stdin_payload()
    if payload is None:
        return 0

    home = ringer_home()
    session_id = payload.get("session_id")

    if mode == "pre-bash":
        if should_nudge_pre_bash(payload, home) and claim_dedupe_marker(home, session_id, mode):
            output_nudge("PreToolUse")
        return 0

    if should_nudge_post_edit(payload, home) and claim_dedupe_marker(home, session_id, mode):
        output_nudge("PostToolUse")
    return 0


def main() -> int:
    try:
        return run(sys.argv)
    except Exception:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
