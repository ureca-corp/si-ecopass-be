# SI-EcoPass Backend - 프로덕션 배포 가이드

## 📦 Docker를 사용한 배포

### 1. 사전 준비

#### 필수 요구사항
- Docker 20.10+ 설치
- Docker Compose 2.0+ 설치
- Supabase 프로젝트 설정 완료

#### 환경 변수 설정
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 실제 값으로 수정
vim .env
```

**필수 환경 변수**:
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_KEY`: Supabase anon 또는 service key
- `DATABASE_URL`: PostgreSQL 연결 URL
- `ALLOWED_ORIGINS`: CORS 허용 도메인 (쉼표로 구분)

### 2. Docker 이미지 빌드

```bash
# 프로덕션 이미지 빌드
docker build -t si-ecopass-api:latest .

# 빌드 확인
docker images | grep si-ecopass-api
```

### 3. 로컬에서 테스트

#### Docker Compose 사용 (권장)
```bash
# 백그라운드에서 실행
docker compose up -d

# 로그 확인
docker compose logs -f api

# 헬스 체크 확인
curl http://localhost:8000/health

# API 문서 확인
# http://localhost:8000/docs

# 중지
docker compose down
```

#### Docker 직접 실행
```bash
# 컨테이너 실행
docker run -d \
  --name si-ecopass-api \
  --env-file .env \
  -p 8000:8000 \
  si-ecopass-api:latest

# 로그 확인
docker logs -f si-ecopass-api

# 중지 및 삭제
docker stop si-ecopass-api
docker rm si-ecopass-api
```

### 4. 프로덕션 배포

#### 4.1. Docker Hub에 푸시
```bash
# Docker Hub 로그인
docker login

# 이미지 태그 지정
docker tag si-ecopass-api:latest yourusername/si-ecopass-api:latest
docker tag si-ecopass-api:latest yourusername/si-ecopass-api:v0.1.0

# 푸시
docker push yourusername/si-ecopass-api:latest
docker push yourusername/si-ecopass-api:v0.1.0
```

#### 4.2. AWS ECS/Fargate 배포 예제
```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그 및 푸시
docker tag si-ecopass-api:latest \
  123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/si-ecopass-api:latest
docker push 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/si-ecopass-api:latest

# ECS 태스크 정의 업데이트 및 서비스 배포
aws ecs update-service --cluster your-cluster --service your-service --force-new-deployment
```

#### 4.3. 클라우드 플랫폼 배포

**Render.com**:
1. Dashboard → New → Web Service
2. Connect your GitHub repository
3. Build Command: `docker build -t app .`
4. Start Command: (Dockerfile의 CMD 사용)
5. Environment Variables 설정

**Railway.app**:
1. New Project → Deploy from GitHub repo
2. Dockerfile을 자동 감지
3. Variables 탭에서 환경 변수 설정
4. Deploy

**Google Cloud Run**:
```bash
# 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/PROJECT_ID/si-ecopass-api

# Cloud Run 배포
gcloud run deploy si-ecopass-api \
  --image gcr.io/PROJECT_ID/si-ecopass-api \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production,DEBUG=False"
```

### 5. 배포 후 확인사항

#### Health Check
```bash
curl https://your-domain.com/health
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

#### API 문서 확인
- Swagger UI: `https://your-domain.com/docs`
- ReDoc: `https://your-domain.com/redoc`

#### 로그 모니터링
```bash
# Docker Compose 로그
docker compose logs -f api

# 특정 컨테이너 로그
docker logs -f si-ecopass-api
```

## 🔒 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] 프로덕션 환경에서 `DEBUG=False` 설정
- [ ] Supabase RLS (Row Level Security) 정책 활성화
- [ ] HTTPS 사용 (Let's Encrypt, Cloudflare 등)
- [ ] CORS `ALLOWED_ORIGINS`를 실제 도메인으로 제한
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] 정기적인 보안 업데이트 적용

## 📊 성능 최적화

### 이미지 크기 최적화
현재 Dockerfile은 multi-stage build를 사용하여 이미지 크기를 최소화합니다:
- Builder stage: 의존성 설치
- Runtime stage: 실행에 필요한 파일만 포함

### 메모리 사용량
- 권장 최소 메모리: 512MB
- 권장 메모리: 1GB
- 높은 트래픽 환경: 2GB+

### 수평 확장
```bash
# Docker Compose로 복제 실행
docker compose up -d --scale api=3
```

## 🔧 문제 해결

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker logs si-ecopass-api

# 일반적인 원인:
# 1. 환경 변수 누락 (.env 확인)
# 2. Supabase 연결 실패 (URL, KEY 확인)
# 3. DATABASE_URL 형식 오류
```

### Health check 실패
```bash
# 컨테이너 내부에서 직접 확인
docker exec -it si-ecopass-api python -c "import httpx; print(httpx.get('http://localhost:8000/health'))"
```

### 데이터베이스 연결 오류
- `DATABASE_URL` 형식 확인
- 비밀번호에 `@` 문자가 있으면 `%40`으로 인코딩
- Supabase 방화벽 설정 확인

## 📚 추가 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase 공식 문서](https://supabase.com/docs)
- [Docker 공식 문서](https://docs.docker.com/)
- [uv 공식 문서](https://github.com/astral-sh/uv)
