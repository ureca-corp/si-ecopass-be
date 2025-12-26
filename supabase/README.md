# Supabase Migrations

SI EcoPass 프로젝트의 Supabase 데이터베이스 마이그레이션 파일들입니다.

## 📁 파일 구조

```
supabase/
├── migrations/
│   └── 20251226000001_initial_schema.sql  # 초기 스키마 (테이블, 인덱스, RLS)
├── seed.sql                                # 샘플 데이터 (대구 지하철 역, 주차장)
├── config.toml                             # Supabase CLI 설정
└── README.md                               # 이 문서
```

## 🚀 마이그레이션 적용 방법

### 방법 1: Supabase CLI (권장)

```bash
# 1. Supabase CLI 설치 (아직 안 했다면)
bun add -g supabase

# 2. Supabase 프로젝트 연결
supabase link --project-ref YOUR_PROJECT_REF

# 3. 마이그레이션 적용
supabase db push

# 4. 샘플 데이터 삽입
supabase db reset --db-url YOUR_DATABASE_URL
# 또는
psql YOUR_DATABASE_URL < supabase/seed.sql
```

### 방법 2: Supabase Dashboard (수동)

1. **Supabase Dashboard 접속**
   - https://app.supabase.com/project/YOUR_PROJECT_ID

2. **SQL Editor 열기**
   - 왼쪽 메뉴에서 "SQL Editor" 클릭

3. **마이그레이션 파일 실행**
   ```sql
   -- migrations/20251226000001_initial_schema.sql 내용 복사 → 붙여넣기 → Run
   ```

4. **샘플 데이터 삽입**
   ```sql
   -- seed.sql 내용 복사 → 붙여넣기 → Run
   ```

5. **결과 확인**
   - "Table Editor"에서 테이블 생성 확인
   - `stations`, `parking_lots` 테이블에 데이터 확인

## 📦 생성되는 스키마

### 테이블

| 테이블명      | 설명                        | 주요 컬럼                                   |
| ------------- | --------------------------- | ------------------------------------------- |
| `users`       | 사용자 프로필 (Auth 확장)   | id, username, vehicle_number, total_points  |
| `stations`    | 대구 지하철 역 정보         | id, name, line_number, location (geography) |
| `parking_lots`| 환승 주차장 정보            | id, station_id, name, address, location     |
| `trips`       | 여정 기록 (출발→환승→도착) | id, user_id, status, locations, images      |

### 확장 기능

- **PostGIS**: GPS 좌표 관리 (`geography(Point)` 타입)
- **pgcrypto**: UUID v7 생성 함수

### RLS (Row Level Security)

- ✅ **users**: 본인 데이터만 조회/수정
- ✅ **stations**: 공개 (모든 사용자 조회 가능)
- ✅ **parking_lots**: 공개 (모든 사용자 조회 가능)
- ✅ **trips**: 본인 여정만 조회/생성/수정

### 트리거

- `updated_at` 자동 업데이트 (users, trips)
- 회원가입 시 `users` 테이블 자동 생성

## 🧪 데이터 확인

### 역 데이터 확인

```sql
-- 노선별 역 개수
SELECT line_number, COUNT(*) as count
FROM stations
GROUP BY line_number
ORDER BY line_number;

-- 전체 역 목록
SELECT name, line_number, 
       ST_Y(location::geometry) as latitude,
       ST_X(location::geometry) as longitude
FROM stations
ORDER BY line_number, name;
```

### 주차장 데이터 확인

```sql
-- 역별 주차장 개수
SELECT s.name, s.line_number, COUNT(p.id) as parking_count
FROM stations s
LEFT JOIN parking_lots p ON p.station_id = s.id
GROUP BY s.id, s.name, s.line_number
ORDER BY parking_count DESC;

-- 특정 역의 주차장 목록
SELECT p.name, p.address, p.distance_to_station_m, p.fee_info
FROM parking_lots p
JOIN stations s ON p.station_id = s.id
WHERE s.name = '중앙로역' AND s.line_number = 1;
```

