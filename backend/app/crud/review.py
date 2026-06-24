# app/crud/review.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.review import Review
from app.models.user import User


class CRUDReview(CRUDBase[Review]):
    async def get_product_reviews(
        self,
        db: AsyncSession,
        *,
        product_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> list[Review]:
        """获取商品评论列表（含用户信息）"""
        result = await db.execute(
            select(Review)
            .where(Review.product_id == product_id)
            .options(selectinload(Review.user))
            .offset(skip)
            .limit(limit)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_product_review_stats(
        self, db: AsyncSession, *, product_id: int
    ) -> dict:
        """获取商品评论统计信息"""
        # 总评论数和平均评分
        stats_result = await db.execute(
            select(
                func.count(Review.id).label("total_reviews"),
                func.coalesce(func.avg(Review.rating), 0).label("avg_rating")
            ).where(Review.product_id == product_id)
        )
        stats_row = stats_result.one()

        # 评分分布（1-5星各有多少条）
        dist_result = await db.execute(
            select(Review.rating, func.count(Review.id))
            .where(Review.product_id == product_id)
            .group_by(Review.rating)
        )
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for row in dist_result.all():
            rating_distribution[row[0]] = row[1]

        return {
            "total_reviews": stats_row.total_reviews or 0,
            "avg_rating": round(float(stats_row.avg_rating), 2) if stats_row.avg_rating else 0.0,
            "rating_distribution": rating_distribution
        }

    async def create_review(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        product_id: int,
        order_id: Optional[int],
        rating: int,
        content: Optional[str] = None
    ) -> Review:
        """创建评论"""
        review = Review(
            user_id=user_id,
            product_id=product_id,
            order_id=order_id,
            rating=rating,
            content=content
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        # 预加载用户信息
        await db.refresh(review, attribute_names=["user"])
        return review

    async def get_user_review(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> Optional[Review]:
        """获取用户对某商品的评论"""
        result = await db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id
            )
        )
        return result.scalar_one_or_none()

    async def has_reviewed(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> bool:
        """检查用户是否已评论某商品"""
        result = await db.execute(
            select(Review.id).where(
                Review.user_id == user_id,
                Review.product_id == product_id
            )
        )
        return result.scalar_one_or_none() is not None


# 单例实例
review = CRUDReview(Review)
