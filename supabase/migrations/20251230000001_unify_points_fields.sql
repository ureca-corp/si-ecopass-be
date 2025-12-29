-- ============================================================================
-- Migration: Unify estimated_points and earned_points into single points field
-- Date: 2025-12-30
-- Description:
--   관리자가 포인트 값을 조정하지 않으므로 두 필드를 points 하나로 통합
--   - estimated_points, earned_points → points
--   - 기존 데이터는 earned_points 우선, 없으면 estimated_points 사용
-- ============================================================================

-- 1. 새 points 컬럼 추가 (NOT NULL이지만 기본값 0으로 설정)
ALTER TABLE public.trips
ADD COLUMN points integer DEFAULT 0;

-- 2. 기존 데이터 마이그레이션
--    earned_points가 있으면 사용, 없으면 estimated_points 사용
UPDATE public.trips
SET points = COALESCE(earned_points, estimated_points, 0);

-- 3. 기존 estimated_points, earned_points 컬럼 제거
ALTER TABLE public.trips
DROP COLUMN estimated_points,
DROP COLUMN earned_points;

-- 4. points 컬럼에 NOT NULL 제약조건 추가 (기본값 제거)
ALTER TABLE public.trips
ALTER COLUMN points SET NOT NULL,
ALTER COLUMN points DROP DEFAULT;

-- 5. CHECK 제약조건 수정
ALTER TABLE public.trips
DROP CONSTRAINT IF EXISTS trips_points_non_negative;

ALTER TABLE public.trips
ADD CONSTRAINT trips_points_non_negative CHECK (points >= 0);

-- 6. 컬럼 설명 업데이트
COMMENT ON COLUMN public.trips.points IS '포인트 (도착 시 계산, 승인 시 지급)';
