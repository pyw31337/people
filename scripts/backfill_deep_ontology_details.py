#!/usr/bin/env python3
"""
backfill_deep_ontology_details.py
렛츠피플(Let's People) 10만 명 인물 온톨로지 심층 백필러:
- 기존에 이름/직업만 있던 레코드에 대해
- 출신 고교/대학교(학력), 부모/배우자/자녀(가계도), 역임 직책 이력을
- 한국 주요 인물 온톨로지 딕셔너리 및 규칙 기반으로 자동 보강(Backfill)합니다.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB_PATH = DATA / "people_master.db"

# 주요 정·재계·학술 인물 심층 온톨로지 팩트셋
DEEP_ONTOLOGY_FACTS = {
    "이재용": {
        "educations": ["경기초등학교", "청운중학교", "경복고등학교", "서울대학교 동양사학 학사", "게이오기주쿠대학 경영학 석사", "하버드 비즈니스 스쿨 최고경영자과정 수료"],
        "family": {
            "father": ["이건희 (전 삼성전자 회장)"],
            "mother": ["홍라희 (전 리움미술관장)"],
            "grandfather": ["이병철 (삼성 창업회장)"],
            "sisters": ["이부진 (호텔신라 사장)", "이서현 (삼성물산 사장)"],
            "children": ["이지호", "이원주"]
        },
        "career_milestones": [
            "1991년 삼성전자 입사",
            "2010년 삼성전자 최고운영책임자(COO) 사장",
            "2012년 삼성전자 부회장",
            "2022년 10월 삼성전자 회장 취임"
        ]
    },
    "최태원": {
        "educations": ["신일고등학교", "고려대학교 물리학 학사", "시카고 대학교 대학원 경제학 석·박사과정"],
        "family": {
            "father": ["최종현 (SK그룹 선대회장)"],
            "uncle": ["최종건 (선경그룹 창업회장)"],
            "cousins": ["최창원 (SK디스커버리 부회장)", "최신원 (전 SK네트웍스 회장)"],
            "spouse_former": ["노소영 (아트센터 나비 관장)"],
            "partner": ["김희영 (티앤씨재단 이사장)"],
            "children": ["최윤정 (SK바이오팜 본부장)", "최민정", "최인근"]
        },
        "career_milestones": [
            "1998년 SK그룹 대표이사 회장 취임",
            "2021년 제24대 대한상공회의소 회장 취임"
        ]
    },
    "정의선": {
        "educations": ["휘문고등학교", "고려대학교 경영학 학사", "샌프란시스코 대학교 경영대학원 MBA"],
        "family": {
            "father": ["정몽구 (현대차그룹 명예회장)"],
            "grandfather": ["정주영 (현대그룹 창업주)"],
            "uncles": ["정몽준 (아산재단 이사장)", "정몽규 (HDC 회장)"],
            "spouse": ["정지선"]
        },
        "career_milestones": [
            "2005년 기아자동차 대표이사 사장",
            "2009년 현대자동차 부회장",
            "2020년 10월 현대자동차그룹 회장 취임"
        ]
    },
    "조정호": {
        "educations": ["경복고등학교", "서던캘리포니아 대학교(USC) 경제학 학사", "스위스 국제경영개발대학원(IMD) 석사"],
        "family": {
            "father": ["조중훈 (한진그룹 창업주)"],
            "brothers": ["조양호 (전 한진그룹 회장)", "조남호 (전 한진중공업 회장)"]
        },
        "career_milestones": [
            "2000년 한진투자증권 대표이사",
            "2005년 메리츠증권 회장",
            "2011년 메리츠금융지주 회장 취임"
        ]
    },
    "서정진": {
        "educations": ["제물포고등학교", "건국대학교 산업공학 학사", "건국대학교 대학원 경영학 석사"],
        "family": {
            "sons": ["서진석 (셀트리온 이사회 공동의장)", "서준석"]
        },
        "career_milestones": [
            "1985년 삼성전기 입사",
            "1991년 대우자동차 기획총괄 임원",
            "2002년 셀트리온 창업 및 바이오시밀러 양산 개척"
        ]
    },
    "이재명": {
        "educations": ["삼계국민학교", "중·고졸 검정고시", "중앙대학교 법학 학사 (장학생)"],
        "family": {
            "spouse": ["김혜경"],
            "sons": ["이동호", "이윤호"]
        },
        "career_milestones": [
            "1986년 제28회 사법시험 합격 (사법연수원 18기)",
            "2010년~2018년 제19·20대 성남시장",
            "2018년~2021년 제35대 경기도지사",
            "2022년 제21대 국회의원 (인천 계양구 을)",
            "2022년~현재 더불어민주당 대표"
        ]
    },
    "한동훈": {
        "educations": ["현대고등학교", "서울대학교 법학 학사", "컬럼비아 로스쿨 LL.M."],
        "family": {
            "spouse": ["진은정 (변호사)"],
            "father_in_law": ["진형구 (전 대전고검장)"]
        },
        "career_milestones": [
            "1995년 제37회 사법시험 합격 (사법연수원 27기)",
            "2017년 서울중앙지검 제3차장검사",
            "2022년 제69대 법무부장관",
            "2024년 국민의힘 당대표"
        ]
    }
}

def backfill():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now_kst = datetime.now(KST).isoformat()

    updated = 0
    for name, facts in DEEP_ONTOLOGY_FACTS.items():
        edu_json = json.dumps(facts.get("educations", []), ensure_ascii=False)
        fam_json = json.dumps(facts.get("family", {}), ensure_ascii=False)
        career_str = " · ".join(facts.get("career_milestones", []))

        cur.execute("""
            UPDATE people SET
                educations_json = ?,
                family_json = ?,
                description = CASE WHEN length(description) < 30 THEN ? ELSE description || ' | ' || ? END,
                updated_at = ?
            WHERE name = ?
        """, (edu_json, fam_json, career_str, career_str, now_kst, name))
        if cur.rowcount > 0:
            updated += cur.rowcount

    conn.commit()

    # 통계 확인
    cur.execute("SELECT count(*) FROM people WHERE family_json != '{}' AND family_json IS NOT NULL")
    fam_cnt = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM people WHERE educations_json != '[]' AND educations_json IS NOT NULL")
    edu_cnt = cur.fetchone()[0]
    conn.close()

    print(f"[{now_kst}] 렛츠피플 심층 온톨로지 보강 완료: 주요 인물 {updated}명 정밀 가계도/학력 매핑 (누적 가계도 보유: {fam_cnt:,}명, 학력 보유: {edu_cnt:,}명)")

if __name__ == "__main__":
    backfill()
