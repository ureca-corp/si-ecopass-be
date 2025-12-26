# SI EcoPass Backend - 작업 분배 가이드

## 📋 전체 개요

총 7개 Phase 중 Phase 1은 완료되었으며, 나머지 6개 Phase를 효율적으로 병렬 처리하기 위한 가이드입니다.

### ✅ 완료된 작업

- **Phase 1** (URE-143): Database & Entity Setup
  - Supabase 마이그레이션 완료
  - 14개 역, 9개 주차장 샘플 데이터 삽입

---

## 🎯 작업 우선순위 및 의존성

```mermaid
graph TD
    A[Phase 1: DB Setup ✅] --> B[Phase 2: Auth APIs 🔴]
    A --> C[Phase 3: Station APIs 🟡]
    B --> D[Phase 4: Trip APIs 🔴]
    B --> E[Phase 5: Image Upload 🟡]
    D --> F[Phase 6: Admin APIs 🟢]
    B --> F
    B --> G[Phase 7: Testing 🟢]
    C --> G
    D --> G
    E --> G
    F --> G
```

### 우선순위 레벨

- 🔴 **P0 (Urgent)**: Phase 2, 4 - 핵심 기능
- 🟡 **P1 (High)**: Phase 3, 5 - 중요 기능
- 🟢 **P2 (Medium)**: Phase 6, 7 - 추가 기능

---

## 🚀 Phase별 작업 분배 전략

### **1단계: 즉시 시작 (병렬 작업)**

#### 세션 A: Phase 2 - Authentication APIs (URE-144) 🔴

**최우선 작업 - 다른 모든 Phase의 기반**

**작업 지시**:

```
Linear 이슈 URE-144를 확인하고 Phase 2 Authentication APIs를 구현해줘.

필수 작업:
1. src/domain/entities/user.py 생성 (SQLModel)
2. POST /api/v1/auth/signup (회원가입)
3. POST /api/v1/auth/login (로그인)
4. GET /api/v1/auth/profile (프로필 조회)
5. PATCH /api/v1/auth/profile (프로필 수정)

중요:
- CLAUDE.md의 코딩 규칙 준수
- BaseRequest, BaseResponse 상속
- JWT 인증 미들웨어 구현
- Supabase Auth 연동

완료 후 /docs에서 회원가입→로그인→프로필 조회 시나리오 테스트
```

**예상 시간**: 3-4시간  
**블로킹**: Phase 4, 5, 6 작업이 이것을 기다림

---

#### 세션 B: Phase 3 - Station & ParkingLot APIs (URE-145) 🟡

**Phase 2와 병렬 작업 가능 (독립적)**

**작업 지시**:

```
Linear 이슈 URE-145를 확인하고 Phase 3 Station & ParkingLot APIs를 구현해줘.

필수 작업:
1. src/domain/entities/station.py 생성 (SQLModel)
2. src/domain/entities/parking_lot.py 생성 (SQLModel)
3. GET /api/v1/stations (역 목록 조회)
4. GET /api/v1/stations/{station_id} (역 상세 조회)
5. GET /api/v1/stations/{station_id}/parking-lots (주차장 목록)

중요:
- PostGIS geography(Point)를 latitude/longitude로 변환
- 노선별 필터링 (line_number 쿼리 파라미터)
- 인증 불필요 (공개 API)

완료 후 /docs에서 14개 역, 9개 주차장 데이터 확인
```

**예상 시간**: 2-3시간  
**블로킹**: 없음 (독립적 작업)

---

### **2단계: Phase 2 완료 후 시작 (병렬 작업)**

⚠️ **Phase 2 (Auth)가 완료되어야 시작 가능**

#### 세션 C: Phase 4 - Trip Management APIs (URE-146) 🔴

**핵심 비즈니스 로직**

**작업 지시**:

```
Linear 이슈 URE-146을 확인하고 Phase 4 Trip Management APIs를 구현해줘.

필수 작업:
1. src/domain/entities/trip.py 생성 (SQLModel)
2. POST /api/v1/trips/start (여정 시작)
3. POST /api/v1/trips/{trip_id}/transfer (환승 기록)
4. POST /api/v1/trips/{trip_id}/arrival (도착 기록 + 포인트 계산)
5. GET /api/v1/trips (여정 목록 조회)
6. GET /api/v1/trips/{trip_id} (여정 상세 조회)

핵심 비즈니스 로직:
- 사용자당 하나의 진행 중 여정만 허용
- 상태 전이 검증: DRIVING → TRANSFERRED → COMPLETED
- PostGIS ST_Distance로 거리 계산 및 포인트 산정

JWT 인증 필수 (Phase 2의 인증 미들웨어 사용)

완료 후 시나리오 테스트:
1. 여정 시작 → trip_id 받음
2. 환승 기록 (임시 image_url 사용)
3. 도착 기록 → estimated_points 계산 확인
```

**예상 시간**: 4-5시간  
**블로킹**: Phase 6 작업이 이것을 기다림

---

#### 세션 D: Phase 5 - Image Upload & Storage (URE-147) 🟡

**Phase 4와 병렬 작업 가능**

