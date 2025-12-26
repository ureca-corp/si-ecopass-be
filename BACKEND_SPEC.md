# SI EcoPass - Backend Specification

## 프로젝트 개요

**목적**: 대구 지하철 환승 주차장 이용 촉진을 위한 여정 기록 및 포인트 적립 앱

**대상 지역**: 대구광역시 지하철 1, 2, 3호선

**핵심 가치**:

- 환승 주차장 정보 제공으로 주차 편의성 향상 (대구 지하철 중심)
- 대중교통 이용 시 절약되는 시간, 비용, CO2 데이터 제시
- 사진 인증 기반 여정 완료 시 포인트 적립
- 관리자 승인 시스템을 통한 부정 사용 방지

## 핵심 기능

### 1. 3단계 여정 프로세스

- **출발 (Start)**: GPS 기록
- **환승 (Transfer)**: GPS + 주차 사진
- **도착 (Arrival)**: GPS + 역 인증 사진

### 2. 사진 인증 시스템

- 카메라 촬영 및 이미지 압축
- Supabase Storage 업로드
- 관리자 검증용 증빙자료

### 3. 관리자 승인 시스템

- 앱에는 미구현 (사용자는 제출만)
- 웹 관리자 도구에서 GPS/사진 검증
- 승인 시 포인트 지급, 반려 시 사유 기록

### 4. PostGIS 기반 위치 관리

- GPS 좌표를 geography(Point) 타입으로 저장
- 거리 계산 (ST_Distance)
- 반경 검색 (ST_DWithin)

### 5. 로그인

- Supabase Auth OAuth 연동 (이메일 로그인)

---

## 도메인 개념

### 비즈니스 엔티티

#### 사용자 (User)

- **계정 정보**: 아이디, 비밀번호, 이메일, 사용자명
- **포인트 누적** 및 여정 기록 소유
- Supabase Auth 기반 인증
- 현재 진행 중인 여정 상태 추적

#### 역 (Station)

- 대구 지하철 1, 2, 3호선 역 정보
- 노선 번호 및 역명
- GPS 좌표 (PostGIS geography 타입)
- 연계 환승 주차장 정보

#### 환승 주차장 (ParkingLot)

- 역과 연계된 주차 시설
- 관리자가 등록한 추천 환승 주차장
- 주차장 명칭, 주소, GPS 좌표
- 역까지의 거리, 요금 정보

#### 여정 (Trip)

- 사용자의 환승 주차 이용 기록
- 3단계 프로세스: 출발(Start) → 환승(Transfer) → 도착(Arrival)
- 각 단계별 시간, GPS 좌표 기록
- 환승 및 도착 시 사진 인증 필수
- 상태: DRIVING → TRANSFERRED → COMPLETED (승인 대기) → APPROVED/REJECTED
- 예상 포인트 및 실제 지급 포인트 관리

#### 관리자 승인 (Admin Approval)

- 앱에는 미구현 (웹 관리자 도구)
- 사용자 제출 여정 검증
- GPS 좌표 및 사진 확인
- 승인/반려 결정 및 포인트 지급

---

### 비즈니스 규칙

#### 여정 3단계 프로세스

**1. 출발 (Start)**

- 사용자가 차량으로 출발할 때 클릭
- 현재 시간과 GPS 좌표 기록
- 상태: DRIVING

**2. 환승 (Transfer)**

- 환승 주차장 도착 시 클릭
- GPS 좌표 수집 (주차장 위치 검증용)
- 카메라 실행: 주차된 차량 사진 촬영 및 업로드
- 상태: TRANSFERRED

**3. 도착 (Arrival)**

- 목적지 지하철역 도착 시 클릭
- GPS 좌표 수집 (역 위치 검증용)
- 카메라 실행: 지하철역 인증 사진 촬영 및 업로드
- 상태: COMPLETED (관리자 승인 대기)

#### 여정 상태 전이

```
NULL (여정 없음)
  ↓ [출발 버튼]
DRIVING (운전 중)
  ↓ [환승 버튼 + 사진 촬영]
TRANSFERRED (환승 완료)
  ↓ [도착 버튼 + 사진 촬영]
COMPLETED (승인 대기)
  ↓ [관리자 검토]
APPROVED (승인 완료, 포인트 지급) 또는 REJECTED (반려)
```

#### 포인트 적립 규칙

