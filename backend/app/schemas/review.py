# app/schemas/review.py
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5, description="评分 1-5")
    content: str | None = None


class ReviewCreate(ReviewBase):
    order_id: int | None = None


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    content: str | None = None


class ReviewUserInfo(BaseModel):
    id: int
    username: str
    full_name: str | None = None

    model_config = {"from_attributes": True}


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    order_id: int | None = None
    created_at: datetime
    user: ReviewUserInfo | None = None

    model_config = {"from_attributes": True}


class ProductReviewStats(BaseModel):
    """商品评分统计"""
    total_reviews: int = 0
    avg_rating: float = 0.0
    rating_distribution: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
