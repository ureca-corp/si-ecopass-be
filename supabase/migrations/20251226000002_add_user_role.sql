-- Add role column to users table
-- 사용자 역할(role) 컬럼 추가: 'user' 또는 'admin'

-- role 컬럼 추가
ALTER TABLE public.users
ADD COLUMN role text NOT NULL DEFAULT 'user'
CHECK (role IN ('user', 'admin'));

COMMENT ON COLUMN public.users.role IS '사용자 역할 (user, admin)';

-- role 인덱스 추가 (관리자 검색 최적화)
CREATE INDEX IF NOT EXISTS users_role_idx ON public.users (role);

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ users 테이블에 role 컬럼 추가 완료';
  RAISE NOTICE '🔑 기본값: user, 허용값: user, admin';
END $$;
