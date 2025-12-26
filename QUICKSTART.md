# 🚀 SI-EcoPass Backend - 빠른 시작 가이드

## 1️⃣ Supabase 프로젝트 생성 (5분)

### A. 프로젝트 생성
1. https://supabase.com 접속
2. "New Project" 클릭
3. 프로젝트명: `si-ecopass`
4. Database Password 설정 (메모해두기!)
5. Region: Northeast Asia (Seoul) 선택
6. "Create new project" 클릭

### B. Database Schema 생성

**SQL Editor에서 실행:**

```sql
-- 1. PostGIS 확장 활성화
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. users 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    vehicle_number TEXT,
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. stations 테이블
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number BETWEEN 1 AND 3),
    location GEOGRAPHY(POINT),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. parking_lots 테이블
CREATE TABLE parking_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    name TEXT NOT NULL,
    address TEXT,
    location GEOGRAPHY(POINT),
    distance_to_station_m INTEGER,
    fee_info TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. trips 테이블
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DRIVING', 'TRANSFERRED', 'COMPLETED', 'APPROVED', 'REJECTED')),
    start_latitude DOUBLE PRECISION NOT NULL,
    start_longitude DOUBLE PRECISION NOT NULL,
    transfer_latitude DOUBLE PRECISION,
    transfer_longitude DOUBLE PRECISION,
    transfer_image_url TEXT,
    arrival_latitude DOUBLE PRECISION,
    arrival_longitude DOUBLE PRECISION,
    arrival_image_url TEXT,
    estimated_points INTEGER,
    earned_points INTEGER,
    admin_note TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    transferred_at TIMESTAMPTZ,
    arrived_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. PostGIS RPC 함수 (좌표 추출용)
CREATE OR REPLACE FUNCTION get_stations_with_coords(p_line_number INT DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    name TEXT,
    line_number INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.line_number,
        ST_Y(s.location::geometry) AS latitude,
        ST_X(s.location::geometry) AS longitude,
        s.created_at,
        s.updated_at
    FROM stations s
    WHERE CASE WHEN p_line_number IS NOT NULL THEN s.line_number = p_line_number ELSE TRUE END
    ORDER BY s.name;
END;
$$;
```

### C. Storage 버킷 생성

1. **Storage** 메뉴 클릭
2. **New Bucket** 클릭
3. 이름: `trips`
4. **Public**: ❌ (Private - JWT 인증 필요)
5. **Create bucket** 클릭

### D. API Keys 복사

1. **Settings** → **API** 메뉴
2. 다음 값들 복사:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJhbG...` (긴 문자열)

---

## 2️⃣ 환경 변수 설정 (1분)

```bash
# .env 파일 생성
cat > .env << 'ENVFILE'
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# App Configuration
DEBUG=true
API_PREFIX=/api/v1
ENVFILE
```

**🔥 중요**: `.env` 파일에 실제 Supabase URL과 Key를 넣으세요!

---

## 3️⃣ 서버 실행 (1분)

```bash
# 서버 시작
uv run python main.py
```

**성공 메시지:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 4️⃣ API 문서 확인 (1분)

브라우저에서 열기:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 5️⃣ 테스트 실행 (선택사항)

```bash
# 전체 테스트
uv run pytest

# 특정 테스트만
uv run pytest tests/test_auth.py -v
```

---

## 🎯 다음 단계

### 옵션 A: Postman으로 API 테스트
```bash
# Postman 열기
open postman/SI-EcoPass-Backend.postman_collection.json
```

### 옵션 B: 관리자 계정 생성
1. Supabase Dashboard → Authentication → Users
2. 사용자 선택 → User Metadata 편집
3. JSON 추가: `{"role": "admin"}`

### 옵션 C: 샘플 데이터 추가
```sql
-- 테스트용 지하철 역 추가
INSERT INTO stations (name, line_number, location) VALUES
('반월당역', 1, ST_SetSRID(ST_MakePoint(128.5974, 35.8575), 4326)),
('중앙로역', 1, ST_SetSRID(ST_MakePoint(128.6069, 35.8687), 4326));
```

---

## ❓ 문제 해결

### "Connection refused" 에러
- `.env` 파일의 SUPABASE_URL 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

### "Invalid API key" 에러
- `.env` 파일의 SUPABASE_KEY 확인
- anon key (service_role key 아님)인지 확인

### Import 에러
```bash
uv sync  # 의존성 재설치
```

---

**준비 완료! 🎉**
