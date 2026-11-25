#!/usr/bin/env python3
"""Collect real global & Korean people profiles via fast Wikidata SPARQL + wbgetentities + local DBs.

Two-stage Wikidata pipeline (avoids SPARQL 503/504 timeouts):
1. Lightweight SPARQL selects only (?person, ?sitelinks) per domain.
2. Wikidata ``wbgetentities`` API fetches full claims in batches of 50:
   photo (P18), birth/death (P569/P570), country (P27), occupation (P106),
   employer (P108), alumni/education (P69), birthplace (P19),
   family (P22/P25/P26), awards (P166), Wikipedia & Wikiquote links.

Builds fine-grained clusters (alumni, regional, family, domain) in SQLite
(``data/people_master.db``) and exports web-ready JSON files.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB_PATH = DATA / "people_master.db"
KST = timezone(timedelta(hours=9))
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WD_API = "https://www.wikidata.org/w/api.php"
UA = "LetsPeopleGlobalCollector/2.0 (https://pyw31337.github.io/people/)"

DOMAIN_QUERIES = [
    {
        "domain": "korean_notables",
        "domain_kr": "한국 주요 인물",
        "category": "corporate",
        "limit": 800,
        "where": "?person wdt:P31 wd:Q5 ; wdt:P27 wd:Q884 ; wikibase:sitelinks ?sitelinks . FILTER(?sitelinks >= 10)",
    },
    {
        "domain": "global_business_tech",
        "domain_kr": "글로벌 기업·테크 리더",
        "category": "corporate",
        "limit": 600,
        "where": "?person wdt:P31 wd:Q5 ; wdt:P106 wd:Q131524 ; wikibase:sitelinks ?sitelinks . FILTER(?sitelinks >= 30)",
    },
    {
        "domain": "global_politics",
        "domain_kr": "글로벌 정계·지도자",
        "category": "politics_policy",
        "limit": 600,
        "where": "?person wdt:P31 wd:Q5 ; wdt:P106 wd:Q82955 ; wikibase:sitelinks ?sitelinks . FILTER(?sitelinks >= 55)",
    },
    {
        "domain": "global_science_medicine",
        "domain_kr": "글로벌 과학·의학·석학",
        "category": "medical_professionals",
        "limit": 600,
        "where": "VALUES ?occ { wd:Q39631 wd:Q186360 wd:Q901 wd:Q169470 } ?person wdt:P31 wd:Q5 ; wdt:P106 ?occ ; wikibase:sitelinks ?sitelinks . FILTER(?sitelinks >= 30)",
    },
    {
        "domain": "global_culture_media",
        "domain_kr": "글로벌 문화·방송·예술",
        "category": "culture",
        "limit": 600,
        "where": "VALUES ?occ { wd:Q33999 wd:Q2526255 wd:Q36180 wd:Q1930187 } ?person wdt:P31 wd:Q5 ; wdt:P106 ?occ ; wikibase:sitelinks ?sitelinks . FILTER(?sitelinks >= 60)",
    },
]


def _get_json(url: str, data: bytes | None = None, headers: dict | None = None, timeout: int = 45) -> dict:
    hdrs = {"Accept": "application/json", "User-Agent": UA}
    if headers:
        hdrs.update(headers)
    req = Request(url, data=data, headers=hdrs)
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sparql_qids(where_clause: str, limit: int) -> list[tuple[str, int]]:
    query = f"""
    SELECT ?person ?sitelinks WHERE {{
      {where_clause}
    }}
    LIMIT {limit}
    """
    body = urlencode({"query": query, "format": "json"}).encode("utf-8")
    payload = _get_json(
        SPARQL_ENDPOINT,
        data=body,
        headers={"Accept": "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded"},
        timeout=45,
    )
    out: list[tuple[str, int]] = []
    for b in (payload.get("results") or {}).get("bindings") or []:
        uri = (b.get("person") or {}).get("value", "")
        qid = uri.rsplit("/", 1)[-1]
        sl = int((b.get("sitelinks") or {}).get("value") or 0)
        if qid.startswith("Q"):
            out.append((qid, sl))
    return out


def _fetch_entities(qids: list[str], props: str = "labels|descriptions|claims|sitelinks") -> dict:
    batches = [qids[i : i + 50] for i in range(0, len(qids), 50)]
    entities: dict = {}

    def fetch_batch(batch: list[str]) -> dict:
        params = urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": props,
                "languages": "ko|en",
                "format": "json",
            }
        )
        try:
            res = _get_json(f"{WD_API}?{params}", timeout=25)
            return res.get("entities") or {}
        except Exception:
            return {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(fetch_batch, b) for b in batches]
        for idx, fut in enumerate(as_completed(futures), 1):
            entities.update(fut.result())
            if idx % 25 == 0 or idx == len(batches):
                print(f"    wbgetentities ({props}): {idx}/{len(batches)} batches", flush=True)
    return entities


def _claim_qids(claims: dict, prop: str, limit: int = 5) -> list[str]:
    out = []
    for st in (claims.get(prop) or [])[:limit]:
        val = ((st.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(val, dict) and isinstance(val.get("id"), str):
            out.append(val["id"])
    return out


def _claim_time(claims: dict, prop: str) -> str:
    for st in (claims.get(prop) or [])[:1]:
        val = ((st.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(val, dict) and isinstance(val.get("time"), str):
            return val["time"].lstrip("+")[:10]
    return ""


def _claim_image(claims: dict) -> str:
    for st in (claims.get("P18") or [])[:1]:
        val = ((st.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(val, str) and val.strip():
            fname = quote(val.strip().replace(" ", "_"))
            return f"https://commons.wikimedia.org/wiki/Special:FilePath/{fname}?width=320"
    return ""


def _label(entity: dict) -> str:
    labels = entity.get("labels") or {}
    return ((labels.get("ko") or labels.get("en") or {}).get("value") or "").strip()


def _desc(entity: dict) -> str:
    descs = entity.get("descriptions") or {}
    return ((descs.get("ko") or descs.get("en") or {}).get("value") or "").strip()


def _classify_category(occs: list[str], default_cat: str) -> tuple[str, str]:
    joined = " ".join(occs).lower()
    if any(k in joined for k in ("의사", "간호사", "한의사", "치과의사", "약사", "physician", "surgeon", "nurse", "doctor", "dentist")):
        return "medical_professionals", "의료인"
    if any(k in joined for k in ("기업인", "경영", "entrepreneur", "businessperson", "chief executive", "investor")):
        return "corporate", "기업인·리더"
    if any(k in joined for k in ("정치인", "대통령", "국회의원", "장관", "politician", "diplomat", "statesperson")):
        return "politics_policy", "정계·관료"
    if any(k in joined for k in ("감독", "연출", "프로듀서", "director", "producer", "showrunner")):
        return "showrunners_pds", "연출·PD·감독"
    if any(k in joined for k in ("작가", "소설가", "시인", "writer", "author", "novelist", "screenwriter")):
        return "writers_screenplay", "작가·저술가"
    if any(k in joined for k in ("기자", "언론인", "아나운서", "방송인", "journalist", "broadcaster", "presenter")):
        return "broadcasters_mcs", "언론·방송인"
    if any(k in joined for k in ("배우", "가수", "음악가", "화가", "actor", "singer", "musician", "painter", "artist")):
        return "culture", "문화·예술"
    if any(k in joined for k in ("과학자", "물리학자", "교수", "researcher", "scientist", "physicist", "chemist")):
        return "science_nobel", "과학·학술"
    return default_cat, "글로벌 인물"


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
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
        """
    )
    conn.commit()


