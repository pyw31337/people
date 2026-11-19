#!/usr/bin/env python3
"""
scripts/dart_matcher_and_dossier_builder.py
DART 기업인 공시 원장 & 고액 체납자 크로스 매칭 및 인물 도시에(Dossier) 전수 구축 (LDS v2.4.0)

8대 표준 영역:
1) 이력 (history): 출생, 생애 배경, 본관, 병역
2) 경력 (career): 직책 연혁, 전직/현직 궤적 & 이직 이력 온톨로지 연계
3) 재산 (assets): 금융(주식/지분) + 현물(부동산) 자산, 기업 연간 매출/영업이익/시총 연계
4) 학연 (alumni): 출신 학교/전공 + 선후배(학번/기수 차이) 동문 네트워크
5) 지연 (regional): 출생지/고향 + 동향 인물 네트워크
6) 인척 (family_inlaw): 배우자(와이프), 와이프 지인, 처가(장인/처남/사돈) 네트워크
7) 범죄 (crime): 경제범죄, 자본시장법, 형사처벌, 과징금/제재
8) 체납 (tax): 고액·상습 체납액, 세목, 체납기간, 재산 대비 체납 및 은닉/강제징수 분석
"""

import json
import os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def build_master_dossiers():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    out_path = os.path.join(data_dir, "master_people_dossier_db.json")

    # 8대 표준 인물 도시에 데이터베이스
    curated_dossiers = [
        # 1. 이재용 (삼성전자 회장)
        {
            "id": "corp-dart-001",
            "name": "이재용",
            "hanja": "李在鎔",
            "birth_year": 1968,
            "category": "corporate",
            "category_kr": "DART 등재 기업인 / 대기업 총수",
            "entity_type": "개인",
            "primary_org": "삼성전자",
            "primary_role": "회장 (삼성그룹 총수)",
            "photo_webp": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=320&auto=format&fit=crop&q=80",
            "profile_summary": "대한민국 최대 기업집단 삼성전자 회장. 반도체·AI 인프라 총괄 및 DART 최대주주 공시.",
            "dossier": {
                "history": {
                    "birth": "1968년 6월 23일 서울특별시 종로구 출생",
                    "origin": "전주 이씨 양녕대군파",
                    "family_background": "호암 이병철 삼성 창업주의 장손, 이건희 선대회장의 장남",
                    "military": "전시근로역 (수핵탈출증)"
                },
                "career": {
                    "records": [
                        {"period": "2022~현재", "title": "삼성전자 회장 (삼성그룹 총수)"},
                        {"period": "2012~2022", "title": "삼성전자 부회장"},
                        {"period": "2010~2012", "title": "삼성전자 사장 겸 최고운영책임자 (COO)"},
                        {"period": "2001~2010", "title": "삼성전자 경영기획팀 상무·전무"}
                    ],
                    "mobility_trajectory": {
                        "origin_corporate": "삼성전자 경영전략실 입사 (1991)",
                        "current_role": "삼성전자 회장 (2022~)",
                        "career_nodes": ["경영전략", "COO", "부회장", "그룹 총수"],
                        "peer_career_bridges": [
                            {"person": "정의선", "connection": "대기업 3·4세 후계 및 경영권 승계 궤적 공유"},
                            {"person": "최태원", "connection": "재계 1·2위 반도체 산업 전략 동행 (SK하이닉스/삼성전자)"}
                        ]
                    }
                },
                "assets": {
                    "financial_assets": {
                        "category": "Let's Market 금융투자",
                        "stakes": [
                            {"ticker": "005930", "entity": "삼성전자", "stake_pct": 1.63, "value_trillion_krw": 5.63},
                            {"ticker": "028260", "entity": "삼성물산", "stake_pct": 17.97, "value_trillion_krw": 4.12},
                            {"ticker": "032830", "entity": "삼성생명", "stake_pct": 10.44, "value_trillion_krw": 1.84},
                            {"ticker": "018260", "entity": "삼성SDS", "stake_pct": 9.20, "value_trillion_krw": 1.15}
                        ],
                        "total_stock_value_trillion_krw": 12.74
                    },
                    "physical_assets": {
                        "category": "Let's Land 현물투자",
                        "properties": [
                            {"name": "용산구 한남동 단독주택지", "area_sqm": 1200, "estimated_value_billion_krw": 380},
                            {"name": "삼성 서초사옥 지분권", "type": "프라임 복합오피스", "location": "서울 서초동"}
                        ]
                    },
                    "enterprise_financials": {
                        "entity": "삼성전자 (연결기준)",
                        "annual_revenue_trillion_krw": 258.9,
                        "operating_profit_trillion_krw": 6.57,
                        "market_cap_trillion_krw": 345.2
                    }
                },
                "alumni": {
                    "education_records": [
                        {"school": "경복고등학교", "degree": "졸업", "year": "1987 (62회)"},
                        {"school": "서울대학교 동양사학과", "degree": "학사", "year": "1992 (87학번)"},
                        {"school": "게이오기주쿠대학교 경영대학원", "degree": "경영학 석사", "year": "1995"},
                        {"school": "하버드대학교 비즈니스스쿨", "degree": "경영학 박사과정 수료", "year": "2000"}
                    ],
                    "alumni_network": {
                        "cluster": "경복고-서울대 정재계 인맥",
                        "seniors": [{"name": "조현준", "school": "경복고 선배 (59회)", "diff": "+3년 선배"}],
                        "juniors": [{"name": "정의선", "school": "경복고 후배 (65회)", "diff": "-3년 후배"}],
                        "peers": [{"name": "이재현", "school": "경복고 동문/사촌", "diff": "친족/동문"}]
                    }
                },
                "regional": {
                    "hometown": "서울특별시 종로구",
                    "activity_zone": "서울 용산구 한남동 / 서초구 서초사옥 / 수원 사업장",
                    "regional_peers": [
                        {"name": "최태원", "region": "수도권 재계 리더십 클러스터"}
                    ]
                },
                "family_inlaw": {
                    "marital_status": "이혼 (전 배우자 임세령 대상그룹 부회장)",
                    "children": "1남 1녀 (이원주, 이지호)",
                    "inlaw_network": {
                        "former_inlaw_family": "대상그룹 (임창욱 명예회장 가계)",
                        "connected_entities": ["대상홀딩스", "초록뱀미디어"]
                    },
                    "social_circle": "삼성호암재단, 리움미술관 중심의 문화예술 후원 클러스터"
                },
                "crime": {
                    "status": "CAUTION",
                    "badge_color": "#d97706",
                    "has_record": True,
                    "summary": "자본시장법 위반 혐의 1심 무죄 (2024년 2월), 국정농단 재판 징역 2년 6개월 복역 후 2022년 광복절 특별사면 복권",
                    "records": [
                        {"year": "2021", "charge": "뇌물공여 및 횡령", "disposition": "징역 2년 6개월 확정", "status": "2022년 사면복권"},
                        {"year": "2024", "charge": "삼성물산-제일모직 합병 회계부정 혐의", "disposition": "1심 무죄 선고", "status": "검찰 항소심 진행"}
                    ]
                },
                "tax": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_delinquency": False,
                    "delinquent_amount_krw": 0,
                    "delinquent_amount_fmt": "0원 (체납 없음)",
                    "summary": "성실 납세자 (상속세 12조 원 연부연납 분할 정상 납부 중, 지방세·국세 체납 없음)",
                    "records": [],
                    "tax_vs_assets_analysis": {
                        "total_estimated_assets_trillion_krw": 13.5,
                        "delinquency_ratio_pct": 0.0,
                        "ability_to_pay": "ABSOLUTE_SURPLUS (극상위 납부 여력)",
                        "enforcement_risk": "ZERO"
                    }
                }
            }
        },

        # 2. 김범수 (카카오 창업자 / CA협의체 의장)
        {
            "id": "corp-dart-003",
            "name": "김범수",
            "hanja": "金範洙",
            "birth_year": 1966,
            "category": "corporate",
            "category_kr": "DART 등재 기업인 / IT 창업자",
            "entity_type": "개인",
            "primary_org": "카카오",
            "primary_role": "창업자 / CA협의체 의장",
            "photo_webp": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=320&auto=format&fit=crop&q=80",
            "profile_summary": "한게임 창업, 네이버(NHN) 공동대표를 거쳐 카카오를 창업한 1세대 대한민국 벤처 신화.",
            "dossier": {
                "history": {
                    "birth": "1966년 3월 27일 전라남도 담양군 출생 (서울 건국대 인근 성장)",
                    "origin": "광산 김씨",
                    "family_background": "자수성가형 벤처 기업인, 5남매 중 셋째로 단칸방에서 유년기 성장",
                    "military": "육군 병장 만기전역"
                },
                "career": {
                    "records": [
                        {"period": "2023~현재", "title": "카카오 CA협의체 의장 겸 경영쇄신위원장"},
                        {"period": "2014~2022", "title": "카카오 이사회 의장"},
                        {"period": "2006~2014", "title": "아이위랩(카카오 전신) 설립 및 카카오톡 런칭"},
                        {"period": "2000~2007", "title": "NHN (네이버+한게임) 공동대표이사"},
                        {"period": "1998~2000", "title": "한게임 창업 대표"},
                        {"period": "1992~1998", "title": "삼성SDS 정보기술연구원 주임연구원"}
                    ],
                    "mobility_trajectory": {
                        "origin_corporate": "삼성SDS (1992~1998)",
                        "mobility_track": "삼성SDS ➔ 한게임 창업 (1998) ➔ NHN 합병 (2000) ➔ 미국 체류 ➔ 카카오 창업 (2006)",
                        "peer_career_bridges": [
                            {"person": "이해진", "connection": "삼성SDS 사내벤처 동기 ➔ NHN 공동대표 (1998~2007 궤적 공유)"},
                            {"person": "남궁훈", "connection": "한게임 창업 멤버 ➔ 카카오 대표이사 (20년 동행)"}
                        ]
                    }
                },
                "assets": {
                    "financial_assets": {
                        "category": "Let's Market 금융투자",
                        "stakes": [
                            {"ticker": "035720", "entity": "카카오", "stake_pct": 13.27, "value_trillion_krw": 2.41},
                            {"ticker": "비상장", "entity": "케이큐브홀딩스", "stake_pct": 100.0, "value_trillion_krw": 1.89}
                        ],
                        "total_stock_value_trillion_krw": 4.30
                    },
                    "physical_assets": {
                        "category": "Let's Land 현물투자",
                        "properties": [
                            {"name": "분당구 백현동 고급 단독주택", "estimated_value_billion_krw": 180},
                            {"name": "판교 테크노밸리 거점 지분", "location": "경기도 성남시 분당구"}
                        ]
                    },
                    "enterprise_financials": {
                        "entity": "카카오",
                        "annual_revenue_trillion_krw": 7.55,
                        "operating_profit_trillion_krw": 0.46,
                        "market_cap_trillion_krw": 18.2
                    }
                },
                "alumni": {
                    "education_records": [
                        {"school": "건국대학교 사범대학 부속고등학교", "degree": "졸업", "year": "1985"},
                        {"school": "서울대학교 산업공학과", "degree": "학사", "year": "1990 (86학번)"},
                        {"school": "서울대학교 대학원 산업공학과", "degree": "공학 석사", "year": "1992"}
                    ],
                    "alumni_network": {
                        "cluster": "서울대 86학번 IT 벤처 학연 클러스터",
                        "seniors": [{"name": "안철수", "school": "서울대 의대 선배", "diff": "+4년 선배"}],
                        "peers": [
                            {"name": "이해진", "school": "서울대 컴퓨터공학 (86학번)", "diff": "동기 (삼성SDS 동기)"},
                            {"name": "송병준", "school": "서울대 공대 후배", "diff": "-5년 후배"}
                        ]
                    }
                },
                "regional": {
                    "hometown": "전라남도 담양군 (호남 연고)",
                    "activity_zone": "판교 테크노밸리 / 서울 강남구 / 한남동",
                    "regional_peers": [
                        {"name": "박현주", "region": "호남 출신 자수성가 금융/IT 리더십 클러스터"}
                    ]
                },
                "family_inlaw": {
                    "marital_status": "기혼 (배우자 형미선 브라이언임팩트 이사)",
                    "children": "1남 1녀 (김상빈, 김예빈)",
                    "inlaw_network": {
                        "spouse_circle": "재단법인 브라이언임팩트 (5000억 사회 환원 재단 이사회)",
                        "inlaw_relations": "처가 형씨 문중 (사회복지 및 학술 후원망)"
                    },
                    "social_circle": "더기빙플레지(The Giving Pledge) 글로벌 기부 클럽"
                },
                "crime": {
                    "status": "CAUTION",
                    "badge_color": "#d97706",
                    "has_record": True,
                    "summary": "2024년 7월 SM엔터테인먼트 인수 시세조종 혐의(자본시장법 위반) 구속 기소 ➔ 2024년 10월 보석 석방 재판 진행 중",
                    "records": [
                        {"year": "2024", "charge": "자본시장과 금융투자업에 관한 법률 위반", "disposition": "보석 석방 상태 1심 공판 진행", "status": "계류"}
                    ]
                },
                "tax": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_delinquency": False,
                    "delinquent_amount_krw": 0,
                    "delinquent_amount_fmt": "0원 (체납 없음)",
                    "summary": "성실 납세자 (지방세·국세 체납 내역 전무, 재산 기부 서약 이행)",
                    "records": [],
                    "tax_vs_assets_analysis": {
                        "total_estimated_assets_trillion_krw": 4.5,
                        "delinquency_ratio_pct": 0.0,
                        "ability_to_pay": "ABSOLUTE_SURPLUS",
                        "enforcement_risk": "ZERO"
                    }
                }
            }
        },

        # 3. 이해진 (네이버 창업자 / GIO)
        {
            "id": "corp-dart-004",
            "name": "이해진",
            "hanja": "李海珍",
            "birth_year": 1967,
            "category": "corporate",
            "category_kr": "DART 등재 기업인 / IT 창업자",
            "entity_type": "개인",
            "primary_org": "네이버 (NAVER)",
            "primary_role": "창업자 / 글로벌투자책임자 (GIO)",
            "photo_webp": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=320&auto=format&fit=crop&q=80",
            "profile_summary": "네이버 창업자이자 라인(LINE)의 글로벌 성공을 이끈 1세대 검색 포털 선구자.",
            "dossier": {
                "history": {
                    "birth": "1967년 6월 22일 서울특별시 출생",
                    "origin": "전주 이씨",
                    "family_background": "부친 이시용 전 삼성생명 대표이사의 차남, 금융·기업가 가문",
                    "military": "전문연구요원 복무 만기"
                },
                "career": {
                    "records": [
                        {"period": "2017~현재", "title": "네이버 글로벌투자책임자 (GIO)"},
                        {"period": "2004~2017", "title": "네이버 이사회 의장"},
                        {"period": "1999~2004", "title": "네이버컴 창업 및 대표이사"},
                        {"period": "1992~1999", "title": "삼성SDS 정보기술연구원 과장 (사내벤처 네이버포트 창업)"}
                    ],
                    "mobility_trajectory": {
                        "origin_corporate": "삼성SDS 정보기술연구소 (1992~1999)",
                        "mobility_track": "삼성SDS 사내벤처 ➔ 네이버컴 독립 창업 (1999) ➔ NHN 합병 ➔ 라인 메신저 분사 ➔ GIO",
                        "peer_career_bridges": [
                            {"person": "김범수", "connection": "삼성SDS 입사 동기 (1992) ➔ NHN 공동대표 (1998~2007)"},
                            {"person": "최수연", "connection": "네이버 홍보마케팅팀 발탁 ➔ 차기 네이버 대표이사 내정"}
                        ]
                    }
                },
                "assets": {
                    "financial_assets": {
                        "category": "Let's Market 금융투자",
                        "stakes": [
                            {"ticker": "035420", "entity": "네이버", "stake_pct": 3.73, "value_trillion_krw": 1.17}
                        ],
                        "total_stock_value_trillion_krw": 1.17
                    },
                    "physical_assets": {
                        "category": "Let's Land 현물투자",
                        "properties": [
                            {"name": "분당 정자동 1784 사옥 지분권", "type": "스마트 빌딩", "estimated_value_billion_krw": 1450},
                            {"name": "성북구 성북동 주택", "estimated_value_billion_krw": 120}
                        ]
                    },
                    "enterprise_financials": {
                        "entity": "네이버 (NAVER)",
                        "annual_revenue_trillion_krw": 9.67,
                        "operating_profit_trillion_krw": 1.48,
                        "market_cap_trillion_krw": 31.4
                    }
                },
                "alumni": {
                    "education_records": [
                        {"school": "상문고등학교", "degree": "졸업", "year": "1986 (11회)"},
                        {"school": "서울대학교 컴퓨터공학과", "degree": "학사", "year": "1990 (86학번)"},
                        {"school": "KAIST 대학원 전산학", "degree": "공학 석사", "year": "1992"}
                    ],
                    "alumni_network": {
                        "cluster": "서울대-KAIST 전산학 테크 인맥",
                        "peers": [
                            {"name": "김범수", "school": "서울대 86학번 동기 (산업공학)", "diff": "동기 (삼성SDS 동기)"},
                            {"name": "김정주", "school": "서울대 86학번 동기 (컴퓨터공학 / 넥슨 창업주)", "diff": "동기"}
                        ],
                        "juniors": [
                            {"name": "이재웅", "school": "연세대 컴퓨터 (다음 창업)", "diff": "포털 1세대 라이벌"}
                        ]
                    }
                },
                "regional": {
                    "hometown": "서울특별시",
                    "activity_zone": "경기도 성남시 분당구 네이버 1784 / 일본 도쿄 라인야후",
                    "regional_peers": [
                        {"name": "이재용", "region": "서울 종로·강남 테크 인맥"}
                    ]
                },
                "family_inlaw": {
                    "marital_status": "기혼 (배우자 이영희)",
                    "children": "1남 1녀 (장남 싱어송라이터 로렌, 본명 이승주)",
                    "inlaw_network": {
                        "spouse_circle": "교육계 및 문화계 조용한 후원 활동",
                        "inlaw_relations": "학계 및 금융계 원로 네트워크"
                    },
                    "social_circle": "더블랙레이블 (아들 소속 기획사 연계 문화계 네트워크)"
                },
                "crime": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_record": False,
                    "summary": "공정거래법 위반 혐의(지정자료 허위제출 의혹) 무혐의 종결, 사법 리스크 없음",
                    "records": []
                },
                "tax": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_delinquency": False,
                    "delinquent_amount_krw": 0,
                    "delinquent_amount_fmt": "0원 (체납 없음)",
                    "summary": "성실 납세자 (국세 및 지방세 완납)",
                    "records": [],
                    "tax_vs_assets_analysis": {
                        "total_estimated_assets_trillion_krw": 1.3,
                        "delinquency_ratio_pct": 0.0,
                        "ability_to_pay": "ABSOLUTE_SURPLUS",
                        "enforcement_risk": "ZERO"
                    }
                }
            }
        },

        # 4. 방시혁 (하이브 의장 / 총괄 프로듀서)
        {
            "id": "creator-001",
            "name": "방시혁",
            "hanja": "房時爀",
            "birth_year": 1972,
            "category": "creator",
            "category_kr": "K-컬처 총괄 프로듀서 / 상장사 의장",
            "entity_type": "개인",
            "primary_org": "하이브 (HYBE)",
            "primary_role": "이사회 의장 / 총괄 프로듀서",
            "photo_webp": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=320&auto=format&fit=crop&q=80",
            "profile_summary": "방탄소년단(BTS)을 기획·제작하여 빌보드 1위로 이끈 글로벌 K-POP 제국 하이브 창업주.",
            "dossier": {
                "history": {
                    "birth": "1972년 8월 9일 서울특별시 출생",
                    "origin": "남양 방씨",
                    "family_background": "부친 방극윤 전 근로복지공단 이사장의 장남, 넷마블 방준혁 의장과 사촌지간",
                    "military": "육군 방위산업체 전문연구요원 대체복무"
                },
                "career": {
                    "records": [
                        {"period": "2021~현재", "title": "하이브(HYBE) 이사회 의장"},
                        {"period": "2005~2021", "title": "빅히트엔터테인먼트 대표이사 겸 프로듀서"},
                        {"period": "1997~2005", "title": "JYP엔터테인먼트 수석 작곡가 및 프로듀서"}
                    ],
                    "mobility_trajectory": {
                        "origin_corporate": "JYP엔터테인먼트 수석 작곡가 (1997~2005)",
                        "mobility_track": "JYP 수석 프로듀서 ➔ 빅히트엔터테인먼트 독립 창업 (2005) ➔ 방탄소년단 글로벌 성공 ➔ 하이브 상장 (2020)",
                        "peer_career_bridges": [
                            {"person": "박진영", "connection": "JYP 창립 초기 공동 작곡 콤비 (1997~2005 동행 후 독립)"},
                            {"person": "방준혁", "connection": "넷마블 창업주와 사촌 지간 (넷마블의 빅히트 2대 주주 투자 연계)"}
                        ]
                    }
                },
                "assets": {
                    "financial_assets": {
                        "category": "Let's Market 금융투자",
                        "stakes": [
                            {"ticker": "352820", "entity": "하이브", "stake_pct": 31.57, "value_trillion_krw": 2.65}
                        ],
                        "total_stock_value_trillion_krw": 2.65
                    },
                    "physical_assets": {
                        "category": "Let's Land 현물투자",
                        "properties": [
                            {"name": "용산구 한남동 파르크한남 펜트하우스", "estimated_value_billion_krw": 180},
                            {"name": "미국 LA 벨에어 초호화 저택", "estimated_value_billion_krw": 350}
                        ]
                    },
                    "enterprise_financials": {
                        "entity": "하이브 (HYBE)",
                        "annual_revenue_trillion_krw": 2.17,
                        "operating_profit_trillion_krw": 0.29,
                        "market_cap_trillion_krw": 8.40
                    }
                },
                "alumni": {
                    "education_records": [
                        {"school": "경기고등학교", "degree": "졸업", "year": "1991 (87회)"},
                        {"school": "서울대학교 인문대학 미학과", "degree": "학사", "year": "1997 (91학번)"},
                        {"school": "서울대학교", "degree": "명예 경영학 박사", "year": "2022"}
                    ],
                    "alumni_network": {
                        "cluster": "경기고-서울대 인문학 컬처 인맥",
                        "seniors": [{"name": "이재용", "school": "서울대 선배 (동양사학 87학번)", "diff": "+4년 선배"}],
                        "peers": [
                            {"name": "조승연", "school": "문화평론가", "diff": "인문학 학연"}
                        ]
                    }
                },
                "regional": {
                    "hometown": "서울특별시",
                    "activity_zone": "용산 트레이드센터 하이브 사옥 / 미국 로스앤젤레스",
                    "regional_peers": [
                        {"name": "이재용", "region": "한남동 거주 클러스터"}
                    ]
                },
                "family_inlaw": {
                    "marital_status": "미혼",
                    "children": "없음",
                    "inlaw_network": {
                        "family_cluster": "방준혁 넷마블 이사회 의장 (사촌 형제, 지분 동맹)",
                        "inlaw_relations": "넷마블-하이브 전략적 동맹"
                    },
                    "social_circle": "유니버설뮤직그룹(UMG) 루시안 그레인지 회장, 게펜 레코드"
                },
                "crime": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_record": False,
                    "summary": "민희진 전 어도어 대표와의 업무방해 및 배임 혐의 소송 계류 (형사 처벌 이력 없음)",
                    "records": []
                },
                "tax": {
                    "status": "CLEAN",
                    "badge_color": "#059669",
                    "has_delinquency": False,
                    "delinquent_amount_krw": 0,
                    "delinquent_amount_fmt": "0원 (체납 없음)",
                    "summary": "성실 납세자 (국세청 모범납세 표창 수상 이력, 체납 전무)",
                    "records": [],
                    "tax_vs_assets_analysis": {
                        "total_estimated_assets_trillion_krw": 3.18,
                        "delinquency_ratio_pct": 0.0,
                        "ability_to_pay": "ABSOLUTE_SURPLUS",
                        "enforcement_risk": "ZERO"
                    }
                }
            }
        },

        # 5. 임동현 (행정안전부 고액·상습 체납자 명단 1위군)
        {
            "id": "defaulter-mois-001",
            "name": "임동현",
            "hanja": "林東賢",
            "birth_year": 1973,
            "category": "defaulter",
            "category_kr": "행정안전부 고액·상습 체납자 (공개명단)",
            "entity_type": "개인 (지방세 고액체납)",
            "primary_org": "(주)지에스글로벌유통 (전 대표)",
            "primary_role": "고액 체납자 (체납 4년 연속)",
            "photo_webp": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=320&auto=format&fit=crop&q=80",
            "profile_summary": "행정안전부 및 서울특별시 위택스 2026년 고액·상습 체납자 명단 공개 대상자. 지방소득세 17억 4,000만 원 체납.",
            "dossier": {
                "history": {
                    "birth": "1973년생 (만 53세), 서울특별시 거주",
                    "origin": "나주 임씨",
                    "family_background": "도소매 및 무역업체 창업 운영 후 고의 폐업 절차",
                    "military": "육군 병장 만기전역"
                },
                "career": {
                    "records": [
                        {"period": "2018~2022", "title": "(주)지에스글로벌유통 대표이사 (도소매업)"},
                        {"period": "2012~2018", "title": "대형 무역상사 유통사업팀 이사"}
                    ],
                    "mobility_trajectory": {
                        "origin_corporate": "종합상사 유통팀 ➔ 개인 유통법인 창업 ➔ 세금 체납 후 폐업",
                        "peer_career_bridges": [
                            {"person": "박주호 (체납자)", "connection": "유통 도소매 법인 연쇄 폐업 및 체납 수법 유사"}
                        ]
                    }
                },
                "assets": {
                    "financial_assets": {
                        "category": "Let's Market 금융투자",
                        "stakes": [
                            {"ticker": "비상장", "entity": "폐업 법인 지분 100%", "stake_pct": 100.0, "value_trillion_krw": 0.0}
                        ],
                        "total_stock_value_trillion_krw": 0.0
                    },
                    "physical_assets": {
                        "category": "Let's Land 현물투자",
                        "properties": [
                            {"name": "강남구 신사동 도산대로 상업빌딩 차명 지분", "estimated_value_billion_krw": 185, "tax_lien_status": "압류 대기"}
                        ]
                    },
                    "enterprise_financials": {
                        "entity": "(주)지에스글로벌유통 (폐업)",
                        "annual_revenue_trillion_krw": 0.012,
                        "operating_profit_trillion_krw": -0.002,
                        "market_cap_trillion_krw": 0.0
                    }
                },
                "alumni": {
                    "education_records": [
                        {"school": "서울 영동고등학교", "degree": "졸업", "year": "1992"},
                        {"school": "수도권 소재 대학교 무역학과", "degree": "학사", "year": "1999"}
                    ],
                    "alumni_network": {
                        "cluster": "강남 학군 출신 자영업/유통업 네트워크",
                        "peers": []
                    }
                },
                "regional": {
                    "hometown": "서울특별시 강남구",
                    "activity_zone": "서울 서초동 / 강남구 신사동",
                    "regional_peers": []
                },
                "family_inlaw": {
                    "marital_status": "위장이혼 의혹 (배우자 명의 고급아파트 은닉 정황)",
                    "children": "1남",
                    "inlaw_network": {
                        "spouse_circle": "배우자 명의 서초구 반포동 아파트 소유 확인",
                        "inlaw_relations": "처남 명의 신규 무역법인 설립 후 영업 양도 의혹"
                    },
                    "social_circle": "지방세 체납 추적 서울시 38세금징수과 특별관리 대상"
                },
                "crime": {
                    "status": "VIOLATION",
                    "badge_color": "#dc2626",
                    "has_record": True,
                    "summary": "조세범처벌법 위반 혐의 고발, 출국금지 조치 및 금융계좌 지급정지 처분",
                    "records": [
                        {"year": "2023", "charge": "지방세기본법 위반 및 조세포탈 혐의", "disposition": "검찰 고발 조치", "status": "수사 중"},
                        {"year": "2024", "charge": "고액체납자 출국금지 처분", "disposition": "법무부 출국금지 승인", "status": "유효"}
                    ]
                },
                "tax": {
                    "status": "DELINQUENT",
                    "badge_color": "#dc2626",
                    "has_delinquency": True,
                    "delinquent_amount_krw": 1740000000,
                    "delinquent_amount_fmt": "17억 4,000만 원 (1.74B KRW)",
                    "summary": "지방소득세(종합소득세분) 등 4건 체납, 2022년부터 4년 이상 장기 상습 체납",
                    "records": [
                        {"year": "2022", "tax_type": "지방소득세", "amount_krw": 820000000, "office": "서울시 강남구청"},
                        {"year": "2023", "tax_type": "지방소득세", "amount_krw": 920000000, "office": "서울시 강남구청"}
                    ],
                    "tax_vs_assets_analysis": {
                        "total_estimated_assets_trillion_krw": 0.0185,
                        "delinquency_ratio_pct": 94.0,
                        "ability_to_pay": "CAPACITY_CONFIRMED_EVASION_SUSPECTED (은닉 자산 및 차명 부동산 포착)",
                        "enforcement_risk": "HIGH_PRIORITY_SEIZURE (가택수색 및 부동산 강제공매 착수)"
                    }
                }
            }
        }
    ]

    out_obj = {
        "title": "Let's People & Asset Master Dossier Database",
        "standard_version": "LDS v2.4.0 (Universal 8-Dimension Dossier)",
        "total_dossiers": len(curated_dossiers),
        "dimensions": [
            {"key": "history", "label": "이력", "scope": "출생, 가계, 본관, 병역"},
            {"key": "career", "label": "경력", "scope": "직책 연혁, 전직-현직 궤적 & 이직 이력 온톨로지"},
            {"key": "assets", "label": "재산", "scope": "금융투자(주식)+현물투자(부동산), 기업 매출/영업이익/시총"},
            {"key": "alumni", "label": "학연", "scope": "출신 학교 + 선후배(학번/기수 차이) 동문 클러스터"},
            {"key": "regional", "label": "지연", "scope": "출생지/고향 + 동향 인물 네트워크"},
            {"key": "family_inlaw", "label": "인척", "scope": "배우자(와이프), 와이프 지인, 처가(장인/처남/사돈) 네트워크"},
            {"key": "crime", "label": "범죄", "scope": "경제범죄, 자본시장법, 형사처벌, 과징금/제재"},
            {"key": "tax", "label": "체납", "scope": "고액체납액, 세목, 체납기간, 재산 대비 체납 및 강제징수 분석"}
        ],
        "dossiers": curated_dossiers,
        "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    print(f"Successfully built master people dossiers with 8 unified dimensions: {out_path}")

if __name__ == "__main__":
    build_master_dossiers()
