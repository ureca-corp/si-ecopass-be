"""
로컬 Supabase 테스트 데이터 정리 스크립트

지하철역(stations)과 주차장(parking_lots)은 유지하고,
사용자(users)와 여정(trips) 데이터만 삭제
"""

import asyncio
from supabase import create_client, Client

# 로컬 Supabase 연결 정보
SUPABASE_URL = "http://127.0.0.1:54321"
SUPABASE_KEY = "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH"


async def cleanup_local_db():
    """로컬 Supabase 데이터 정리"""

    # Supabase 클라이언트 초기화
    db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("🧹 로컬 Supabase 데이터 정리 시작...\n")

    # 1. trips 테이블 데이터 확인
    trips_before = db.table("trips").select("id", count="exact").execute()
    print(f"📊 trips 테이블: {trips_before.count}개 데이터")

    # 2. users 테이블 데이터 확인
    users_before = db.table("users").select("id", count="exact").execute()
    print(f"📊 users 테이블: {users_before.count}개 데이터")

    # 3. stations 테이블 데이터 확인 (유지)
    stations = db.table("stations").select("id", count="exact").execute()
    print(f"✅ stations 테이블: {stations.count}개 데이터 (유지)")

    # 4. parking_lots 테이블 데이터 확인 (유지)
    parking_lots = db.table("parking_lots").select("id", count="exact").execute()
    print(f"✅ parking_lots 테이블: {parking_lots.count}개 데이터 (유지)")

    print("\n🗑️  데이터 삭제 중...\n")

    # 5. trips 테이블 전체 삭제
    if trips_before.count > 0:
        # Supabase는 TRUNCATE를 직접 지원하지 않으므로, DELETE FROM 사용
        # neq를 사용하여 모든 레코드 삭제 (빈 문자열과 같지 않은 모든 id)
        db.table("trips").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"✅ trips 테이블 {trips_before.count}개 데이터 삭제 완료")

    # 6. users 테이블 전체 삭제
    if users_before.count > 0:
        db.table("users").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"✅ users 테이블 {users_before.count}개 데이터 삭제 완료")

    # 7. 결과 확인
    print("\n📊 정리 후 데이터 개수:")
    trips_after = db.table("trips").select("id", count="exact").execute()
    users_after = db.table("users").select("id", count="exact").execute()
    stations_after = db.table("stations").select("id", count="exact").execute()
    parking_lots_after = db.table("parking_lots").select("id", count="exact").execute()

    print(f"   - trips: {trips_after.count}개")
    print(f"   - users: {users_after.count}개")
    print(f"   - stations: {stations_after.count}개 (유지됨)")
    print(f"   - parking_lots: {parking_lots_after.count}개 (유지됨)")

    print("\n✅ 로컬 Supabase 데이터 정리 완료!")
    print("\nℹ️  Supabase Auth 사용자는 Studio에서 수동으로 삭제하세요:")
    print("   http://127.0.0.1:54323")


if __name__ == "__main__":
    asyncio.run(cleanup_local_db())
