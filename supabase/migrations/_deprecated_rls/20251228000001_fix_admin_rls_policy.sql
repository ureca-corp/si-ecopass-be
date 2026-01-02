-- Fix admin RLS policy to avoid infinite recursion
-- JWT user_metadata에서 직접 role을 확인하여 무한 재귀 방지

-- 기존 정책 삭제
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Admins can update all users" ON public.users;

-- 개선된 SELECT 정책: JWT user_metadata 직접 확인
CREATE POLICY "Admins can view all users"
ON public.users
FOR SELECT
TO public
USING (
  -- 자기 자신이거나, JWT의 user_metadata.role이 'admin'인 경우
  auth.uid() = id
  OR
  (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin'
);

-- 개선된 UPDATE 정책: JWT user_metadata 직접 확인
CREATE POLICY "Admins can update all users"
ON public.users
FOR UPDATE
TO public
USING (
  -- 자기 자신이거나, JWT의 user_metadata.role이 'admin'인 경우
  auth.uid() = id
  OR
  (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin'
)
WITH CHECK (
  -- 자기 자신이거나, JWT의 user_metadata.role이 'admin'인 경우
  auth.uid() = id
  OR
  (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin'
);

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ 관리자용 RLS 정책 수정 완료 (무한 재귀 해결)';
  RAISE NOTICE '🔑 JWT user_metadata에서 직접 role 확인';
END $$;