- 여정 완료 후 관리자 승인 시에만 포인트 지급
- 예상 포인트는 출발-환승-도착 거리 기반 사전 계산
- 실제 지급 포인트는 관리자가 GPS 및 사진 검증 후 결정
- 거리당 포인트 비율은 서버 설정으로 관리

#### 관리자 승인 기준

- GPS 좌표가 등록된 주차장 및 역 위치와 일치하는지 확인
- 제출된 사진 2장 (주차 인증, 역 인증) 검토
- 동선의 논리적 일관성 확인
- **승인 시**: earned_points 업데이트, user.total_points 합산
- **반려 시**: 사유 기록, 포인트 미지급

#### 주차장 정보 제공

- 관리자가 등록한 대구 지하철 역별 추천 환승 주차장
- 주차장 명칭, 주소, 역까지 거리, 요금 정보
- 노선도 UI에서 역 클릭 시 해당 역 주차장 리스트 표시

---

## 데이터 모델 구조 (Supabase)

### UUID v7 사용

> **모든 테이블**(stations, parking_lots, trips)에서 UUID v7을 기본 키로 사용합니다.

**UUID v7의 장점**:

- 시간 순서대로 정렬 가능 (생성 시간 내장)
- B-tree 인덱스 성능 향상 (순차적 삽입으로 페이지 분할 최소화)
- UUID v4보다 쿼리 성능 우수
- 분산 시스템에서 충돌 없이 고유 ID 생성

### 테이블 스키마

#### 1. users 테이블 (Supabase Auth 확장)

| 필드           | 타입        | 설명                    | 제약조건            |
| -------------- | ----------- | ----------------------- | ------------------- |
| id             | uuid        | Supabase Auth 사용자 ID | PK, FK → auth.users |
| username       | text        | 사용자명                | UNIQUE, NOT NULL    |
| vehicle_number | text        | 차량 번호               | NULL 허용           |
| total_points   | integer     | 누적 포인트             | DEFAULT 0           |
| updated_at     | timestamptz | 수정 일시               | DEFAULT now()       |

> **참고**: `email`과 `created_at`은 Supabase Auth의 `auth.users` 테이블에서 관리됩니다.

#### 2. stations 테이블

| 필드        | 타입             | 설명                | 제약조건                                 |
| ----------- | ---------------- | ------------------- | ---------------------------------------- |
| id          | uuid             | 역 고유 ID          | PK, DEFAULT uuid_generate_v7()           |
| name        | text             | 역명                | NOT NULL                                 |
| line_number | integer          | 노선 번호 (1, 2, 3) | NOT NULL, CHECK (line_number IN (1,2,3)) |
| location    | geography(Point) | GPS 좌표 (PostGIS)  | NOT NULL                                 |
| created_at  | timestamptz      | 등록 일시           | DEFAULT now()                            |

#### 3. parking_lots 테이블

| 필드                  | 타입             | 설명               | 제약조건                       |
| --------------------- | ---------------- | ------------------ | ------------------------------ |
| id                    | uuid             | 주차장 고유 ID     | PK, DEFAULT uuid_generate_v7() |
| station_id            | uuid             | 연계 역 ID         | FK → stations(id), NOT NULL    |
| name                  | text             | 주차장 명칭        | NOT NULL                       |
| address               | text             | 주소               | NOT NULL                       |
| location              | geography(Point) | GPS 좌표 (PostGIS) | NOT NULL                       |
| distance_to_station_m | integer          | 역까지 거리 (미터) | NULL 허용                      |
| fee_info              | text             | 요금 정보          | NULL 허용                      |
| created_at            | timestamptz      | 등록 일시          | DEFAULT now()                  |

#### 4. trips 테이블