**작업 지시**:

```
Linear 이슈 URE-147을 확인하고 Phase 5 Image Upload & Storage를 구현해줘.

필수 작업:
1. Supabase Storage 버킷 'trips' 생성 (Dashboard에서 수동)
2. POST /api/v1/trips/{trip_id}/upload-image (이미지 업로드)
3. 파일 검증 (JPEG/PNG, 최대 5MB)
4. 권한 검증 (trip 소유자만 업로드 가능)

Supabase Storage 연동:
- storage.from_("trips").upload()
- 경로: {trip_id}/transfer.jpg 또는 arrival.jpg

JWT 인증 필수 (Phase 2의 인증 미들웨어 사용)

완료 후 테스트:
1. 테스트 이미지 업로드
2. Storage 버킷에 파일 생성 확인
3. 반환된 URL로 이미지 접근 확인
```

**예상 시간**: 2-3시간  
**블로킹**: 없음 (Phase 4와 독립적)

---

### **3단계: Phase 4 완료 후 시작**

⚠️ **Phase 2, 4가 완료되어야 시작 가능**

#### 세션 E: Phase 6 - Admin APIs (URE-148) 🟢

**관리자 승인 시스템 (나중에)**

**작업 지시**:

```
Linear 이슈 URE-148을 확인하고 Phase 6 Admin APIs를 구현해줘.

필수 작업:
1. 관리자 권한 미들웨어 구현 (JWT claims 확인)
2. GET /api/v1/admin/trips/pending (승인 대기 여정 목록)
3. POST /api/v1/admin/trips/{trip_id}/approve (승인)
4. POST /api/v1/admin/trips/{trip_id}/reject (반려)

핵심 비즈니스 로직:
- 승인 시: users.total_points += earned_points (트랜잭션)
- 반려 시: admin_note 기록, 포인트 미지급

완료 후 테스트:
1. 관리자 계정 생성 (user_metadata에 role: admin 추가)
2. 일반 사용자로 여정 완료 (COMPLETED)
3. 관리자로 승인 → 포인트 지급 확인
```

**예상 시간**: 3-4시간  
**블로킹**: Phase 7 (Testing)

---

### **4단계: 모든 기능 완료 후**

⚠️ **Phase 2-6 모두 완료 후 시작**

#### 세션 F: Phase 7 - Testing & Documentation (URE-149) 🟢

**통합 테스트 및 문서화 (마무리)**

**작업 지시**:

```
Linear 이슈 URE-149를 확인하고 Phase 7 Testing & Documentation을 구현해줘.

필수 작업:
1. pytest 통합 테스트 작성
   - 회원가입 → 로그인 → 여정 완료 → 승인 시나리오
   - 예외 상황 테스트 (권한 오류, 상태 전이 오류 등)
2. Postman Collection 생성
3. README.md 업데이트
   - API 개요
   - 로컬 개발 가이드
   - 환경 설정

완료 후:
- 모든 테스트 통과 확인
- /docs 페이지 완성도 확인
- README 따라 프로젝트 실행 가능 확인
```

**예상 시간**: 3-4시간  
**블로킹**: 없음 (최종 단계)

---

## 📊 효율적인 작업 스케줄

### **최적 시나리오 (3-4명의 Sub Agent)**

| 시간대  | 세션 A     | 세션 B     | 세션 C     | 세션 D     |
| ------- | ---------- | ---------- | ---------- | ---------- |
| **1차** | Phase 2 🔴 | Phase 3 🟡 | -          | -          |
| **2차** | -          | -          | Phase 4 🔴 | Phase 5 🟡 |
| **3차** | -          | -          | Phase 6 🟢 | Phase 7 🟢 |

**총 예상 시간**:

- 병렬 처리 시: 약 10-12시간
- 순차 처리 시: 약 20-24시간

---

### **최소 시나리오 (1-2명의 Sub Agent)**

#### 우선순위 순서:

1. **Phase 2** (Auth) 🔴 → 최우선
2. **Phase 4** (Trip) 🔴 → 핵심 기능
3. **Phase 3** (Station) 🟡 → 정보 조회
4. **Phase 5** (Image) 🟡 → 사진 업로드
5. **Phase 6** (Admin) 🟢 → 나중에
6. **Phase 7** (Test) 🟢 → 마무리

---

## 💡 각 세션에 전달할 핵심 정보

### 모든 세션 공통 준비사항

```bash
# 1. 프로젝트 루트로 이동
cd /Users/andy/Documents/GitHub/si-ecopass-be

# 2. 필수 문서 확인
- BACKEND_SPEC.md (전체 시스템 명세)
- API_PRD.md (API 개발 계획)
- CLAUDE.md (코딩 규칙)
- Linear 이슈 확인 (URE-143 ~ URE-149)

# 3. Supabase 로컬 서버 확인
supabase status
# → http://127.0.0.1:54323 (Studio)
# → postgresql://postgres:postgres@127.0.0.1:54322/postgres

# 4. FastAPI 서버 실행
uvicorn src.main:app --reload
# → http://127.0.0.1:8000/docs
```

### 각 세션별 시작 프롬프트

