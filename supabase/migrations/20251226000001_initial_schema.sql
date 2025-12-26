-- SI EcoPass - Initial Schema Migration
-- 대구 지하철 환승 주차장 여정 기록 시스템
-- Created: 2025-12-26

-- ============================================================================
-- 1. 확장 기능 활성화
-- ============================================================================

-- PostGIS 확장 (geography 타입 사용)
CREATE EXTENSION IF NOT EXISTS postgis;

-- UUID v7 지원 (시간 기반 정렬 가능한 UUID)
-- PostgreSQL 13+ 에서는 pgcrypto 기반으로 UUID v7 구현
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================================
-- 2. UUID v7 생성 함수
-- ============================================================================

-- UUID v7: 시간 기반 정렬 가능, B-tree 인덱스 성능 향상
CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS uuid
AS $$
DECLARE
  unix_ts_ms bytea;
  uuid_bytes bytea;
BEGIN
  unix_ts_ms = substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3);
  
  -- 48 bits timestamp (milliseconds) + 4 bits version + 12 bits random + 2 bits variant + 62 bits random
  uuid_bytes = unix_ts_ms || gen_random_bytes(10);
  
  -- Set version to 7
  uuid_bytes = set_byte(uuid_bytes, 6, (get_byte(uuid_bytes, 6) & 15) | 112);
  
  -- Set variant to RFC4122
  uuid_bytes = set_byte(uuid_bytes, 8, (get_byte(uuid_bytes, 8) & 63) | 128);
  
  RETURN encode(uuid_bytes, 'hex')::uuid;
END
$$
LANGUAGE plpgsql
VOLATILE;

-- ============================================================================
-- 3. 테이블 생성
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 3.1 users 테이블 (Supabase Auth 확장)
-- ----------------------------------------------------------------------------
-- auth.users 테이블의 사용자 프로필 확장
-- email과 created_at은 auth.users에서 관리됨

CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL UNIQUE,
  vehicle_number text,
  total_points integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  
  CONSTRAINT users_total_points_non_negative CHECK (total_points >= 0)
);

COMMENT ON TABLE public.users IS '사용자 프로필 (auth.users 확장)';
COMMENT ON COLUMN public.users.id IS 'Supabase Auth 사용자 ID (FK → auth.users)';
COMMENT ON COLUMN public.users.username IS '사용자명 (고유)';
COMMENT ON COLUMN public.users.vehicle_number IS '차량 번호 (선택)';
COMMENT ON COLUMN public.users.total_points IS '누적 포인트';

-- ----------------------------------------------------------------------------
-- 3.2 stations 테이블 (대구 지하철 역 정보)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.stations (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v7(),
  name text NOT NULL,
  line_number integer NOT NULL CHECK (line_number IN (1, 2, 3)),
  location geography(Point, 4326) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  
  CONSTRAINT stations_unique_name_line UNIQUE (name, line_number)
);

COMMENT ON TABLE public.stations IS '대구 지하철 역 정보 (1, 2, 3호선)';
COMMENT ON COLUMN public.stations.name IS '역명';
COMMENT ON COLUMN public.stations.line_number IS '노선 번호 (1, 2, 3)';
COMMENT ON COLUMN public.stations.location IS 'GPS 좌표 (PostGIS geography)';

-- 공간 인덱스 (위치 기반 검색 최적화)
CREATE INDEX IF NOT EXISTS stations_location_idx 
  ON public.stations USING GIST (location);

-- 노선 검색 인덱스
CREATE INDEX IF NOT EXISTS stations_line_number_idx 
  ON public.stations (line_number);

