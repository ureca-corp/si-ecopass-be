-- Migration: Add latitude/longitude columns with auto-sync trigger
-- 목적: RPC 함수 없이 표준 SQL로 좌표 데이터 관리
--
-- 전략:
-- 1. latitude/longitude 컬럼 추가 (애플리케이션이 직접 CRUD)
-- 2. PostgreSQL 트리거로 lat/lng → location 자동 동기화
-- 3. 기존 location 데이터에서 lat/lng 역산하여 백필

-- ============================================================================
-- STEP 1: Add latitude/longitude columns to stations
-- ============================================================================
ALTER TABLE public.stations
ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;

-- ============================================================================
-- STEP 2: Add latitude/longitude columns to parking_lots
-- ============================================================================
ALTER TABLE public.parking_lots
ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;

-- ============================================================================
-- STEP 3: Backfill lat/lng from existing location data
-- ============================================================================
UPDATE public.stations
SET
    latitude = ST_Y(location::geometry),
    longitude = ST_X(location::geometry)
WHERE location IS NOT NULL AND latitude IS NULL;

UPDATE public.parking_lots
SET
    latitude = ST_Y(location::geometry),
    longitude = ST_X(location::geometry)
WHERE location IS NOT NULL AND latitude IS NULL;

-- ============================================================================
-- STEP 4: Create trigger function to sync lat/lng → location
-- ============================================================================
CREATE OR REPLACE FUNCTION sync_location_from_lat_lng()
RETURNS TRIGGER AS $$
BEGIN
    -- latitude와 longitude가 모두 있으면 location 자동 생성
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 5: Attach triggers to tables
-- ============================================================================
-- Stations 테이블 트리거
DROP TRIGGER IF EXISTS trg_stations_sync_location ON public.stations;
CREATE TRIGGER trg_stations_sync_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON public.stations
    FOR EACH ROW
    EXECUTE FUNCTION sync_location_from_lat_lng();

-- Parking Lots 테이블 트리거
DROP TRIGGER IF EXISTS trg_parking_lots_sync_location ON public.parking_lots;
CREATE TRIGGER trg_parking_lots_sync_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON public.parking_lots
    FOR EACH ROW
    EXECUTE FUNCTION sync_location_from_lat_lng();

-- ============================================================================
-- STEP 6: Add comments for documentation
-- ============================================================================
COMMENT ON COLUMN public.stations.latitude IS '역 위도 (WGS84)';
COMMENT ON COLUMN public.stations.longitude IS '역 경도 (WGS84)';
COMMENT ON COLUMN public.parking_lots.latitude IS '주차장 위도 (WGS84)';
COMMENT ON COLUMN public.parking_lots.longitude IS '주차장 경도 (WGS84)';
COMMENT ON FUNCTION sync_location_from_lat_lng() IS 'lat/lng 변경 시 PostGIS location 컬럼 자동 동기화';
