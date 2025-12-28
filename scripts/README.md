# 스크립트 가이드

이 디렉토리에는 데이터베이스 마이그레이션 및 유틸리티 스크립트가 포함되어 있습니다.

## 📁 파일 목록

### `migrate_image_urls_to_signed.py`

기존 trips 테이블의 public URL을 Signed URL로 변환하는 일회성 마이그레이션 스크립트입니다.

#### 배경

- **문제**: Supabase Storage 버킷을 비공개로 설정한 후, 기존 public URL로 저장된 이미지에 접근할 수 없게 됨
- **해결**: 모든 이미지 URL을 Signed URL(24시간 유효)로 일괄 변환

#### 실행 방법

```bash
# 스크립트 실행
uv run python scripts/migrate_image_urls_to_signed.py
```

#### 실행 전 체크리스트

- [ ] `.env` 파일에 `SUPABASE_URL`과 `SUPABASE_KEY` 설정 확인
- [ ] 데이터베이스 백업 완료 (권장)
- [ ] 테스트 환경에서 먼저 실행 (권장)

#### 처리 과정

1. 모든 trips 레코드 조회
2. `transfer_image_url`, `arrival_image_url` 필드 확인
3. public URL 형식(`/object/public/trips/...`)인 경우:
   - 파일 경로 추출
   - Signed URL 생성 (24시간 유효)
   - 데이터베이스 업데이트
4. 이미 Signed URL인 경우 건너뜀

#### 실행 결과 예시

```
==============================================================
🚀 Trips 이미지 URL 마이그레이션 시작
   (public URL → Signed URL)
==============================================================

⚠️  계속하시겠습니까? (y/N): y

🔍 기존 trips 데이터 조회 중...
📊 총 15개의 trips 발견
  ✅ Trip 550e8400... - transfer_image_url 변환 완료
  ✅ Trip 550e8400... - arrival_image_url 변환 완료
  ✅ Trip 660e8400... - transfer_image_url 변환 완료
  ⏭️  Trip 770e8400... - 변환 불필요 (이미 Signed URL)

==============================================================
🎉 마이그레이션 완료!
==============================================================
총 trips: 15
업데이트됨: 10개
  - transfer_image_url: 8개
  - arrival_image_url: 7개
건너뜀: 5개 (이미 Signed URL)
오류: 0개
==============================================================
✅ 모든 trips가 성공적으로 처리되었습니다!
```

#### 주의사항

1. **한 번만 실행**: 이 스크립트는 일회성 마이그레이션이므로 한 번만 실행하세요
2. **Signed URL 만료**: Signed URL은 24시간 후 만료됩니다
   - 장기적으로는 API 응답 시점에 동적으로 Signed URL을 생성하는 것을 권장합니다
   - 또는 주기적으로 이 스크립트를 실행하여 URL을 갱신할 수 있습니다
3. **백업**: 실행 전 데이터베이스 백업을 권장합니다
4. **권한**: Supabase Storage에 대한 읽기/쓰기 권한이 필요합니다

#### 롤백 방법

문제가 발생한 경우 데이터베이스 백업에서 복원하거나, 다시 public URL로 변환하는 역방향 스크립트를 실행할 수 있습니다.

## 📝 새 스크립트 추가 가이드

새로운 유틸리티 스크립트를 추가할 때는 다음 사항을 지켜주세요:

1. **파일명**: `{동작}_{대상}.py` 형식 사용 (예: `migrate_image_urls_to_signed.py`)
2. **Shebang**: 파일 최상단에 `#!/usr/bin/env python3` 추가
3. **Docstring**: 스크립트 목적과 사용법을 명시
4. **환경 설정**: `src.config.settings`를 사용하여 환경 변수 로드
5. **로깅**: 진행 상황과 결과를 명확하게 출력
6. **에러 처리**: 예외 처리 및 사용자 친화적인 오류 메시지
7. **확인 프롬프트**: 데이터 변경 작업은 실행 전 사용자 확인 필수
8. **문서화**: 이 README에 사용법 추가

### 예시 템플릿

```python
#!/usr/bin/env python3
"""
스크립트 설명

실행 방법:
    uv run python scripts/your_script.py

주의사항:
    - 주의사항 1
    - 주의사항 2
"""

from src.config import settings
from supabase import create_client


def main():
    """메인 로직"""
    print("🚀 스크립트 시작")

    # 사용자 확인
    response = input("계속하시겠습니까? (y/N): ").strip().lower()
    if response != "y":
        print("❌ 취소되었습니다.")
        return

    # 실제 작업
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    # ...

    print("✅ 완료!")


if __name__ == "__main__":
    main()
```

## 🔗 관련 문서

- [프로젝트 README](../README.md)
- [백엔드 명세](../BACKEND_SPEC.md)
- [배포 가이드](../DEPLOYMENT.md)
