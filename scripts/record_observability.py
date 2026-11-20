#!/usr/bin/env python3
"""Write an honest public state while a real source collector is unavailable."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(timezone.utc)
payload = {
    "schema": "lets_observability_v1",
    "run_id": f"people-unimplemented-{now.strftime('%Y%m%dT%H%M%SZ')}",
    "observed_at": now.isoformat(),
    "service_id": "people",
    "source": "workflow_guard",
    "stages": {
        "collect": {"status": "not_implemented", "ok": None},
        "analyze": {"status": "not_started", "ok": None},
        "quality": {"status": "not_started", "quality_issue_count": None},
        "publish": {"status": "not_started"},
    },
    "counts": {},
    "note": "No source-backed people collector is configured. Synthetic counter updates are disabled.",
}
out = ROOT / "data" / "observability" / "latest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(payload["note"])
