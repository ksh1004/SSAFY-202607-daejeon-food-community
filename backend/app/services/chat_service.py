from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Post, Restaurant


MAX_RESTAURANTS = 3
MAX_POSTS = 2
MAX_POST_CONTENT = 250


def search_restaurants(
    db: Session,
    keyword: str,
    limit: int = MAX_RESTAURANTS,
) -> list[dict]:
    """
    음식점명 또는 주소를 기준으로 음식점을 검색합니다.

    우선순위:
    1. 검색 조건 일치
    2. LocalHub 관련 게시글이 있는 음식점 우선
    3. 관련 게시글 수가 많은 음식점 우선
    4. 음식점명 가나다순
    """

    pattern = f"%{keyword.strip()}%"

    post_count = func.count(Post.id).label("post_count")

    rows = db.execute(
        select(
            Restaurant,
            post_count,
        )
        .outerjoin(
            Post,
            Post.restaurant_id == Restaurant.content_id,
        )
        .where(
            or_(
                Restaurant.title.ilike(pattern),
                Restaurant.addr1.ilike(pattern),
                Restaurant.addr2.ilike(pattern),
            )
        )
        .group_by(Restaurant.content_id)
        .order_by(
            post_count.desc(),
            Restaurant.title.asc(),
        )
        .limit(limit)
    ).all()

    return [
        {
            "content_id": restaurant.content_id,
            "title": restaurant.title,
            "address": restaurant.addr1,
            "post_count": post_count_value,
        }
        for restaurant, post_count_value in rows
    ]


def search_posts(
    db: Session,
    keyword: str,
    limit: int = MAX_POSTS,
) -> list[dict]:
    pattern = f"%{keyword.strip()}%"

    rows = db.execute(
        select(
            Post,
            Restaurant.title.label("restaurant_title"),
        )
        .outerjoin(
            Restaurant,
            Post.restaurant_id == Restaurant.content_id,
        )
        .where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Restaurant.title.ilike(pattern),
            )
        )
        .order_by(Post.created_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "id": post.id,
            "restaurant_id": post.restaurant_id,
            "restaurant_title": restaurant_title,
            "title": post.title,
            "content": post.content[:MAX_POST_CONTENT],
        }
        for post, restaurant_title in rows
    ]


def search_restaurant_with_posts(
    db: Session,
    keyword: str,
) -> dict:
    restaurants = search_restaurants(
        db=db,
        keyword=keyword,
        limit=MAX_RESTAURANTS,
    )

    results = []

    for restaurant in restaurants:
        posts = db.scalars(
            select(Post)
            .where(
                Post.restaurant_id
                == restaurant["content_id"]
            )
            .order_by(Post.created_at.desc())
            .limit(MAX_POSTS)
        ).all()

        results.append(
            {
                "restaurant": {
                    "content_id": restaurant["content_id"],
                    "title": restaurant["title"],
                    "address": restaurant["address"],
                    "post_count": restaurant["post_count"],
                },
                "posts": [
                    {
                        "id": post.id,
                        "title": post.title,
                        "content": post.content[:MAX_POST_CONTENT],
                    }
                    for post in posts
                ],
            }
        )

    return {
        "results": results,
    }