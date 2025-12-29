-- stations 테이블에 updated_at 컬럼 추가
ALTER TABLE stations
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- parking_lots 테이블에 updated_at 컬럼 추가
ALTER TABLE parking_lots
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- 기존 레코드에 updated_at 값 설정 (created_at 값으로)
UPDATE stations SET updated_at = created_at WHERE updated_at IS NULL;
UPDATE parking_lots SET updated_at = created_at WHERE updated_at IS NULL;

COMMENT ON COLUMN stations.updated_at IS '최종 수정 시각';
COMMENT ON COLUMN parking_lots.updated_at IS '최종 수정 시각';
