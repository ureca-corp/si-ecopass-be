# SI EcoPass - API Product Requirement Document (PRD)

## 문서 개요

**목적**: BACKEND_SPEC.md의 모든 기능을 충족하는 API 구현 계획  
**대상**: Sub Agent 병렬 작업 할당  
**작업 원칙**: 의존성 순서 준수, 코드 예시 최소화, Supabase MCP 활용

---

## 작업 Phase 구조

각 Phase는 독립적인 Linear 이슈로 관리하며, 의존성이 있는 경우 명시합니다.

```
Phase 1: Database & Entity Setup (기초 작업)
  ↓
Phase 2: Authentication APIs (사용자 인증)
  ↓
Phase 3: Station & ParkingLot APIs (정보 조회)
  ↓
Phase 4: Trip Management APIs (핵심 기능)
  ↓
Phase 5: Image Upload & Storage (파일 처리)
  ↓
Phase 6: Admin APIs (관리자 기능)
  ↓
Phase 7: Testing & Documentation (검증 및 문서화)
```

---

## Phase 1: Database & Entity Setup

**목표**: Supabase 데이터베이스 스키마 구성 및 FastAPI 엔티티 정의

**의존성**: 없음 (최우선 작업)

### 1.1 Supabase Database Setup

**📦 마이그레이션 파일 준비 완료**: `supabase/migrations/20251226000001_initial_schema.sql`  
**🌱 샘플 데이터 준비 완료**: `supabase/seed.sql`

**작업 내용**:

1. **마이그레이션 적용**

   **방법 A: Supabase CLI (권장)**

   ```bash
   # Supabase 프로젝트 연결
   supabase link --project-ref YOUR_PROJECT_REF

   # 마이그레이션 적용
   supabase db push

   # 샘플 데이터 삽입
   psql YOUR_DATABASE_URL < supabase/seed.sql
   ```

   **방법 B: Supabase Dashboard (수동)**

   - SQL Editor에서 `supabase/migrations/20251226000001_initial_schema.sql` 실행
   - 이어서 `supabase/seed.sql` 실행

2. **마이그레이션 파일에 포함된 내용**

   - ✅ UUID v7 함수 (`uuid_generate_v7()`)
   - ✅ PostGIS 확장 활성화
   - ✅ 4개 테이블 생성 (users, stations, parking_lots, trips)
   - ✅ 공간 인덱스 및 일반 인덱스
   - ✅ RLS 정책 (사용자별 데이터 격리)
   - ✅ 트리거 (updated_at, users 자동 생성)
   - ✅ 유틸리티 함수 (거리 계산, 반경 검색)

3. **Storage 버킷 생성 (수동 작업 필요)**

   - Supabase Dashboard → Storage → New Bucket
   - 버킷명: `trips`
   - Public: No (JWT 인증 필요)
   - 경로 구조: `{trip_id}/transfer.jpg`, `{trip_id}/arrival.jpg`

4. **샘플 데이터 확인**
   - 대구 지하철 14개 역 (1호선 5개, 2호선 5개, 3호선 4개)
   - 9개 환승 주차장

**체크리스트**:

- [ ] 마이그레이션 파일 실행 성공 (완료 메시지 확인)
- [ ] Table Editor에서 4개 테이블 확인
- [ ] `SELECT COUNT(*) FROM stations;` → 14개
- [ ] `SELECT COUNT(*) FROM parking_lots;` → 9개
- [ ] Storage 버킷 `trips` 생성 및 업로드 권한 테스트
- [ ] RLS 정책 작동 확인 (테스트 JWT 토큰 사용)

**검증 방법**:

```sql
-- 역 데이터 확인
SELECT name, line_number FROM stations ORDER BY line_number, name;

-- 주차장 데이터 확인
SELECT s.name, COUNT(p.id) as parking_count
FROM stations s
LEFT JOIN parking_lots p ON p.station_id = s.id
GROUP BY s.id, s.name;

-- 거리 계산 테스트
SELECT calculate_distance_meters(
  (SELECT location FROM stations WHERE name = '중앙로역' LIMIT 1),
  (SELECT location FROM stations WHERE name = '대구역' LIMIT 1)
) as distance_meters;
```

**참고**: 자세한 내용은 `supabase/README.md` 참조

---

### 1.2 FastAPI Entity Models (SQLModel)

**작업 내용**:

