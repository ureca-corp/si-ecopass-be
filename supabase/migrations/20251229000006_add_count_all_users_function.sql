-- count_all_users: RLS를 우회하여 전체 사용자 수 조회
CREATE OR REPLACE FUNCTION public.count_all_users()
RETURNS integer
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN (SELECT COUNT(*)::integer FROM public.users);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.count_all_users IS '전체 사용자 수 조회 (관리자 대시보드용)';
