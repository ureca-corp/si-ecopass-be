# API 호출 플로우

주요 기능별 API 호출 순서 가이드

---

## 1. 회원가입 및 로그인

### 회원가입

```
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "password123",
  "username": "에코유저",
  "vehicle_number": "12가3456"
}

→ access_token 자동 발급 (자동 로그인)
→ 토큰 저장 (flutter_secure_storage)
```

### 로그인

```
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

→ access_token 획득
→ 토큰 저장
```

---

## 2. 여정 완료 플로우 (핵심)

### Step 1: 출발

```
사용자가 "출발" 버튼 클릭
↓
GPS 위치 획득
↓
POST /api/v1/trips/start
Authorization: Bearer {token}
{
  "latitude": 35.8809,
  "longitude": 128.6286
}

→ trip_id 저장 (로컬 상태)
→ status: DRIVING
```

### Step 2: 환승 (주차장 도착)

```
사용자가 "환승" 버튼 클릭
↓
카메라로 주차 사진 촬영
↓
이미지 압축 (flutter_image_compress)
↓
POST /api/v1/storage/upload/transfer
Authorization: Bearer {token}
Content-Type: multipart/form-data
file: {compressed_image}

→ image_url 획득
↓
GPS 위치 획득
↓
POST /api/v1/trips/{trip_id}/transfer
Authorization: Bearer {token}
{
  "latitude": 35.8714,
  "longitude": 128.5988,
  "transfer_image_url": "{image_url}"
}

→ status: TRANSFERRED
```

### Step 3: 도착 (지하철역 도착)

```
사용자가 "도착" 버튼 클릭
↓
카메라로 역 사진 촬영
↓
이미지 압축
↓
POST /api/v1/storage/upload/arrival
Authorization: Bearer {token}
Content-Type: multipart/form-data
file: {compressed_image}

→ image_url 획득
↓
GPS 위치 획득
↓
POST /api/v1/trips/{trip_id}/arrival
Authorization: Bearer {token}
{
  "latitude": 35.8569,
  "longitude": 128.5932,
  "arrival_image_url": "{image_url}"
}

→ status: COMPLETED
→ estimated_points 표시
→ 관리자 승인 대기 안내
```

### Step 4: 승인 확인

```
주기적으로 또는 사용자 요청 시:

GET /api/v1/trips/{trip_id}
Authorization: Bearer {token}

→ status 확인
   - COMPLETED: 아직 승인 대기 중
   - APPROVED: 승인 완료, earned_points 지급됨
   - REJECTED: 반려됨, admin_note 확인

승인 완료 시:
GET /api/v1/auth/profile
→ 업데이트된 total_points 확인
```

---

## 3. 역 및 주차장 조회

### 앱 시작 시 역 목록 로드

```
GET /api/v1/stations

→ 전체 역 목록 캐싱
→ 노선별로 그룹화하여 UI 표시
```

### 호선별 필터링

```
GET /api/v1/stations?line_number=1

→ 1호선 역만 표시
```

### 역 선택 시 주차장 정보

```
사용자가 지도에서 역 클릭
↓
GET /api/v1/stations/{station_id}/parking-lots

→ 해당 역의 주차장 목록 표시
→ 주차장별 거리, 요금 정보 표시
```

### 현재 위치 기반 주변 역 검색

```
GPS 위치 획득
↓
GET /api/v1/stations/nearby?latitude=35.8809&longitude=128.6286&radius=5000

→ 반경 5km 내 역 목록 표시
→ 거리순 정렬
```

---

## 4. 여정 이력 조회

### 전체 여정 목록

```
GET /api/v1/trips?limit=20&offset=0
Authorization: Bearer {token}

→ 최근 20개 여정 표시
→ 무한 스크롤 구현 (offset 증가)
```

### 상태별 필터링

```
# 승인 대기 중인 여정만
GET /api/v1/trips?status=COMPLETED

# 승인 완료된 여정만
GET /api/v1/trips?status=APPROVED

# 반려된 여정만
GET /api/v1/trips?status=REJECTED
```

### 특정 여정 상세보기

```
사용자가 여정 항목 클릭
↓
GET /api/v1/trips/{trip_id}
Authorization: Bearer {token}

→ 상세 정보 표시:
   - 출발/환승/도착 위치 (지도에 마커)
   - 인증 사진 2장
   - 상태 및 포인트
   - 날짜/시간
```

---

## 5. 프로필 관리

### 프로필 조회

```
GET /api/v1/auth/profile
Authorization: Bearer {token}

→ 사용자 정보 표시:
   - 이메일
   - 사용자명
   - 차량 번호
   - 누적 포인트
```

### 프로필 수정

```
사용자가 프로필 편집
↓
PUT /api/v1/auth/profile
Authorization: Bearer {token}
{
  "username": "새닉네임",
  "vehicle_number": "56나7890"
}

→ 업데이트된 정보 표시
```

---

## 6. 에러 처리 패턴

### 401 Unauthorized (토큰 만료)

```
API 호출
↓
401 응답
↓
로그인 화면으로 리디렉션
↓
재로그인
↓
새 토큰 저장
↓
이전 작업 재시도
```

### 409 Conflict (중복 여정)

```
POST /api/v1/trips/start
↓
409 응답: "이미 진행 중인 여정이 있습니다"
↓
GET /api/v1/trips?status=DRIVING
↓
진행 중인 여정 표시
↓
"계속하기" 또는 "취소" 옵션 제공
```

### 네트워크 오류

```
API 호출
↓
네트워크 오류 발생
↓
로컬 DB에 임시 저장
↓
재시도 큐에 추가
↓
네트워크 복구 감지 (connectivity_plus)
↓
큐의 요청 순차 처리
```

---

## 7. 실시간 업데이트 (선택사항)

### 폴링 방식

```dart
// 5초마다 여정 상태 확인
Timer.periodic(Duration(seconds: 5), (timer) async {
  if (currentTripId != null) {
    final trip = await api.getTrip(currentTripId);
    if (trip.status == 'APPROVED' || trip.status == 'REJECTED') {
      // UI 업데이트 및 알림 표시
      timer.cancel();
    }
  }
});
```

### Supabase Realtime (향후 확장)

```dart
// Supabase Realtime으로 여정 상태 변경 구독
supabase
  .from('trips')
  .stream(primaryKey: ['id'])
  .eq('user_id', currentUserId)
  .listen((data) {
    // 실시간 업데이트 처리
  });
```

---

## 💡 베스트 프랙티스

### 1. 토큰 자동 갱신

```dart
// Dio 인터셉터로 401 자동 처리
dio.interceptors.add(InterceptorsWrapper(
  onError: (error, handler) async {
    if (error.response?.statusCode == 401) {
      // 로그인 페이지로 리디렉션
      navigateToLogin();
    }
    return handler.next(error);
  },
));
```

### 2. 낙관적 UI 업데이트

```dart
// API 호출 전 UI 먼저 업데이트
setState(() => tripStatus = 'TRANSFERRED');

try {
  await api.transferTrip(...);
} catch (e) {
  // 실패 시 롤백
  setState(() => tripStatus = 'DRIVING');
  showError(e);
}
```

### 3. 오프라인 지원

```dart
// 오프라인 시 로컬 저장
if (await isOffline()) {
  await localDb.savePendingTrip(tripData);
  showMessage('온라인 연결 시 자동으로 동기화됩니다');
} else {
  await api.createTrip(tripData);
}
```

---

**관련 문서**: 
- [00-quick-start.md](./00-quick-start.md)
- [swagger-guide.md](./swagger-guide.md)

