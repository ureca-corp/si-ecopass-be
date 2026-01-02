"""
기존 관리자 계정의 user_metadata 업데이트 스크립트

admin@ecopass.com 계정의 user_metadata에 role: admin을 설정합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def update_admin_metadata():
    """관리자 계정 메타데이터 업데이트"""

    # Supabase 클라이언트 초기화
    supabase_url = os.getenv("SUPABASE_URL")
    # Service Role Key 필요 (SUPABASE_KEY는 anon key라서 권한 부족)
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 환경 변수가 설정되지 않았습니다.")
        print("ℹ️  .env 파일에 SUPABASE_SERVICE_ROLE_KEY를 추가하세요.")
        return

    db: Client = create_client(supabase_url, service_role_key)

    email = "admin@ecopass.com"
    user_id = "985741fb-27c3-4362-ad42-db35cf349d30"

    print(f"📝 관리자 계정 메타데이터 업데이트 중... (email: {email})")

    try:
        # Admin API로 user_metadata 업데이트
        # https://supabase.com/docs/reference/python/auth-admin-updateuserbyid
        response = db.auth.admin.update_user_by_id(
            user_id,
            {
                "user_metadata": {
                    "username": "admin",
                    "role": "admin"
                }
            }
        )

        if response.user:
            print("✅ 관리자 메타데이터 업데이트 완료!")
            print(f"\n📋 계정 정보:")
            print(f"   이메일: {response.user.email}")
            print(f"   사용자명: admin")
            print(f"   역할: admin (user_metadata)")
            print(f"   ID: {response.user.id}")
            print(f"\n✓ user_metadata: {response.user.user_metadata}")
        else:
            print("❌ 메타데이터 업데이트에 실패했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    update_admin_metadata()
