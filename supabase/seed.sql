-- SI EcoPass - Sample Data (Seed)
-- 대구 지하철 역 및 주차장 샘플 데이터
-- Created: 2025-12-26

-- ============================================================================
-- 1. 대구 지하철 역 데이터
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1.1 1호선 주요 역 (빨간색)
-- ----------------------------------------------------------------------------

INSERT INTO public.stations (name, line_number, location) VALUES
  ('중앙로역', 1, ST_GeogFromText('POINT(128.5989 35.8694)')),
  ('반월당역', 1, ST_GeogFromText('POINT(128.5924 35.8581)')),
  ('대구역', 1, ST_GeogFromText('POINT(128.6283 35.8797)')),
  ('설화명곡역', 1, ST_GeogFromText('POINT(128.4542 35.8776)')),
  ('안심역', 1, ST_GeogFromText('POINT(128.7287 35.8864)'))
ON CONFLICT (name, line_number) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1.2 2호선 주요 역 (초록색)
-- ----------------------------------------------------------------------------

INSERT INTO public.stations (name, line_number, location) VALUES
  ('반월당역', 2, ST_GeogFromText('POINT(128.5924 35.8581)')),
  ('경대병원역', 2, ST_GeogFromText('POINT(128.6192 35.8717)')),
  ('대공원역', 2, ST_GeogFromText('POINT(128.6339 35.8392)')),
  ('문양역', 2, ST_GeogFromText('POINT(128.5389 35.9151)')),
  ('영남대역', 2, ST_GeogFromText('POINT(128.7537 35.8388)'))
ON CONFLICT (name, line_number) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1.3 3호선 주요 역 (주황색, 모노레일)
-- ----------------------------------------------------------------------------

INSERT INTO public.stations (name, line_number, location) VALUES
  ('칠곡경대병원역', 3, ST_GeogFromText('POINT(128.5622 35.9488)')),
  ('만촌역', 3, ST_GeogFromText('POINT(128.6153 35.8636)')),
  ('수성못역', 3, ST_GeogFromText('POINT(128.6411 35.8255)')),
  ('용지역', 3, ST_GeogFromText('POINT(128.6899 35.7932)'))
ON CONFLICT (name, line_number) DO NOTHING;

-- ============================================================================
-- 2. 환승 주차장 데이터
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 2.1 중앙로역 (1호선) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '중앙로역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '동성로 공영주차장',
  '대구광역시 중구 동성로2가 88',
  ST_GeogFromText('POINT(128.6000 35.8700)'),
  500,
  '10분당 500원, 1일 최대 10,000원'
FROM station
ON CONFLICT DO NOTHING;

WITH station AS (
  SELECT id FROM public.stations WHERE name = '중앙로역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '대구백화점 주차장',
  '대구광역시 중구 동성로 15',
  ST_GeogFromText('POINT(128.5980 35.8690)'),
  300,
  '30분당 2,000원, 구매 시 할인'
FROM station
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2.2 반월당역 (1/2호선 환승역) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '반월당역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '반월당 공영주차장',
  '대구광역시 중구 남산동 1050',
  ST_GeogFromText('POINT(128.5930 35.8575)'),
  400,
  '10분당 600원, 환승 주차 할인'
FROM station
ON CONFLICT DO NOTHING;

WITH station AS (
  SELECT id FROM public.stations WHERE name = '반월당역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '롯데백화점 대구점',
  '대구광역시 중구 남산동 1050',
  ST_GeogFromText('POINT(128.5915 35.8585)'),
  200,
  '30분당 2,500원, 구매 시 할인'
FROM station
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2.3 대구역 (1호선) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '대구역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '대구역 환승주차장',
  '대구광역시 동구 동대구로 550',
  ST_GeogFromText('POINT(128.6280 35.8795)'),
  100,
  '1일 3,000원 (환승 주차 전용)'
FROM station
ON CONFLICT DO NOTHING;

WITH station AS (
  SELECT id FROM public.stations WHERE name = '대구역' AND line_number = 1 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  'KTX 대구역 주차장',
  '대구광역시 동구 동대구로 550',
  ST_GeogFromText('POINT(128.6290 35.8800)'),
  200,
  '30분당 1,000원, 1일 최대 15,000원'
FROM station
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2.4 수성못역 (3호선) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '수성못역' AND line_number = 3 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '수성못 공영주차장',
  '대구광역시 수성구 두산동 산 180-1',
  ST_GeogFromText('POINT(128.6420 35.8245)'),
  600,
  '1일 2,000원 (주말 및 공휴일)'
FROM station
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2.5 경대병원역 (2호선) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '경대병원역' AND line_number = 2 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '경북대학교병원 주차장',
  '대구광역시 중구 동덕로 130',
  ST_GeogFromText('POINT(128.6195 35.8720)'),
  250,
  '30분당 1,500원, 진료 시 할인'
FROM station
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2.6 대공원역 (2호선) 주차장
-- ----------------------------------------------------------------------------

WITH station AS (
  SELECT id FROM public.stations WHERE name = '대공원역' AND line_number = 2 LIMIT 1
)
INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT
  station.id,
  '대공원 환승주차장',
  '대구광역시 수성구 대공원로 200',
  ST_GeogFromText('POINT(128.6345 35.8385)'),
  450,
  '1일 2,000원, 환승 주차 우대'
FROM station
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 3. 데이터 검증 쿼리
-- ============================================================================

-- 역 데이터 확인
DO $$
DECLARE
  station_count integer;
  parking_count integer;
BEGIN
  SELECT COUNT(*) INTO station_count FROM public.stations;
  SELECT COUNT(*) INTO parking_count FROM public.parking_lots;
  
  RAISE NOTICE '✅ Seed 데이터 삽입 완료!';
  RAISE NOTICE '🚇 역 개수: %', station_count;
  RAISE NOTICE '🅿️  주차장 개수: %', parking_count;
  
  -- 노선별 역 개수
  RAISE NOTICE '1호선: % 개 역', (SELECT COUNT(*) FROM public.stations WHERE line_number = 1);
  RAISE NOTICE '2호선: % 개 역', (SELECT COUNT(*) FROM public.stations WHERE line_number = 2);
  RAISE NOTICE '3호선: % 개 역', (SELECT COUNT(*) FROM public.stations WHERE line_number = 3);
END $$;