| 필드               | 타입             | 설명               | 제약조건                                                                          |
| ------------------ | ---------------- | ------------------ | --------------------------------------------------------------------------------- |
| id                 | uuid             | 여정 고유 ID       | PK, DEFAULT uuid_generate_v7()                                                    |
| user_id            | uuid             | 사용자 ID          | FK → users(id), NOT NULL                                                          |
| start_time         | timestamptz      | 출발 시간          | NULL 허용                                                                         |
| start_location     | geography(Point) | 출발 GPS 좌표      | NULL 허용                                                                         |
| transfer_time      | timestamptz      | 환승 시간          | NULL 허용                                                                         |
| transfer_location  | geography(Point) | 환승 GPS 좌표      | NULL 허용                                                                         |
| transfer_image_url | text             | 주차 인증 사진 URL | NULL 허용                                                                         |
| arrival_time       | timestamptz      | 도착 시간          | NULL 허용                                                                         |
| arrival_location   | geography(Point) | 도착 GPS 좌표      | NULL 허용                                                                         |
| arrival_image_url  | text             | 역 인증 사진 URL   | NULL 허용                                                                         |
| status             | text             | 여정 상태          | CHECK (status IN ('DRIVING', 'TRANSFERRED', 'COMPLETED', 'APPROVED', 'REJECTED')) |
| estimated_points   | integer          | 예상 포인트        | DEFAULT 0                                                                         |
| earned_points      | integer          | 실제 지급 포인트   | DEFAULT 0                                                                         |
| admin_note         | text             | 관리자 메모        | NULL 허용                                                                         |
| created_at         | timestamptz      | 생성 일시          | DEFAULT now()                                                                     |
| updated_at         | timestamptz      | 수정 일시          | DEFAULT now()                                                                     |

### 데이터 관계

```
auth.users (Supabase Auth - email, created_at 등)
  ↓ (1:1, FK: id)
users (프로필 확장 - username, vehicle_number, total_points 등)
  ↓ (1:N, FK: user_id)
trips (여정 기록)
  ├─ start_location: geography(Point)
  ├─ transfer_location: geography(Point)
  ├─ arrival_location: geography(Point)
  ├─ transfer_image_url: Supabase Storage 경로
  └─ arrival_image_url: Supabase Storage 경로

stations (역 정보)
  ↓ (1:N, FK: station_id)
parking_lots (환승 주차장)
```

### Supabase Storage 구조

#### trips 버킷

```
trips/
  {trip_id}/
    transfer.jpg    # 환승 주차 인증 사진
    arrival.jpg     # 도착 역 인증 사진
```

**접근 권한**

- JWT 토큰 기반 인증 사용
- 애플리케이션 레벨에서 user_id 검증
- 사용자는 자신의 trip_id에 해당하는 사진만 업로드/조회 가능

---

## 데이터 저장 및 관리

### 데이터 저장소

#### 1. Supabase PostgreSQL (클라우드 DB)

- **auth.users 테이블**: Supabase Auth 기본 계정 정보 (email, created_at 등)
- **users 테이블**: 사용자 프로필 확장 (username, vehicle_number, total_points 등)
- **stations 테이블**: 대구 지하철 1, 2, 3호선 역 정보
- **parking_lots 테이블**: 역별 추천 환승 주차장
- **trips 테이블**: 사용자 여정 기록 및 승인 상태
- PostGIS 확장: geography(Point) 타입으로 GPS 좌표 저장

#### 2. Supabase Storage (파일 저장소)

- **trips 버킷**: 여정별 인증 사진 저장
  - `{trip_id}/transfer.jpg`: 주차 인증 사진
  - `{trip_id}/arrival.jpg`: 역 인증 사진
- JWT 토큰 기반 접근 제어 (애플리케이션 레벨)

#### 3. Supabase Auth (인증)

- 이메일/비밀번호 인증
- JWT 기반 세션 관리
- auth.users 테이블 (email, created_at 등)과 public.users 테이블 (username, vehicle_number 등) 연동

### 데이터 생명주기

#### 사용자 데이터

```
회원가입 → Supabase Auth 계정 생성 (email, password → auth.users)
         → users 테이블에 프로필 생성 (username, vehicle_number 등 - 트리거)
로그인 → Supabase Auth JWT 발급 (email 인증)
       → users 테이블에서 추가 프로필 조회
로그아웃 → JWT 세션 종료
```

#### 여정 데이터

```
출발 클릭 → trips 테이블 INSERT (status: DRIVING)
         → start_time, start_location 저장

환승 클릭 → trips UPDATE (status: TRANSFERRED)
         → transfer_time, transfer_location 저장
         → 사진 촬영 → Supabase Storage 업로드
         → transfer_image_url 업데이트

도착 클릭 → trips UPDATE (status: COMPLETED)
         → arrival_time, arrival_location 저장
         → 사진 촬영 → Supabase Storage 업로드
         → arrival_image_url 업데이트
         → estimated_points 계산 및 저장

관리자 승인 → trips UPDATE (status: APPROVED, earned_points 설정)
           → users.total_points += earned_points

관리자 반려 → trips UPDATE (status: REJECTED, admin_note 설정)
```