def _upsert_person(conn: sqlite3.Connection, rec: dict) -> None:
    conn.execute(
        """
        INSERT INTO people (
            id, name, source, category, category_kr, description, photo_url,
            birth_date, death_date, country, primary_org, primary_role,
            sitelinks, wikipedia_url, wikiquote_url,
            educations_json, birth_places_json, family_json, awards_json, occupations_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            category=excluded.category,
            category_kr=excluded.category_kr,
            description=COALESCE(NULLIF(excluded.description, ''), people.description),
            photo_url=COALESCE(NULLIF(excluded.photo_url, ''), people.photo_url),
            birth_date=COALESCE(NULLIF(excluded.birth_date, ''), people.birth_date),
            country=COALESCE(NULLIF(excluded.country, ''), people.country),
            primary_org=COALESCE(NULLIF(excluded.primary_org, ''), people.primary_org),
            primary_role=COALESCE(NULLIF(excluded.primary_role, ''), people.primary_role),
            sitelinks=MAX(excluded.sitelinks, people.sitelinks),
            wikipedia_url=COALESCE(NULLIF(excluded.wikipedia_url, ''), people.wikipedia_url),
            wikiquote_url=COALESCE(NULLIF(excluded.wikiquote_url, ''), people.wikiquote_url),
            educations_json=excluded.educations_json,
            birth_places_json=excluded.birth_places_json,
            family_json=excluded.family_json,
            awards_json=excluded.awards_json,
            occupations_json=excluded.occupations_json,
            updated_at=excluded.updated_at
        """,
        (
            rec["id"], rec["name"], rec["source"], rec["category"], rec["category_kr"],
            rec.get("description", ""), rec.get("photo_url", ""), rec.get("birth_date", ""),
            rec.get("death_date", ""), rec.get("country", ""), rec.get("primary_org", ""),
            rec.get("primary_role", ""), int(rec.get("sitelinks") or 0),
            rec.get("wikipedia_url", ""), rec.get("wikiquote_url", ""),
            json.dumps(rec.get("educations", []), ensure_ascii=False),
            json.dumps(rec.get("birth_places", []), ensure_ascii=False),
            json.dumps(rec.get("family", {}), ensure_ascii=False),
            json.dumps(rec.get("awards", []), ensure_ascii=False),
            json.dumps(rec.get("occupations", []), ensure_ascii=False),
            rec.get("updated_at", ""),
        ),
    )