### 거리 계산 테스트

```sql
-- 두 역 간 거리 계산 (미터)
SELECT 
  calculate_distance_meters(
    (SELECT location FROM stations WHERE name = '중앙로역' AND line_number = 1),
    (SELECT location FROM stations WHERE name = '대구역' AND line_number = 1)
  ) as distance_meters;

-- 반경 500m 내 주차장 검색
SELECT p.name, p.address
FROM parking_lots p
WHERE is_within_radius(
  p.location,
  ST_GeogFromText('POINT(128.5989 35.8694)'),  -- 중앙로역 좌표
  500
);
```

## 🔧 유틸리티 함수

### UUID v7 생성

```sql
SELECT uuid_generate_v7();
-- 예: 018d8e3a-1234-7abc-8def-0123456789ab
-- 시간 순서대로 정렬 가능
```

### 거리 계산

```sql
-- 두 GPS 좌표 간 거리 (미터)
SELECT calculate_distance_meters(
  ST_GeogFromText('POINT(128.5989 35.8694)'),  -- 중앙로역
  ST_GeogFromText('POINT(128.6283 35.8797)')   -- 대구역
) as distance_meters;
```

### 반경 검색

```sql
-- 특정 좌표 반경 1km 내 역 검색
SELECT name, line_number
FROM stations
WHERE is_within_radius(
  location,
  ST_GeogFromText('POINT(128.5989 35.8694)'),
  1000  -- 1km
);
```

## 📝 샘플 데이터 현황

### 역 (Stations)

- **1호선**: 5개 역 (중앙로역, 반월당역, 대구역, 설화명곡역, 안심역)
- **2호선**: 5개 역 (반월당역, 경대병원역, 대공원역, 문양역, 영남대역)
- **3호선**: 4개 역 (칠곡경대병원역, 만촌역, 수성못역, 용지역)

### 주차장 (Parking Lots)

- 중앙로역: 2개 (동성로 공영주차장, 대구백화점)
- 반월당역: 2개 (반월당 공영주차장, 롯데백화점)
- 대구역: 2개 (환승주차장, KTX 주차장)
- 수성못역: 1개 (수성못 공영주차장)
- 경대병원역: 1개 (경북대학교병원)
- 대공원역: 1개 (대공원 환승주차장)

**Total**: 14개 역, 9개 주차장

> **참고**: 대구 지하철 전체 역 데이터는 추후 추가 예정입니다.

## 🔄 마이그레이션 롤백

```bash
# Supabase CLI로 롤백 (신중하게!)
supabase db reset

# 또는 수동으로 테이블 삭제
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS parking_lots CASCADE;
DROP TABLE IF EXISTS stations CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS uuid_generate_v7();
DROP FUNCTION IF EXISTS calculate_distance_meters(geography, geography);
DROP FUNCTION IF EXISTS is_within_radius(geography, geography, numeric);
```

## 🚨 주의사항

1. **RLS 정책**: 프로덕션 환경에서는 RLS가 활성화되어 있으므로 JWT 토큰 필요
2. **Storage 버킷**: 마이그레이션에서는 생성되지 않으므로 Dashboard에서 수동 생성 필요
   - 버킷명: `trips`
   - 경로 구조: `{trip_id}/transfer.jpg`, `{trip_id}/arrival.jpg`
3. **관리자 권한**: Admin API 사용을 위해 `user_metadata`에 `role: admin` 추가 필요

## 📚 참고 문서

- [Supabase CLI 문서](https://supabase.com/docs/guides/cli)
- [PostGIS 문서](https://postgis.net/documentation/)
- [BACKEND_SPEC.md](../BACKEND_SPEC.md) - 전체 시스템 명세
- [API_PRD.md](../API_PRD.md) - API 개발 계획

---

**최종 업데이트**: 2025-12-26  
**Supabase 버전**: PostgreSQL 15.x + PostGIS 3.x