#### 포인트 데이터

```
여정 완료 (COMPLETED) → estimated_points 자동 계산 및 표시
관리자 승인 (APPROVED) → earned_points 확정
                      → users.total_points 누적 (DB 트리거 또는 Edge Function)
```

---

## 카메라 인증 프로세스

### 사진 촬영 요구사항

#### 환승 단계 (주차 인증)

- **촬영 대상**: 주차된 차량
- **포함 요소**: 차량 번호판, 주차 위치
- **권장 사항**: 주차장 시설물이 보이도록 촬영

#### 도착 단계 (역 인증)

- **촬영 대상**: 지하철역 내부 또는 출구
- **포함 요소**: 역명 표지판, 지하철 시설물
- **권장 사항**: 역명이 명확히 보이는 사진

### 사진 업로드 플로우

```
1. 버튼 클릭 (환승 또는 도착)
   ↓
2. 권한 확인
   - 카메라 권한 체크
   - 없으면 권한 요청
   - 거부 시 설정 화면 안내
   ↓
3. 카메라 실행
   - 네이티브 카메라 앱 또는 인앱 카메라
   - 촬영 완료 → 프리뷰 표시
   ↓
4. 이미지 처리
   - 압축 (최대 1920x1080, PNG 80%)
   - 파일명 생성: {trip_id}_{stage}.jpg
   ↓
5. Supabase Storage 업로드
   - 경로: trips/{trip_id}/transfer.jpg 또는 arrival.jpg
   - 업로드 진행률 표시
   - 실패 시 재시도 옵션
   ↓
6. DB 업데이트
   - trips 테이블에 이미지 URL 저장
   - GPS 좌표 및 시간 함께 저장
   ↓
7. UI 피드백
   - 업로드 완료 메시지
   - 다음 단계 버튼 활성화
```

### 오류 처리

| 오류 상황        | 대응 방안                       |
| ---------------- | ------------------------------- |
| 카메라 권한 거부 | 설정 화면 안내, 대체 방법 제시  |
| 네트워크 오류    | 로컬 저장 후 나중에 업로드      |
| 업로드 실패      | 재시도 버튼 표시, 최대 3회 시도 |
| 용량 초과        | 압축 비율 증가 또는 해상도 감소 |

---

## 핵심 데이터 흐름

### 1. 여정 기록 및 포인트 적립 흐름

#### 단계 1: 출발 (Start)

```
사용자 "출발" 버튼 클릭
→ GPS 위치 수집
→ Supabase trips 테이블 INSERT:
   - user_id: 현재 로그인 사용자
   - start_time: 현재 시간
   - start_location: geography(Point) 형식 GPS 좌표
   - status: 'DRIVING'
→ 로컬에 trip_id 저장 (진행 중 여정 추적용)
```

#### 단계 2: 환승 (Transfer)

```
사용자 "환승" 버튼 클릭
→ GPS 위치 수집
→ 카메라 실행 → 주차 차량 사진 촬영
→ Supabase Storage 업로드:
   - 버킷: trips
   - 경로: {trip_id}/transfer.jpg
   - 권한: JWT 토큰으로 user_id 검증
→ Supabase trips 테이블 UPDATE:
   - transfer_time: 현재 시간
   - transfer_location: GPS 좌표
   - transfer_image_url: Storage 경로
   - status: 'TRANSFERRED'
```

#### 단계 3: 도착 (Arrival)

```
사용자 "도착" 버튼 클릭
→ GPS 위치 수집
→ 카메라 실행 → 지하철역 인증 사진 촬영
→ Supabase Storage 업로드:
   - 경로: {trip_id}/arrival.jpg
→ 거리 계산 (PostGIS ST_Distance):
   - start_location ↔ transfer_location
   - transfer_location ↔ arrival_location
   - 총 이동 거리 계산
→ 예상 포인트 계산 (거리 기반 공식)
→ Supabase trips 테이블 UPDATE:
   - arrival_time: 현재 시간
   - arrival_location: GPS 좌표
   - arrival_image_url: Storage 경로
   - estimated_points: 계산된 예상 포인트
   - status: 'COMPLETED'
→ 로컬 진행 중 여정 정보 삭제
```

#### 단계 4: 관리자 승인 (앱 외부 - 웹 관리자 도구)