1. **SQLModel 엔티티 정의**

   - `src/domain/entities/user.py` (User)
   - `src/domain/entities/station.py` (Station)
   - `src/domain/entities/parking_lot.py` (ParkingLot)
   - `src/domain/entities/trip.py` (Trip)

2. **주요 고려사항**
   - `table=True` 설정으로 DB 테이블 매핑
   - `__tablename__` 명시
   - PostGIS geography(Point) 타입은 문자열로 변환하여 처리
   - timezone-aware datetime 필드 사용
   - 한글 주석 1-2줄 필수

**체크리스트**:

- [ ] 4개 엔티티 파일 생성
- [ ] SQLModel `table=True` 설정
- [ ] Supabase 테이블 스키마와 일치 확인
- [ ] 한글 주석 추가

**검증 방법**:

- Supabase MCP로 DB 스키마 가져와서 엔티티와 비교
- 타입 힌트 및 제약조건 확인

---

## Phase 2: Authentication APIs

**목표**: 사용자 회원가입, 로그인, 프로필 관리 API 구현

**의존성**: Phase 1 완료 후 시작

### 2.1 회원가입 API

**엔드포인트**: `POST /api/v1/auth/signup`

**기능**:

- Supabase Auth 계정 생성 (email, password)
- `users` 테이블에 프로필 정보 저장 (username, vehicle_number)
- 자동 로그인 (JWT 발급)

**Request Schema**: `SignupRequest`

- email: str
- password: str
- username: str
- vehicle_number: str (optional)

**Response Schema**: `SignupResponse`

- user_id: UUID
- email: str
- username: str
- access_token: str

**검증 규칙**:

- 이메일 형식 검증
- 비밀번호 최소 8자 이상
- username 중복 확인

---

### 2.2 로그인 API

**엔드포인트**: `POST /api/v1/auth/login`

**기능**:

- Supabase Auth 인증
- JWT 발급
- `users` 테이블에서 프로필 정보 조회

**Request Schema**: `LoginRequest`

- email: str
- password: str

**Response Schema**: `LoginResponse`

- user_id: UUID
- email: str
- username: str
- total_points: int
- access_token: str

---

### 2.3 프로필 조회 API

**엔드포인트**: `GET /api/v1/auth/profile`

**기능**:

- JWT 토큰으로 현재 사용자 정보 조회
- total_points 포함

**Response Schema**: `UserProfileResponse`

- user_id: UUID
- email: str
- username: str
- vehicle_number: str | None
- total_points: int

**인증**: Bearer Token 필수

---

### 2.4 프로필 수정 API

**엔드포인트**: `PATCH /api/v1/auth/profile`

**기능**:

- username, vehicle_number 수정

**Request Schema**: `UpdateProfileRequest`

- username: str | None
- vehicle_number: str | None

**Response Schema**: `UserProfileResponse`

**인증**: Bearer Token 필수

---

**Phase 2 체크리스트**:

- [ ] 4개 API 엔드포인트 구현
- [ ] Supabase Auth 연동
- [ ] JWT 인증 미들웨어 설정
- [ ] Request/Response 스키마 정의 (BaseRequest, BaseResponse 상속)
- [ ] 예외 처리 (BaseAppException 사용)
- [ ] 한글 주석 추가
- [ ] API 테스트 (FastAPI TestClient 또는 수동 테스트)

---

## Phase 3: Station & ParkingLot APIs

**목표**: 대구 지하철 역 및 주차장 정보 조회 API 구현

**의존성**: Phase 1 완료 후 시작 (Phase 2와 병렬 가능)

### 3.1 역 목록 조회 API

**엔드포인트**: `GET /api/v1/stations`

**기능**:

- 대구 지하철 1, 2, 3호선 전체 역 목록 조회
- 노선별 필터링 가능

**Query Parameters**:

- line_number: int | None (1, 2, 3 중 선택)

**Response Schema**: `StationListResponse`

- stations: List[StationResponse]
  - id: UUID
  - name: str
  - line_number: int
  - latitude: float
  - longitude: float

**인증**: 불필요 (공개 정보)

---

### 3.2 특정 역 정보 조회 API

**엔드포인트**: `GET /api/v1/stations/{station_id}`

**기능**:

- 특정 역의 상세 정보 조회
- 연계된 주차장 목록 포함

**Response Schema**: `StationDetailResponse`

