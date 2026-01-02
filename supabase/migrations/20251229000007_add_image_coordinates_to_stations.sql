-- Add image coordinates to stations table
-- 앱 내 노선도 이미지에서 역의 픽셀 좌표 저장
-- Created: 2025-12-29

-- ============================================================================
-- 1. 컬럼 추가
-- ============================================================================

-- 노선도 이미지 내 X 좌표 (픽셀)
ALTER TABLE public.stations
  ADD COLUMN IF NOT EXISTS image_x float;

-- 노선도 이미지 내 Y 좌표 (픽셀)
ALTER TABLE public.stations
  ADD COLUMN IF NOT EXISTS image_y float;

-- ============================================================================
-- 2. 컬럼 주석
-- ============================================================================

COMMENT ON COLUMN public.stations.image_x IS '노선도 이미지 내 X 픽셀 좌표 (앱 UI용)';
COMMENT ON COLUMN public.stations.image_y IS '노선도 이미지 내 Y 픽셀 좌표 (앱 UI용)';

-- ============================================================================
-- 3. 완료 메시지
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ stations 테이블에 image_x, image_y 컬럼 추가 완료';
  RAISE NOTICE '📱 앱 노선도 이미지와 실제 GPS 좌표 동기화 가능';
  RAISE NOTICE '⚙️ 어드민 웹에서 픽셀 좌표 입력 필요';
END $$;
