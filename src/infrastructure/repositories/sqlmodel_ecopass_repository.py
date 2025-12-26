"""
SQLModel EcoPass Repository Implementation

SQLModel Session을 사용한 EcoPass 데이터 접근 구현
"""

from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from src.domain.entities.ecopass import EcoPass
from src.domain.repositories.ecopass_repository import IEcoPassRepository


class SQLModelEcoPassRepository(IEcoPassRepository):
    """
    SQLModel을 사용한 EcoPass Repository 구현
    Session을 통해 직접 DB 쿼리 실행
    """

    def __init__(self, session: Session):
        """
        SQLModel Session을 주입받아 초기화
        """
        self.session = session

    async def create(self, ecopass: EcoPass) -> EcoPass:
        """
        새로운 EcoPass 생성
        """
        self.session.add(ecopass)
        self.session.commit()
        self.session.refresh(ecopass)
        return ecopass

    async def get_by_id(self, ecopass_id: UUID) -> Optional[EcoPass]:
        """
        ID로 특정 EcoPass 조회
        """
        statement = select(EcoPass).where(EcoPass.id == ecopass_id)
        return self.session.exec(statement).first()

    async def get_by_user_id(self, user_id: str) -> list[EcoPass]:
        """
        사용자 ID로 모든 EcoPass 목록 조회
        """
        statement = select(EcoPass).where(EcoPass.user_id == user_id)
        return list(self.session.exec(statement).all())

    async def update(self, ecopass: EcoPass) -> EcoPass:
        """
        EcoPass 정보 업데이트
        """
        self.session.add(ecopass)
        self.session.commit()
        self.session.refresh(ecopass)
        return ecopass

    async def delete(self, ecopass_id: UUID) -> bool:
        """
        EcoPass 삭제
        삭제 성공 시 True, 존재하지 않으면 False 반환
        """
        statement = select(EcoPass).where(EcoPass.id == ecopass_id)
        ecopass = self.session.exec(statement).first()

        if ecopass is None:
            return False

        self.session.delete(ecopass)
        self.session.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[EcoPass]:
        """
        전체 EcoPass 목록 조회 (페이지네이션)
        """
        statement = select(EcoPass).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
