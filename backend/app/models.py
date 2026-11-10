from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    # 관광공사 음식점 고유 식별자 자체를 PK로 사용
    content_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    addr1: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
        index=True,
    )

    addr2: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    mapx: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    mapy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    l_dong_regn_cd: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    l_dong_signgu_cd: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    firstimage: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    firstimage2: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="restaurant",
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # 음식점을 선택하지 않아도 게시글 작성 가능
    # 값이 있을 경우 restaurants.content_id 참조
    restaurant_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "restaurants.content_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    restaurant: Mapped["Restaurant | None"] = relationship(
        back_populates="posts",
    )