# 렛츠 패밀리 통합 디자인 시스템 (Let's Design System, LDS v2.3.0)
> **최종 개정일**: 2026-11-19  
> **기준 레퍼런스**: Taste Skill 분석 결과 ("Tactile Modernism & Digital Craft"), Dieter Rams 물리적 에르고노믹스, Swiss Editorial Grid, Linear/Raycast 마이크로 인터랙션  
> **적용 대상**: `Let's Hub`, `Let's People`, `Let's Law`, `Let's Insu`, `Let's Asset`, `Let's Art`, `Let's View`, `MeatTracker`, `Let's Camp` 등 생태계 전 서비스

---

## 1. Taste Archetype: Tactile Modernism & Digital Craft

### 1.1 스퀘어클 벤토 & 단순 라운드 박스 남발 탈피 원칙
- **박스 중첩(Box-in-Box) 원천 배제**:
  - 흰색 라운드 상자 안에 또 다른 흰색 라운드 상자를 계속해서 중첩 배치하는 획일적 박스 디자인을 엄격히 금지합니다.
  - 구획을 나눌 때는 박스 테두리를 반복하지 않고, **Swiss Grid Dividers(1px 정밀 헤어라인 구분선: `rgba(0,0,0,0.06)`)**와 **오프셋 타이포그래피**로 자연스러운 공간 위계를 만듭니다.
- **물리적 서피스 깊이감 (Tactile Depth & Recessed Insets)**:
  - 트랙 및 그룹 컨테이너는 솟아오른 흰색 박스 대신, 은은하게 파여 있는 **선큰 트랙 (Sunken Recessed Well: `background: #eceef2; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); border-radius: 14px;`)**으로 설계합니다.
  - 그 위에 얹히는 활성 탭 및 제어 버튼은 물리적 스위치처럼 살짝 솟아오른 **택타일 리프트(Tactile Lift: `background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,1); border: 1px solid rgba(0,0,0,0.06);`)**를 적용합니다.
- **림 라이팅 (Rim Lighting Shader)**:
  - 주요 카드 및 헤더 상단에 섬세한 림 라이트(`box-shadow: 0 1px 3px rgba(0,0,0,0.02), inset 0 1px 0 rgba(255,255,255,0.95)`)를 부여하여 아날로그 금속/글래스 하드웨어의 감각을 살립니다.

### 1.2 고정폭 타뷸러 숫자 (Tabular Figures Standard)
- 대시보드의 실시간 수집량, 처리율, 타임스탬프, 인퍼런스 건수, 체납액 등 모든 메트릭 수치에는 반드시 **`font-variant-numeric: tabular-nums;`** 속성을 강제합니다.
- 숫자가 카운트업되거나 변할 때 텍스트 폭이 좌우로 흔들리는(jittering) 현상을 원천 방지하여 시각적 안정감을 보장합니다.

### 1.3 스프링 피직스 트랜지션 (Spring Physics)
- 기계적인 선형(Linear) 페이드를 금지하고, 실제 물리적 탄성을 모사한 **감쇠 스프링 커브(`cubic-bezier(0.16, 1, 0.3, 1)`)**를 기본 모션으로 사용합니다.

---

## 2. 가로 캐러셀 및 마우스 드래그·터치 스와이프 인터랙션 표준 (Horizontal Carousel Standard)

> **핵심 원칙**: 렛츠 생태계 내의 모든 가로 캐러셀(서비스 내비게이션 바, 카테고리 필 트랙, 세그먼트 메뉴 등)은 **마우스 포인터 드래그와 모바일 터치 스와이프가 100% 무결하게 동작**해야 합니다.