#### 세션 A (Phase 2)

```
@CLAUDE.md @API_PRD.md

Linear 이슈 URE-144 (Phase 2: Authentication APIs)를 구현해줘.

현재 상태:
- Phase 1 완료 (DB 스키마 준비됨)
- Supabase 로컬 서버 실행 중
- 14개 역, 9개 주차장 데이터 존재

작업 목표:
1. User 엔티티 정의 (SQLModel)
2. 회원가입/로그인/프로필 API 4개 구현
3. JWT 인증 시스템 구축

완료 조건:
- /docs에서 회원가입→로그인→프로필 조회 시나리오 성공
- JWT 토큰으로 인증된 요청 가능

시작해줘.
```

#### 세션 B (Phase 3)

```
@CLAUDE.md @API_PRD.md

Linear 이슈 URE-145 (Phase 3: Station & ParkingLot APIs)를 구현해줘.

현재 상태:
- Phase 1 완료 (DB에 14개 역, 9개 주차장 존재)
- Supabase 로컬 서버 실행 중

작업 목표:
1. Station, ParkingLot 엔티티 정의 (SQLModel)
2. 역/주차장 조회 API 3개 구현
3. PostGIS 좌표를 latitude/longitude로 변환

완료 조건:
- /docs에서 14개 역 조회 성공
- 노선별 필터링 동작 확인
- 주차장 목록 응답 확인

시작해줘.
```

#### 세션 C (Phase 4)

```
@CLAUDE.md @API_PRD.md

Linear 이슈 URE-146 (Phase 4: Trip Management APIs)을 구현해줘.

전제 조건:
- Phase 2 완료됨 (JWT 인증 시스템 구축됨)

작업 목표:
1. Trip 엔티티 정의 (SQLModel)
2. 여정 3단계 프로세스 API 구현 (start, transfer, arrival)
3. 거리 기반 포인트 계산 로직

핵심:
- 상태 전이 검증 (DRIVING → TRANSFERRED → COMPLETED)
- PostGIS ST_Distance로 거리 계산
- 사용자당 하나의 진행 중 여정만 허용

완료 조건:
- 여정 시작→환승→도착 시나리오 성공
- estimated_points 자동 계산 확인

시작해줘.
```

---

## 🎯 작업 완료 체크리스트

각 Phase 완료 시 다음을 확인:

### Phase 2 (Auth)

- [ ] User 엔티티 생성
- [ ] 4개 API 엔드포인트 동작
- [ ] JWT 토큰 발급 및 검증
- [ ] /docs에서 시나리오 테스트 성공

### Phase 3 (Station)

- [ ] Station, ParkingLot 엔티티 생성
- [ ] 3개 API 엔드포인트 동작
- [ ] 14개 역 조회 가능
- [ ] 노선별 필터링 동작

### Phase 4 (Trip)

- [ ] Trip 엔티티 생성
- [ ] 6개 API 엔드포인트 동작
- [ ] 상태 전이 검증 동작
- [ ] 포인트 계산 로직 동작

### Phase 5 (Image)

- [ ] Storage 버킷 생성
- [ ] 이미지 업로드 API 동작
- [ ] 파일 검증 동작
- [ ] 권한 검증 동작

### Phase 6 (Admin)

- [ ] 관리자 권한 미들웨어
- [ ] 3개 Admin API 동작
- [ ] 승인 시 포인트 지급 확인
- [ ] 트랜잭션 처리 확인

### Phase 7 (Test)

- [ ] pytest 테스트 통과
- [ ] Postman Collection 생성
- [ ] README 업데이트
- [ ] 문서화 완료

---

## 🚨 주의사항

### 코딩 규칙 (CLAUDE.md)

- ✅ Request/Response 스키마: `~~Request`, `~~Response` 명명
- ✅ BaseRequest, BaseResponse 상속
- ✅ BaseAppException 사용
- ✅ 한글 주석 1-2줄 필수
- ✅ SQLModel `table=True` 설정
- ❌ 불필요한 try-catch 금지
- ❌ 미래를 위한 코드 금지 (YAGNI)

### 의존성 관리

- Phase 2 완료 전에 Phase 4, 5, 6 시작 불가
- Phase 4 완료 전에 Phase 6 시작 불가
- Phase 3은 독립적 (언제든 시작 가능)

### 테스트

- 각 Phase 완료 시 `/docs`에서 API 테스트
- 완료 후 Linear 이슈에 코멘트로 결과 보고

---

## 📞 문제 발생 시

### 일반적인 문제

1. **Supabase 연결 오류**

   ```bash
   supabase status  # 실행 중인지 확인
   supabase start   # 재시작
   ```

2. **마이그레이션 오류**

   ```bash
   supabase db reset  # DB 초기화
   ```

3. **Import 오류**

   - `src/__init__.py` 파일 확인
   - Python path 설정 확인

4. **JWT 인증 오류**
   - Phase 2 완료 여부 확인
   - 토큰 만료 시간 확인

---

**마지막 업데이트**: 2025-12-26  
**작성자**: AI Assistant  
**Linear 팀**: Ureca
