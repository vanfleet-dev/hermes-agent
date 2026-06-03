from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from hermes_constants import get_hermes_home


SessionRow = dict[str, Any]


def _read_text(path: str) -> str:
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", "ignore")


def _classify_operator_argv(argv: list[str]) -> str | None:
    joined = " ".join(argv)
    if "tui_gateway.slash_worker" in joined:
        return None
    if "hermes_cli.main dashboard" in joined:
        return None
    if any(arg.endswith("/bin/hermes") for arg in argv):
        return "cli"
    if any(arg.endswith("src/index.tsx") for arg in argv):
        return "herm-tui"
    return None


def list_operator_active_sessions(
    proc_root: str = "/proc",
    hermes_home: str | Path | None = None,
) -> list[SessionRow]:
    """Return live interactive operator-session rows from /proc.

    This intentionally excludes dashboard server and slash-worker helper
    processes. The goal is the operator-facing active-session inventory: local
    Hermes CLI sessions and the Herm TUI process tree.
    """

    target_home = str(Path(hermes_home or get_hermes_home()).resolve())
    rows: list[SessionRow] = []
    try:
        entries = os.scandir(proc_root)
    except Exception:
        return rows

    with entries:
        for ent in entries:
            if not ent.is_dir() or not ent.name.isdigit():
                continue
            pid = ent.name
            try:
                env_text = _read_text(f"{proc_root}/{pid}/environ")
                if f"HERMES_HOME={target_home}" not in env_text:
                    continue
                if "HERMES_INTERACTIVE=1" not in env_text:
                    continue
                argv = [a for a in _read_text(f"{proc_root}/{pid}/cmdline").split("\0") if a]
                kind = _classify_operator_argv(argv)
                if not kind:
                    continue
                env = {}
                for item in env_text.split("\0"):
                    if "=" not in item:
                        continue
                    key, value = item.split("=", 1)
                    env[key] = value
                session_id = str(env.get("HERMES_SESSION_ID") or "").strip()
                if not session_id:
                    continue
                session_key = str(env.get("HERMES_SESSION_KEY") or session_id).strip() or session_id
                started_at = None
                try:
                    started_at = float(os.stat(f"{proc_root}/{pid}").st_ctime)
                except Exception:
                    pass
                rows.append(
                    {
                        "id": session_id,
                        "pid": int(pid),
                        "session_id": session_id,
                        "session_key": session_key,
                        "source": kind,
                        "status": "idle",
                        "started_at": started_at,
                        "last_active": started_at,
                        "model": str(env.get("HERMES_MODEL") or ""),
                    }
                )
            except Exception:
                continue
    return rows


def _persisted_session_index(db: Any, limit: int = 200) -> dict[str, SessionRow]:
    if db is None:
        return {}
    rows = db.list_sessions_rich(limit=limit, offset=0, min_message_count=0) or []
    index: dict[str, SessionRow] = {}
    for row in rows:
        sid = str(row.get("id") or "").strip()
        if sid:
            index[sid] = dict(row)
    return index


def _merge_operator_rows(operator_rows: Iterable[SessionRow], persisted: dict[str, SessionRow]) -> tuple[list[str], dict[str, SessionRow]]:
    order: list[str] = []
    merged: dict[str, SessionRow] = {}
    for raw in operator_rows:
        sid = str(raw.get("session_id") or raw.get("id") or "").strip()
        if not sid:
            continue
        if sid not in merged:
            order.append(sid)
            merged[sid] = {
                "id": sid,
                "session_key": str(raw.get("session_key") or sid),
                "status": str(raw.get("status") or "idle"),
            }
        row = merged[sid]
        db_row = persisted.get(sid, {})
        row["session_key"] = str(raw.get("session_key") or row.get("session_key") or sid)
        row["title"] = db_row.get("title") or row.get("title") or sid
        row["preview"] = db_row.get("lastMessage") or row.get("preview") or ""
        row["model"] = raw.get("model") or db_row.get("model") or row.get("model") or ""
        row["message_count"] = db_row.get("message_count") or row.get("message_count") or 0
        row["started_at"] = raw.get("started_at") or db_row.get("started_at") or row.get("started_at")
        row["last_active"] = max(
            float(x)
            for x in [
                row.get("last_active") or 0,
                raw.get("last_active") or 0,
                db_row.get("last_active") or db_row.get("started_at") or 0,
            ]
        )
        row["status"] = str(raw.get("status") or row.get("status") or "idle")
    return order, merged


def canonical_active_sessions(
    db: Any = None,
    operator_rows: Iterable[SessionRow] | None = None,
    live_gateway_sessions: Iterable[SessionRow] | None = None,
    current_session_id: str = "",
) -> list[SessionRow]:
    """Merge operator process inventory with live gateway sessions.

    Output shape matches the ``session.active_list`` / Herm SessionActiveItem
    contract.
    """

    persisted = _persisted_session_index(db)
    order, merged = _merge_operator_rows(operator_rows or [], persisted)

    for live in live_gateway_sessions or []:
        sid = str(live.get("id") or live.get("session_id") or "").strip()
        if not sid:
            continue
        if sid not in merged:
            order.append(sid)
            merged[sid] = {"id": sid}
        row = merged[sid]
        row.update({k: v for k, v in dict(live).items() if v is not None})
        row.setdefault("session_key", str(live.get("session_key") or sid))
        row.setdefault("status", "idle")
        row.setdefault("title", sid)
        row.setdefault("preview", "")
        row.setdefault("model", "")
        row.setdefault("message_count", 0)

    for sid in order:
        row = merged[sid]
        key = str(row.get("session_key") or sid)
        row["current"] = bool(current_session_id and current_session_id in {sid, key})

    return [merged[sid] for sid in order]
