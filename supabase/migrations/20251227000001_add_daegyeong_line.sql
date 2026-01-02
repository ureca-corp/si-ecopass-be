-- Add Daegyeong Line (대경선) support to stations table
-- Migration: 20251229000001_add_daegyeong_line.sql
-- 대경선을 line_number = 4로 추가

-- ============================================================================
-- 1. 기존 CHECK 제약조건 삭제
-- ============================================================================

-- stations 테이블의 line_number 제약조건 수정
-- 기존: CHECK (line_number IN (1, 2, 3))
-- 변경: CHECK (line_number IN (1, 2, 3, 4))

ALTER TABLE public.stations
DROP CONSTRAINT IF EXISTS stations_line_number_check;

-- ============================================================================
-- 2. 새로운 CHECK 제약조건 추가 (대경선 포함)
-- ============================================================================

ALTER TABLE public.stations
ADD CONSTRAINT stations_line_number_check
CHECK (line_number IN (1, 2, 3, 4));

-- 코멘트 업데이트
COMMENT ON COLUMN public.stations.line_number IS '노선 번호 (1=1호선, 2=2호선, 3=3호선, 4=대경선)';

-- ============================================================================
-- 3. 완료 메시지
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ 대경선(line_number=4) 지원 추가 완료!';
  RAISE NOTICE '📋 stations.line_number: 1=1호선, 2=2호선, 3=3호선, 4=대경선';
END $$;
