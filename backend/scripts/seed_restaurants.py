import json
from pathlib import Path

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Restaurant

JSON_PATH = Path("data/대전_충청권_음식점.json")


def empty_to_none(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


def to_float(value: object) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def seed_restaurants() -> None:
    Base.metadata.create_all(bind=engine)

    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON 파일이 없습니다: {JSON_PATH}")

    with JSON_PATH.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    items = raw_data.get("items", [])
    if not isinstance(items, list):
        raise ValueError("JSON의 items 필드는 배열이어야 합니다.")

    db = SessionLocal()

    try:
        existing_ids = set(
            db.scalars(select(Restaurant.content_id)).all()
        )

        inserted_count = 0
        skipped_count = 0

        for item in items:
            content_id = empty_to_none(item.get("contentid"))

            if not content_id or content_id in existing_ids:
                skipped_count += 1
                continue

            restaurant = Restaurant(
                content_id=content_id,
                title=empty_to_none(item.get("title")) or "이름 없음",
                addr1=empty_to_none(item.get("addr1")),
                addr2=empty_to_none(item.get("addr2")),
                mapx=to_float(item.get("mapx")),
                mapy=to_float(item.get("mapy")),
                l_dong_regn_cd=empty_to_none(item.get("lDongRegnCd")),
                l_dong_signgu_cd=empty_to_none(item.get("lDongSignguCd")),
                firstimage=empty_to_none(item.get("firstimage")),
                firstimage2=empty_to_none(item.get("firstimage2")),
            )

            db.add(restaurant)
            existing_ids.add(content_id)
            inserted_count += 1

        db.commit()

        print(f"JSON 전체 데이터: {len(items)}건")
        print(f"신규 삽입: {inserted_count}건")
        print(f"중복 또는 제외: {skipped_count}건")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_restaurants()