def _ingest_elite_network(conn: sqlite3.Connection, now_iso: str) -> int:
    elite_path = DATA / "elite_network.json"
    if not elite_path.exists():
        return 0
    elite = json.loads(elite_path.read_text(encoding="utf-8"))
    added = 0
    group_map = [
        ("corporate_leaders", "corporate", "DART 등재 기업인"),
        ("high_officials", "politics_policy", "고위 공직자·관료"),
        ("legal_elites", "legal", "법조인"),
        ("journalists", "broadcasters_mcs", "언론인·기자"),
        ("assembly_families", "politics_policy", "국회의원·가족"),
    ]
    for key, cat, cat_kr in group_map:
        section = elite.get(key)
        if not isinstance(section, dict):
            continue
        for name, info in section.items():
            if not isinstance(info, dict):
                continue
            pid = "elite-" + hashlib.sha1(f"{key}:{name}".encode("utf-8")).hexdigest()[:12]
            edus = []
            for ek in ("school", "university", "education", "alumni"):
                val = info.get(ek)
                if isinstance(val, str) and val.strip():
                    edus.append(val.strip())
                elif isinstance(val, list):
                    edus.extend(str(x).strip() for x in val if str(x).strip())
            bps = [str(info.get(k)).strip() for k in ("hometown", "birthplace", "region") if info.get(k)]
            org = str(info.get("company") or info.get("org") or info.get("ministry") or info.get("affiliation") or "")
            role = str(info.get("role") or info.get("position") or info.get("title") or cat_kr)
            _upsert_person(
                conn,
                {
                    "id": pid, "name": str(name).strip(), "source": "elite_network",
                    "category": cat, "category_kr": cat_kr,
                    "description": str(info.get("summary") or f"{org} {role}".strip()),
                    "photo_url": str(info.get("photo_webp") or info.get("photo") or ""),
                    "birth_date": str(info.get("birth") or info.get("birth_year") or ""),
                    "country": "대한민국", "primary_org": org, "primary_role": role, "sitelinks": 1,
                    "educations": list(dict.fromkeys(edus)), "birth_places": list(dict.fromkeys(bps)),
                    "family": {"members": info.get("family")} if info.get("family") else {},
                    "awards": [], "occupations": [role] if role else [], "updated_at": now_iso,
                },
            )
            added += 1
    conn.commit()
    return added


