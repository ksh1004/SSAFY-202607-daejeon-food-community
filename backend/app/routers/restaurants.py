from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Restaurant
from app.schemas.restaurant import (
    RestaurantListResponse,
    RestaurantResponse,
)

router = APIRouter(
    prefix="/api/restaurants",
    tags=["restaurants"],
)


@router.get("", response_model=RestaurantListResponse)
def get_restaurants(
    keyword: str | None = Query(
        default=None,
        max_length=100,
    ),
    region_code: str | None = Query(
        default=None,
        max_length=10,
    ),
    signgu_code: str | None = Query(
        default=None,
        max_length=10,
    ),
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
) -> RestaurantListResponse:
    conditions = []

    if keyword:
        pattern = f"%{keyword.strip()}%"

        conditions.append(
            or_(
                Restaurant.title.ilike(pattern),
                Restaurant.addr1.ilike(pattern),
                Restaurant.addr2.ilike(pattern),
            )
        )

    if region_code:
        conditions.append(
            Restaurant.l_dong_regn_cd == region_code
        )

    if signgu_code:
        conditions.append(
            Restaurant.l_dong_signgu_cd == signgu_code
        )

    count_query = select(
        func.count(Restaurant.content_id)
    )

    data_query = select(Restaurant)

    if conditions:
        count_query = count_query.where(
            *conditions
        )

        data_query = data_query.where(
            *conditions
        )

    total = db.scalar(
        count_query
    ) or 0

    restaurants = db.scalars(
        data_query
        .order_by(
            Restaurant.title.asc()
        )
        .offset(
            (page - 1) * size
        )
        .limit(size)
    ).all()

    return RestaurantListResponse(
        total=total,
        page=page,
        size=size,
        items=list(restaurants),
    )


@router.get(
    "/{content_id}",
    response_model=RestaurantResponse,
)
def get_restaurant(
    content_id: str,
    db: Session = Depends(get_db),
) -> Restaurant:
    restaurant = db.get(
        Restaurant,
        content_id,
    )

    if restaurant is None:
        raise HTTPException(
            status_code=404,
            detail="음식점 정보를 찾을 수 없습니다.",
        )

    return restaurant