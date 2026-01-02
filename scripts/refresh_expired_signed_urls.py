#!/usr/bin/env python3
"""
만료된 Signed URL 갱신 스크립트
trips 테이블의 모든 이미지 URL을 새로운 24시간 유효 URL로 업데이트
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

def main():
    load_dotenv()

    supabase_url = "https://cozcysbrzmmumutivtny.supabase.co"
    supabase_key = os.getenv("SUPABASE_KEY")

    print("🔧 Supabase 클라이언트 생성 중...")
    supabase: Client = create_client(supabase_url, supabase_key)

    # trips 테이블에서 이미지 URL이 있는 모든 레코드 조회
    print("\n📋 만료된 URL이 있는 여정 조회 중...")
    response = supabase.table("trips").select("id, transfer_image_url, arrival_image_url").execute()

    trips = response.data
    print(f"✅ 총 {len(trips)}개의 여정 발견\n")

    storage = supabase.storage.from_("trips")
    updated_count = 0

    for trip in trips:
        trip_id = trip["id"]
        transfer_url = trip.get("transfer_image_url")
        arrival_url = trip.get("arrival_image_url")

        updates = {}

        # transfer_image_url 갱신
        if transfer_url and "/sign/" in transfer_url:
            # URL에서 파일 경로 추출
            file_path = transfer_url.split("/trips/")[1].split("?")[0]
            try:
                new_url = storage.create_signed_url(file_path, expires_in=86400)["signedURL"]
                updates["transfer_image_url"] = new_url
                print(f"✅ {trip_id[:8]}... transfer 갱신")
            except Exception as e:
                print(f"❌ {trip_id[:8]}... transfer 실패: {e}")

        # arrival_image_url 갱신
        if arrival_url and "/sign/" in arrival_url:
            file_path = arrival_url.split("/trips/")[1].split("?")[0]
            try:
                new_url = storage.create_signed_url(file_path, expires_in=86400)["signedURL"]
                updates["arrival_image_url"] = new_url
                print(f"✅ {trip_id[:8]}... arrival 갱신")
            except Exception as e:
                print(f"❌ {trip_id[:8]}... arrival 실패: {e}")

        # DB 업데이트
        if updates:
            supabase.table("trips").update(updates).eq("id", trip_id).execute()
            updated_count += 1

    print(f"\n🎉 완료! {updated_count}개 여정의 URL 갱신됨")
    print("⏰ 새 URL은 24시간 동안 유효합니다")

if __name__ == "__main__":
    main()
