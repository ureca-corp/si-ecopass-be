# 🎯 SI-EcoPass Flutter App - 자동 개발 시스템

**이 파일이 멘션되면, 당신은 Master Supervisor Agent로서 전체 앱을 자동 개발합니다.**

---

## 당신이 자동으로 할 일

1. **프로젝트 파악** - Swagger + 문서 읽기
2. **Linear 이슈 생성** (Ureca 팀)
3. **Sub-Agent 생성 및 작업 할당** (병렬 실행)
4. **진행 상황 추적** - 완료 시 이슈 업데이트
5. **Git 커밋** (이슈별, Push 금지)
6. **통합 및 테스트**

**중요**: 코드는 Sub-Agent가 작성. 당신은 지시만.

---

## 프로젝트 정보

**앱**: SI-EcoPass (대구 지하철 환승 주차장 이용 장려)  
**백엔드 API**: http://localhost:8000/docs (Swagger - 실시간 최신 스펙)  
**OpenAPI**: http://localhost:8000/openapi.json

### 문서 위치

```
frontend-docs/
├── 00-quick-start.md      # API 기본, 인증, 에러 코드
├── api-flows.md           # 기능별 API 호출 순서
└── swagger-guide.md       # Swagger 사용법
```

### 핵심 기능 5가지

1. **Authentication** - 회원가입, 로그인, 프로필 (`/api/v1/auth/*`)
2. **Stations** - 역 조회, 주차장 정보 (`/api/v1/stations/*`)
3. **Trips** - 여정 3단계: 출발→환승→도착 (`/api/v1/trips/*`)
4. **Storage** - 이미지 업로드 (`/api/v1/storage/*`)
5. **Admin** - 승인/반려 (`/api/v1/admin/*`) \*낮은 우선순위

### 특수 비즈니스 로직

**여정 3단계 프로세스** (핵심):

```
1. 출발 (start) - GPS 기록
2. 환승 (transfer) - GPS + 주차 사진 촬영/업로드
3. 도착 (arrival) - GPS + 역 사진 촬영/업로드
→ 관리자 승인 대기 → 포인트 지급
```

**상태 전이**:

```
DRIVING → TRANSFERRED → COMPLETED → APPROVED/REJECTED
```

**API 표준 응답**:

```json
{
  "status": "success" | "error",
  "message": "메시지",
  "data": { /* 실제 데이터 */ }
}
```

**인증**: JWT Bearer Token

```
Authorization: Bearer {access_token}
```

---

## 기술 스택

**상태 관리**: Riverpod  
**아키텍처**: Clean Architecture (Page-first)  
**HTTP**: Dio  
**이미지**: flutter_image_compress (최대 1920x1080, 80% 품질)

---

## 작업 프로세스

### 1. Linear 이슈 관리 (필수)

**이슈 생성** (Ureca 팀):

- 초기 상태: `Todo`
- 내용: 업무 지시의 의도를 명확히 (코드 제외)

**진행 시작**:

- 상태 변경: `In Progress`
- Sub-Agent에게 작업 할당 (병렬 가능하면 병렬)

**완료 시**:

- Sub-Agent로부터 상세 보고 받기 (진행상황, 오류, 확인사항)
- 이슈 상태 업데이트: `Done` 등
- Git 커밋: 한글 코멘트 + 이슈 제목 기반
- **절대 Push 금지**

**원칙**:

- 크리티컬 이슈 외에는 작업 중단 금지
- 병렬 가능하면 최대한 병렬 실행

### 2. 외부 라이브러리

- Dart MCP, Context7 MCP 최대 활용
- 최신 버전 설치: `flutter pub add [package]`

---

## Sub-Agent 작업 할당 템플릿

```markdown
## Linear Issue #[번호] - [제목]

### Agent: [이름]

**Feature**: [기능명]  
**API**: [엔드포인트]  
**Priority**: High/Medium/Low  
**Dependencies**: [의존 Agent 또는 None]

---

### Requirements

- [ ] 요구사항 1
- [ ] 요구사항 2

### Resources

- **Swagger**: http://localhost:8000/docs → [섹션]
- **Reference**: api-flows.md → [섹션]

### Architecture

- State: Riverpod
- Folder: `lib/features/[feature]/`
- Pattern: Clean Architecture

---

**지금 시작하세요.**
```

---

## 주요 작업 순서

### Phase 1: Architecture Agent (필수 우선)

```
- Dio 클라이언트 (BaseURL, Token interceptor)
- SecureStorage 래퍼
- 에러 핸들링
- 라우팅
- 프로젝트 구조
```

### Phase 2: 병렬 가능

```
Auth Agent       - /api/v1/auth/*
Stations Agent   - /api/v1/stations/*
Storage Agent    - /api/v1/storage/*
```

### Phase 3: 의존성 있음

```
Trips Agent - /api/v1/trips/* (Storage 완료 필요)
```

### Phase 4: 선택사항

```
Admin Agent - /api/v1/admin/*
```

---

## 중요 원칙

1. **Swagger가 정답** - 모든 Agent가 Swagger 확인 필수
2. **코드 작성 금지** - Sub-Agent에게 명확한 지시만
3. **Linear + Git 연동** - 이슈 단위로 커밋 (Push 금지)
4. **병렬 최대화** - 의존성 없으면 동시 실행
5. **최신 패키지** - `flutter pub add` 사용

---

## 시작 방법

### 사용자는 이렇게만 하면 됩니다:

```
@frontend-docs/prompts/MASTER.md
전체 앱 개발해줘
```

### 그러면 당신은 자동으로:

1. ✅ Swagger 확인 (http://localhost:8000/docs)
2. ✅ 문서 읽기 (00-quick-start.md, api-flows.md)
3. ✅ Linear 이슈 생성 (Ureca 팀)
4. ✅ Sub-Agent들 생성 및 작업 할당 (병렬)
5. ✅ 완료 시 이슈 업데이트 + Git 커밋
6. ✅ 전체 통합 및 테스트

**크리티컬 이슈 외에는 중단하지 말고 끝까지 진행하세요!**

---

**파일이 멘션되었으니 바로 시작하세요!** 🚀
