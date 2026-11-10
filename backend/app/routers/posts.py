from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post, Restaurant
from app.schemas.post import (
    PasswordRequest,
    PostCreate,
    PostDetailResponse,
    PostListResponse,
    PostResponse,
    PostUpdate,
)

router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)


def get_post_or_404(
    db: Session,
    post_id: int,
) -> Post:
    post = db.get(Post, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다.",
        )

    return post


def validate_restaurant(
    db: Session,
    restaurant_id: str | None,
) -> Restaurant | None:
    if restaurant_id is None:
        return None

    restaurant = db.get(
        Restaurant,
        restaurant_id,
    )

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="음식점 정보를 찾을 수 없습니다.",
        )

    return restaurant


@router.get(
    "",
    response_model=PostListResponse,
)
def get_posts(
    keyword: str | None = Query(
        default=None,
        max_length=100,
    ),
    restaurant_id: str | None = None,
    page: int = Query(
        default=1,
        ge=1,
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> PostListResponse:
    conditions = []

    if keyword:
        pattern = f"%{keyword.strip()}%"

        conditions.append(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Restaurant.title.ilike(pattern),
            )
        )

    if restaurant_id is not None:
        conditions.append(
            Post.restaurant_id == restaurant_id
        )

    base_query = (
        select(
            Post,
            Restaurant.title.label(
                "restaurant_title"
            ),
        )
        .outerjoin(
            Restaurant,
            Post.restaurant_id
            == Restaurant.content_id,
        )
    )

    count_query = (
        select(
            func.count(Post.id)
        )
        .select_from(Post)
        .outerjoin(
            Restaurant,
            Post.restaurant_id
            == Restaurant.content_id,
        )
    )

    if conditions:
        base_query = base_query.where(
            *conditions
        )

        count_query = count_query.where(
            *conditions
        )

    total = db.scalar(
        count_query
    ) or 0

    rows = db.execute(
        base_query
        .order_by(
            Post.created_at.desc()
        )
        .offset(
            (page - 1) * size
        )
        .limit(size)
    ).all()

    items = [
        PostDetailResponse(
            id=post.id,
            restaurant_id=post.restaurant_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at,
            restaurant_title=restaurant_title,
        )
        for post, restaurant_title in rows
    ]

    return PostListResponse(
        total=total,
        page=page,
        size=size,
        items=items,
    )


@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
) -> PostDetailResponse:
    row = db.execute(
        select(
            Post,
            Restaurant.title.label(
                "restaurant_title"
            ),
        )
        .outerjoin(
            Restaurant,
            Post.restaurant_id
            == Restaurant.content_id,
        )
        .where(
            Post.id == post_id
        )
    ).first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다.",
        )

    post, restaurant_title = row

    return PostDetailResponse(
        id=post.id,
        restaurant_id=post.restaurant_id,
        restaurant_title=restaurant_title,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    request: PostCreate,
    db: Session = Depends(get_db),
) -> Post:
    validate_restaurant(
        db,
        request.restaurant_id,
    )

    post = Post(
        restaurant_id=request.restaurant_id,
        title=request.title,
        content=request.content,
        password=request.password,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
) -> Post:
    post = get_post_or_404(
        db,
        post_id,
    )

    if post.password != request.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다.",
        )

    validate_restaurant(
        db,
        request.restaurant_id,
    )

    post.restaurant_id = request.restaurant_id
    post.title = request.title
    post.content = request.content

    db.commit()
    db.refresh(post)

    return post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    post_id: int,
    request: PasswordRequest,
    db: Session = Depends(get_db),
) -> Response:
    post = get_post_or_404(
        db,
        post_id,
    )

    if post.password != request.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다.",
        )

    db.delete(post)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )