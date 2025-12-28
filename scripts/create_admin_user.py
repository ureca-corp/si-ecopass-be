"""
관리자 계정 생성 스크립트

admin/admin 계정을 생성하고 role을 'admin'으로 설정합니다.
"""

import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


async def create_admin_user():
    """관리자 계정 생성"""

    # Supabase 클라이언트 초기화
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_KEY 환경 변수가 설정되지 않았습니다.")
        return

    db: Client = create_client(supabase_url, supabase_key)

    # 1. 회원가입 (이미 존재하면 에러 발생)
    email = "admin@ecopass.com"
    password = "admin123"  # 최소 6자 이상 필요
    username = "admin"

    print(f"📝 관리자 계정 생성 중... (email: {email})")

    try:
        # Supabase Auth에 사용자 등록 (user_metadata에 role 포함)
        auth_response = db.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "role": "admin",  # JWT 토큰에 포함됨
                }
            }
        })

        if not auth_response.user:
            print("❌ 회원가입에 실패했습니다.")
            return

        user_id = auth_response.user.id
        print(f"✅ 사용자 생성 완료 (ID: {user_id})")

        # 2. users 테이블에서 role을 'admin'으로 업데이트
        print(f"🔧 role을 'admin'으로 변경 중...")

        update_response = db.table("users").update({
            "username": username,
            "role": "admin"
        }).eq("id", user_id).execute()

        if update_response.data:
            print("✅ 관리자 계정 생성 완료!")
            print(f"\n📋 계정 정보:")
            print(f"   이메일: {email}")
            print(f"   비밀번호: {password}")
            print(f"   사용자명: {username}")
            print(f"   역할: admin")
            print(f"   ID: {user_id}")
        else:
            print("❌ role 업데이트에 실패했습니다.")

    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower():
            print(f"⚠️  이미 등록된 이메일입니다: {email}")
            print(f"ℹ️  기존 계정의 role을 'admin'으로 변경하려면 다음 SQL을 실행하세요:")
            print(f"   UPDATE users SET role = 'admin' WHERE email = '{email}';")
        else:
            print(f"❌ 오류 발생: {error_message}")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
