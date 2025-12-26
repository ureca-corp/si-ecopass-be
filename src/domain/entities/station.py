"""
Station Domain Entity

대구 지하철 역 정보를 나타내는 도메인 엔티티
PostGIS geography(Point) 타입의 좌표 데이터를 latitude/longitude로 변환
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """
    현재 UTC 시간을 timezone 정보와 함께 반환
    모든 timestamp 필드의 기본값으로 사용
    """
    return datetime.now(timezone.utc)


class Station(SQLModel, table=True):
    """
    대구 지하철 역 엔티티 (DB 테이블)

    PostGIS geography(Point) 타입으로 저장된 좌표를 latitude/longitude로 변환하여 제공
    """

    __tablename__ = "stations"  # Supabase 테이블명

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="역 고유 식별자",
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="역명 (예: 반월당역)",
    )
    line_number: int = Field(
        ge=1,
        le=3,
        description="노선 번호 (1, 2, 3호선)",
    )
    # PostGIS geography(Point) 타입 - DB에만 존재
    location: Any = Field(
        default=None,
        sa_column=Column(Geography(geometry_type='POINT', srid=4326)),
        description="GPS 좌표 (PostGIS geography)",
        exclude=True,  # API 응답에서 제외
    )
    # 좌표는 latitude, longitude 필드로 별도 제공 (computed)
    latitude: Optional[float] = Field(
        default=None,
        description="위도 (PostGIS ST_Y 함수로 추출)",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="경도 (PostGIS ST_X 함수로 추출)",
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
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "반월당역",
                "line_number": 1,
                "latitude": 35.8575,
                "longitude": 128.5974,
            }
        }

    @classmethod
    def from_postgis(cls, data: dict) -> "Station":
        """
        PostGIS 쿼리 결과에서 Station 엔티티 생성
        ST_X(), ST_Y() 함수로 추출된 좌표를 latitude, longitude에 매핑
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            line_number=data.get("line_number"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
