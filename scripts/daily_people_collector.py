#!/usr/bin/env python3
"""LetsPeople 24/7 real-data collector pipeline.

Replaces legacy static counters with genuine source-backed collection:
- Korean medical professionals (doctors, nurses, dentists, pharmacists) via Wikipedia API
- Global & Korean notable figures via Wikidata SPARQL + wbgetentities
- Local elite network (high officials, corporate leaders, legal elites, journalists)
- Alumni / regional / family / domain cluster analysis in SQLite + JSON
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from collection_health_monitor import run_health_check
from global_people_wikidata_collector import collect_all
from medical_professionals_collector import collect_medical_professionals

KST = timezone(timedelta(hours=9))


def run_ingest() -> dict:
    now_kst = datetime.now(KST).isoformat()
    med_res = collect_medical_professionals()
    global_res = collect_all()
    total_people = int(global_res.get("total_people") or 0)
    print(
        f"[{now_kst}] 렛츠피플 실측 수집 완료: "
        f"총 {total_people:,}명 (의료인 {med_res.get('total_medical_indexed', 0)}명, "
        f"사진 {global_res.get('with_photo_count', 0):,}명, "
        f"학연 클러스터 {global_res.get('alumni_clusters_total', 0):,}개, "
        f"지연 클러스터 {global_res.get('regional_clusters_total', 0):,}개)"
    )
    run_health_check(total_people)
    return global_res


if __name__ == "__main__":
    run_ingest()
