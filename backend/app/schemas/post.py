from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    restaurant_id: str | None = None
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    content: str = Field(
        min_length=1,
        max_length=5000,
    )
    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PostUpdate(BaseModel):
    restaurant_id: str | None = None
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    content: str = Field(
        min_length=1,
        max_length=5000,
    )
    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PasswordRequest(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PostResponse(BaseModel):
    id: int
    restaurant_id: str | None
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PostDetailResponse(PostResponse):
    restaurant_title: str | None


class PostListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[PostDetailResponse]