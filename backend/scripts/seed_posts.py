import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Post, Restaurant


JSON_PATH = Path("data/sample_posts.json")


def empty_to_none(value: object) -> str | None:
    if value is None or value == "":
        return None

    return str(value)


def to_datetime(value: object) -> datetime:
    if value is None or value == "":
        return datetime.utcnow()

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return datetime.utcnow()


def seed_posts() -> None:
    Base.metadata.create_all(bind=engine)

    if not JSON_PATH.exists():
        raise FileNotFoundError(
            f"JSON 파일이 없습니다: {JSON_PATH}"
        )

    with JSON_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError(
            "게시글 JSON의 최상위 데이터는 배열이어야 합니다."
        )

    db = SessionLocal()

    try:
        inserted_count = 0
        skipped_count = 0

        for item in raw_data:
            restaurant_id = empty_to_none(
                item.get("restaurant_id")
            )

            title = empty_to_none(
                item.get("title")
            )

            content = empty_to_none(
                item.get("content")
            )

            password = empty_to_none(
                item.get("password")
            )

            if not title or not content or not password:
                print(
                    "필수 값이 없어 건너뜁니다:",
                    item,
                )

                skipped_count += 1
                continue

            # 음식점이 연결된 게시글이라면
            # 실제 restaurants 테이블에 존재하는지 확인
            if restaurant_id is not None:
                restaurant = db.get(
                    Restaurant,
                    restaurant_id,
                )

                if restaurant is None:
                    print(
                        "존재하지 않는 음식점 ID라 "
                        f"건너뜁니다: {restaurant_id}"
                    )

                    skipped_count += 1
                    continue

            # 같은 음식점 + 같은 제목의 게시글 중복 방지
            existing_post = db.scalar(
                select(Post).where(
                    Post.restaurant_id
                    == restaurant_id,
                    Post.title
                    == title,
                )
            )

            if existing_post is not None:
                skipped_count += 1
                continue

            post = Post(
                restaurant_id=restaurant_id,
                title=title,
                content=content,
                password=password,
                created_at=to_datetime(
                    item.get("created_at")
                ),
                updated_at=to_datetime(
                    item.get("updated_at")
                ),
            )

            db.add(post)
            inserted_count += 1

        db.commit()

        print(
            f"JSON 전체 데이터: "
            f"{len(raw_data)}건"
        )

        print(
            f"신규 삽입: "
            f"{inserted_count}건"
        )

        print(
            f"중복 또는 제외: "
            f"{skipped_count}건"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_posts()