```
관리자 검토 페이지에서 COMPLETED 여정 조회
→ 제출된 정보 확인:
   - GPS 좌표 3개 (출발/환승/도착) 지도 표시
   - 사진 2장 (주차 인증/역 인증) 표시
   - 이동 거리 및 예상 포인트 표시

→ 검증:
   - 환승 GPS가 등록된 주차장 근처인지 확인
   - 도착 GPS가 등록된 역 근처인지 확인
   - 사진이 적절한지 육안 검증

→ 승인 결정:
   [승인] → trips UPDATE:
            - status: 'APPROVED'
            - earned_points: estimated_points (또는 조정값)
          → users UPDATE:
            - total_points += earned_points

   [반려] → trips UPDATE:
            - status: 'REJECTED'
            - admin_note: 반려 사유

→ 사용자 앱에서 실시간 또는 새로고침 시 결과 확인
```

### 2. 역 및 주차장 정보 조회 흐름

#### 대구 지하철 노선도 UI

```
앱 시작 또는 지도 탭 진입
→ Supabase stations, parking_lots 테이블 조회
   - SELECT * FROM stations WHERE line_number IN (1, 2, 3)
   - JOIN parking_lots ON parking_lots.station_id = stations.id
→ 노선별로 그룹화하여 UI 렌더링
→ 노선도 이미지 위에 역 마커 표시
```

#### 역 선택 및 주차장 정보 표시

```
사용자가 노선도에서 특정 역 클릭
→ 선택된 역의 station_id로 주차장 조회:
   SELECT * FROM parking_lots WHERE station_id = {선택된 역 ID}

→ 하단 시트 또는 모달에 정보 표시:
   - 역명 (예: "중앙로역")
   - 노선 (예: "1호선")
   - 연계 주차장 리스트:
     * 주차장 명칭
     * 주소
     * 역까지 거리 (m)
     * 요금 정보
→ 선택적으로 지도 위에 주차장 위치 마커 표시
```

### 3. 인증 흐름

#### 회원가입

```
이메일/비밀번호/사용자명/차량번호(선택) 입력
→ Supabase Auth 계정 생성:
   - email은 auth.users 테이블에 저장
→ 성공 시 자동으로 users 테이블에 레코드 생성:
   - id: auth.uid() (트리거로 자동)
   - username, vehicle_number
   - total_points: 0 (기본값)
→ 이메일 인증 하지 않음
→ 자동 로그인 (JWT 발급)
→ 홈 화면 이동
```

#### 로그인

```
이메일/비밀번호 입력
→ Supabase Auth 인증:
   - email 정보는 auth.users에서 확인
→ JWT 발급 및 세션 저장
→ users 테이블에서 추가 프로필 조회:
   SELECT username, vehicle_number, total_points FROM users WHERE id = auth.uid()
→ 앱 상태에 사용자 정보 로드
→ 홈 화면 이동
```

#### 인증 가드

```
미인증 사용자 + 보호된 경로 접근
  → Supabase Auth 세션 확인
  → 세션 없음 → /auth/login 리디렉션

인증된 사용자 + /auth/* 접근
  → 세션 있음 → / 홈 리디렉션

자동 세션 갱신
  → Supabase SDK가 JWT 만료 시 자동 갱신
  → 갱신 실패 시 로그아웃 처리
```

---

## 샘플 데이터 (대구 지하철)

### 대구 지하철 노선 정보

**1호선** (빨간색)

- 총 30개 역
- 설화명곡 ~ 안심 구간
- 주요 역: 중앙로, 대구역, 반월당

**2호선** (초록색)

- 총 31개 역
- 문양 ~ 영남대 구간
- 주요 역: 반월당, 경대병원, 대공원

**3호선** (주황색, 모노레일)

- 총 30개 역
- 칠곡경대병원 ~ 용지 구간
- 주요 역: 칠곡경대병원, 만촌, 수성못

### 샘플 역 및 주차장 데이터

#### 1. 중앙로역 (1호선)

- **GPS 좌표**: 35.8694° N, 128.5989° E
- **연계 주차장**:
  - 동성로 공영주차장: 500m, 10분당 500원
  - 대구백화점 주차장: 300m, 30분당 2000원

#### 2. 반월당역 (1/2호선 환승역)

- **GPS 좌표**: 35.8581° N, 128.5924° E
- **연계 주차장**:
  - 반월당 공영주차장: 400m, 10분당 600원
  - 롯데백화점 대구점: 200m, 30분당 2500원

#### 3. 대구역 (1호선)

