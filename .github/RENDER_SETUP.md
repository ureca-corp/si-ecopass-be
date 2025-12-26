# Render 배포 설정 가이드

## 📋 사전 준비

### 1. Render 계정 생성
1. [Render.com](https://render.com)에서 계정 생성
2. GitHub 계정과 연동

### 2. GitHub Repository Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

다음 시크릿을 추가하세요:

| Secret Name | 설명 | 예시 |
|------------|------|------|
| `RENDER_API_KEY` | Render API 키 | `rnd_xxxxxxxxxxxxx` |
| `RENDER_SERVICE_ID` | Render 서비스 ID | `srv-xxxxxxxxxxxxx` |
| `SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/service key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `DATABASE_URL` | PostgreSQL 연결 URL | `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres` |

### 3. Render API Key 발급

1. Render Dashboard → Account Settings
2. API Keys → Create API Key
3. 키를 복사하여 GitHub Secrets의 `RENDER_API_KEY`에 저장

### 4. Render Service ID 확인

**방법 1: Render Dashboard에서**
1. Render Dashboard → 서비스 선택
2. URL의 마지막 부분이 Service ID
   - 예: `https://dashboard.render.com/web/srv-xxxxxxxxxxxxx`
   - Service ID: `srv-xxxxxxxxxxxxx`

**방법 2: 첫 배포 후 (수동 배포)**
아래 "수동 배포" 단계를 먼저 수행한 후, Dashboard에서 Service ID를 확인할 수 있습니다.

## 🚀 배포 방법

### 방법 1: GitHub Actions 자동 배포 (권장)

#### 초기 설정
```bash
# 1. render.yaml 파일이 있는지 확인
ls render.yaml

# 2. GitHub Actions 워크플로우 확인
ls .github/workflows/deploy-render.yml

# 3. GitHub Secrets 설정 확인 (위 "사전 준비" 참조)
```

#### 자동 배포
```bash
# main 브랜치에 푸시하면 자동으로 배포됩니다
git add .
git commit -m "Deploy to Render"
git push origin main
```

#### 수동 트리거
GitHub Repository → Actions → Deploy to Render → Run workflow

### 방법 2: Render Dashboard 수동 배포

#### 첫 배포 (Blueprint 사용)
1. Render Dashboard → New → Blueprint
2. GitHub repository 선택
3. `render.yaml` 자동 감지
4. Deploy

#### 환경 변수 설정
Dashboard → 서비스 선택 → Environment
- `SUPABASE_URL` (Secret)
- `SUPABASE_KEY` (Secret)
- `DATABASE_URL` (Secret)

### 방법 3: Render CLI 배포

```bash
# Render CLI 설치
npm install -g @render/cli

# 로그인
render login

# 서비스 생성 (최초 1회)
render blueprint launch

# 배포
render deploy --service si-ecopass-api
```

## 📊 배포 프로세스 모니터링

### GitHub Actions 로그 확인
```
GitHub Repository → Actions → 최근 워크플로우 실행 선택
```

4개의 Job 실행 순서:
1. **Test**: 테스트 실행 (pytest)
2. **Build**: Docker 이미지 빌드 및 테스트
3. **Deploy**: Render에 배포
4. **Smoke Test**: 배포 후 헬스 체크

### Render Dashboard 로그 확인
```
Dashboard → 서비스 선택 → Logs
```

## ✅ 배포 검증

### 1. Health Check
```bash
curl https://si-ecopass-api.onrender.com/health
```

**예상 응답**:
```json
{
  "status": "success",
  "message": "Server is running",
  "data": {
    "app_name": "SI-EcoPass Backend",
    "version": "0.1.0",
    "environment": "production"
  }
}
```

### 2. API 문서 확인
- Swagger UI: https://si-ecopass-api.onrender.com/docs
- ReDoc: https://si-ecopass-api.onrender.com/redoc

### 3. API 테스트
```bash
# 역 목록 조회
curl https://si-ecopass-api.onrender.com/api/v1/stations

# 회원가입 (예시)
curl -X POST https://si-ecopass-api.onrender.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

## 🔧 문제 해결

### 배포 실패 시

#### 1. GitHub Actions 로그 확인
```
Actions → 실패한 워크플로우 → 각 Job 로그 확인
```

**일반적인 오류**:
- 테스트 실패 → `test` job 로그 확인
- Docker 빌드 실패 → `build` job 로그 확인
- Render 배포 실패 → `deploy` job 로그 확인

#### 2. Render 서비스 로그 확인
```
Dashboard → 서비스 → Logs → Deploy Logs / Service Logs
```

#### 3. Secrets 확인
```bash
# GitHub Secrets가 올바르게 설정되었는지 확인
# Settings → Secrets and variables → Actions
```

### 일반적인 문제

**문제: `RENDER_SERVICE_ID` 없음**
- 수동으로 첫 배포를 진행한 후 Dashboard에서 Service ID를 확인
- Settings → Secrets → `RENDER_SERVICE_ID` 추가

**문제: Health check 실패**
- Render Dashboard → Logs에서 에러 확인
- 환경 변수가 올바르게 설정되었는지 확인
- Supabase 연결 정보 확인

**문제: Docker 빌드 타임아웃**
- Render의 free plan은 빌드 시간 제한이 있음
- Starter plan 이상으로 업그레이드 고려

## 🔒 보안 고려사항

- ✅ 모든 민감한 정보는 GitHub Secrets에 저장
- ✅ `render.yaml`에는 민감한 정보 포함 금지
- ✅ Render Dashboard에서 환경 변수를 "Secret" 타입으로 설정
- ✅ CORS `ALLOWED_ORIGINS`를 실제 도메인으로 제한
- ✅ Supabase RLS (Row Level Security) 활성화

## 📈 성능 최적화

### Render Plan 비교

| Plan | CPU | RAM | 가격 | 추천 |
|------|-----|-----|------|------|
| Free | 0.5 | 512MB | $0 | 테스트/개발 |
| Starter | 1 | 512MB | $7/월 | 소규모 프로덕션 |
| Standard | 2 | 2GB | $25/월 | 중간 규모 |
| Pro | 4 | 4GB | $85/월 | 대규모 |

### Auto-Deploy 설정
- `render.yaml`의 `autoDeploy: true`로 설정
- main 브랜치 푸시 시 자동 배포

### 캐시 최적화
GitHub Actions는 Docker layer caching 사용:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

## 📚 참고 자료

- [Render 공식 문서](https://render.com/docs)
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Render Blueprint 문서](https://render.com/docs/infrastructure-as-code)
- [Render Deploy Action](https://github.com/marketplace/actions/render-deploy-action)
