#!/usr/bin/env python3
"""Collect a public Korean-politicians feed and publish run-level evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(timezone.utc)
params = urlencode({"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": "Category:South Korean politicians", "gcmlimit": "50", "prop": "pageprops|info"})
source_url = f"https://en.wikipedia.org/w/api.php?{params}"
request = Request(source_url, headers={"Accept": "application/json", "User-Agent": "LetsPeople observability"})
with urlopen(request, timeout=30) as response:
    source = json.loads(response.read().decode("utf-8"))
pages = (source.get("query") or {}).get("pages") or {}
records = [{"pageid": page.get("pageid"), "title": page.get("title"), "touched": page.get("touched")} for page in pages.values() if page.get("pageid") and page.get("title")]
if not records or len({record["pageid"] for record in records}) != len(records):
    raise RuntimeError("Wikipedia response has no unique person pages")
raw = {"source": "Wikipedia category feed", "source_url": source_url, "observed_at": now.isoformat(), "category": "South Korean politicians", "records": records}
raw_bytes = json.dumps(raw, ensure_ascii=False, sort_keys=True).encode("utf-8")
raw_path = ROOT / "data" / "raw" / "wikipedia_south_korean_politicians.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_bytes(raw_bytes + b"\n")
out = ROOT / "data" / "observability" / "latest.json"
med_path = ROOT / "data" / "medical_professionals_db.json"
med_count = 0
if med_path.exists():
    try:
        med_count = int(json.loads(med_path.read_text(encoding="utf-8")).get("total_medical_indexed") or 0)
    except (OSError, json.JSONDecodeError, ValueError):
        med_count = 0
total_records = len(records) + med_count
prev_records = None
if out.exists():
    try:
        prev_records = (json.loads(out.read_text(encoding="utf-8")).get("counts") or {}).get("records")
    except (OSError, json.JSONDecodeError):
        pass
increment = max(0, total_records - int(prev_records)) if isinstance(prev_records, (int, float)) else 0
payload = {
    "schema": "lets_observability_v1",
    "run_id": f"people-{now.strftime('%Y%m%dT%H%M%SZ')}",
    "observed_at": now.isoformat(),
    "service_id": "people",
    "source": "wikipedia_category_feed",
    "stages": {
        "collect": {"status": "success", "ok": total_records, "artifact": True},
        "analyze": {"status": "not_started", "ok": None},
        "quality": {"status": "success", "quality_issue_count": 0, "detail": "unique page identifiers"},
        "publish": {"status": "success", "artifact": True},
    },
    "counts": {"records": total_records, "politicians": len(records), "medical_professionals": med_count, "increment": increment},
    "artifacts": {"raw": hashlib.sha256(raw_bytes).hexdigest()},
    "note": "Wikipedia South Korean politicians & medical professionals snapshot.",
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wikipedia people pages observed: {len(records)}")
