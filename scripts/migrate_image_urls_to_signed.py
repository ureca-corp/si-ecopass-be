#!/usr/bin/env python3
"""
기존 trips 테이블의 public URL을 Signed URL로 변환하는 마이그레이션 스크립트

실행 방법:
    # Dry-run (시뮬레이션, 실제 변경 없음)
    uv run python scripts/migrate_image_urls_to_signed.py --dry-run

    # 실제 마이그레이션 실행
    uv run python scripts/migrate_image_urls_to_signed.py

주의사항:
    - 이 스크립트는 한 번만 실행해야 합니다
    - 실행 전 데이터베이스 백업을 권장합니다
    - Signed URL은 24시간 유효하므로 주기적으로 재생성이 필요할 수 있습니다
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client

from src.config import get_settings

# 설정 로드
settings = get_settings()


def extract_file_path_from_public_url(url: str) -> str | None:
    """
    public URL에서 파일 경로 추출

    예시:
        입력: https://xxx.supabase.co/storage/v1/object/public/trips/user_id/file.jpg
        출력: user_id/file.jpg
    """
    if not url or "/object/public/trips/" not in url:
        return None

    # /object/public/trips/ 이후의 경로 추출
    match = re.search(r"/object/public/trips/(.+)", url)
    if match:
        return match.group(1)

    return None


def create_signed_url(supabase_client, file_path: str) -> str:
    """
    파일 경로로부터 Signed URL 생성

    Args:
        supabase_client: Supabase 클라이언트
        file_path: 버킷 내 파일 경로 (예: "user_id/file.jpg")

    Returns:
        Signed URL (24시간 유효)
    """
    storage = supabase_client.storage.from_("trips")
    response = storage.create_signed_url(file_path, expires_in=86400)
    return response["signedURL"]


def migrate_trip_image_urls(dry_run: bool = False):
    """
    모든 trips의 이미지 URL을 public URL에서 Signed URL로 변환

    Args:
        dry_run: True일 경우 실제 업데이트 없이 시뮬레이션만 수행
    """
    # Supabase 클라이언트 초기화
    supabase = create_client(settings.supabase_url, settings.supabase_key)

    if dry_run:
        print("🧪 DRY-RUN 모드: 실제 데이터베이스 변경 없이 시뮬레이션만 수행됩니다.")
        print()

    print("🔍 기존 trips 데이터 조회 중...")

    # 모든 trips 조회
    response = supabase.table("trips").select("*").execute()
    trips = response.data

    if not trips:
        print("⚠️  처리할 trips가 없습니다.")
        return

    print(f"📊 총 {len(trips)}개의 trips 발견")
    print()

    # 통계
    updated_count = 0
    transfer_updated = 0
    arrival_updated = 0
    skipped_count = 0
    error_count = 0

    for trip in trips:
        trip_id = trip["id"]
        updates = {}

        try:
            # transfer_image_url 처리
            if trip.get("transfer_image_url"):
                transfer_url = trip["transfer_image_url"]
                file_path = extract_file_path_from_public_url(transfer_url)

                if file_path:
                    # public URL이므로 Signed URL로 변환
                    signed_url = create_signed_url(supabase, file_path)
                    updates["transfer_image_url"] = signed_url
                    transfer_updated += 1
                    print(f"  ✅ Trip {trip_id[:8]}... - transfer_image_url 변환 완료")

            # arrival_image_url 처리
            if trip.get("arrival_image_url"):
                arrival_url = trip["arrival_image_url"]
                file_path = extract_file_path_from_public_url(arrival_url)

                if file_path:
                    # public URL이므로 Signed URL로 변환
                    signed_url = create_signed_url(supabase, file_path)
                    updates["arrival_image_url"] = signed_url
                    arrival_updated += 1
                    print(f"  ✅ Trip {trip_id[:8]}... - arrival_image_url 변환 완료")

            # 업데이트 실행
            if updates:
                if not dry_run:
                    # 실제 업데이트 수행
                    supabase.table("trips").update(updates).eq("id", trip_id).execute()
                updated_count += 1
            else:
                skipped_count += 1
                print(f"  ⏭️  Trip {trip_id[:8]}... - 변환 불필요 (이미 Signed URL)")

        except Exception as e:
            error_count += 1
            print(f"  ❌ Trip {trip_id[:8]}... - 오류 발생: {str(e)}")

    # 최종 결과 출력
    print("\n" + "="*60)
    if dry_run:
        print("🧪 DRY-RUN 완료 (실제 변경 없음)")
    else:
        print("🎉 마이그레이션 완료!")
    print("="*60)
    print(f"총 trips: {len(trips)}")
    print(f"업데이트 대상: {updated_count}개")
    print(f"  - transfer_image_url: {transfer_updated}개")
    print(f"  - arrival_image_url: {arrival_updated}개")
    print(f"건너뜀: {skipped_count}개 (이미 Signed URL)")
    print(f"오류: {error_count}개")
    print("="*60)

    if dry_run:
        print("ℹ️  실제 마이그레이션을 실행하려면 --dry-run 플래그 없이 다시 실행하세요.")
    elif error_count > 0:
        print("⚠️  일부 trips에서 오류가 발생했습니다. 로그를 확인하세요.")
    else:
        print("✅ 모든 trips가 성공적으로 처리되었습니다!")


if __name__ == "__main__":
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description="Trips 테이블의 public URL을 Signed URL로 변환"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 변경 없이 시뮬레이션만 수행",
    )
    args = parser.parse_args()

    print("="*60)
    print("🚀 Trips 이미지 URL 마이그레이션 시작")
    print("   (public URL → Signed URL)")
    print("="*60)
    print()

    # dry-run이 아닌 경우에만 사용자 확인
    if not args.dry_run:
        response = input("⚠️  실제 데이터베이스를 변경합니다. 계속하시겠습니까? (y/N): ").strip().lower()

        if response != "y":
            print("❌ 마이그레이션이 취소되었습니다.")
            print("ℹ️  먼저 --dry-run 플래그로 시뮬레이션을 실행해보세요.")
            exit(0)

        print()

    migrate_trip_image_urls(dry_run=args.dry_run)