- **GPS 좌표**: 35.8797° N, 128.6283° E
- **연계 주차장**:
  - 대구역 환승주차장: 100m, 1일 3000원
  - KTX 대구역 주차장: 200m, 30분당 1000원

#### 4. 수성못역 (3호선)

- **GPS 좌표**: 35.8255° N, 128.6411° E
- **연계 주차장**:
  - 수성못 공영주차장: 600m, 1일 2000원

---

## 주요 고려사항

### GPS 정확도 및 검증

**문제**: 사용자가 주차장/역이 아닌 곳에서 버튼 클릭

**해결 방안**:

1. **클라이언트 측 사전 검증**

   - 등록된 주차장/역 위치와 현재 GPS 거리 계산
   - 일정 반경 (예: 500m) 이내일 때만 허용
   - 경고 메시지 표시

2. **서버 측 검증 (권장)**
   - Supabase Edge Function 사용
   - PostGIS ST_DWithin 함수로 반경 검증
   - JWT 토큰으로 사용자 인증 및 user_id 검증
   - 부정 요청 자동 차단

### 사진 업로드 최적화

**문제**: 고해상도 사진으로 인한 업로드 지연 및 저장소 용량 증가

**해결**:

- 촬영 즉시 이미지 압축
- 최대 해상도 제한 (예: 1920x1080)
- 압축 품질 80% 적용
- 업로드 전 프리뷰 표시 및 재촬영 옵션 제공

### 오프라인 대응

**문제**: 네트워크 불안정 시 데이터 손실

**해결**:

- 로컬 DB에 임시 저장
- 네트워크 복구 시 자동 동기화
- 업로드 대기 큐 관리
- 사용자에게 상태 표시 (동기화 중, 오프라인 등)

### Supabase 실시간 구독

**실시간 여정 상태 업데이트**

**적용 시나리오**:

- 여정 상태가 COMPLETED → APPROVED/REJECTED로 변경될 때
- 포인트가 지급되어 total_points가 업데이트될 때

---

## 확장 가능성

### 관리자 기능 확장

1. **웹 관리자 도구**:

   - 여정 승인/반려 시스템
   - GPS 트래킹 시각화 (지도에 동선 표시)
   - 사진 일괄 검토 인터페이스
   - 통계 대시보드 (승인율, 부정 사용 패턴 등)

2. **자동화 검증**:

   - AI 기반 사진 인증 자동 검증
   - GPS 패턴 이상 탐지
   - 자동 승인 규칙 설정

3. **역/주차장 관리**:
   - 웹에서 역 및 주차장 등록/수정
   - 주차장 요금 업데이트
   - 운영 시간 관리

### 데이터 기능 확장

1. **실시간 주차장 정보**: IoT 센서 연동으로 실시간 주차 가능 대수 표시
2. **경로 추천 시스템**: GPS 기반 최적 환승 주차장 추천
3. **예측 분석**: 시간대별 주차장 혼잡도 예측
4. **리워드 시스템**: 포인트 사용처 확장 (주차 할인, 지하철 이용권 등)
5. **통계 대시보드**: 개인별 CO2 절감 누적, 월별/연간 이동 통계

### 데이터 소스 개선

1. **공공 데이터 연동**:

   - 대구 도시철도공사 실시간 운행 정보
   - 주차장 공공 데이터 API

2. **알림 시스템**:
   - 여정 승인/반려 푸시 알림
   - 포인트 적립 알림
   - 이벤트 및 프로모션 알림

---

## 현재 제약사항

1. **초기 데이터 부족**:

   - 대구 지하철 전체 역 데이터 미등록
   - 추천 주차장 관리자가 수동 등록 필요

2. **수동 승인 필요**:

   - 관리자가 모든 여정 수동 검증
   - 자동 승인 기능 없음

3. **앱 단독 운영**:

   - 관리자 웹 도구 미구현
   - 앱에서는 승인 기능 없음

4. **사진 인증 의존**:

   - 사진 위조 가능성
   - 사진 품질에 따른 검증 난이도

5. **GPS 정확도**:

   - 실내/지하에서 GPS 오차 발생 가능
   - 터널, 빌딩 밀집 지역에서 부정확

6. **단일 언어**: 한국어만 지원

---

**마지막 업데이트**: 2025-12-26  
**백엔드**: Supabase (Auth + PostgreSQL + PostGIS + Storage)  
**대상 지역**: 대구광역시 지하철 1, 2, 3호선
