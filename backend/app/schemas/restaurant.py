from pydantic import BaseModel, ConfigDict


class RestaurantResponse(BaseModel):
    content_id: str
    title: str
    addr1: str | None
    addr2: str | None
    mapx: float | None
    mapy: float | None
    l_dong_regn_cd: str | None
    l_dong_signgu_cd: str | None
    firstimage: str | None
    firstimage2: str | None

    model_config = ConfigDict(from_attributes=True)


class RestaurantListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[RestaurantResponse]