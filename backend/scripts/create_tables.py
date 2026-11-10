from app.database import Base, engine
from app.models import Post, Restaurant


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("restaurants, posts 테이블 생성 완료")


if __name__ == "__main__":
    create_tables()
