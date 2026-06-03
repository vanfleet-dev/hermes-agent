def test_canonical_active_sessions_dedupes_process_rows_and_enriches_from_db():
    from session_runtime_inventory import canonical_active_sessions

    class _DB:
        def list_sessions_rich(self, limit=200, offset=0, min_message_count=0):
            return [{
                "id": "sid-live",
                "title": "Long-running CLI",
                "message_count": 4,
                "started_at": 100.0,
                "last_active": 190.0,
                "model": "gpt-5.4",
                "source": "cli",
                "ended_at": None,
                "lastMessage": "hello from disk",
            }]

    rows = canonical_active_sessions(
        db=_DB(),
        operator_rows=[
            {
                "session_id": "sid-live",
                "session_key": "sid-live",
                "started_at": 100.0,
                "last_active": 200.0,
                "source": "cli",
                "model": "gpt-5.4",
                "status": "idle",
            },
            {
                "session_id": "sid-live",
                "session_key": "sid-live",
                "started_at": 100.0,
                "last_active": 201.0,
                "source": "cli",
                "model": "gpt-5.4",
                "status": "idle",
            },
        ],
        live_gateway_sessions=[],
        current_session_id="",
    )

    assert [row["id"] for row in rows] == ["sid-live"]
    assert rows[0]["title"] == "Long-running CLI"
    assert rows[0]["preview"] == "hello from disk"
    assert rows[0]["message_count"] == 4
    assert rows[0]["status"] == "idle"


def test_canonical_active_sessions_marks_current_and_keeps_gateway_only_rows():
    from session_runtime_inventory import canonical_active_sessions

    rows = canonical_active_sessions(
        db=None,
        operator_rows=[],
        live_gateway_sessions=[
            {
                "id": "sid-gateway",
                "session_key": "sid-gateway",
                "title": "Remote active",
                "preview": "working",
                "model": "gpt-5.4",
                "status": "working",
                "message_count": 3,
                "started_at": 10.0,
                "last_active": 20.0,
            }
        ],
        current_session_id="sid-gateway",
    )

    assert [row["id"] for row in rows] == ["sid-gateway"]
    assert rows[0]["current"] is True
    assert rows[0]["status"] == "working"
