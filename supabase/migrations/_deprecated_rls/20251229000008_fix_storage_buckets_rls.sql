-- Fix storage.buckets RLS policies
-- 400 오류 해결: signed URL이 작동하려면 storage.buckets에 대한 SELECT 권한 필요

-- storage.buckets에 대한 SELECT 정책 추가
CREATE POLICY "Allow authenticated users to read buckets"
ON storage.buckets
FOR SELECT
TO authenticated
USING (true);

-- 추가: public 사용자도 버킷 메타데이터를 읽을 수 있도록 허용 (signed URL을 위해)
CREATE POLICY "Allow public to read buckets"
ON storage.buckets
FOR SELECT
TO public
USING (true);
