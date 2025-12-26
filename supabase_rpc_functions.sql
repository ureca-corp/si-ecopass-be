-- Supabase RPC Functions for PostGIS Coordinate Extraction
--
-- 이 SQL 스크립트를 Supabase SQL Editor에서 실행하여
-- PostGIS geography(Point) 타입의 좌표를 추출하는 RPC 함수 생성
--
-- Usage: Supabase Dashboard > SQL Editor > 이 스크립트 붙여넣기 > Run

-- =============================================================================
-- 1. 모든 역 조회 (좌표 포함, 선택적 노선 필터링)
-- =============================================================================
CREATE OR REPLACE FUNCTION get_stations_with_coords(p_line_number INT DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    name TEXT,
    line_number INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
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
    WHERE
        CASE
            WHEN p_line_number IS NOT NULL THEN s.line_number = p_line_number
            ELSE TRUE
        END
    ORDER BY s.name;
END;
$$;

-- =============================================================================
-- 2. 특정 역 조회 (ID로, 좌표 포함)
-- =============================================================================
CREATE OR REPLACE FUNCTION get_station_by_id_with_coords(p_station_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    line_number INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
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
    WHERE s.id = p_station_id;
END;
$$;

-- =============================================================================
-- 3. 특정 역의 주차장 목록 조회 (좌표 포함)
-- =============================================================================
CREATE OR REPLACE FUNCTION get_parking_lots_with_coords(p_station_id UUID)
RETURNS TABLE (
    id UUID,
    station_id UUID,
    name TEXT,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    distance_to_station_m INT,
    fee_info TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.station_id,
        p.name,
        p.address,
        ST_Y(p.location::geometry) AS latitude,
        ST_X(p.location::geometry) AS longitude,
        p.distance_to_station_m,
        p.fee_info,
        p.created_at,
        p.updated_at
    FROM parking_lots p
    WHERE p.station_id = p_station_id
    ORDER BY p.distance_to_station_m NULLS LAST;
END;
$$;

-- =============================================================================
-- 테스트 쿼리 (선택 사항)
-- =============================================================================
-- 모든 역 조회
-- SELECT * FROM get_stations_with_coords(NULL);

-- 1호선 역만 조회
-- SELECT * FROM get_stations_with_coords(1);

-- 특정 역 조회 (ID는 실제 데이터로 교체)
-- SELECT * FROM get_station_by_id_with_coords('your-station-uuid-here');

-- 특정 역의 주차장 조회
-- SELECT * FROM get_parking_lots_with_coords('your-station-uuid-here');
