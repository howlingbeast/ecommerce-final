# app/models/address.py
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Address(Base):
    """用户收货地址"""
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="收货人姓名")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="联系电话")
    province: Mapped[str] = mapped_column(String(50), nullable=False, comment="省份")
    city: Mapped[str] = mapped_column(String(50), nullable=False, comment="城市")
    district: Mapped[str] = mapped_column(String(50), nullable=False, comment="区县")
    detail: Mapped[str] = mapped_column(String(500), nullable=False, comment="详细地址")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否默认地址")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="addresses")
