# app/models/logistics.py
import enum
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LogisticsStatus(str, enum.Enum):
    PENDING = "pending"           # 待发货
    SHIPPED = "shipped"           # 已发货
    IN_TRANSIT = "in_transit"     # 运输中
    DELIVERING = "delivering"     # 派送中
    DELIVERED = "delivered"       # 已签收
    EXCEPTION = "exception"       # 异常


class LogisticsTracking(Base):
    """订单物流追踪"""
    __tablename__ = "logistics_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="物流单号")
    carrier: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="快递公司")
    status: Mapped[LogisticsStatus] = mapped_column(Enum(LogisticsStatus), default=LogisticsStatus.PENDING, nullable=False)
    events: Mapped[str | None] = mapped_column(Text, nullable=True, comment="物流事件(JSON数组)")
    estimated_delivery: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, comment="预计送达时间")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    order: Mapped["Order"] = relationship("Order", back_populates="logistics")
