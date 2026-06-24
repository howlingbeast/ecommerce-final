# app/models/review.py
from sqlalchemy import String, Integer, Text, SmallInteger, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Review(Base):
    """商品评论与评分"""
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="评分 1-5")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="评论内容")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    user: Mapped["User"] = relationship("User")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