- id: UUID
- name: str
- line_number: int
- latitude: float
- longitude: float
- parking_lots: List[ParkingLotResponse]

---

### 3.3 역별 주차장 목록 조회 API

**엔드포인트**: `GET /api/v1/stations/{station_id}/parking-lots`

**기능**:

- 특정 역과 연계된 주차장 목록 조회

**Response Schema**: `ParkingLotListResponse`

- parking_lots: List[ParkingLotResponse]
  - id: UUID
  - name: str
  - address: str
  - latitude: float
  - longitude: float
  - distance_to_station_m: int | None
  - fee_info: str | None

---

**Phase 3 체크리스트**:

- [ ] 3개 API 엔드포인트 구현
- [ ] PostGIS 좌표를 latitude/longitude로 변환
- [ ] 노선별 필터링 기능 구현
- [ ] Request/Response 스키마 정의
- [ ] 한글 주석 추가
- [ ] API 테스트

**참고**: 초기 샘플 데이터는 수동으로 Supabase Dashboard에서 INSERT

---

## Phase 4: Trip Management APIs

**목표**: 여정 3단계 프로세스 API 구현 (출발 → 환승 → 도착)

**의존성**: Phase 1, 2 완료 후 시작

### 4.1 여정 시작 API (출발)

**엔드포인트**: `POST /api/v1/trips/start`

**기능**:

- 새로운 여정 시작
- GPS 좌표 및 현재 시간 기록
- 상태: DRIVING

**Request Schema**: `StartTripRequest`

- latitude: float
- longitude: float

**Response Schema**: `TripResponse`

- trip_id: UUID
- user_id: UUID
- status: str (DRIVING)
- start_time: datetime
- start_location: dict (lat, lng)

**비즈니스 규칙**:

- 사용자당 하나의 진행 중 여정만 허용
- 이미 DRIVING, TRANSFERRED, COMPLETED 상태의 여정이 있으면 에러

**인증**: Bearer Token 필수

---

### 4.2 여정 환승 API (환승)

**엔드포인트**: `POST /api/v1/trips/{trip_id}/transfer`

**기능**:

- 환승 주차장 도착 기록
- GPS 좌표 및 현재 시간 기록
- 주차 인증 사진 URL 저장
- 상태: TRANSFERRED

**Request Schema**: `TransferTripRequest`

- latitude: float
- longitude: float
- transfer_image_url: str

**Response Schema**: `TripResponse`

- trip_id: UUID
- status: str (TRANSFERRED)
- transfer_time: datetime
- transfer_location: dict (lat, lng)
- transfer_image_url: str

**비즈니스 규칙**:

- 현재 상태가 DRIVING이어야 함
- GPS 좌표가 등록된 주차장 근처인지 검증 (선택적)

**인증**: Bearer Token 필수

---

### 4.3 여정 완료 API (도착)

**엔드포인트**: `POST /api/v1/trips/{trip_id}/arrival`

**기능**:

- 목적지 역 도착 기록
- GPS 좌표 및 현재 시간 기록
- 역 인증 사진 URL 저장
- 예상 포인트 계산 (PostGIS ST_Distance 사용)
- 상태: COMPLETED

**Request Schema**: `ArrivalTripRequest`

- latitude: float
- longitude: float
- arrival_image_url: str

**Response Schema**: `TripResponse`

- trip_id: UUID
- status: str (COMPLETED)
- arrival_time: datetime
- arrival_location: dict (lat, lng)
- arrival_image_url: str
- estimated_points: int

**비즈니스 규칙**:

- 현재 상태가 TRANSFERRED이어야 함
- GPS 좌표가 등록된 역 근처인지 검증 (선택적)
- 거리 기반 포인트 계산:
  - start → transfer 거리
  - transfer → arrival 거리
  - 총 거리 × 포인트 비율

**인증**: Bearer Token 필수

---

### 4.4 여정 목록 조회 API

**엔드포인트**: `GET /api/v1/trips`

**기능**:

- 현재 사용자의 여정 목록 조회
- 상태별 필터링 가능

**Query Parameters**:

- status: str | None (DRIVING, TRANSFERRED, COMPLETED, APPROVED, REJECTED)
- limit: int (default 20)
- offset: int (default 0)

**Response Schema**: `TripListResponse`

- trips: List[TripResponse]
- total: int

**인증**: Bearer Token 필수

---

### 4.5 여정 상세 조회 API

