# app/schemas/order.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.product import ProductOut

# ========== 订单项 ==========
class OrderItemOut(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: int
    price: float
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True

class UserBrief(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# ========== 订单 ==========
class OrderOut(BaseModel):
    id: int
    order_number: str
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []
    user: Optional[UserBrief] = None

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    items: list[OrderOut]
    total: int

class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=5, max_length=500, description="收货地址")
    coupon_code: Optional[str] = Field(None, description="优惠券码（可选）")

class OrderDiscountInfo(BaseModel):
    coupon_code: str
    coupon_name: str
    discount_amount: float

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="新状态: pending/paid/shipped/completed/cancelled")
