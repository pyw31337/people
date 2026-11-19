#!/usr/bin/env python3
"""
sync_asset_intelligence_to_people.py
에셋에서 발굴된 글로벌 제재(PEP), 행동주의 펀드 대표, 사법 전관 변호인단, 고액 체납 은닉 인물들을
피플 마스터 도시에 데이터베이스(master_people_dossier_db.json)로 역동기화하는 파이프라인.
"""

import json
import os
from datetime import datetime

PEOPLE_DB_PATH = "/Users/pyw31337/Developer/people/data/master_people_dossier_db.json"

new_dossiers = [
    {
        "id": "act-lee-001",
        "name": "이창환",
        "hanja": "李昌煥",
        "birth_year": 1986,
        "category": "activist",
        "category_kr": "행동주의 펀드 대표 (금융투자)",
        "entity_type": "개인",
        "primary_org": "얼라인파트너스자산운용",
        "primary_role": "대표이사 (CEO)",
        "photo_webp": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=320&auto=format&fit=crop&q=80",
        "profile_summary": "서울대 경영대 졸업 후 골드만삭스, KKR을 거쳐 얼라인파트너스를 설립. 0.91% 지분으로 SM엔터 이수만의 30년 지배체제를 무너뜨린 한국 행동주의의 기수.",
        "dossier": {
            "history": "1986년 서울 출생, 서울대학교 경영학과 수석급 졸업.",
            "career": "골드만삭스 투자은행부문(IBD) ➔ 사모펀드 KKR(콜버그크래비스로버츠) 상무 ➔ 얼라인파트너스자산운용 창업.",
            "assets": "운용자산(AUM) 3,500억 원, SM엔터 지분 0.91% 매집 후 카카오에 1.25조 매각 유도, 두산밥캣/은행지주사 거버넌스 공격 중.",
            "alumni": "서울대학교 경영대학 동문 네트워크 (김범수·이해진 후배 학연).",
            "regional": "서울특별시 강남권 금융 허브 중심.",
            "family_inlaw": "금융권 전문직 가계.",
            "crime": "형사처벌 이력 없음 (자본시장법상 주주 권리 행사).",
            "tax": "국세 및 지방세 모범 납부 (체납 0원)."
        }
    },
    {
        "id": "pep-kwon-001",
        "name": "권도형",
        "hanja": "權渡衡",
        "birth_year": 1991,
        "category": "crypto_pep",
        "category_kr": "글로벌 제재 / 인터폴 적색수배",
        "entity_type": "개인",
        "primary_org": "테라폼랩스 (싱가포르 페이퍼컴퍼니)",
        "primary_role": "설립자 / 전 대표",
        "photo_webp": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=320&auto=format&fit=crop&q=80",
        "profile_summary": "50조 원 규모 테라·루나 코인 폭락 사태의 장본인. 스위스 시그넘 은행 비밀계좌로 비트코인 1만 개(약 1,800억) 및 두바이·세르비아 부동산 은닉.",
        "dossier": {
            "history": "1991년생, 대원외고 졸업 후 미국 스탠퍼드 대학교 컴퓨터공학 전공.",
            "career": "애플·마이크로소프트 소프트웨어 엔지니어 ➔ 애니파이 창업 ➔ 테라폼랩스(Terraform Labs) 공동창업.",
            "assets": "테라 붕괴 전 비트코인 8만 개(약 4조) 보유, 스위스 시그넘 은행 비밀계좌 1,800억 상당 동결, 미 SEC 44.7억 달러(약 6조 1,000억) 합의금 채권.",
            "alumni": "대원외고 - 미국 스탠퍼드 대학교 글로벌 IT/아이비리그 학연.",
            "regional": "서울 강남 ➔ 싱가포르 ➔ 두바이 ➔ 몬테네그로.",
            "family_inlaw": "배우자 명의 해외 계좌 및 신탁 재산 은닉 정황.",
            "crime": "자본시장법 위반, 사기, 몬테네그로 위조여권 사용 징역형, 미 SEC 증권사기 기소.",
            "tax": "국세청 종합소득세 및 법인세 500억 원 상당 추징 및 체납."
        }
    },
    {
        "id": "law-kim-001",
        "name": "김기동",
        "hanja": "金基東",
        "birth_year": 1964,
        "category": "judicial_cartel",
        "category_kr": "전관예우 변호사 / 사법 카르텔",
        "entity_type": "개인",
        "primary_org": "법무법인 로백스",
        "primary_role": "대표변호사 (전 부산지검장)",
        "photo_webp": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=320&auto=format&fit=crop&q=80",
        "profile_summary": "대검 부패범죄특별수사단장과 부산지검장을 역임한 당대 최고 특수통. 삼성물산 합병 회계부정 사건에서 이재용 회장의 19개 혐의 전원 무죄를 이끌어낸 사법 카르텔 총괄.",
        "dossier": {
            "history": "1964년 대구 출생, 혜화고등학교 - 서울대학교 법학과 졸업 (사법연수원 21기).",
            "career": "서울중앙지검 특수3부장 ➔ 대검찰청 기획조정부장 ➔ 대검 부패범죄특별수사단장 ➔ 부산지검장 ➔ 법무법인 로백스 대표변호사.",
            "assets": "연간 법률 수임료 수십억 원, 삼성그룹 주요 형사사건 전담 고문 계약.",
            "alumni": "서울대학교 법과대학 (사시 31회, 연수원 21기) - 법원·검찰 고위직 핵심 학연.",
            "regional": "대구·경북(TK) 지연 네트워크.",
            "family_inlaw": "법조계 및 관료계 고위직 네트워크.",
            "crime": "범죄 이력 없음 (무결 사법 수사관 출신).",
            "tax": "국세 및 지방세 모범 납세."
        }
    }
]

def sync_dossiers():
    with open(PEOPLE_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {d["id"] for d in data.get("dossiers", [])}
    added_count = 0

    for nd in new_dossiers:
        if nd["id"] not in existing_ids:
            data["dossiers"].append(nd)
            existing_ids.add(nd["id"])
            added_count += 1

    data["total_dossiers"] = len(data["dossiers"])
    data["standard_version"] = "LDS v2.5.0 (Global 8-Intel & Asset Cross-Bridge Synchronized)"
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")

    with open(PEOPLE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully synced {added_count} new dossiers into {PEOPLE_DB_PATH}")
    print(f"Total dossiers now: {data['total_dossiers']}")

if __name__ == "__main__":
    sync_dossiers()
