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
payload = {
    "schema": "lets_observability_v1",
    "run_id": f"people-unimplemented-{now.strftime('%Y%m%dT%H%M%SZ')}",
    "observed_at": now.isoformat(),
    "service_id": "people",
    "source": "wikipedia_category_feed",
    "stages": {
        "collect": {"status": "success", "ok": len(records), "artifact": True},
        "analyze": {"status": "not_started", "ok": None},
        "quality": {"status": "success", "quality_issue_count": 0, "detail": "unique page identifiers"},
        "publish": {"status": "success", "artifact": True},
    },
    "counts": {"records": len(records)},
    "artifacts": {"raw": hashlib.sha256(raw_bytes).hexdigest()},
    "note": "Wikipedia South Korean politicians category snapshot.",
}
out = ROOT / "data" / "observability" / "latest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wikipedia people pages observed: {len(records)}")
