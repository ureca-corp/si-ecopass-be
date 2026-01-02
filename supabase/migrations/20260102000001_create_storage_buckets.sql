-- 스토리지 버킷 생성 마이그레이션
-- 여정 인증 이미지 저장을 위한 'trips' 버킷 생성

-- trips 버킷 생성 (공개 접근 허용)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'trips',
    'trips',
    true,  -- 공개 버킷 (Public URL 사용)
    5242880,  -- 5MB 제한
    ARRAY['image/jpeg', 'image/png']::text[]
)
ON CONFLICT (id) DO NOTHING;

-- trips 버킷에 대한 스토리지 정책 (모든 사용자 업로드/조회 가능)
CREATE POLICY "Allow authenticated users to upload trip images"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'trips');

CREATE POLICY "Allow public read access to trip images"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'trips');

CREATE POLICY "Allow users to update their own trip images"
ON storage.objects
FOR UPDATE
TO authenticated
USING (bucket_id = 'trips');

CREATE POLICY "Allow users to delete their own trip images"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'trips');
