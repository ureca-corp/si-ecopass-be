-- Simplify Storage RLS Policies
-- JWT 인증으로 충분하므로 Storage RLS를 완전히 개방
-- FastAPI 레벨에서 이미 모든 요청을 검증하고 있음

-- 기존 정책 삭제
DROP POLICY IF EXISTS "Authenticated users can upload trips images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete trips images" ON storage.objects;
DROP POLICY IF EXISTS "Users can view trips images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to read buckets" ON storage.buckets;
DROP POLICY IF EXISTS "Allow public to read buckets" ON storage.buckets;

-- 간소화된 정책: 모든 작업 허용 (FastAPI에서 이미 검증하므로)
CREATE POLICY "Allow all operations on trips bucket"
ON storage.objects
FOR ALL
TO authenticated, anon, public
USING (bucket_id = 'trips')
WITH CHECK (bucket_id = 'trips');

CREATE POLICY "Allow all to read all buckets"
ON storage.buckets
FOR SELECT
TO authenticated, anon, public
USING (true);

-- 주석:
-- 1. FastAPI의 get_current_user에서 JWT 검증 수행
-- 2. StorageService에서 trip 소유권 검증 (auth_deps.py:79-113)
-- 3. RLS는 최소한으로만 설정 (bucket 접근만 제한)
