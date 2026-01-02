-- 로컬 Supabase 테스트 데이터 정리 스크립트
-- 지하철역(stations)과 주차장(parking_lots)은 유지하고 나머지 삭제

-- 1. trips 테이블 전체 삭제 (CASCADE로 관련 데이터도 삭제)
TRUNCATE TABLE trips CASCADE;

-- 2. users 테이블 전체 삭제 (CASCADE로 관련 데이터도 삭제)
TRUNCATE TABLE users CASCADE;

-- 3. Supabase Auth 사용자 삭제 (auth.users)
-- 주의: 이 작업은 Supabase Admin API를 통해 수행해야 함
-- 또는 Supabase Studio에서 수동으로 삭제

-- 결과 확인
SELECT 'trips' as table_name, COUNT(*) as row_count FROM trips
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'stations', COUNT(*) FROM stations
UNION ALL
SELECT 'parking_lots', COUNT(*) FROM parking_lots;