**엔드포인트**: `GET /api/v1/trips/{trip_id}`

**기능**:

- 특정 여정의 상세 정보 조회
- 모든 단계의 GPS 좌표 및 사진 URL 포함

**Response Schema**: `TripDetailResponse`

- trip_id: UUID
- user_id: UUID
- status: str
- start_time: datetime | None
- start_location: dict | None
- transfer_time: datetime | None
- transfer_location: dict | None
- transfer_image_url: str | None
- arrival_time: datetime | None
- arrival_location: dict | None
- arrival_image_url: str | None
- estimated_points: int
- earned_points: int
- admin_note: str | None

**인증**: Bearer Token 필수

---

**Phase 4 체크리스트**:

- [ ] 5개 API 엔드포인트 구현
- [ ] 여정 상태 전이 로직 구현
- [ ] PostGIS ST_Distance로 거리 계산
- [ ] 예상 포인트 계산 로직 구현
- [ ] Request/Response 스키마 정의
- [ ] 비즈니스 규칙 검증 (예: 진행 중 여정 중복 방지)
- [ ] 한글 주석 추가
- [ ] API 테스트

---

## Phase 5: Image Upload & Storage

**목표**: Supabase Storage를 활용한 사진 업로드 처리

**의존성**: Phase 1 완료 후 시작

### 5.1 사진 업로드 API

**엔드포인트**: `POST /api/v1/trips/{trip_id}/upload-image`

**기능**:

- 클라이언트에서 압축된 이미지 업로드
- Supabase Storage에 저장
- 경로: `trips/{trip_id}/transfer.jpg` 또는 `trips/{trip_id}/arrival.jpg`
- 공개 URL 반환

**Request**:

- Content-Type: multipart/form-data
- image: file (JPEG/PNG, 최대 5MB)
- stage: str (transfer 또는 arrival)

**Response Schema**: `ImageUploadResponse`

- image_url: str
- uploaded_at: datetime

**비즈니스 규칙**:

- 사용자는 자신의 trip_id에만 업로드 가능
- 이미지 크기 및 형식 검증
- 기존 이미지가 있으면 덮어쓰기

**인증**: Bearer Token 필수

---

**Phase 5 체크리스트**:

- [ ] 이미지 업로드 API 구현
- [ ] Supabase Storage 클라이언트 연동
- [ ] 파일 형식 및 크기 검증
- [ ] JWT 토큰으로 user_id 검증
- [ ] 한글 주석 추가
- [ ] API 테스트

**참고**: 클라이언트에서 이미지 압축 후 전송

---

## Phase 6: Admin APIs

**목표**: 관리자 승인 시스템 API 구현 (웹 관리자 도구용)

**의존성**: Phase 4 완료 후 시작

### 6.1 승인 대기 여정 목록 조회 API

**엔드포인트**: `GET /api/v1/admin/trips/pending`

**기능**:

- 상태가 COMPLETED인 여정 목록 조회
- 관리자 검토용 정보 포함 (GPS 좌표, 사진 URL)

**Query Parameters**:

- limit: int (default 20)
- offset: int (default 0)

**Response Schema**: `AdminTripListResponse`

- trips: List[AdminTripDetailResponse]
- total: int

**인증**: 관리자 권한 필수 (JWT claims 확인)

---

### 6.2 여정 승인 API

**엔드포인트**: `POST /api/v1/admin/trips/{trip_id}/approve`

**기능**:

- 여정 승인 처리
- 상태: APPROVED
- earned_points 설정
- users.total_points 업데이트

**Request Schema**: `ApproveTripRequest`

- earned_points: int (기본값: estimated_points)

**Response Schema**: `TripResponse`

**비즈니스 규칙**:

- 현재 상태가 COMPLETED이어야 함
- earned_points가 설정되면 users.total_points에 합산

**인증**: 관리자 권한 필수

---

### 6.3 여정 반려 API

**엔드포인트**: `POST /api/v1/admin/trips/{trip_id}/reject`

**기능**:

- 여정 반려 처리
- 상태: REJECTED
- admin_note에 반려 사유 기록

**Request Schema**: `RejectTripRequest`

- admin_note: str

**Response Schema**: `TripResponse`

**비즈니스 규칙**:

- 현재 상태가 COMPLETED이어야 함
- 포인트는 지급하지 않음

**인증**: 관리자 권한 필수

---

**Phase 6 체크리스트**:

