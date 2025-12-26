# Frontend API Documentation

SI-EcoPass 백엔드 API를 Flutter 프론트엔드에서 사용하기 위한 간결한 가이드

---

## 📚 문서 구조

### 1. [Quick Start Guide](./00-quick-start.md) ⭐ **여기서 시작하세요**

- 기본 정보 (Base URL, 인증 방법)
- 핵심 API 엔드포인트 목록
- 에러 코드 정의
- Flutter 개발 팁

**읽는 시간**: 5분  
**용도**: 빠른 참조, 첫 시작

---

### 2. [Swagger Guide](./swagger-guide.md) ⭐ **상세 스펙 확인**

- Swagger UI 사용법
- API 테스트 방법
- OpenAPI 스펙 다운로드
- Flutter 클라이언트 자동 생성

**읽는 시간**: 10분  
**용도**: 모든 API 스펙 확인, 코드 생성

---

### 3. [API Flows](./api-flows.md) ⭐ **실제 구현**

- 기능별 API 호출 순서
- 여정 완료 플로우 (핵심)
- 에러 처리 패턴
- 베스트 프랙티스

**읽는 시간**: 15분  
**용도**: 실제 개발 시 참고

---

### 4. [AI Agent Master Prompt](./prompts/MASTER.md) 🤖 **올인원 자동 개발**

하나의 파일로 전체 앱을 자동 개발하는 마스터 프롬프트

- Supervisor 패턴 자동 실행
- Sub-Agent 자동 생성 및 관리
- Linear 이슈 자동 관리
- Git 자동 커밋

**사용법**: `@frontend-docs/prompts/MASTER.md` + "전체 앱 개발해줘"  
**읽는 시간**: 15분  
**용도**: AI 완전 자동 개발

---

## 🚀 빠른 시작

### ⚡ AI 자동 개발 (1단계)

```
@frontend-docs/prompts/MASTER.md
전체 앱 개발해줘
```

끝! AI가 알아서 개발합니다.

### 📖 수동 개발 (3단계)

1️⃣ **Swagger로 API 탐색**: http://localhost:8000/docs  
2️⃣ **Quick Start Guide 읽기**: [00-quick-start.md](./00-quick-start.md)  
3️⃣ **API Flows로 구현**: [api-flows.md](./api-flows.md)

---

## 🎯 사용 시나리오별 가이드

### "AI로 전체 앱을 자동 개발하고 싶어요" ⭐
→ **Master Prompt** ([prompts/MASTER.md](./prompts/MASTER.md))
```
@frontend-docs/prompts/MASTER.md
전체 앱 개발해줘
```

### "API 스펙이 궁금해요"
→ **Swagger UI** (`http://localhost:8000/docs`)

### "수동으로 개발하려면 어떻게 시작하죠?"
→ **Quick Start Guide** ([00-quick-start.md](./00-quick-start.md))

### "여정 기록 기능을 어떻게 구현하죠?"
→ **API Flows - 여정 완료 플로우** ([api-flows.md](./api-flows.md#2-여정-완료-플로우-핵심))

### "에러가 발생했어요"
→ **Quick Start Guide - 에러 코드** ([00-quick-start.md](./00-quick-start.md#-에러-코드))  
→ **API Flows - 에러 처리 패턴** ([api-flows.md](./api-flows.md#6-에러-처리-패턴))

---

## 📦 권장 Flutter 패키지

### HTTP 클라이언트
- `dio` - HTTP 클라이언트 (인터셉터 지원)

### 인증 & 저장소
- `flutter_secure_storage` - 토큰 안전 저장

### 이미지 처리
- `flutter_image_compress` - 이미지 압축
- `image_picker` - 카메라/갤러리 접근

### 위치
- `geolocator` - GPS 위치 획득
- `permission_handler` - 권한 관리

### 네트워크
- `connectivity_plus` - 네트워크 상태 확인

### 상태 관리 (선택)
- `riverpod` 또는 `bloc` 또는 `provider`

---

## 🔧 개발 환경 설정

### 백엔드 서버 실행

```bash
cd /path/to/si-ecopass-be
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### API 문서 접속

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 💡 중요한 개념

### 1. 표준 응답 형식

모든 API는 동일한 구조로 응답:

```json
{
  "status": "success" | "error",
  "message": "사람이 읽을 수 있는 메시지",
  "data": { /* 실제 데이터 */ }
}
```

### 2. 인증 방식

JWT Bearer Token 사용:

```http
Authorization: Bearer {access_token}
```

### 3. 여정 상태 전이

```
NULL → DRIVING → TRANSFERRED → COMPLETED → APPROVED/REJECTED
```

정해진 순서대로만 상태 변경 가능

---

## 🤝 프론트엔드-백엔드 협업

### API 변경 사항 확인

백엔드 API가 변경되면:

1. Swagger UI 새로고침 (`/docs`)
2. OpenAPI JSON 재다운로드
3. 필요시 Flutter 클라이언트 재생성

### 질문이 있을 때

1. **먼저 Swagger 확인** - 최신 스펙 자동 반영
2. **Quick Start 참조** - 기본 개념 확인
3. **API Flows 확인** - 호출 순서 확인
4. **백엔드 팀에 문의** - 문서에 없는 내용

---

## 📝 문서 업데이트 정책

### 자동 업데이트
- ✅ **Swagger UI** - 코드 변경 시 자동 반영

### 수동 업데이트 (필요시)
- ⚠️ **Quick Start Guide** - 주요 변경 사항만
- ⚠️ **API Flows** - 새로운 플로우 추가 시

---

## 📞 문의

- **백엔드 문서**: `BACKEND_SPEC.md`, `API_PRD.md`
- **프로젝트 가이드**: `CLAUDE.md`
- **Postman Collection**: `postman/SI-EcoPass-Backend.postman_collection.json`

---

**마지막 업데이트**: 2025-12-26  
**API 버전**: v1  
**프론트엔드**: Flutter

