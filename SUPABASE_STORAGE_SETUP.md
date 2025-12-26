# Supabase Storage Setup Guide

## 개요

이 가이드는 SI-EcoPass 백엔드에서 여행 인증 이미지를 저장하기 위한 Supabase Storage 버킷 설정 방법을 안내합니다.

**중요**: Supabase Storage 버킷은 프로그래밍 방식으로 생성할 수 없으므로, **반드시 Supabase Dashboard에서 수동으로 설정**해야 합니다.

---

## 1. Storage Bucket 생성

### 1.1 Supabase Dashboard 접속

1. [Supabase Dashboard](https://app.supabase.com)에 로그인
2. 프로젝트 선택
3. 왼쪽 메뉴에서 **Storage** 클릭

### 1.2 새 버킷 생성

1. **"New Bucket"** 버튼 클릭
2. 버킷 설정:
   - **Name**: `trips`
   - **Public**: **No** (비공개 - JWT 인증 필요)
   - **File size limit**: `5MB`
   - **Allowed MIME types**: `image/jpeg, image/png`

3. **"Create bucket"** 클릭하여 생성 완료

---

## 2. Row Level Security (RLS) 정책 설정

버킷을 생성한 후, 사용자가 **자신의 여행 이미지만** 업로드/조회/삭제할 수 있도록 RLS 정책을 설정해야 합니다.

### 2.1 SQL Editor 접속

1. Supabase Dashboard에서 왼쪽 메뉴의 **SQL Editor** 클릭
2. **"New query"** 클릭

### 2.2 RLS 정책 SQL 실행

아래 SQL을 복사하여 실행:

```sql
-- ============================================================
-- RLS 정책: 사용자가 자신의 여행 이미지만 관리
-- ============================================================

-- 1. 업로드 정책: 본인 여행에만 이미지 업로드 가능
CREATE POLICY "Users can upload to their own trips"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'trips' AND
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM trips WHERE user_id = auth.uid()
  )
);

-- 2. 조회 정책: 본인 여행 이미지만 조회 가능
CREATE POLICY "Users can view their own trip images"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'trips' AND
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM trips WHERE user_id = auth.uid()
  )
);

-- 3. 삭제 정책: 본인 여행 이미지만 삭제 가능
CREATE POLICY "Users can delete their own trip images"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'trips' AND
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM trips WHERE user_id = auth.uid()
  )
);

-- 4. 업데이트 정책: 본인 여행 이미지만 업데이트 가능
CREATE POLICY "Users can update their own trip images"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'trips' AND
  (storage.foldername(name))[1] IN (
    SELECT id::text FROM trips WHERE user_id = auth.uid()
  )
);
```

### 2.3 정책 설명

- **`storage.foldername(name)[1]`**: 파일 경로에서 첫 번째 폴더명 추출 (= trip_id)
- **`auth.uid()`**: 현재 로그인한 사용자의 UUID (JWT 토큰에서 추출)
- **`trips` 테이블 조인**: 해당 trip_id가 현재 사용자 소유인지 검증

**파일 경로 예시**:
- 경로: `{trip_id}/{stage}.jpg`
- 실제: `123e4567-e89b-12d3-a456-426614174000/transfer.jpg`
- `foldername(name)[1]` → `123e4567-e89b-12d3-a456-426614174000` (trip_id)

---

## 3. 설정 검증

### 3.1 API 테스트

1. FastAPI 서버 실행:
   ```bash
   uv run python main.py
   ```

2. Swagger UI 접속: http://localhost:8000/docs

3. 인증 토큰 발급:
   - `POST /api/v1/auth/signup` 또는 `POST /api/v1/auth/login` 실행
   - 응답에서 `access_token` 복사

4. 여행 생성 (Phase 4 API):
   - `POST /api/v1/trips` 엔드포인트 실행
   - 응답에서 `trip_id` 복사

5. 이미지 업로드:
   - `POST /api/v1/trips/{trip_id}/upload-image` 실행
   - **Authorization**: `Bearer {access_token}`
   - **Form Data**:
     - `image`: 이미지 파일 선택 (JPEG/PNG, 5MB 이하)
     - `stage`: `transfer` 또는 `arrival`

6. 성공 응답 예시:
   ```json
   {
     "status": "success",
     "message": "transfer 이미지가 업로드되었습니다",
     "data": {
       "image_url": "https://[project-id].supabase.co/storage/v1/object/public/trips/123e4567-e89b-12d3-a456-426614174000/transfer.jpg",
       "uploaded_at": "2025-01-26T12:00:00Z",
       "stage": "transfer"
     }
   }
   ```

### 3.2 Storage 확인

1. Supabase Dashboard → **Storage** → **trips** 버킷 클릭
2. `{trip_id}/transfer.jpg` 또는 `{trip_id}/arrival.jpg` 파일 확인
3. 파일 클릭 시 공개 URL로 접근 가능

---

## 4. 트러블슈팅

### 4.1 업로드 실패: "new row violates row-level security policy"

**원인**: RLS 정책이 제대로 설정되지 않았거나, trip_id가 현재 사용자 소유가 아님

**해결**:
1. SQL Editor에서 RLS 정책이 올바르게 생성되었는지 확인:
   ```sql
   SELECT * FROM pg_policies WHERE tablename = 'objects';
   ```
2. `trips` 테이블에서 해당 여행이 현재 사용자 소유인지 확인:
   ```sql
   SELECT * FROM trips WHERE id = '{trip_id}' AND user_id = auth.uid();
   ```

### 4.2 파일 크기 초과

**증상**: `"파일 크기가 너무 큽니다"` 에러

**해결**:
- 이미지를 5MB 이하로 압축
- JPEG 품질을 낮춤 (예: 80%)
- 이미지 해상도 조정

### 4.3 MIME 타입 오류

**증상**: `"지원하지 않는 파일 형식입니다"` 에러

**해결**:
- JPEG 또는 PNG 형식만 허용됨
- HEIC, WebP 등의 형식은 변환 필요

### 4.4 동일 단계 이미지 중복

**동작**: 동일한 단계(transfer/arrival)에 이미지를 다시 업로드하면 **기존 이미지가 자동 삭제**되고 새 이미지로 교체됩니다.

---

## 5. API 명세

### 엔드포인트

```
POST /api/v1/trips/{trip_id}/upload-image
```

### 요청

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Form Data**:
- `image` (File, required): 이미지 파일 (JPEG/PNG, 최대 5MB)
- `stage` (string, required): 이미지 단계 (`transfer` 또는 `arrival`)

### 응답

**성공 (200 OK)**:
```json
{
  "status": "success",
  "message": "transfer 이미지가 업로드되었습니다",
  "data": {
    "image_url": "https://[project-id].supabase.co/storage/v1/object/public/trips/{trip_id}/{stage}.jpg",
    "uploaded_at": "2025-01-26T12:00:00Z",
    "stage": "transfer"
  }
}
```

**에러 (422 Unprocessable Entity)**:
```json
{
  "status": "error",
  "message": "파일 크기가 너무 큽니다. 최대 5MB 허용 (현재: 8.5MB)",
  "data": null
}
```

**에러 (401 Unauthorized)**:
```json
{
  "status": "error",
  "message": "본인의 여행에만 이미지를 업로드할 수 있습니다",
  "data": null
}
```

**에러 (404 Not Found)**:
```json
{
  "status": "error",
  "message": "여행을 찾을 수 없습니다 (ID: {trip_id})",
  "data": null
}
```

---

## 6. 파일 구조

업로드된 이미지는 다음 경로에 저장됩니다:

```
trips/
└── {trip_id}/
    ├── transfer.jpg  (환승 인증 이미지)
    └── arrival.jpg   (도착 인증 이미지)
```

**예시**:
```
trips/
└── 123e4567-e89b-12d3-a456-426614174000/
    ├── transfer.jpg
    └── arrival.jpg
```

---

## 7. 보안 고려사항

1. **비공개 버킷**: `trips` 버킷은 비공개로 설정하여 JWT 인증 없이는 접근 불가
2. **RLS 정책**: 사용자는 오직 자신의 여행 이미지만 관리 가능
3. **파일 검증**: 서버에서 MIME 타입과 파일 크기 검증
4. **토큰 검증**: Supabase Auth를 통한 JWT 토큰 검증

---

## 8. 참고 자료

- [Supabase Storage 공식 문서](https://supabase.com/docs/guides/storage)
- [Supabase RLS 정책 가이드](https://supabase.com/docs/guides/storage/security/access-control)
- [FastAPI File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)

---

**설정 완료 후**: Phase 5 구현이 완료되었습니다. 이미지 업로드 API를 테스트하고, 필요 시 Phase 4 (Trip Management)와 통합하세요.
