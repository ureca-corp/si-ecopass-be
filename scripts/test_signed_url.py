#!/usr/bin/env python3
"""
Signed URL 생성 및 테스트 스크립트
RLS 제거 후 400 오류 해결 확인
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

def main():
    # .env 파일 로드
    load_dotenv()

    # .env에서 Supabase 정보 로드
    supabase_url = "https://cozcysbrzmmumutivtny.supabase.co"
    supabase_key = os.getenv("SUPABASE_KEY")

    print("🔧 Supabase 클라이언트 생성 중...")
    supabase: Client = create_client(supabase_url, supabase_key)

    # 테스트할 파일 경로들
    test_files = [
        "fe633521-fd61-45ec-8cce-18adf2e0d9b3/20251229_180416_transfer.jpg",
        "fe633521-fd61-45ec-8cce-18adf2e0d9b3/20251229_180433_arrival.jpg",
        "fe633521-fd61-45ec-8cce-18adf2e0d9b3/20251229_105910_arrival.jpg",
    ]

    print("\n" + "="*70)
    print("🧪 Signed URL 생성 테스트")
    print("="*70 + "\n")

    for file_path in test_files:
        print(f"📁 파일: {file_path}")

        try:
            # 24시간 유효한 signed URL 생성
            result = supabase.storage.from_("trips").create_signed_url(
                file_path,
                expires_in=86400  # 24시간
            )

            signed_url = result['signedURL']

            print(f"✅ 성공!\n")
            print(f"🔗 Signed URL:\n{signed_url}\n")

            # 첫 번째 파일만 curl 테스트
            if file_path == test_files[0]:
                print("📝 curl 테스트 명령:")
                print(f'curl -I "{signed_url}"\n')

                import subprocess
                try:
                    result = subprocess.run(
                        ["curl", "-I", signed_url],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    # HTTP 상태 코드 추출
                    if "HTTP" in result.stdout:
                        status_line = [line for line in result.stdout.split('\n') if 'HTTP' in line][0]
                        if "200" in status_line:
                            print(f"✅ HTTP 200 OK - 파일 접근 성공!\n")
                        else:
                            print(f"⚠️  {status_line}\n")
                except Exception as e:
                    print(f"❌ curl 테스트 실패: {e}\n")

            print("-" * 70 + "\n")

        except Exception as e:
            print(f"❌ 오류: {e}\n")
            print("-" * 70 + "\n")

if __name__ == "__main__":
    main()
