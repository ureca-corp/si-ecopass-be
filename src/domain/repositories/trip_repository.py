"""
Trip Repository Interface

여행 데이터 접근을 위한 레포지토리 인터페이스 (계약)
구현 세부사항은 인프라 계층에서 정의
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.trip import Trip, TripStatus


class ITripRepository(ABC):
    """
    Trip 레포지토리 인터페이스
    데이터 접근 계약을 정의하고 인프라 계층에서 구현
    """

    @abstractmethod
    async def create(self, trip: Trip) -> Trip:
        """
        새로운 여행 생성
        생성된 Trip 엔티티 반환
        """
        pass

    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """
        ID로 특정 여행 조회
        존재하지 않으면 None 반환
        """
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        사용자 ID로 여행 목록 조회
        선택적으로 상태별 필터링 및 페이지네이션 지원
        """
        pass

    @abstractmethod
    async def get_active_trip(self, user_id: UUID) -> Optional[Trip]:
        """
        사용자의 활성 여행 조회 (DRIVING 또는 TRANSFERRED)
        활성 여행이 없으면 None 반환
        """
        pass

    @abstractmethod
    async def update(self, trip: Trip) -> Trip:
        """
        여행 정보 업데이트
        업데이트된 Trip 엔티티 반환
        """
        pass

    @abstractmethod
    async def count_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
    ) -> int:
        """
        사용자의 여행 개수 조회
        선택적으로 상태별 필터링 지원
        """
        pass

    @abstractmethod
    async def get_by_status(
        self,
        status: TripStatus,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        특정 상태의 여행 목록 조회 (관리자용)
        페이지네이션 지원
        """
        pass

    @abstractmethod
    async def count_by_status(self, status: TripStatus) -> int:
        """
        특정 상태의 여행 개수 조회 (관리자용)
        페이지네이션의 total_count 계산에 사용
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        전체 여행 목록 조회 (관리자용)
        페이지네이션 지원
        """
        pass

    @abstractmethod
    async def count_all(self) -> int:
        """
        전체 여행 개수 조회 (관리자용)
        페이지네이션의 total_count 계산에 사용
        """
        pass

    @abstractmethod
    async def get_with_filters(
        self,
        status: Optional[TripStatus] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        필터를 적용하여 여행 목록 조회 (관리자용)
        상태, 사용자, 날짜 범위로 필터링 지원
        """
        pass

    @abstractmethod
    async def count_with_filters(
        self,
        status: Optional[TripStatus] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        """
        필터를 적용하여 여행 개수 조회 (관리자용)
        페이지네이션의 total_count 계산에 사용
        """
        pass

    @abstractmethod
    async def count_approved_today(self) -> int:
        """
        오늘 승인된 여정 개수 조회 (관리자 대시보드용)
        KST(Asia/Seoul) 기준으로 오늘 승인된 여정만 카운트

        NOTE: approved_at 필드가 없어 updated_at을 사용하므로
        승인 후 다른 업데이트가 있으면 부정확할 수 있음
        향후 approved_at 필드 추가 권장
        """
        pass
