-- get_user_with_email: auth.users의 email을 포함한 사용자 정보 조회 함수
CREATE OR REPLACE FUNCTION public.get_user_with_email(p_user_id uuid)
RETURNS TABLE (
    id uuid,
    username text,
    vehicle_number text,
    role text,
    total_points integer,
    created_at timestamptz,
    updated_at timestamptz,
    email text
)
SECURITY DEFINER
SET search_path = public, auth
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.vehicle_number,
        u.role,
        u.total_points,
        u.created_at,
        u.updated_at,
        au.email::text
    FROM public.users u
    LEFT JOIN auth.users au ON u.id = au.id
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.get_user_with_email IS 'auth.users의 email을 포함한 사용자 정보 조회';