-- ----------------------------------------------------------------------------
-- 3.3 parking_lots 테이블 (환승 주차장 정보)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.parking_lots (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v7(),
  station_id uuid NOT NULL REFERENCES public.stations(id) ON DELETE CASCADE,
  name text NOT NULL,
  address text NOT NULL,
  location geography(Point, 4326) NOT NULL,
  distance_to_station_m integer,
  fee_info text,
  created_at timestamptz NOT NULL DEFAULT now(),
  
  CONSTRAINT parking_lots_distance_non_negative 
    CHECK (distance_to_station_m IS NULL OR distance_to_station_m >= 0)
);

COMMENT ON TABLE public.parking_lots IS '환승 주차장 정보';
COMMENT ON COLUMN public.parking_lots.station_id IS '연계 역 ID (FK → stations)';
COMMENT ON COLUMN public.parking_lots.name IS '주차장 명칭';
COMMENT ON COLUMN public.parking_lots.address IS '주소';
COMMENT ON COLUMN public.parking_lots.location IS 'GPS 좌표 (PostGIS geography)';
COMMENT ON COLUMN public.parking_lots.distance_to_station_m IS '역까지 거리 (미터)';
COMMENT ON COLUMN public.parking_lots.fee_info IS '요금 정보';

-- 공간 인덱스
CREATE INDEX IF NOT EXISTS parking_lots_location_idx 
  ON public.parking_lots USING GIST (location);

-- 역별 주차장 검색 인덱스
CREATE INDEX IF NOT EXISTS parking_lots_station_id_idx 
  ON public.parking_lots (station_id);

-- ----------------------------------------------------------------------------
-- 3.4 trips 테이블 (여정 기록)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.trips (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v7(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  
  -- 출발 단계 (Start)
  start_time timestamptz,
  start_location geography(Point, 4326),
  
  -- 환승 단계 (Transfer)
  transfer_time timestamptz,
  transfer_location geography(Point, 4326),
  transfer_image_url text,
  
  -- 도착 단계 (Arrival)
  arrival_time timestamptz,
  arrival_location geography(Point, 4326),
  arrival_image_url text,
  
  -- 여정 상태 및 포인트
  status text NOT NULL DEFAULT 'DRIVING' 
    CHECK (status IN ('DRIVING', 'TRANSFERRED', 'COMPLETED', 'APPROVED', 'REJECTED')),
  estimated_points integer NOT NULL DEFAULT 0,
  earned_points integer NOT NULL DEFAULT 0,
  
  -- 관리자 메모
  admin_note text,
  
  -- 타임스탬프
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  
  CONSTRAINT trips_points_non_negative 
    CHECK (estimated_points >= 0 AND earned_points >= 0)
);

COMMENT ON TABLE public.trips IS '사용자 여정 기록 (출발 → 환승 → 도착)';
COMMENT ON COLUMN public.trips.user_id IS '사용자 ID (FK → users)';
COMMENT ON COLUMN public.trips.status IS '여정 상태 (DRIVING, TRANSFERRED, COMPLETED, APPROVED, REJECTED)';
COMMENT ON COLUMN public.trips.estimated_points IS '예상 포인트 (거리 기반 계산)';
COMMENT ON COLUMN public.trips.earned_points IS '실제 지급 포인트 (관리자 승인 후)';
COMMENT ON COLUMN public.trips.admin_note IS '관리자 메모 (반려 사유 등)';

-- 사용자별 여정 검색 인덱스
CREATE INDEX IF NOT EXISTS trips_user_id_idx 
  ON public.trips (user_id);

-- 상태별 검색 인덱스 (관리자 승인 대기 목록 조회용)
CREATE INDEX IF NOT EXISTS trips_status_idx 
  ON public.trips (status);

-- 생성 시간 기반 정렬 인덱스
CREATE INDEX IF NOT EXISTS trips_created_at_idx 
  ON public.trips (created_at DESC);

-- 공간 인덱스 (GPS 좌표 검색용)
CREATE INDEX IF NOT EXISTS trips_start_location_idx 
  ON public.trips USING GIST (start_location);
CREATE INDEX IF NOT EXISTS trips_transfer_location_idx 
  ON public.trips USING GIST (transfer_location);
CREATE INDEX IF NOT EXISTS trips_arrival_location_idx 
  ON public.trips USING GIST (arrival_location);

-- ============================================================================
-- 4. 트리거 설정
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 4.1 updated_at 자동 업데이트 트리거
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- users 테이블
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- trips 테이블
CREATE TRIGGER update_trips_updated_at
  BEFORE UPDATE ON public.trips
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 4.2 회원가입 시 users 테이블 자동 생성 트리거
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, username, created_at)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', 'user_' || substr(NEW.id::text, 1, 8)),
    NEW.created_at
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

