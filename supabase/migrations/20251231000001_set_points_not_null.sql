-- Migration: Set trips.points to NOT NULL with default 0
-- Description: 포인트 필드를 NOT NULL로 변경하여 null 값 방지
-- Date: 2025-01-02

-- 1. 기존 NULL 값을 0으로 업데이트
UPDATE trips
SET points = 0
WHERE points IS NULL;

-- 2. NOT NULL 제약 조건 추가 및 DEFAULT 0 설정
ALTER TABLE trips
ALTER COLUMN points SET NOT NULL,
ALTER COLUMN points SET DEFAULT 0;

-- 3. 코멘트 업데이트
COMMENT ON COLUMN trips.points IS '포인트 (출발 시 0, 도착 시 계산, 승인 시 지급, NOT NULL)';
