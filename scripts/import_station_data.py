"""
역 및 주차장 데이터 임포트 스크립트
Excel 파일을 읽어 Kakao Maps API로 지오코딩 후 Supabase에 삽입
"""

import os
import re
import time
import json
import pandas as pd
import requests
from typing import Optional, Tuple

# ============================================================================
# 설정
# ============================================================================

KAKAO_API_KEY = os.environ.get("KAKAO_API_KEY", "2249828b1d89ea36ac582812f308e713")
STATIONS_FILE = "stations.xlsx"
PARKINGLOTS_FILE = "parkinglots.xlsx"
OUTPUT_DIR = "scripts/output"

# 노선명 → 숫자 매핑
LINE_MAPPING = {
    "대구1호선": 1,
    "대구2호선": 2,
    "대구3호선": 3,
    "대경선": 4,
}


# ============================================================================
# 지오코딩 함수
# ============================================================================

def geocode_keyword(query: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Kakao 키워드 검색으로 위도/경도 조회
    역 이름이나 장소명으로 검색할 때 사용
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("documents"):
            doc = data["documents"][0]
            return float(doc["y"]), float(doc["x"])  # latitude, longitude
    except Exception as e:
        print(f"  ⚠️ Geocoding error for '{query}': {e}")

    return None, None


def geocode_address(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Kakao 주소 검색으로 위도/경도 조회
    정확한 주소가 있을 때 사용
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("documents"):
            doc = data["documents"][0]
            # address 타입에 따라 좌표 위치가 다름
            if "address" in doc:
                return float(doc["y"]), float(doc["x"])
            elif "road_address" in doc and doc["road_address"]:
                return float(doc["y"]), float(doc["x"])
    except Exception as e:
        print(f"  ⚠️ Address geocoding error for '{address}': {e}")

    return None, None


# ============================================================================
# 데이터 정규화 함수
# ============================================================================

def normalize_distance(distance_str: str) -> Optional[int]:
    """
    거리 문자열을 숫자(미터)로 변환
    예: "310m" → 310, "150" → 150, "정보없음" → None
    """
    if pd.isna(distance_str) or distance_str == "정보없음":
        return None

    # 'm' 제거하고 숫자만 추출
    match = re.search(r"(\d+)", str(distance_str))
    if match:
        return int(match.group(1))
    return None


def normalize_fee_info(fee_str: str) -> Optional[str]:
    """
    요금 정보 정규화
    """
    if pd.isna(fee_str) or fee_str == "정보없음":
        return None
    return str(fee_str)


# ============================================================================
# 역 데이터 처리
# ============================================================================

def process_stations() -> list[dict]:
    """
    stations.xlsx 파일을 읽어 지오코딩 후 데이터 반환
    """
    print("\n📍 역(Stations) 데이터 처리 중...")

    # 첫 행도 데이터이므로 header=None
    df = pd.read_excel(STATIONS_FILE, header=None, names=["name", "line", "address"])

    stations = []
    total = len(df)

    for idx, row in df.iterrows():
        name = row["name"]
        line = row["line"]
        address = row["address"]

        # 노선 번호 변환
        line_number = LINE_MAPPING.get(line)
        if line_number is None:
            print(f"  ⚠️ Unknown line: {line} for station {name}")
            continue

        # 지오코딩 - 역 이름으로 검색 (더 정확함)
        search_query = f"대구 {name}"
        lat, lng = geocode_keyword(search_query)

        # 키워드 검색 실패시 주소로 시도
        if lat is None:
            lat, lng = geocode_address(address)

        if lat is None:
            print(f"  ❌ Failed to geocode: {name} ({address})")
            # 기본값으로 대구 중심 좌표 사용 (나중에 수정 필요)
            lat, lng = 35.8714, 128.6014

        stations.append({
            "name": name,
            "line_number": line_number,
            "latitude": lat,
            "longitude": lng,
            "address": address,  # 참고용
        })

        print(f"  [{idx+1}/{total}] {name} ({line}) → ({lat:.6f}, {lng:.6f})")

        # API 속도 제한 방지 (초당 10회 제한)
        time.sleep(0.1)

    print(f"\n✅ 총 {len(stations)}개 역 처리 완료")
    return stations


# ============================================================================
# 주차장 데이터 처리
# ============================================================================

def process_parking_lots(station_name_to_id: dict[str, str]) -> list[dict]:
    """
    parkinglots.xlsx 파일을 읽어 지오코딩 후 데이터 반환
    station_name_to_id: 역 이름 → station_id 매핑
    """
    print("\n🅿️ 주차장(Parking Lots) 데이터 처리 중...")

    df = pd.read_excel(PARKINGLOTS_FILE)

    parking_lots = []
    total = len(df)

    for idx, row in df.iterrows():
        name = row["주차장명"]
        station_name = row["가까운 역"]
        fee_info = normalize_fee_info(row["이용요금"])
        distance = normalize_distance(row["거리"])
        address = row["주소"]
        operating_hours = row["운영시간"] if pd.notna(row["운영시간"]) else None

        # station_id 찾기
        station_id = station_name_to_id.get(station_name)
        if station_id is None:
            # 역 이름에 '역' 접미사 처리
            alt_name = station_name.replace("역", "") + "역" if "역" not in station_name else station_name
            station_id = station_name_to_id.get(alt_name)

        if station_id is None:
            print(f"  ⚠️ Station not found: {station_name} for parking lot {name}")
            continue

        # 지오코딩 - 주차장 이름으로 검색
        search_query = f"대구 {name}"
        lat, lng = geocode_keyword(search_query)

        # 키워드 검색 실패시 주소로 시도
        if lat is None and pd.notna(address):
            lat, lng = geocode_address(str(address))

        if lat is None:
            print(f"  ❌ Failed to geocode: {name} ({address})")
            lat, lng = 35.8714, 128.6014  # 기본값

        # 요금 정보 조합
        full_fee_info = fee_info
        if operating_hours and operating_hours != "정보없음":
            full_fee_info = f"{fee_info or '정보없음'} (운영: {operating_hours})"

        parking_lots.append({
            "station_id": station_id,  # 나중에 실제 ID로 대체
            "station_name": station_name,  # 참조용
            "name": name,
            "address": str(address) if pd.notna(address) else "",
            "latitude": lat,
            "longitude": lng,
            "distance_to_station_m": distance,
            "fee_info": full_fee_info,
        })

        print(f"  [{idx+1}/{total}] {name} (역: {station_name}) → ({lat:.6f}, {lng:.6f})")

        time.sleep(0.1)

    print(f"\n✅ 총 {len(parking_lots)}개 주차장 처리 완료")
    return parking_lots


# ============================================================================
# SQL 생성
# ============================================================================

def generate_stations_sql(stations: list[dict]) -> str:
    """
    역 데이터를 SQL INSERT 문으로 변환
    """
    lines = [
        "-- 역(Stations) 데이터 삽입",
        "-- Generated by import_station_data.py",
        "",
        "INSERT INTO public.stations (name, line_number, location)",
        "VALUES"
    ]

    values = []
    for s in stations:
        # PostGIS geography 포맷: ST_MakePoint(longitude, latitude)
        value = f"  ('{s['name']}', {s['line_number']}, ST_MakePoint({s['longitude']}, {s['latitude']})::geography)"
        values.append(value)

    lines.append(",\n".join(values) + ";")

    return "\n".join(lines)


def generate_parking_lots_sql(parking_lots: list[dict]) -> str:
    """
    주차장 데이터를 SQL INSERT 문으로 변환
    station_id는 서브쿼리로 처리
    """
    lines = [
        "-- 주차장(Parking Lots) 데이터 삽입",
        "-- Generated by import_station_data.py",
        "",
    ]

    for p in parking_lots:
        # station_id를 서브쿼리로 조회
        name_escaped = p['name'].replace("'", "''")
        address_escaped = p['address'].replace("'", "''") if p['address'] else ""
        fee_info_escaped = p['fee_info'].replace("'", "''") if p['fee_info'] else ""
        station_name = p['station_name'].replace("'", "''")

        distance = p['distance_to_station_m']
        distance_sql = str(distance) if distance is not None else "NULL"
        fee_sql = f"'{fee_info_escaped}'" if p['fee_info'] else "NULL"

        sql = f"""INSERT INTO public.parking_lots (station_id, name, address, location, distance_to_station_m, fee_info)
SELECT id, '{name_escaped}', '{address_escaped}', ST_MakePoint({p['longitude']}, {p['latitude']})::geography, {distance_sql}, {fee_sql}
FROM public.stations
WHERE name = '{station_name}'
LIMIT 1;
"""
        lines.append(sql)

    return "\n".join(lines)


# ============================================================================
# 메인 함수
# ============================================================================

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚇 SI-EcoPass 역/주차장 데이터 임포트")
    print("=" * 60)

    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 역 데이터 처리
    stations = process_stations()

    # 2. SQL 생성 (역)
    stations_sql = generate_stations_sql(stations)
    stations_sql_path = os.path.join(OUTPUT_DIR, "01_insert_stations.sql")
    with open(stations_sql_path, "w", encoding="utf-8") as f:
        f.write(stations_sql)
    print(f"\n📄 역 SQL 저장: {stations_sql_path}")

    # 3. 역 이름 → ID 매핑 (임시, 실제로는 DB에서 조회해야 함)
    # 여기서는 SQL 생성용으로 역 이름만 사용
    station_name_to_id = {s["name"]: s["name"] for s in stations}

    # 4. 주차장 데이터 처리
    parking_lots = process_parking_lots(station_name_to_id)

    # 5. SQL 생성 (주차장)
    parking_lots_sql = generate_parking_lots_sql(parking_lots)
    parking_lots_sql_path = os.path.join(OUTPUT_DIR, "02_insert_parking_lots.sql")
    with open(parking_lots_sql_path, "w", encoding="utf-8") as f:
        f.write(parking_lots_sql)
    print(f"📄 주차장 SQL 저장: {parking_lots_sql_path}")

    # 6. JSON 백업
    json_backup = {
        "stations": stations,
        "parking_lots": parking_lots,
    }
    json_path = os.path.join(OUTPUT_DIR, "data_backup.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_backup, f, ensure_ascii=False, indent=2)
    print(f"📄 JSON 백업 저장: {json_path}")

    print("\n" + "=" * 60)
    print("✅ 데이터 처리 완료!")
    print(f"   - 역: {len(stations)}개")
    print(f"   - 주차장: {len(parking_lots)}개")
    print("=" * 60)
    print("\n다음 단계:")
    print(f"  1. {stations_sql_path} 검토")
    print(f"  2. {parking_lots_sql_path} 검토")
    print("  3. Supabase에 SQL 실행")


if __name__ == "__main__":
    main()
