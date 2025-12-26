"""
SQLModel Trip Repository Implementation

SQLModel Session을 사용한 Trip 데이터 접근 구현
"""

from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from src.domain.entities.trip import Trip, TripStatus
from src.domain.repositories.trip_repository import ITripRepository


class SQLModelTripRepository(ITripRepository):
    """
    SQLModel을 사용한 Trip Repository 구현
    Session을 통해 직접 DB 쿼리 실행
    """

    def __init__(self, session: Session):
        """
        SQLModel Session을 주입받아 초기화
        """
        self.session = session

    async def create(self, trip: Trip) -> Trip:
        """
        새로운 여행 생성
        """
        self.session.add(trip)
        self.session.commit()
        self.session.refresh(trip)
        return trip

    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """
        ID로 특정 여행 조회
        """
        statement = select(Trip).where(Trip.id == trip_id)
        return self.session.exec(statement).first()

    async def get_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        사용자 ID로 여행 목록 조회
        상태별 필터링 및 페이지네이션 지원
        """
        statement = select(Trip).where(Trip.user_id == user_id)

        if status is not None:
            statement = statement.where(Trip.status == status.value)

        statement = statement.order_by(Trip.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    async def get_active_trip(self, user_id: UUID) -> Optional[Trip]:
        """
        사용자의 활성 여행 조회 (DRIVING 또는 TRANSFERRED)
        """
        statement = (
            select(Trip)
            .where(Trip.user_id == user_id)
            .where(
                Trip.status.in_(
                    [TripStatus.DRIVING.value, TripStatus.TRANSFERRED.value]
                )
            )
            .order_by(Trip.created_at.desc())
            .limit(1)
        )
        return self.session.exec(statement).first()

    async def update(self, trip: Trip) -> Trip:
        """
        여행 정보 업데이트
        """
        self.session.add(trip)
        self.session.commit()
        self.session.refresh(trip)
        return trip

    async def count_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
    ) -> int:
        """
        사용자의 여행 개수 조회
        """
        statement = select(Trip).where(Trip.user_id == user_id)

        if status is not None:
            statement = statement.where(Trip.status == status.value)

        results = self.session.exec(statement).all()
        return len(results)

    async def get_by_status(
        self,
        status: TripStatus,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        특정 상태의 여행 목록 조회 (관리자용)
        최신순으로 정렬하여 반환
        """
        statement = (
            select(Trip)
            .where(Trip.status == status.value)
            .order_by(Trip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    async def count_by_status(self, status: TripStatus) -> int:
        """
        특정 상태의 여행 개수 조회 (관리자용)
        """
        statement = select(Trip).where(Trip.status == status.value)
        results = self.session.exec(statement).all()
        return len(results)

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        전체 여행 목록 조회 (관리자용)
        최신순으로 정렬하여 반환
        """
        statement = select(Trip).order_by(Trip.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    async def count_all(self) -> int:
        """
        전체 여행 개수 조회 (관리자용)
        """
        statement = select(Trip)
        results = self.session.exec(statement).all()
        return len(results)
