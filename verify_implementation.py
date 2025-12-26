#!/usr/bin/env python3
"""
Station & ParkingLot API 구현 검증 스크립트

FastAPI 서버가 실행 중인 상태에서 실행하세요:
python verify_implementation.py
"""

import sys
from pathlib import Path


def check_file_exists(file_path: str) -> bool:
    """파일 존재 여부 확인"""
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {file_path}")
    return exists


def main():
    print("=" * 80)
    print("Station & ParkingLot API 구현 검증")
    print("=" * 80)
    print()

    # 프로젝트 루트 디렉토리
    root = Path(__file__).parent

    all_files_exist = True

    print("📁 Domain Layer")
    all_files_exist &= check_file_exists(str(root / "src/domain/entities/station.py"))
    all_files_exist &= check_file_exists(str(root / "src/domain/entities/parking_lot.py"))
    all_files_exist &= check_file_exists(str(root / "src/domain/repositories/station_repository.py"))
    print()

    print("📁 Infrastructure Layer")
    all_files_exist &= check_file_exists(str(root / "src/infrastructure/repositories/station_repository_impl.py"))
    print()

    print("📁 Application Layer")
    all_files_exist &= check_file_exists(str(root / "src/application/services/station_service.py"))
    print()

    print("📁 API Layer")
    all_files_exist &= check_file_exists(str(root / "src/api/schemas/station_schemas.py"))
    all_files_exist &= check_file_exists(str(root / "src/api/dependencies/station_deps.py"))
    all_files_exist &= check_file_exists(str(root / "src/api/routes/station_routes.py"))
    print()

    print("📁 Documentation")
    all_files_exist &= check_file_exists(str(root / "STATION_API_IMPLEMENTATION.md"))
    all_files_exist &= check_file_exists(str(root / "TESTING_GUIDE.md"))
    all_files_exist &= check_file_exists(str(root / "supabase_rpc_functions.sql"))
    print()

    print("=" * 80)
    if all_files_exist:
        print("✅ 모든 파일이 정상적으로 생성되었습니다!")
        print()
        print("다음 단계:")
        print("1. .env 파일에 Supabase 자격증명 입력")
        print("2. supabase_rpc_functions.sql을 Supabase SQL Editor에서 실행")
        print("3. 서버 시작: uv run python main.py")
        print("4. API 테스트: http://localhost:8000/docs")
        return 0
    else:
        print("❌ 일부 파일이 누락되었습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
