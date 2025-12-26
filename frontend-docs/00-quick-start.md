# SI-EcoPass API - Quick Start Guide

## 📋 기본 정보

**Base URL**: `http://localhost:8000` (개발) / `https://api.siecopass.com` (프로덕션)  
**API Prefix**: `/api/v1`

## 📚 API 문서

### 🔥 추천: Swagger UI (실시간 API 문서)

모든 API 스펙과 스키마는 Swagger에서 확인하세요:

```
http://localhost:8000/docs         # 개발 환경
https://api.siecopass.com/docs      # 프로덕션
```

**Swagger 장점:**

- 🔄 최신 API 스펙 자동 반영
- 🧪 브라우저에서 직접 테스트 가능
- 📖 모든 Request/Response 스키마 확인
- 🔍 검색 및 필터링 지원

**OpenAPI JSON** (코드 생성용):

```
http://localhost:8000/openapi.json
```

### 📄 추가 문서

- [swagger-guide.md](./swagger-guide.md) - Swagger 사용법 및 Flutter 코드 생성
- [api-flows.md](./api-flows.md) - 주요 API 호출 순서

---

## 🔐 인증 방법

대부분의 API는 JWT Bearer Token 인증이 필요합니다.

**1. 로그인으로 토큰 획득**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

→ Response: { "data": { "access_token": "eyJ..." } }
```

**2. 인증이 필요한 API 호출**

```http
GET /api/v1/trips
Authorization: Bearer {access_token}
```

---

## 📦 표준 응답 형식

모든 API는 동일한 응답 구조를 사용합니다:

**성공 응답**

```json
{
  "status": "success",
  "message": "작업이 완료되었습니다",
  "data": {
    /* 실제 데이터 */
  }
}
```

**에러 응답**

```json
{
  "status": "error",
  "message": "에러 메시지",
  "data": null
}
```

---

## 🚀 핵심 API 엔드포인트

### 인증 (Authentication)

- `POST /api/v1/auth/signup` - 회원가입
- `POST /api/v1/auth/login` - 로그인 (토큰 발급)
- `GET /api/v1/auth/profile` - 프로필 조회 🔒
- `PUT /api/v1/auth/profile` - 프로필 수정 🔒

### 역 & 주차장 (Stations)

- `GET /api/v1/stations` - 역 목록 조회
- `GET /api/v1/stations/{id}` - 역 상세 정보
- `GET /api/v1/stations/{id}/parking-lots` - 역별 주차장 목록
- `GET /api/v1/stations/nearby` - 주변 역 검색

### 여정 관리 (Trips)

- `POST /api/v1/trips/start` - 여정 시작 (1단계) 🔒
- `POST /api/v1/trips/{id}/transfer` - 환승 기록 (2단계) 🔒
- `POST /api/v1/trips/{id}/arrival` - 도착 기록 (3단계) 🔒
- `GET /api/v1/trips` - 내 여정 목록 🔒
- `GET /api/v1/trips/{id}` - 여정 상세 정보 🔒

### 이미지 업로드 (Storage)

- `POST /api/v1/storage/upload/transfer` - 환승 사진 업로드 🔒
- `POST /api/v1/storage/upload/arrival` - 도착 사진 업로드 🔒

### 관리자 (Admin)

- `GET /api/v1/admin/trips` - 전체 여정 목록 🔒👮
- `POST /api/v1/admin/trips/{id}/approve` - 여정 승인 🔒👮
- `POST /api/v1/admin/trips/{id}/reject` - 여정 반려 🔒👮

🔒 = JWT 인증 필요  
👮 = 관리자 권한 필요

---

## 🚨 에러 코드

| 코드 | 의미             | 처리 방법                  |
| ---- | ---------------- | -------------------------- |
| 400  | 잘못된 요청      | 요청 파라미터 확인         |
| 401  | 인증 실패        | 로그인 필요 또는 토큰 갱신 |
| 403  | 권한 없음        | 관리자 권한 필요           |
| 404  | 리소스 없음      | 존재하지 않는 ID           |
| 409  | 충돌             | 중복 데이터 또는 상태 충돌 |
| 422  | 유효성 검증 실패 | 입력 데이터 형식 확인      |
| 500  | 서버 오류        | 관리자에게 문의            |

---

## 💡 Flutter 개발 팁

### 1. HTTP 클라이언트 설정 (Dio 추천)

```dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final dio = Dio(BaseOptions(
  baseUrl: 'http://localhost:8000/api/v1',
  connectTimeout: Duration(seconds: 5),
  receiveTimeout: Duration(seconds: 3),
));

// 토큰 자동 추가 인터셉터
dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) async {
    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return handler.next(options);
  },
));
```

### 2. 토큰 관리

```dart
// flutter_secure_storage 사용
final storage = FlutterSecureStorage();

// 저장
await storage.write(key: 'access_token', value: token);

// 읽기
final token = await storage.read(key: 'access_token');

// 삭제 (로그아웃)
await storage.delete(key: 'access_token');
```

### 3. 이미지 압축

```dart
// flutter_image_compress 사용
import 'package:flutter_image_compress/flutter_image_compress.dart';

Future<File> compressImage(File file) async {
  final result = await FlutterImageCompress.compressAndGetFile(
    file.absolute.path,
    '${file.parent.path}/compressed_${file.path.split('/').last}',
    quality: 80,
    minWidth: 1920,
    minHeight: 1080,
  );
  return File(result!.path);
}
```

### 4. 위치 권한 처리

```dart
// geolocator 사용
import 'package:geolocator/geolocator.dart';

Future<Position> getCurrentLocation() async {
  bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    throw Exception('위치 서비스가 비활성화되어 있습니다');
  }

  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      throw Exception('위치 권한이 거부되었습니다');
    }
  }

  return await Geolocator.getCurrentPosition();
}
```

### 5. 네트워크 상태 확인

```dart
// connectivity_plus 사용
import 'package:connectivity_plus/connectivity_plus.dart';

final connectivity = Connectivity();
final result = await connectivity.checkConnectivity();

if (result == ConnectivityResult.none) {
  // 오프라인 처리
}
```

---

## 🔧 개발 환경 설정

```bash
# 서버 실행 (개발)
python main.py

# API 문서 확인
http://localhost:8000/docs

# 헬스 체크
curl http://localhost:8000/health
```

---

**마지막 업데이트**: 2025-12-26  
**API 버전**: v1
