# 👤 렛츠피플 (Let's People) — 글로벌 12만 인물 & 영화·뮤지컬 포스터·제작비·BEP 인텔리전스

> **"모든 일은 사람이 한다"**는 대원칙 하에, **글로벌 124,500명 인물 원장**과 **영화·뮤지컬 14,200편 공식 포스터·제작비·손익분기점(BEP)·핵심 스태프 온톨로지**를 결합하여 **컬처플로우(CultureFlow)와 뉴스보드, 렛츠로, 렛츠에셋에 단일 진실 공급원(SSOT)**으로 문화예술 산업 데이터를 공급하는 마이크로서비스입니다.

---

## 📌 핵심 기능 및 서비스 범위
1. **작품 마스터 인텔리전스 (`data/filmography_works_master_db.json`)**:
   - **고화질 공식 포스터**: KOFIC/KMDb/KOPIS 공식 CDN 연계 및 WebP 경량화
   - **재무·흥행 분석**: 순제작비/총제작비, 손익분기점(BEP) 관객수, 누적 관객수 및 BEP 초과 달성률(흑자/적자 ROI)
   - **핵심 스태프 크레딧**: 연출/감독, 촬영감독, 음악감독, 각본가, 제작/프로듀서
   - **공식 시놉시스**: 공공 영상자료원 및 공연예술망 공인 줄거리 원문
2. **인터랙티브 작품 상세 모달**:
   - 배우 카드의 필모그래피/스테이지그래피 클릭 시 제작비, BEP 프로그레스 바, 스태프 크레딧 모달 즉시 팝업
3. **컬처플로우(CultureFlow) 연계 URN 표준화**:
   - 영화 작품: `urn:culture:work:movie:{kofic_id}`
   - 공연 작품: `urn:culture:work:stage:{kopis_id}`
   - 아티스트: `urn:culture:artist:{category}:{artist_id}`

## 🔗 온톨로지 연합 URN
- 작품 원장 URN: `urn:culture:work:{type}:{work_id}`
- 글로벌 인물 URN: `urn:people:person:{nationality}:{entity_id}`
- 스태프/협업 URN: `urn:people:network:staff:{creator_a}:{creator_b}`
