# Swagger UI 사용 가이드

## 📖 Swagger 접속

### 개발 환경

```
http://localhost:8000/docs
```

### 프로덕션 환경

```
https://api.siecopass.com/docs
```

---

## 🎯 Swagger UI 사용법

### 1. API 탐색

- **Tags**: Authentication, Stations, Trips, Storage, Admin으로 그룹화
- **클릭**: 각 엔드포인트를 클릭하면 상세 정보 확인
- **스키마**: Request/Response 스키마 자동 표시

### 2. API 테스트

#### Step 1: 로그인으로 토큰 획득

1. `POST /api/v1/auth/login` 엔드포인트 클릭
2. **Try it out** 버튼 클릭
3. Request body 입력:
   ```json
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```
4. **Execute** 버튼 클릭
5. Response에서 `access_token` 복사

#### Step 2: 인증 설정

1. 페이지 상단의 **Authorize** 🔓 버튼 클릭
2. Value 필드에 토큰 입력: `Bearer {access_token}`
3. **Authorize** 버튼 클릭
4. **Close** 버튼 클릭

이제 모든 🔒 표시 API를 테스트할 수 있습니다!

#### Step 3: 인증 필요한 API 테스트

1. 원하는 엔드포인트 클릭 (예: `GET /api/v1/trips`)
2. **Try it out** 버튼 클릭
3. 필요한 파라미터 입력
4. **Execute** 버튼 클릭
5. Response 확인

---

## 🤖 OpenAPI 스펙 다운로드

### JSON 형식

```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

### 브라우저에서 직접 다운로드

```
http://localhost:8000/openapi.json
```

---

## 🚀 Flutter 클라이언트 자동 생성

OpenAPI Generator를 사용하여 Flutter Dio 클라이언트를 자동으로 생성할 수 있습니다.

### 1. OpenAPI Generator 설치

```bash
# Homebrew (macOS)
brew install openapi-generator

# npm
npm install -g @openapitools/openapi-generator-cli

# Docker
docker pull openapitools/openapi-generator-cli
```

### 2. Flutter Dio 클라이언트 생성

```bash
# 서버에서 OpenAPI 스펙 다운로드
curl http://localhost:8000/openapi.json -o openapi.json

# Flutter Dio 클라이언트 생성
openapi-generator generate \
  -i openapi.json \
  -g dart-dio \
  -o lib/api_client \
  --additional-properties=pubName=si_ecopass_api,pubAuthor=SI-EcoPass
```

### 3. 생성된 파일 사용

```dart
import 'package:si_ecopass_api/si_ecopass_api.dart';

// API 클라이언트 초기화
final api = SiEcopassApi(
  basePathOverride: 'http://localhost:8000/api/v1',
);

// 로그인
final loginResponse = await api.getAuthenticationApi().apiV1AuthLoginPost(
  loginRequest: LoginRequest(
    email: 'user@example.com',
    password: 'password123',
  ),
);

// 토큰 설정
final token = loginResponse.data.accessToken;
api.setAccessToken(token);

// 인증 필요한 API 호출
final tripsResponse = await api.getTripsApi().apiV1TripsGet();
```

---

## 📚 추가 도구

### ReDoc (대안 문서)

더 읽기 쉬운 문서 형식:

```
http://localhost:8000/redoc
```

### Postman Collection 생성

Swagger에서 OpenAPI JSON을 다운받아 Postman으로 가져올 수 있습니다:

1. `openapi.json` 다운로드
2. Postman 실행
3. **Import** → **Upload Files**
4. `openapi.json` 선택
5. 자동으로 Collection 생성됨

---

## 💡 팁

### 1. 스키마 정의 확인

Swagger UI 하단의 **Schemas** 섹션에서 모든 데이터 타입 확인 가능:

- `LoginRequest`
- `TripResponse`
- `StationResponse`
- 등등...

### 2. 빠른 검색

Swagger UI 상단의 검색창으로 원하는 API를 빠르게 찾을 수 있습니다.

### 3. 예시 값 확인

각 스키마의 **Example Value** 탭을 클릭하면 실제 데이터 구조를 확인할 수 있습니다.

### 4. cURL 명령 복사

**Execute** 후 **Curl** 탭을 클릭하면 터미널에서 실행 가능한 cURL 명령을 복사할 수 있습니다.

---

**관련 문서**: [00-quick-start.md](./00-quick-start.md)
