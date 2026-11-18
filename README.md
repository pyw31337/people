# 렛츠피플 (Let's People) — 다차원 인물 백과 & 노화 타임랩스 독립 원장

> 정계·재계·법조·언론·엔터 79,493명 다차원 인물 백과사전 및 학연·지연·경력망, WebP 85% 압축 및 6개월~30년 노화 타임랩스를 전담하는 독립 인물 원장입니다.
> 컬처플로우 ➔ 렛츠캠핑과 동일하게, 뉴스보드 및 패밀리 서비스에 인물 온톨로지 정보를 전담 공급합니다.

---

## 1. 글로벌 온톨로지 식별자 (Global Federated URN)
- **인물 식별자**: `urn:people:person:{p_id}` (예: `urn:people:person:p-lee-jaeyong`, `urn:people:person:p-jensen-huang`)
- **학교/학연 식별자**: `urn:people:school:{school_code}:{grad_year}`
- **조직/경력 식별자**: `urn:people:org:{org_id}:{role}`

## 2. 핵심 데이터 자산
- `data/aging_photos_index.json`: WebP 85% 압축 및 노화 타임랩스 아카이브 원장
- `data/elite_network.json`: 파벌 및 학연/지연 관계망 원장
- `scripts/aging_photo_pipeline.py`: 사진 수집 ➔ WebP 변환 ➔ 6개월 중복 방지 ➔ R2 이관 엔진
- `index.html`: 인물 백과 & 노화 타임랩스 웹 앱