```
┌────────────────────────────────────────────────────────────────────────┐
│  [마우스 드래그] ───►  cursor: grab ─(다운)─► cursor: grabbing          │
│  [오클릭 방지]   ───►  이동거리 > 4px 이면 click 이벤트 캡처 차단      │
│  [터치 스와이프] ───►  -webkit-overflow-scrolling: touch & 관성 스크롤   │
│  [선택 피드백]   ───►  scrollIntoView({ behavior: 'smooth', inline: 'center' }) │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 마우스 드래그 (Mouse Drag-to-Scroll)
- `pointerdown`, `pointermove`, `pointerup`, `pointercancel` 이벤트 기반 1:1 드래그 스크롤.
- 커서 어포던스: 마우스 호버 시 `cursor: grab;`, 드래그 중 `cursor: grabbing; user-select: none;` 자동 적용.
- **오클릭 방지 (Drag Click-Suppression)**:
  - 사용자가 메뉴를 넘기려고 가로로 4px 이상 드래그한 경우, 마우스를 뗄 때 자식 버튼/링크의 `click` 이벤트가 트리거되지 않도록 `preventDefault()`, `stopPropagation()`을 캡처 단계에서 자동 차단합니다.

### 2.2 모바일 터치 스와이프 (Touch Momentum)
- `-webkit-overflow-scrolling: touch; scroll-behavior: smooth; touch-action: pan-x pan-y;`를 부여하여 네이티브 모바일 앱과 동일한 관성 스크롤을 제공합니다.
- 스크롤바는 가려져 깔끔한 외관을 유지(`scrollbar-width: none; &::-webkit-scrollbar { display: none; }`)하면서도 부드러운 스와이프를 보장합니다.

### 2.3 활성 아이템 자동 중앙 정렬
- 탭이나 카테고리를 클릭하거나 라우팅으로 선택되었을 때, 해당 요소가 시야 밖으로 벗어나지 않도록 항상 가로 트랙의 정중앙으로 부드럽게 스크롤합니다:
  ```javascript
  activeElement.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  ```

---

## 3. 인물 온톨로지 전수 도시에 표준 (Universal People Dossier Standard)

렛츠피플(`Let's People`) 및 관련 서비스에 등재되는 모든 인물(기업인, 고액 체납자, 연출진/PD, 작가, 문화예술인, 법조인 등)은 다음 **7대 공통 영역을 반드시 균일하게 수집·관리**합니다:

1. **이력 (History & Origins)**: 출생지, 생애 배경, 가계/가족 배경, 병역 등
2. **경력 (Career Track Record)**: 주요 직책, 전직, 대표이사/임원 재직 이력, 사업체 운영 이력
3. **학력 (Education)**: 출신 고등학교, 대학교, 대학원, 전공 및 수료 내역
4. **학연 (Alumni Network)**: 동문 네트워크, 주요 재계·문화계 학연 클러스터
5. **지연 (Regional Network)**: 출신 지역, 연고지 및 주요 활동 권역 클러스터
6. **범죄 이력 (Criminal Record & Regulatory Sanctions)**: 경제범죄(횡령·배임, 자본시장법 위반), 형사처벌, 과징금/행정제재 내역 (무결 인물은 `CLEAN` 명시)
7. **체납 이력 (Tax Delinquency Record)**: 체납 세목, 체납액, 체납 기간, 관할 지자체/세무서, 행정제재(출국금지/감치/압류) 상태 (성실 납세자는 `CLEAN` 명시)

---

## 4. 로컬 에지 AI & 무중단 PC 인계 (Local AI & Handoff Standard)

- **Ollama 모델 2종 규격**: `qwen2.5vl:3b` (3.2 GB 비전 OCR), `llama3.2:1b` (1.3 GB 문화 지능 브리핑 로컬 요약).
- **9대 로컬 LaunchAgents 데몬 사활 감시**: Apple Silicon 온디바이스 에지 연산 (100% Zero-Cloud-Cost).
- **원클릭 PC 인계 시스템**: 새 머신에서 `./scripts/restore_on_new_pc.sh` 1줄로 환경 완전 복구 지원.
