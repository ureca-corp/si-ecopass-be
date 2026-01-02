-- Disable All RLS Policies
-- JWT 인증으로 충분하므로 모든 RLS를 비활성화하여 복잡도 제거
-- FastAPI의 get_current_user + Service Layer에서 모든 권한 검증 수행

-- =============================================================================
-- 1. PUBLIC 테이블 RLS 비활성화
-- =============================================================================

-- trips 테이블 RLS 제거
DROP POLICY IF EXISTS "Users can create own trips" ON public.trips;
DROP POLICY IF EXISTS "Users can view own trips" ON public.trips;
DROP POLICY IF EXISTS "Users can update own trips" ON public.trips;
DROP POLICY IF EXISTS "Admins can view all trips" ON public.trips;
DROP POLICY IF EXISTS "Admins can update all trips" ON public.trips;
ALTER TABLE public.trips DISABLE ROW LEVEL SECURITY;

-- users 테이블 RLS 제거
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Admins can update all users" ON public.users;
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;

-- stations 테이블 RLS 제거
DROP POLICY IF EXISTS "Stations are viewable by everyone" ON public.stations;
DROP POLICY IF EXISTS "Admins can insert stations" ON public.stations;
DROP POLICY IF EXISTS "Admins can update stations" ON public.stations;
DROP POLICY IF EXISTS "Admins can delete stations" ON public.stations;
ALTER TABLE public.stations DISABLE ROW LEVEL SECURITY;

-- parking_lots 테이블 RLS 제거
DROP POLICY IF EXISTS "Parking lots are viewable by everyone" ON public.parking_lots;
DROP POLICY IF EXISTS "Admins can insert parking_lots" ON public.parking_lots;
DROP POLICY IF EXISTS "Admins can update parking_lots" ON public.parking_lots;
DROP POLICY IF EXISTS "Admins can delete parking_lots" ON public.parking_lots;
ALTER TABLE public.parking_lots DISABLE ROW LEVEL SECURITY;

-- =============================================================================
-- 2. STORAGE RLS 최소화 (Supabase 내부 기능 유지를 위해 완전 제거는 불가)
-- =============================================================================

-- 기존 복잡한 정책 제거
DROP POLICY IF EXISTS "Authenticated users can upload trips images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete trips images" ON storage.objects;
DROP POLICY IF EXISTS "Users can view trips images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to read buckets" ON storage.buckets;
DROP POLICY IF EXISTS "Allow public to read buckets" ON storage.buckets;

-- 간소화된 정책: 모든 사용자에게 trips 버킷 전체 접근 허용
-- (FastAPI StorageService에서 trip 소유권 검증함)
CREATE POLICY "Allow all operations on trips bucket"
ON storage.objects
FOR ALL
TO public, authenticated, anon
USING (bucket_id = 'trips')
WITH CHECK (bucket_id = 'trips');

-- 버킷 메타데이터 조회 허용 (signed URL 작동을 위해 필수)
CREATE POLICY "Allow all to read buckets"
ON storage.buckets
FOR SELECT
TO public, authenticated, anon
USING (true);

-- =============================================================================
-- 주석: 보안 계층 단순화 이유
-- =============================================================================
-- 1. FastAPI auth_deps.py의 get_current_user()에서 JWT 검증 수행
-- 2. StorageService, TripService 등에서 소유권 검증 수행
-- 3. RLS는 오히려 디버깅을 어렵게 만들고 400 오류 원인 파악 지연
-- 4. 단일 클라이언트(FastAPI)만 DB 접근 → 다층 보안 불필요
-- 5. DB 직접 접근은 개발자만 → RLS 없어도 문제 없음
