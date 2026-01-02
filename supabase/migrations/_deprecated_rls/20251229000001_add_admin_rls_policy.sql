-- Add admin RLS policy for users table
-- 관리자가 모든 사용자 정보를 조회/수정할 수 있도록 RLS 정책 추가

-- 관리자용 SELECT 정책 추가
CREATE POLICY "Admins can view all users"
ON public.users
FOR SELECT
TO public
USING (
  -- 자기 자신이거나, 관리자인 경우
  auth.uid() = id
  OR
  EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid() AND role = 'admin'
  )
);

-- 관리자용 UPDATE 정책 추가
CREATE POLICY "Admins can update all users"
ON public.users
FOR UPDATE
TO public
USING (
  -- 자기 자신이거나, 관리자인 경우
  auth.uid() = id
  OR
  EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid() AND role = 'admin'
  )
)
WITH CHECK (
  -- 자기 자신이거나, 관리자인 경우
  auth.uid() = id
  OR
  EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid() AND role = 'admin'
  )
);

-- 기존 정책 삭제 (새 정책으로 대체)
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ 관리자용 RLS 정책 추가 완료';
  RAISE NOTICE '🔑 관리자는 모든 사용자 정보 조회/수정 가능';
END $$;
