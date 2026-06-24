# app/schemas/coupon.py
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.coupon import CouponType


class CouponCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    type: CouponType
    value: float
    min_amount: float = 0
    start_date: date
    end_date: date
    usage_limit: int = 0
    is_active: bool = True


class CouponUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    value: float | None = None
    min_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    usage_limit: int | None = None
    is_active: bool | None = None


class CouponResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    type: CouponType
    value: float
    min_amount: float
    start_date: date
    end_date: date
    usage_limit: int
    used_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ClaimCouponRequest(BaseModel):
    code: str


class UserCouponResponse(BaseModel):
    id: int
    user_id: int
    coupon_id: int
    is_used: bool
    used_at: datetime | None = None
    order_id: int | None = None
    created_at: datetime
    coupon: CouponResponse | None = None

    model_config = {"from_attributes": True}


class ApplyCouponRequest(BaseModel):
    coupon_code: str
    order_amount: float = Field(gt=0)

    model_config = {"from_attributes": True}


class ApplyCouponResult(BaseModel):
    coupon_id: int
    code: str
    name: str
    type: CouponType
    value: float
    discount_amount: float
    final_amount: float
