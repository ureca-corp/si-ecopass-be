# Admin Setup Guide

## 개요

SI-EcoPass 백엔드의 관리자 권한 시스템 설정 가이드입니다. 관리자는 사용자가 완료한 여정(Trip)을 검토하고 승인/반려할 수 있는 권한을 가집니다.

## 관리자 권한 부여 방법

### 1. Supabase Dashboard를 통한 관리자 설정

관리자 권한은 Supabase Authentication의 사용자 메타데이터를 수정하여 부여합니다.

#### 단계별 설정

1. **Supabase Dashboard 접속**
   - 프로젝트의 Supabase Dashboard에 로그인
   - URL: `https://app.supabase.com/project/<YOUR_PROJECT_ID>`

2. **사용자 메타데이터 수정**
   - 좌측 메뉴에서 **Authentication** → **Users** 클릭
   - 관리자 권한을 부여할 사용자 찾기
   - 사용자 행을 클릭하여 상세 페이지 진입

3. **User Metadata 편집**
   - 우측 패널에서 **User Metadata** 섹션 찾기
   - **Edit** 버튼 클릭
   - 다음 JSON 추가:
     ```json
     {
       "role": "admin"
     }
     ```
   - **Save** 버튼 클릭

4. **변경사항 확인**
   - 사용자 상세 페이지에서 User Metadata가 업데이트되었는지 확인
   - `role: "admin"`이 표시되어야 함

### 2. 관리자 권한 검증

관리자로 설정된 사용자가 정상적으로 관리자 API에 접근할 수 있는지 테스트합니다.

#### 테스트 절차

1. **관리자 사용자로 로그인**
   ```bash
   POST /api/v1/auth/login
   Content-Type: application/json

   {
     "email": "admin@example.com",
     "password": "your_password"
   }
   ```

2. **JWT 토큰 복사**
   - 응답에서 `access_token` 복사
   - 예: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. **관리자 API 호출 테스트**
   ```bash
   GET /api/v1/admin/trips/pending
   Authorization: Bearer <YOUR_ACCESS_TOKEN>
   ```

4. **응답 확인**
   - 정상: `200 OK` + 승인 대기 여정 목록
   - 권한 없음: `403 Forbidden` + "관리자 권한이 필요합니다"
   - 토큰 없음: `401 Unauthorized` + "인증 토큰이 필요합니다"

## 관리자 API 사용 가이드

### 1. 승인 대기 여정 목록 조회

COMPLETED 상태의 여정 목록을 조회합니다.

```bash
GET /api/v1/admin/trips/pending?limit=10&offset=0
Authorization: Bearer <ACCESS_TOKEN>
```

**쿼리 파라미터:**
- `limit` (선택): 조회할 여정 개수 (기본값: 10, 최대: 100)
- `offset` (선택): 건너뛸 여정 개수 (기본값: 0)

**응답 예시:**
```json
{
  "status": "success",
  "message": "승인 대기 여정 목록 조회 성공",
  "data": {
    "trips": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "start_latitude": 37.5665,
        "start_longitude": 126.9780,
        "transfer_latitude": 37.5700,
        "transfer_longitude": 126.9800,
        "transfer_image_url": "https://storage.example.com/transfer.jpg",
        "arrival_latitude": 37.5750,
        "arrival_longitude": 126.9850,
        "arrival_image_url": "https://storage.example.com/arrival.jpg",
        "status": "COMPLETED",
        "estimated_points": 150,
        "earned_points": null,
        "admin_note": null,
        "started_at": "2025-01-01T09:00:00Z",
        "transferred_at": "2025-01-01T09:15:00Z",
        "arrived_at": "2025-01-01T09:30:00Z",
        "approved_at": null,
        "rejected_at": null,
        "created_at": "2025-01-01T09:00:00Z",
        "updated_at": "2025-01-01T09:30:00Z"
      }
    ],
    "total_count": 25
  }
}
```

### 2. 여정 승인 및 포인트 지급

