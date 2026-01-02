# Database Migrations

마이그레이션 파일은 시간순으로 적용되며, 한 번 적용된 파일은 수정하지 않습니다.

## 현재 활성 마이그레이션

### 2025-12-26: 초기 스키마
- `20251226000001_initial_schema.sql` - 기본 테이블 생성 (users, stations, parking_lots, trips)
- `20251226000002_add_user_role.sql` - users 테이블에 role 컬럼 추가

### 2025-12-27: 호선 확장
- `20251227000001_add_daegyeong_line.sql` - 대경선(line_number=4) 지원 추가

### 2025-12-29: PostGIS 및 RLS 설정
- `20251229000002_add_lat_lng_columns_with_trigger.sql` - 위/경도 컬럼 추가 및 PostGIS 활성화
- `20251229000004_add_updated_at_to_stations_and_parking_lots.sql` - updated_at 컬럼 추가
- `20251229000010_disable_all_rls.sql` - **모든 RLS 비활성화 (JWT 인증으로 충분)**

### 2025-12-30: 포인트 시스템 통합
- `20251230000001_unify_points_fields.sql` - estimated_points와 earned_points를 단일 points 필드로 통합

### 2025-12-31: 포인트 제약 조건
- `20251231000001_set_points_not_null.sql` - points 필드를 NOT NULL로 변경 (기본값 0)

### 2026-01-02: Storage 버킷 생성
- `20260102000001_create_storage_buckets.sql` - trips 버킷 생성 (이미지 업로드용)

## 정리된 마이그레이션

다음 마이그레이션들은 불필요하거나 무효화되어 제거되었습니다:

### Deprecated RLS 마이그레이션 (삭제됨)
`20251229000010_disable_all_rls.sql`에서 모든 RLS를 비활성화하면서 다음 파일들이 무효화됨:
- `20251228000001_fix_admin_rls_policy.sql`
- `20251229000001_add_admin_rls_policy.sql`
- `20251229000003_add_admin_rls_policies.sql`
- `20251229000008_fix_storage_buckets_rls.sql`
- `20251229000009_simplify_storage_rls.sql`

### 사용하지 않는 함수 마이그레이션 (삭제됨)
코드베이스에서 사용되지 않는 함수들:
- `20251229000005_add_get_user_with_email_function.sql` - 이메일로 사용자 조회 (레포지토리로 대체)
- `20251229000006_add_count_all_users_function.sql` - 사용자 수 집계 (직접 쿼리로 대체)
- `20251229000007_add_image_coordinates_to_stations.sql` - 역 이미지 좌표 (미사용 기능)

**이유**: 애플리케이션 계층에서 직접 처리하는 것이 더 명확하고 유지보수가 용이함

## 보안 정책

- **RLS**: 모든 public 테이블에서 비활성화됨
- **인증**: JWT 토큰 기반 (Supabase Auth)
- **권한 검증**: FastAPI `get_current_user()` + Service Layer
- **Storage**: 최소 RLS 유지 (버킷 메타데이터 조회만 허용)

## 새 마이그레이션 생성 시 주의사항

1. **파일명 형식**: `YYYYMMDDNNNNNN_description.sql`
   - 예: `20260103000001_add_rewards_table.sql`

2. **롤백 불가**: 마이그레이션은 전진만 가능 (수정 필요 시 새 마이그레이션 생성)

3. **프로덕션 적용 전 테스트**: 로컬 Supabase 또는 브랜치에서 먼저 테스트

```bash
# 로컬 Supabase에서 테스트
supabase db reset
# 또는
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -f supabase/migrations/새파일.sql
```

4. **의존성 확인**: 새 마이그레이션이 기존 테이블/컬럼을 참조하는 경우 순서 확인

5. **백업 권장**: 프로덕션 적용 전 데이터베이스 백업 필수
