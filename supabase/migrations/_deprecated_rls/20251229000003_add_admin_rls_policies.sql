-- Migration: Add RLS policies for admin CRUD operations on stations and parking_lots
-- 목적: 관리자(role='admin')가 역/주차장 데이터를 관리할 수 있도록 RLS 정책 추가

-- ============================================================================
-- Helper function: Check if user is admin
-- ============================================================================
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.users
        WHERE id = auth.uid()
        AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.is_admin() IS '현재 인증된 사용자가 관리자인지 확인';

-- ============================================================================
-- Stations: Admin CRUD policies
-- ============================================================================

-- Admin can INSERT stations
CREATE POLICY "Admins can insert stations"
ON public.stations
FOR INSERT
TO authenticated
WITH CHECK (public.is_admin());

-- Admin can UPDATE stations
CREATE POLICY "Admins can update stations"
ON public.stations
FOR UPDATE
TO authenticated
USING (public.is_admin())
WITH CHECK (public.is_admin());

-- Admin can DELETE stations
CREATE POLICY "Admins can delete stations"
ON public.stations
FOR DELETE
TO authenticated
USING (public.is_admin());

-- ============================================================================
-- Parking Lots: Admin CRUD policies
-- ============================================================================

-- Admin can INSERT parking lots
CREATE POLICY "Admins can insert parking_lots"
ON public.parking_lots
FOR INSERT
TO authenticated
WITH CHECK (public.is_admin());

-- Admin can UPDATE parking lots
CREATE POLICY "Admins can update parking_lots"
ON public.parking_lots
FOR UPDATE
TO authenticated
USING (public.is_admin())
WITH CHECK (public.is_admin());

-- Admin can DELETE parking lots
CREATE POLICY "Admins can delete parking_lots"
ON public.parking_lots
FOR DELETE
TO authenticated
USING (public.is_admin());