여정을 승인하고 사용자에게 포인트를 지급합니다.

```bash
POST /api/v1/admin/trips/{trip_id}/approve
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "earned_points": 150
}
```

**요청 바디:**
- `earned_points` (선택): 지급할 포인트 (미입력 시 `estimated_points` 사용)

**응답 예시:**
```json
{
  "status": "success",
  "message": "여정이 승인되었습니다 (지급 포인트: 150점)",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "APPROVED",
    "earned_points": 150,
    "approved_at": "2025-01-01T10:00:00Z",
    ...
  }
}
```

**동작:**
1. 여정 상태를 `COMPLETED` → `APPROVED`로 변경
2. `earned_points` 설정 (미입력 시 `estimated_points` 사용)
3. 사용자의 `total_points`에 `earned_points` 추가
4. `approved_at` 타임스탬프 기록

### 3. 여정 반려 및 사유 기록

여정을 반려하고 반려 사유를 기록합니다.

```bash
POST /api/v1/admin/trips/{trip_id}/reject
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "admin_note": "주차 인증 사진이 명확하지 않습니다"
}
```

**요청 바디:**
- `admin_note` (필수): 반려 사유 (1-500자)

**응답 예시:**
```json
{
  "status": "success",
  "message": "여정이 반려되었습니다",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "REJECTED",
    "admin_note": "주차 인증 사진이 명확하지 않습니다",
    "rejected_at": "2025-01-01T10:00:00Z",
    ...
  }
}
```

**동작:**
1. 여정 상태를 `COMPLETED` → `REJECTED`로 변경
2. `admin_note`에 반려 사유 기록
3. `rejected_at` 타임스탬프 기록
4. 포인트는 지급되지 않음

## 관리자 워크플로우 예시

### 시나리오 1: 정상 여정 승인

1. **여정 검토**
   - 관리자가 승인 대기 목록 조회: `GET /admin/trips/pending`
   - GPS 좌표 확인 (출발 → 환승 → 도착 경로가 합리적인가?)
   - 증빙 이미지 확인 (환승 주차 사진, 도착 대중교통 사진)

2. **여정 승인**
   - 예상 포인트 그대로 승인: `POST /admin/trips/{trip_id}/approve` (바디 없음)
   - 또는 포인트 조정하여 승인: `{"earned_points": 200}`

3. **결과**
   - 여정 상태: `APPROVED`
   - 사용자 포인트 증가: `total_points += earned_points`
   - 사용자는 앱에서 승인된 여정과 지급된 포인트 확인 가능

### 시나리오 2: 부적절한 여정 반려

1. **문제 발견**
   - GPS 좌표가 실제 주차장/대중교통 역과 거리가 멈
   - 증빙 이미지가 흐릿하거나 관련 없는 사진
   - 출발-환승-도착 경로가 비정상적

2. **여정 반려**
   ```json
   POST /admin/trips/{trip_id}/reject
   {
     "admin_note": "GPS 좌표가 주차장 위치와 일치하지 않습니다. 실제 주차 위치를 확인해주세요."
   }
   ```

3. **결과**
   - 여정 상태: `REJECTED`
   - 포인트 지급 없음
   - 사용자는 반려 사유를 확인하고 다음번에 더 정확하게 인증 가능

### 시나리오 3: 포인트 조정 승인

1. **부분 승인 필요**
   - 여정은 유효하나 일부 기준 미달 (예: 이미지 품질 낮음)
   - 예상 포인트보다 낮게 지급하여 승인

2. **포인트 조정**
   ```json
   POST /admin/trips/{trip_id}/approve
   {
     "earned_points": 100
   }
   ```
   - 예상 포인트(150점)보다 낮은 100점만 지급

3. **결과**
   - 여정 상태: `APPROVED`
   - 사용자 포인트: +100점 (estimated_points 대신 earned_points 적용)

## 보안 및 주의사항

### 1. 관리자 권한 관리

