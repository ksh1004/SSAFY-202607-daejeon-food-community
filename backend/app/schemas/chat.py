from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=300,
    )
    history: list[ChatMessage] = []


class CommunityPostInfo(BaseModel):
    post_id: int
    text: str


class ChatRestaurantInfo(BaseModel):
    content_id: str
    title: str
    address: str | None
    community_post: CommunityPostInfo | None = None


class ChatResponse(BaseModel):
    answer: str
    restaurants: list[ChatRestaurantInfo] = []