- [ ] 3개 Admin API 엔드포인트 구현
- [ ] 관리자 권한 검증 미들웨어 구현
- [ ] 포인트 업데이트 로직 구현
- [ ] Request/Response 스키마 정의
- [ ] 한글 주석 추가
- [ ] API 테스트

**참고**: 관리자 권한은 Supabase Auth의 user_metadata 또는 별도 roles 테이블로 관리

---

## Phase 7: Testing & Documentation

**목표**: 전체 API 테스트 및 문서화

**의존성**: Phase 2-6 완료 후 시작

### 7.1 통합 테스트

**작업 내용**:

1. **시나리오 기반 테스트**

   - 회원가입 → 로그인 → 여정 시작 → 환승 → 도착 → 승인
   - 각 단계별 API 호출 검증

2. **예외 상황 테스트**

   - 중복 여정 시작 시도
   - 잘못된 상태 전이 시도
   - 권한 없는 리소스 접근
   - 잘못된 파라미터 전달

3. **성능 테스트**
   - 동시 여정 기록 처리
   - 대량 데이터 조회

**도구**:

- FastAPI TestClient
- pytest
- Supabase 테스트 인스턴스

---

### 7.2 API 문서화

**작업 내용**:

1. **OpenAPI (Swagger) 문서 자동 생성**

   - FastAPI 내장 기능 활용
   - `/docs` 엔드포인트 확인

2. **Postman Collection 생성**

   - 각 API별 샘플 요청/응답 포함
   - 환경 변수 설정 (BASE_URL, ACCESS_TOKEN)

3. **README 업데이트**
   - API 개요
   - 인증 방법
   - 에러 코드 정의

---

**Phase 7 체크리스트**:

- [ ] 시나리오 기반 통합 테스트 작성 및 실행
- [ ] 예외 상황 테스트 작성 및 실행
- [ ] OpenAPI 문서 확인 및 보완
- [ ] Postman Collection 생성
- [ ] README 업데이트

---

## 공통 규칙

### 1. 코딩 규칙

**명명 규칙**:

- Request 스키마: `~~Request`
- Response 스키마: `~~Response`
- BaseRequest, BaseResponse 상속 필수

**예외 처리**:

- BaseAppException 계열만 사용
- 불필요한 try-catch 제거
- 표준 응답 형식: `SuccessResponse.create()`

**주석**:

- 모든 함수/클래스에 한글 주석 1-2줄
- Docstring보다는 간결한 주석 선호

**SQLModel**:

- `table=True` 설정
- `__tablename__` 명시
- timezone-aware datetime 사용

---

### 2. 검증 전략

각 Phase 완료 시:

1. Supabase MCP로 DB 상태 확인
2. FastAPI `/docs`에서 API 테스트
3. 관련 Phase 간 통합 테스트
4. 코드 리뷰 (CLAUDE.md 규칙 준수 확인)

---

### 3. 우선순위

**P0 (필수)**:

- Phase 1, 2, 4 (인증 및 여정 관리)

**P1 (중요)**:

- Phase 3, 5 (정보 조회 및 이미지 업로드)

**P2 (나중에)**:

- Phase 6 (관리자 기능 - 웹 도구와 함께 개발)

---

## Linear 이슈 템플릿

각 Phase를 Linear 이슈로 등록할 때 사용할 템플릿:

```markdown
# [Phase N] {제목}

## 목표

{Phase 목표 1-2줄}

## 의존성

- Phase X 완료 필요 (또는 "없음")

## 작업 내용

- [ ] Task 1
- [ ] Task 2
- [ ] ...

## 검증 방법

- 체크리스트 항목 확인
- API 테스트 성공
- Supabase MCP로 데이터 확인

## 참고 문서

- BACKEND_SPEC.md
- CLAUDE.md
- API_PRD.md (이 문서)
```

---

## 다음 단계

1. **Phase 1 시작**: Supabase 스키마 생성 (수동 작업)
2. **Phase 2-3 병렬 진행**: 인증 API와 역/주차장 API 동시 개발 가능
3. **Phase 4 집중**: 핵심 여정 관리 API 구현
4. **Phase 5-6 순차 진행**: 이미지 업로드 및 관리자 기능
5. **Phase 7 마무리**: 테스트 및 문서화

---

**최종 업데이트**: 2025-12-26  
**작성자**: API PRD Generator  
**버전**: 1.0