def _ingest_medical_db(conn: sqlite3.Connection, now_iso: str) -> int:
    med_path = DATA / "medical_professionals_db.json"
    if not med_path.exists():
        return 0
    med = json.loads(med_path.read_text(encoding="utf-8"))
    added = 0
    for p in med.get("featured_medical_profiles", []):
        _upsert_person(
            conn,
            {
                "id": p["id"], "name": p["name"], "source": "wikipedia_medical",
                "category": "medical_professionals", "category_kr": p.get("category_kr", "의료인"),
                "description": p.get("profile_summary", ""), "photo_url": p.get("photo_webp", ""),
                "country": "대한민국", "primary_org": p.get("primary_org", "대한민국 보건의료계"),
                "primary_role": p.get("primary_role", "의료인"), "sitelinks": 5,
                "wikipedia_url": p.get("source_url", ""), "occupations": [p.get("primary_role", "의료인")],
                "updated_at": now_iso,
            },
        )
        added += 1
    conn.commit()
    return added


def build_clusters_and_exports(conn: sqlite3.Connection, now_iso: str) -> dict:
    rows = conn.execute(
        """
        SELECT id, name, source, category, category_kr, description, photo_url,
               birth_date, death_date, country, primary_org, primary_role,
               sitelinks, wikipedia_url, wikiquote_url,
               educations_json, birth_places_json, family_json, awards_json, occupations_json
        FROM people
        ORDER BY sitelinks DESC, name ASC
        """
    ).fetchall()

    alumni_map: dict[str, list[dict]] = defaultdict(list)
    regional_map: dict[str, list[dict]] = defaultdict(list)
    domain_counts: dict[str, int] = defaultdict(int)
    family_linked_count = 0
    with_photo_count = 0
    with_quote_count = 0
    featured_profiles: list[dict] = []

    for row in rows:
        (
            pid, name, source, cat, cat_kr, desc, photo, birth, death,
            country, org, role, sitelinks, wiki_url, quote_url,
            edus_j, bps_j, fam_j, awards_j, occs_j,
        ) = row
        edus = json.loads(edus_j or "[]")
        bps = json.loads(bps_j or "[]")
        fam = json.loads(fam_j or "{}")
        awards = json.loads(awards_j or "[]")
        occs = json.loads(occs_j or "[]")

        domain_counts[cat] += 1
        if photo:
            with_photo_count += 1
        if quote_url:
            with_quote_count += 1
        if any(fam.values()):
            family_linked_count += 1

        mini = {"id": pid, "name": name, "category": cat, "role": role, "org": org, "photo": photo}
        for school in edus:
            alumni_map[school].append(mini)
        for place in bps:
            regional_map[place].append(mini)

        if len(featured_profiles) < 1200:
            featured_profiles.append(
                {
                    "id": pid, "name": name, "category": cat, "category_kr": cat_kr,
                    "entity_type": "개인", "primary_org": org or country or "글로벌",
                    "primary_role": role or ", ".join(occs[:2]) or cat_kr,
                    "photo_webp": photo, "profile_summary": desc,
                    "birth_date": birth, "death_date": death, "country": country,
                    "sitelinks": sitelinks, "source_url": wiki_url, "wikiquote_url": quote_url,
                    "educations": edus, "birth_places": bps, "family": fam, "awards": awards,
                }
            )

    alumni_clusters = [
        {"cluster": k, "count": len(v), "members": v[:25]}
        for k, v in sorted(alumni_map.items(), key=lambda kv: -len(kv[1]))
        if len(v) >= 2
    ][:300]

    regional_clusters = [
        {"cluster": k, "count": len(v), "members": v[:25]}
        for k, v in sorted(regional_map.items(), key=lambda kv: -len(kv[1]))
        if len(v) >= 2
    ][:300]

    clusters_payload = {
        "schema": "lets_people_clusters_v1",
        "generated_at": now_iso,
        "total_people": len(rows),
        "with_photo_count": with_photo_count,
        "with_wikiquote_count": with_quote_count,
        "family_linked_count": family_linked_count,
        "domain_breakdown": dict(domain_counts),
        "alumni_clusters_total": len(alumni_map),
        "regional_clusters_total": len(regional_map),
        "alumni_clusters": alumni_clusters,
        "regional_clusters": regional_clusters,
    }
    (DATA / "people_clusters.json").write_text(
        json.dumps(clusters_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    catalog_payload = {
        "schema": "lets_people_global_catalog_v1",
        "last_updated": now_iso,
        "source": "Wikidata SPARQL + wbgetentities + Elite Network + Medical DB",
        "total_indexed_people": len(rows),
        "with_photo_count": with_photo_count,
        "domain_breakdown": dict(domain_counts),
        "featured_profiles": featured_profiles,
    }
    (DATA / "global_people_catalog.json").write_text(
        json.dumps(catalog_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Export 64 sharded JSON files (data/profiles/00.json .. 3f.json) so every
    # single one of the 21,710+ people has an instant person.html?id=... page.
    profiles_dir = DATA / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    buckets: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        (
            pid, name, source, cat, cat_kr, desc, photo, birth, death,
            country, org, role, sitelinks, wiki_url, quote_url,
            edus_j, bps_j, fam_j, awards_j, occs_j,
        ) = row
        bucket_key = f"{sum(ord(c) for c in pid) % 64:02x}"
        buckets[bucket_key][pid] = {
            "id": pid,
            "name": name,
            "source": source,
            "category": cat,
            "category_kr": cat_kr,
            "description": desc,
            "photo_url": photo,
            "birth_date": birth,
            "death_date": death,
            "country": country,
            "primary_org": org,
            "primary_role": role,
            "sitelinks": sitelinks,
            "wikipedia_url": wiki_url,
            "wikiquote_url": quote_url,
            "educations": json.loads(edus_j or "[]"),
            "birth_places": json.loads(bps_j or "[]"),
            "family": json.loads(fam_j or "{}"),
            "awards": json.loads(awards_j or "[]"),
            "occupations": json.loads(occs_j or "[]"),
        }
    for bkey, bmap in buckets.items():
        (profiles_dir / f"{bkey}.json").write_text(
            json.dumps({"bucket": bkey, "count": len(bmap), "profiles": bmap}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return clusters_payload


def collect_all() -> dict:
    now_iso = datetime.now(KST).isoformat()
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    _init_db(conn)

    elite_count = _ingest_elite_network(conn, now_iso)
    med_count = _ingest_medical_db(conn, now_iso)

    qid_meta: dict[str, tuple[int, str]] = {}
    for q in DOMAIN_QUERIES:
        try:
            pairs = _sparql_qids(q["where"], q["limit"])
            for qid, sl in pairs:
                if qid not in qid_meta or sl > qid_meta[qid][0]:
                    qid_meta[qid] = (sl, q["category"])
            print(f"  - {q['domain']}: {len(pairs)} QIDs")
            time.sleep(0.5)
        except Exception as exc:
            print(f"  ! {q['domain']} SPARQL error: {exc}")

    all_qids = list(qid_meta.keys())
    entities = _fetch_entities(all_qids, props="labels|descriptions|claims|sitelinks")

    # Collect all referenced QIDs (occupations, schools, birthplaces, countries, orgs, awards, family)
    ref_qids: set[str] = set()
    for ent in entities.values():
        claims = ent.get("claims") or {}
        for prop in ("P106", "P69", "P19", "P27", "P108", "P166", "P26", "P22", "P25"):
            ref_qids.update(_claim_qids(claims, prop, limit=5))
    ref_labels = _fetch_entities(list(ref_qids), props="labels") if ref_qids else {}

    def resolve_labels(claims: dict, prop: str, limit: int = 5) -> list[str]:
        out = []
        for rq in _claim_qids(claims, prop, limit=limit):
            lbl = _label(ref_labels.get(rq) or {})
            if lbl:
                out.append(lbl)
        return list(dict.fromkeys(out))

    wikidata_count = 0
    for qid, ent in entities.items():
        name = _label(ent)
        if not name:
            continue
        claims = ent.get("claims") or {}
        sitelinks = ent.get("sitelinks") or {}
        sl_count = max(len(sitelinks), qid_meta.get(qid, (0, "corporate"))[0])
        default_cat = qid_meta.get(qid, (0, "corporate"))[1]

        occs = resolve_labels(claims, "P106", 6)
        cat, cat_kr = _classify_category(occs, default_cat)
        edus = resolve_labels(claims, "P69", 6)
        bps = resolve_labels(claims, "P19", 4)
        countries = resolve_labels(claims, "P27", 3)
        orgs = resolve_labels(claims, "P108", 4)
        awards = resolve_labels(claims, "P166", 5)
        spouses = resolve_labels(claims, "P26", 4)
        fathers = resolve_labels(claims, "P22", 2)
        mothers = resolve_labels(claims, "P25", 2)
        family = {}
        if fathers:
            family["father"] = fathers
        if mothers:
            family["mother"] = mothers
        if spouses:
            family["spouse"] = spouses

        ko_wiki = (sitelinks.get("kowiki") or {}).get("title")
        en_wiki = (sitelinks.get("enwiki") or {}).get("title")
        en_quote = (sitelinks.get("enwikiquote") or {}).get("title")
        wiki_url = f"https://ko.wikipedia.org/wiki/{quote(ko_wiki.replace(' ', '_'))}" if ko_wiki else (
            f"https://en.wikipedia.org/wiki/{quote(en_wiki.replace(' ', '_'))}" if en_wiki else ""
        )
        quote_url = f"https://en.wikiquote.org/wiki/{quote(en_quote.replace(' ', '_'))}" if en_quote else ""

        _upsert_person(
            conn,
            {
                "id": f"wd-{qid}", "name": name, "source": "wikidata_sparql",
                "category": cat, "category_kr": cat_kr, "description": _desc(ent),
                "photo_url": _claim_image(claims), "birth_date": _claim_time(claims, "P569"),
                "death_date": _claim_time(claims, "P570"), "country": ", ".join(countries),
                "primary_org": ", ".join(orgs[:2]), "primary_role": ", ".join(occs[:2]) or cat_kr,
                "sitelinks": sl_count, "wikipedia_url": wiki_url, "wikiquote_url": quote_url,
                "educations": edus, "birth_places": bps, "family": family,
                "awards": awards, "occupations": occs, "updated_at": now_iso,
            },
        )
        wikidata_count += 1
    conn.commit()

    clusters = build_clusters_and_exports(conn, now_iso)
    conn.close()
    print(
        f"Total real people in SQLite: {clusters['total_people']} "
        f"(wikidata={wikidata_count}, elite={elite_count}, medical={med_count}, "
        f"photos={clusters['with_photo_count']}, "
        f"alumni_clusters={clusters['alumni_clusters_total']}, "
        f"regional_clusters={clusters['regional_clusters_total']}, "
        f"family_linked={clusters['family_linked_count']})"
    )
    return clusters


if __name__ == "__main__":
    collect_all()
