"""
Distance Calculation Utilities

여정 거리 계산 및 포인트 산정을 위한 유틸리티 함수
Haversine 공식을 사용하여 두 좌표 간 거리를 계산
"""

import logging
from typing import Optional

from geopy.distance import geodesic

logger = logging.getLogger(__name__)

# 포인트 계산 기준: 500m당 1포인트
METERS_PER_POINT = 500


def calculate_distance_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    두 좌표 간 거리 계산 (미터 단위)
    Haversine 공식 기반 geodesic 거리 사용

    Args:
        lat1: 출발지 위도
        lon1: 출발지 경도
        lat2: 도착지 위도
        lon2: 도착지 경도

    Returns:
        거리 (미터 단위)

    Raises:
        ValueError: 좌표 값이 유효하지 않은 경우
    """
    # 좌표 유효성 검증
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError(f"위도 값은 -90 ~ 90 범위여야 합니다: lat1={lat1}, lat2={lat2}")

    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError(f"경도 값은 -180 ~ 180 범위여야 합니다: lon1={lon1}, lon2={lon2}")

    # 좌표 형식: (위도, 경도)
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)

    # geodesic 거리 계산 (기본 단위: 킬로미터)
    distance_km = geodesic(point1, point2).kilometers

    # 미터로 변환
    distance_meters = distance_km * 1000

    return distance_meters


def calculate_trip_total_distance(
    start_lat: float,
    start_lon: float,
    transfer_lat: Optional[float],
    transfer_lon: Optional[float],
    arrival_lat: Optional[float],
    arrival_lon: Optional[float],
) -> float:
    """
    여정 전체 거리 계산 (출발 → 환승 → 도착)

    Args:
        start_lat: 출발지 위도
        start_lon: 출발지 경도
        transfer_lat: 환승지 위도 (선택)
        transfer_lon: 환승지 경도 (선택)
        arrival_lat: 도착지 위도 (선택)
        arrival_lon: 도착지 경도 (선택)

    Returns:
        총 거리 (미터 단위)

    Notes:
        - 환승지가 없으면 출발 → 도착 직선 거리
        - 도착지가 없으면 0 반환
    """
    total_distance = 0.0

    # 도착 위치가 없으면 거리 계산 불가
    if arrival_lat is None or arrival_lon is None:
        logger.warning("도착 위치가 없어 거리를 계산할 수 없습니다")
        return 0.0

    # 환승 위치가 있는 경우: 출발 → 환승 → 도착
    if transfer_lat is not None and transfer_lon is not None:
        # 출발 → 환승 거리
        start_to_transfer = calculate_distance_meters(
            start_lat,
            start_lon,
            transfer_lat,
            transfer_lon,
        )

        # 환승 → 도착 거리
        transfer_to_arrival = calculate_distance_meters(
            transfer_lat,
            transfer_lon,
            arrival_lat,
            arrival_lon,
        )

        total_distance = start_to_transfer + transfer_to_arrival

        logger.debug(
            f"여정 거리 계산: "
            f"출발→환승={start_to_transfer:.2f}m, "
            f"환승→도착={transfer_to_arrival:.2f}m, "
            f"총={total_distance:.2f}m"
        )

    # 환승 위치가 없는 경우: 출발 → 도착 직선 거리
    else:
        total_distance = calculate_distance_meters(
            start_lat,
            start_lon,
            arrival_lat,
            arrival_lon,
        )

        logger.debug(f"여정 거리 계산 (환승 없음): 출발→도착={total_distance:.2f}m")

    return total_distance


def calculate_points_from_distance(distance_meters: float) -> int:
    """
    거리 기반 포인트 계산
    500m당 1포인트 (소수점 버림)

    Args:
        distance_meters: 거리 (미터 단위)

    Returns:
        포인트 (정수)

    Examples:
        >>> calculate_points_from_distance(3500)
        7
        >>> calculate_points_from_distance(499)
        0
        >>> calculate_points_from_distance(500)
        1
    """
    if distance_meters < 0:
        raise ValueError(f"거리는 0 이상이어야 합니다: {distance_meters}")

    points = int(distance_meters / METERS_PER_POINT)

    logger.debug(f"포인트 계산: {distance_meters:.2f}m → {points}포인트")

    return points


def validate_points_consistency(
    calculated_points: int,
    client_points: int,
    tolerance: int = 1,
) -> tuple[bool, Optional[str]]:
    """
    서버 계산 포인트와 클라이언트 포인트 일치성 검증

    Args:
        calculated_points: 서버에서 계산한 포인트
        client_points: 클라이언트가 보낸 포인트
        tolerance: 허용 오차 (기본 1포인트)

    Returns:
        (일치 여부, 경고 메시지)

    Notes:
        - GPS 오차로 인해 1포인트 이내 차이는 허용
        - 1포인트 초과 차이는 부정 가능성으로 간주
    """
    difference = abs(calculated_points - client_points)

    if difference <= tolerance:
        # 허용 범위 내
        return True, None
    else:
        # 허용 범위 초과
        warning_message = (
            f"포인트 불일치 감지: "
            f"서버={calculated_points}, 클라이언트={client_points}, "
            f"차이={difference} (허용 오차={tolerance})"
        )
        return False, warning_message