- 관리자 권한은 신중하게 부여
- 최소 권한 원칙: 필요한 인원에게만 관리자 권한 부여
- 정기적인 관리자 계정 검토 및 불필요한 권한 회수

### 2. 권한 검증 메커니즘

관리자 API는 다음과 같이 검증됩니다:

```python
# src/api/dependencies/admin_deps.py
async def get_admin_user(...) -> User:
    # 1. JWT 토큰 검증
    user_response = db.auth.get_user(token)

    # 2. user_metadata.role 확인
    user_metadata = user_response.user.user_metadata
    if user_metadata.get("role") != "admin":
        raise ForbiddenError("관리자 권한이 필요합니다")

    # 3. 관리자 User 객체 반환
    return user
```

### 3. 트랜잭션 제한사항

**중요**: Supabase Python 클라이언트는 현재 트랜잭션을 지원하지 않습니다.

**영향:**
- 여정 승인 시 "여정 업데이트" → "포인트 지급"이 별도 쿼리로 실행
- 중간에 오류 발생 시 일관성 문제 가능 (여정은 승인되었으나 포인트 미지급)

**대응 방안:**
- 현재: 오류 발생 시 ValidationError로 실패 처리
- 향후: 에러 로깅 및 수동 복구, 또는 Supabase Edge Function 활용

### 4. 감사 로그

향후 추가 권장사항:
- 모든 관리자 작업(승인/반려)을 별도 테이블에 로깅
- 누가(admin_id), 언제(timestamp), 무엇을(trip_id, action) 기록
- 감사 추적 및 문제 발생 시 원인 분석 용이

## API 문서

관리자 API의 상세 스펙은 Swagger UI에서 확인 가능합니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Admin** 태그의 3개 엔드포인트:
1. `GET /api/v1/admin/trips/pending` - 승인 대기 목록
2. `POST /api/v1/admin/trips/{trip_id}/approve` - 여정 승인
3. `POST /api/v1/admin/trips/{trip_id}/reject` - 여정 반려

## 문제 해결 (Troubleshooting)

### Q1: 관리자로 설정했는데 403 Forbidden 발생

**원인:** User Metadata가 제대로 설정되지 않음

**해결:**
1. Supabase Dashboard → Authentication → Users에서 사용자 확인
2. User Metadata에 `"role": "admin"`이 정확히 입력되었는지 확인
3. JSON 형식 오류 체크 (쉼표, 따옴표 등)
4. 브라우저 캐시 삭제 후 재시도

### Q2: 여정 승인 후 포인트가 증가하지 않음

**원인:** AuthService의 add_points 실패

**해결:**
1. API 응답 확인: 에러 메시지에 "포인트 지급 실패" 포함되어 있는지 확인
2. Supabase 로그 확인: users 테이블 업데이트 쿼리 실패 여부
3. 사용자 ID가 유효한지 확인 (user_id가 users 테이블에 존재해야 함)

### Q3: COMPLETED 상태가 아닌 여정을 승인하려고 할 때

**에러:**
```json
{
  "status": "error",
  "message": "현재 상태(DRIVING)에서는 승인할 수 없습니다"
}
```

**해결:**
- 여정이 COMPLETED 상태인지 확인
- 사용자가 "도착 완료"까지 정상적으로 진행했는지 확인
- 필요 시 사용자에게 도착 완료 요청

## 다음 단계

1. **관리자 대시보드 UI 개발** (프론트엔드)
   - 승인 대기 목록을 표 형태로 표시
   - 지도에 GPS 좌표 시각화
   - 이미지 미리보기 및 확대 기능
   - 승인/반려 버튼과 포인트 입력 UI

2. **통계 API 추가**
   - 일별/월별 승인/반려 통계
   - 사용자별 승인율
   - 평균 포인트 지급액

3. **알림 시스템**
   - 여정 승인/반려 시 사용자에게 푸시 알림
   - 승인 대기 여정 누적 시 관리자에게 알림

4. **감사 로그 테이블 추가**
   - 모든 관리자 작업 기록
   - 보안 및 규정 준수
