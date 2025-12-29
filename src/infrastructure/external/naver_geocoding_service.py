"""
Naver Geocoding Service

네이버 클라우드 플랫폼 Maps API를 활용한 주소 검색 및 좌표 변환
- 주소 검색 (자동완성용)
- 주소 → 좌표 변환 (Geocoding)
"""

import httpx
from typing import Optional

from pydantic import BaseModel

from src.shared.exceptions import InternalServerError


class AddressSearchResult(BaseModel):
    """
    주소 검색 결과
    네이버 Geocoding API 응답 파싱
    """

    address: str  # 도로명 주소
    jibun_address: Optional[str] = None  # 지번 주소
    latitude: float  # 위도
    longitude: float  # 경도

    class Config:
        json_schema_extra = {
            "example": {
                "address": "대구광역시 중구 동성로2가 123",
                "jibun_address": "대구광역시 중구 동성로2가 123",
                "latitude": 35.8580,
                "longitude": 128.5980,
            }
        }


class NaverGeocodingService:
    """
    네이버 클라우드 Maps API 통합 서비스

    기능:
    - 주소 검색 (자동완성)
    - 주소 → 좌표 변환 (Geocoding)

    API 문서:
    https://api.ncloud-docs.com/docs/ai-naver-mapsgeocoding-geocode
    """

    def __init__(self, client_id: str, client_secret: str):
        """
        네이버 Geocoding 서비스 초기화

        Args:
            client_id: 네이버 클라우드 플랫폼 Client ID
            client_secret: 네이버 클라우드 플랫폼 Client Secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.geocode_url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"

    def _get_headers(self) -> dict:
        """
        API 인증 헤더 생성
        X-NCP-APIGW-API-KEY-ID와 X-NCP-APIGW-API-KEY 사용
        """
        return {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
        }

    async def search_addresses(self, query: str, limit: int = 10) -> list[AddressSearchResult]:
        """
        주소 검색 (자동완성용)

        Args:
            query: 검색 키워드 (예: "대구 중구 동성로")
            limit: 최대 결과 개수 (기본 10개)

        Returns:
            주소 검색 결과 리스트

        Raises:
            InternalServerError: API 호출 실패 시
        """
        params = {
            "query": query,
            "count": limit,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.geocode_url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=10.0,
                )

                # API 에러 처리
                if response.status_code != 200:
                    raise InternalServerError(
                        f"네이버 Geocoding API 호출 실패 (status={response.status_code})"
                    )

                data = response.json()

                # 검색 결과 파싱
                addresses = data.get("addresses", [])

                results = []
                for addr in addresses:
                    # 도로명 주소 우선, 없으면 지번 주소
                    road_address = addr.get("roadAddress", "")
                    jibun_address = addr.get("jibunAddress", "")

                    results.append(
                        AddressSearchResult(
                            address=road_address or jibun_address,
                            jibun_address=jibun_address if jibun_address else None,
                            latitude=float(addr["y"]),
                            longitude=float(addr["x"]),
                        )
                    )

                return results

        except httpx.RequestError as e:
            raise InternalServerError(f"네이버 Geocoding API 요청 실패: {str(e)}")
        except (KeyError, ValueError) as e:
            raise InternalServerError(f"네이버 Geocoding API 응답 파싱 실패: {str(e)}")

    async def geocode_address(self, address: str) -> Optional[tuple[float, float]]:
        """
        주소 → 좌표 변환 (단일 결과)

        Args:
            address: 도로명 또는 지번 주소

        Returns:
            (latitude, longitude) 또는 None (변환 실패 시)
        """
        results = await self.search_addresses(query=address, limit=1)

        if not results:
            return None

        first = results[0]
        return (first.latitude, first.longitude)
