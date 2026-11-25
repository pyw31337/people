#!/usr/bin/env python3
"""
sync_real_people_data.py
Synchronize all 79,496 people from NewsBoard (people_bio.json + National Assembly photos)
directly into Let's People master SQLite DB and web JSON artifacts.
Eliminates mock dossiers and establishes a massive, genuine people database.
"""
from __future__ import annotations

import json
import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB_PATH = DATA / "people_master.db"

NEWS_DIR = Path("/Users/pyw31337/Developer/newsboard-local/news")
PEOPLE_BIO_PATH = NEWS_DIR / "data" / "people_bio.json"
POL_PHOTOS_DIR = NEWS_DIR / "data" / "pol" / "photos"
POL_ROSTER_PATH = NEWS_DIR / "data" / "pol" / "roster.json"

def make_id(name: str, org: str = "") -> str:
    seed = f"{name.strip()}::{org.strip()}".encode("utf-8")
    return f"p-{hashlib.sha1(seed).hexdigest()[:12]}"

def sync_data():
    now_kst = datetime.now(KST).isoformat()
    print(f"[{now_kst}] Starting full sync of real people data...")

    # 1. Load NewsBoard people_bio.json (79,496 records)
    if not PEOPLE_BIO_PATH.exists():
        print(f"Error: {PEOPLE_BIO_PATH} not found")
        return

    with open(PEOPLE_BIO_PATH, "r", encoding="utf-8") as f:
        bio_data = json.load(f)
    print(f"Loaded {len(bio_data)} people from {PEOPLE_BIO_PATH}")

    # 2. Build politician photo lookup from pol/roster.json or pol/photos
    photo_map = {}
    if POL_ROSTER_PATH.exists():
        try:
            with open(POL_ROSTER_PATH, "r", encoding="utf-8") as f:
                roster = json.load(f)
                for item in roster:
                    name = item.get("name") or item.get("hg_nm")
                    photo = item.get("photo") or item.get("img_url")
                    if name and photo:
                        photo_map[name.strip()] = photo
        except Exception as e:
            print("Notice loading roster:", e)

    # 3. Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            category_kr TEXT NOT NULL,
            description TEXT,
            photo_url TEXT,
            birth_date TEXT,
            death_date TEXT,
            country TEXT,
            primary_org TEXT,
            primary_role TEXT,
            sitelinks INTEGER DEFAULT 0,
            wikipedia_url TEXT,
            wikiquote_url TEXT,
            educations_json TEXT,
            birth_places_json TEXT,
            family_json TEXT,
            awards_json TEXT,
            occupations_json TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_people_name ON people(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_people_category ON people(category)")

    inserted_or_updated = 0
    records_batch = []

    for name, info in bio_data.items():
        name_clean = str(name).strip()
        if not name_clean:
            continue
        pid = make_id(name_clean, info.get("org", ""))
        kind = info.get("kind", "general")
        role = info.get("role_title") or info.get("title") or ""
        org = info.get("org", "")
        birth_desc = info.get("birth_desc", "")
        events = info.get("events") or []
        events_desc = " · ".join([f"{e.get('d')}: {e.get('t')}" for e in events[:3]]) if events else ""
        desc = f"{org} {role}".strip()
        if events_desc:
            desc = f"{desc} | {events_desc}" if desc else events_desc

        category = "political" if "politician" in kind or "정치" in role else (
            "corporate" if "business" in kind or "기업" in role or "회장" in role or "대표" in role else (
                "legal" if "법조" in role or "판사" in role or "검사" in role or "변호사" in role else (
                    "culture" if "artist" in kind or "작가" in role or "가수" in role or "배우" in role else "public"
                )
            )
        )
        category_kr = {
            "political": "정치·행정",
            "corporate": "기업·경제",
            "legal": "법조·사법",
            "culture": "문화·예술",
            "public": "사회·공공"
        }.get(category, "인물")

        photo_url = photo_map.get(name_clean, "")
        if not photo_url and info.get("photo"):
            photo_url = info.get("photo")

        records_batch.append((
            pid,
            name_clean,
            "newsboard_people_bio",
            category,
            category_kr,
            desc[:500],
            photo_url,
            birth_desc[:120],
            "",
            "대한민국",
            org[:100],
            role[:120],
            len(events),
            f"https://ko.wikipedia.org/wiki/{name_clean}",
            "",
            json.dumps(info.get("education") or [], ensure_ascii=False),
            json.dumps([birth_desc] if birth_desc else [], ensure_ascii=False),
            json.dumps(info.get("family") or {}, ensure_ascii=False),
            json.dumps(info.get("awards") or [], ensure_ascii=False),
            json.dumps([role] if role else [], ensure_ascii=False),
            now_kst
        ))

        if len(records_batch) >= 2000:
            cur.executemany("""
                INSERT INTO people (
                    id, name, source, category, category_kr, description, photo_url,
                    birth_date, death_date, country, primary_org, primary_role,
                    sitelinks, wikipedia_url, wikiquote_url, educations_json,
                    birth_places_json, family_json, awards_json, occupations_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    description=excluded.description,
                    photo_url=CASE WHEN excluded.photo_url != '' THEN excluded.photo_url ELSE people.photo_url END,
                    primary_org=excluded.primary_org,
                    primary_role=excluded.primary_role,
                    updated_at=excluded.updated_at
            """, records_batch)
            inserted_or_updated += len(records_batch)
            records_batch = []

    if records_batch:
        cur.executemany("""
            INSERT INTO people (
                id, name, source, category, category_kr, description, photo_url,
                birth_date, death_date, country, primary_org, primary_role,
                sitelinks, wikipedia_url, wikiquote_url, educations_json,
                birth_places_json, family_json, awards_json, occupations_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                description=excluded.description,
                photo_url=CASE WHEN excluded.photo_url != '' THEN excluded.photo_url ELSE people.photo_url END,
                primary_org=excluded.primary_org,
                primary_role=excluded.primary_role,
                updated_at=excluded.updated_at
        """, records_batch)
        inserted_or_updated += len(records_batch)

    conn.commit()

    cur.execute("SELECT count(*) FROM people")
    total_db_count = cur.fetchone()[0]
    print(f"Sync complete! Total people in SQLite: {total_db_count} (Processed: {inserted_or_updated})")

    # 4. Export Top Dossiers (Master Dossier DB)
    cur.execute("""
        SELECT id, name, category, category_kr, description, photo_url, birth_date, primary_org, primary_role, wikipedia_url, sitelinks
        FROM people
        ORDER BY sitelinks DESC, length(description) DESC
        LIMIT 500
    """)
    top_people = []
    for row in cur.fetchall():
        top_people.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "category_kr": row[3],
            "bio_summary": row[4],
            "photo_url": row[5],
            "birth_date": row[6],
            "primary_org": row[7],
            "primary_role": row[8],
            "wikipedia_url": row[9],
            "significance_score": row[10]
        })

    master_dossier_path = DATA / "master_people_dossier_db.json"
    with open(master_dossier_path, "w", encoding="utf-8") as f:
        json.dump({
            "schema_version": "3.0.0",
            "last_synced": now_kst,
            "total_catalog_size": total_db_count,
            "featured_dossiers_count": len(top_people),
            "dossiers": top_people
        }, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(top_people)} master dossiers to {master_dossier_path}")

    # 5. Export Global People Catalog (Fast search index)
    cur.execute("SELECT name, primary_org, primary_role, category_kr, photo_url FROM people LIMIT 5000")
    catalog = [{"name": r[0], "org": r[1], "role": r[2], "cat": r[3], "photo": r[4]} for r in cur.fetchall()]
    catalog_path = DATA / "global_people_catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": now_kst,
            "total_indexed": total_db_count,
            "fast_search_index": catalog
        }, f, ensure_ascii=False, indent=2)
    print(f"Exported fast catalog with {len(catalog)} entries to {catalog_path}")

    conn.close()

if __name__ == "__main__":
    sync_data()
