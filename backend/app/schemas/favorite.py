# app/schemas/favorite.py
from datetime import datetime
from pydantic import BaseModel


class FavoriteBase(BaseModel):
    product_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteProductInfo(BaseModel):
    """收藏时返回的商品简略信息"""
    id: int
    name: str
    price: float
    image_url: str | None = None
    category: str | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class FavoriteWithProduct(FavoriteResponse):
    """含商品详情的收藏响应"""
    product: FavoriteProductInfo | None = None
