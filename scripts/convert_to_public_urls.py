#!/usr/bin/env python3
"""
Signed URL을 Public URL로 변환
버킷이 public이므로 signed URL 불필요
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

    print("\n📋 Signed URL이 있는 여정 조회 중...")
    response = supabase.table("trips").select("id, transfer_image_url, arrival_image_url").execute()

    trips = response.data
    print(f"✅ 총 {len(trips)}개의 여정 발견\n")

    updated_count = 0

    for trip in trips:
        trip_id = trip["id"]
        transfer_url = trip.get("transfer_image_url")
        arrival_url = trip.get("arrival_image_url")

        updates = {}

        # transfer_image_url을 public URL로 변환
        if transfer_url and "/sign/" in transfer_url:
            # URL에서 파일 경로 추출
            file_path = transfer_url.split("/trips/")[1].split("?")[0]
            public_url = f"{supabase_url}/storage/v1/object/public/trips/{file_path}"
            updates["transfer_image_url"] = public_url
            print(f"✅ {trip_id[:8]}... transfer → public URL")

        # arrival_image_url을 public URL로 변환
        if arrival_url and "/sign/" in arrival_url:
            file_path = arrival_url.split("/trips/")[1].split("?")[0]
            public_url = f"{supabase_url}/storage/v1/object/public/trips/{file_path}"
            updates["arrival_image_url"] = public_url
            print(f"✅ {trip_id[:8]}... arrival → public URL")

        # DB 업데이트
        if updates:
            supabase.table("trips").update(updates).eq("id", trip_id).execute()
            updated_count += 1

    print(f"\n🎉 완료! {updated_count}개 여정의 URL을 public URL로 변환")
    print("⏰ Public URL은 영구적으로 유효합니다 (만료 없음)")

if __name__ == "__main__":
    main()
