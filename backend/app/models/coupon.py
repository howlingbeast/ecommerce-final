# app/models/coupon.py
import enum
from sqlalchemy import (
    String, Integer, DECIMAL, Boolean, DateTime, Date, ForeignKey, Enum, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CouponType(str, enum.Enum):
    FIXED = "fixed"       # 固定金额
    PERCENT = "percent"   # 百分比折扣


class Coupon(Base):
    """优惠券模板"""
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="优惠券码")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="优惠券名称")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    type: Mapped[CouponType] = mapped_column(Enum(CouponType), nullable=False, comment="优惠类型")
    value: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="优惠金额/折扣百分比")
    min_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0, comment="最低使用金额")
    start_date: Mapped[Date] = mapped_column(Date, nullable=False, comment="生效日期")
    end_date: Mapped[Date] = mapped_column(Date, nullable=False, comment="失效日期")
    usage_limit: Mapped[int] = mapped_column(Integer, default=0, comment="使用次数上限(0=无限制)")
    used_count: Mapped[int] = mapped_column(Integer, default=0, comment="已使用次数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    user_coupons: Mapped[list["UserCoupon"]] = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")


class UserCoupon(Base):
    """用户领取的优惠券"""
    __tablename__ = "user_coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coupon_id: Mapped[int] = mapped_column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已使用")
    used_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    user: Mapped["User"] = relationship("User")
    coupon: Mapped["Coupon"] = relationship("Coupon", back_populates="user_coupons")
    order: Mapped["Order"] = relationship("Order")
