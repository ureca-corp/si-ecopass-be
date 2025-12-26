"""
ParkingLot Domain Entity

대구 지하철 역 주변 주차장 정보를 나타내는 도메인 엔티티
Station과 FK 관계를 맺으며 PostGIS 좌표 데이터 지원
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """
    현재 UTC 시간을 timezone 정보와 함께 반환
    모든 timestamp 필드의 기본값으로 사용
    """
    return datetime.now(timezone.utc)


class ParkingLot(SQLModel, table=True):
    """
    주차장 엔티티 (DB 테이블)

    지하철 역 주변의 환승 주차장 정보
    PostGIS geography(Point) 타입으로 저장된 좌표를 latitude/longitude로 변환하여 제공
    """

    __tablename__ = "parking_lots"  # Supabase 테이블명

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="주차장 고유 식별자",
    )
    station_id: UUID = Field(
        foreign_key="stations.id",
        description="연결된 지하철 역 ID (FK)",
    )
    name: str = Field(
        min_length=1,
        max_length=200,
        description="주차장명",
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="주차장 주소",
    )
    # PostGIS geography(Point) 타입은 Supabase에서 조회 시 WKT 문자열로 변환됨
    # 실제 좌표는 latitude, longitude 필드로 별도 제공
    latitude: Optional[float] = Field(
        default=None,
        description="위도 (PostGIS ST_Y 함수로 추출)",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="경도 (PostGIS ST_X 함수로 추출)",
    )
    distance_to_station_m: Optional[int] = Field(
        default=None,
        ge=0,
        description="역까지 거리 (미터)",
    )
    fee_info: Optional[str] = Field(
        default=None,
        max_length=500,
        description="주차 요금 정보",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="생성 시각",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="최종 수정 시각",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "station_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "반월당역 환승주차장",
                "address": "대구광역시 중구 동성로2가 123",
                "latitude": 35.8580,
                "longitude": 128.5980,
                "distance_to_station_m": 150,
                "fee_info": "1시간 1,000원, 추가 10분당 500원",
            }
        }

    @classmethod
    def from_postgis(cls, data: dict) -> "ParkingLot":
        """
        PostGIS 쿼리 결과에서 ParkingLot 엔티티 생성
        ST_X(), ST_Y() 함수로 추출된 좌표를 latitude, longitude에 매핑
        """
        return cls(
            id=data.get("id"),
            station_id=data.get("station_id"),
            name=data.get("name"),
            address=data.get("address"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            distance_to_station_m=data.get("distance_to_station_m"),
            fee_info=data.get("fee_info"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