COMMENT ON FUNCTION handle_new_user() IS 'auth.users 회원가입 시 public.users 자동 생성';

-- ============================================================================
-- 5. Row Level Security (RLS) 정책
-- ============================================================================

-- RLS 활성화
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.stations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parking_lots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trips ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------------------------
-- 5.1 users 테이블 RLS
-- ----------------------------------------------------------------------------

-- 모든 사용자는 자신의 프로필만 조회 가능
CREATE POLICY "Users can view own profile"
  ON public.users
  FOR SELECT
  USING (auth.uid() = id);

-- 모든 사용자는 자신의 프로필만 수정 가능
CREATE POLICY "Users can update own profile"
  ON public.users
  FOR UPDATE
  USING (auth.uid() = id);

-- ----------------------------------------------------------------------------
-- 5.2 stations 테이블 RLS (공개 읽기)
-- ----------------------------------------------------------------------------

-- 모든 사용자는 역 정보 조회 가능 (인증 불필요)
CREATE POLICY "Stations are viewable by everyone"
  ON public.stations
  FOR SELECT
  USING (true);

-- ----------------------------------------------------------------------------
-- 5.3 parking_lots 테이블 RLS (공개 읽기)
-- ----------------------------------------------------------------------------

-- 모든 사용자는 주차장 정보 조회 가능 (인증 불필요)
CREATE POLICY "Parking lots are viewable by everyone"
  ON public.parking_lots
  FOR SELECT
  USING (true);

-- ----------------------------------------------------------------------------
-- 5.4 trips 테이블 RLS
-- ----------------------------------------------------------------------------

-- 사용자는 자신의 여정만 조회 가능
CREATE POLICY "Users can view own trips"
  ON public.trips
  FOR SELECT
  USING (auth.uid() = user_id);

-- 사용자는 자신의 여정만 생성 가능
CREATE POLICY "Users can create own trips"
  ON public.trips
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 사용자는 자신의 여정만 수정 가능
CREATE POLICY "Users can update own trips"
  ON public.trips
  FOR UPDATE
  USING (auth.uid() = user_id);

-- ============================================================================
-- 6. 유틸리티 함수
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 6.1 거리 계산 함수 (미터 단위)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_distance_meters(
  loc1 geography,
  loc2 geography
)
RETURNS numeric AS $$
BEGIN
  RETURN ST_Distance(loc1, loc2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_distance_meters IS '두 GPS 좌표 간 거리 계산 (미터)';

-- ----------------------------------------------------------------------------
-- 6.2 반경 내 위치 확인 함수
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION is_within_radius(
  loc1 geography,
  loc2 geography,
  radius_meters numeric
)
RETURNS boolean AS $$
BEGIN
  RETURN ST_DWithin(loc1, loc2, radius_meters);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION is_within_radius IS '두 GPS 좌표가 지정된 반경 내에 있는지 확인';

-- ============================================================================
-- 7. 완료 메시지
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ SI EcoPass 초기 스키마 생성 완료!';
  RAISE NOTICE '📦 테이블: users, stations, parking_lots, trips';
  RAISE NOTICE '🔧 확장: PostGIS, pgcrypto';
  RAISE NOTICE '🔒 RLS 정책 활성화 완료';
  RAISE NOTICE '⚡ UUID v7 함수 생성 완료';
END $$;

