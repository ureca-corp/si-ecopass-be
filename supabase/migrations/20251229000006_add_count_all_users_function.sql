-- count_all_users: 관리자를 제외한 일반 사용자 수만 조회
CREATE OR REPLACE FUNCTION public.count_all_users()
RETURNS integer
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN (SELECT COUNT(*)::integer FROM public.users WHERE role != 'admin');
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.count_all_users IS '일반 사용자 수 조회 (관리자 제외, 대시보드용)';
