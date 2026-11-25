#!/usr/bin/env python3
"""Collect real public profiles of Korean medical professionals (doctors, nurses, etc.).

Fetches category members, summaries, and thumbnails from Korean & English
Wikipedia APIs and writes ``data/medical_professionals_db.json``.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
KST = timezone(timedelta(hours=9))
OUT_PATH = ROOT / "data" / "medical_professionals_db.json"

CATEGORY_SPECS = [
    {
        "api": "https://ko.wikipedia.org/w/api.php",
        "wiki_base": "https://ko.wikipedia.org/wiki/",
        "category": "분류:대한민국의 의사",
        "role_group": "doctors",
        "category_kr": "의료인 · 의사",
        "default_role": "의사",
        "limit": 50,
    },
    {
        "api": "https://ko.wikipedia.org/w/api.php",
        "wiki_base": "https://ko.wikipedia.org/wiki/",
        "category": "분류:대한민국의 간호사",
        "role_group": "nurses",
        "category_kr": "의료인 · 간호사",
        "default_role": "간호사",
        "limit": 50,
    },
    {
        "api": "https://ko.wikipedia.org/w/api.php",
        "wiki_base": "https://ko.wikipedia.org/wiki/",
        "category": "분류:대한민국의 한의사",
        "role_group": "oriental_doctors",
        "category_kr": "의료인 · 한의사",
        "default_role": "한의사",
        "limit": 50,
    },
    {
        "api": "https://ko.wikipedia.org/w/api.php",
        "wiki_base": "https://ko.wikipedia.org/wiki/",
        "category": "분류:대한민국의 치과의사",
        "role_group": "dentists",
        "category_kr": "의료인 · 치과의사",
        "default_role": "치과의사",
        "limit": 50,
    },
    {
        "api": "https://ko.wikipedia.org/w/api.php",
        "wiki_base": "https://ko.wikipedia.org/wiki/",
        "category": "분류:대한민국의 약사",
        "role_group": "pharmacists",
        "category_kr": "의료인 · 약사",
        "default_role": "약사",
        "limit": 50,
    },
    {
        "api": "https://en.wikipedia.org/w/api.php",
        "wiki_base": "https://en.wikipedia.org/wiki/",
        "category": "Category:South Korean physicians",
        "role_group": "doctors",
        "category_kr": "의료인 · 의사 (영문)",
        "default_role": "Physician",
        "limit": 50,
    },
    {
        "api": "https://en.wikipedia.org/w/api.php",
        "wiki_base": "https://en.wikipedia.org/wiki/",
        "category": "Category:South Korean nurses",
        "role_group": "nurses",
        "category_kr": "의료인 · 간호사 (영문)",
        "default_role": "Nurse",
        "limit": 50,
    },
]


def _fetch_category(spec: dict) -> list[dict]:
    params = urlencode(
        {
            "action": "query",
            "format": "json",
            "generator": "categorymembers",
            "gcmtitle": spec["category"],
            "gcmnamespace": "0",
            "gcmlimit": str(spec["limit"]),
            "prop": "pageimages|extracts|info",
            "piprop": "thumbnail",
            "pithumbsize": "320",
            "exintro": "1",
            "explaintext": "1",
            "exsentences": "2",
        }
    )
    url = f"{spec['api']}?{params}"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "LetsPeople/1.0 (medical-collector)"})
    with urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pages = (data.get("query") or {}).get("pages") or {}
    results = []
    for page in pages.values():
        pageid = page.get("pageid")
        title = (page.get("title") or "").strip()
        if not pageid or not title or title.startswith("분류:") or title.startswith("Category:"):
            continue
        extract = (page.get("extract") or "").strip()
        thumb = (page.get("thumbnail") or {}).get("source")
        results.append(
            {
                "id": f"med-{spec['role_group']}-{pageid}",
                "name": title,
                "category": "medical_professionals",
                "role_group": spec["role_group"],
                "category_kr": spec["category_kr"],
                "entity_type": "개인",
                "primary_org": "대한민국 보건의료계",
                "primary_role": spec["default_role"],
                "photo_webp": thumb or "",
                "profile_summary": extract or f"{spec['category_kr']} 등재 인물",
                "source_url": f"{spec['wiki_base']}{quote(title.replace(' ', '_'))}",
                "touched": page.get("touched"),
            }
        )
    return results


def collect_medical_professionals() -> dict:
    """Fetch and deduplicate Korean medical professionals from Wikipedia."""
    now_kst = datetime.now(KST).isoformat()
    seen_names: set[str] = set()
    profiles: list[dict] = []
    breakdown: dict[str, int] = {}
    errors: list[str] = []

    for spec in CATEGORY_SPECS:
        try:
            items = _fetch_category(spec)
        except Exception as exc:
            errors.append(f"{spec['category']}: {exc}")
            continue
        for item in items:
            norm = item["name"].lower()
            if norm in seen_names:
                continue
            seen_names.add(norm)
            profiles.append(item)
            rg = item["role_group"]
            breakdown[rg] = breakdown.get(rg, 0) + 1

    profiles.sort(key=lambda x: (x["role_group"], x["name"]))
    payload = {
        "schema": "lets_people_medical_v1",
        "last_updated": now_kst,
        "source": "ko/en.wikipedia.org API",
        "total_medical_indexed": len(profiles),
        "breakdown": breakdown,
        "fetch_errors": errors,
        "featured_medical_profiles": profiles,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = collect_medical_professionals()
    print(f"Medical professionals observed: {result['total_medical_indexed']} ({result['breakdown']})")
