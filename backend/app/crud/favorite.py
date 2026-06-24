# app/crud/favorite.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.favorite import Favorite


class CRUDFavorite(CRUDBase[Favorite]):
    async def get_by_user_and_product(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> Optional[Favorite]:
        """查询用户对某商品的收藏记录"""
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_favorites(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Favorite]:
        """获取用户的收藏列表（分页，含商品信息）"""
        result = await db.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(selectinload(Favorite.product))
            .offset(skip)
            .limit(limit)
            .order_by(Favorite.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_user_favorites(
        self, db: AsyncSession, *, user_id: int
    ) -> int:
        """统计用户的收藏总数"""
        result = await db.execute(
            select(func.count(Favorite.id))
            .where(Favorite.user_id == user_id)
        )
        return result.scalar() or 0

    async def add_favorite(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> Favorite:
        """添加收藏"""
        fav = Favorite(user_id=user_id, product_id=product_id)
        db.add(fav)
        await db.commit()
        await db.refresh(fav)
        return fav

    async def remove_favorite(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> bool:
        """取消收藏，返回是否成功删除"""
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        fav = result.scalar_one_or_none()
        if fav:
            await db.delete(fav)
            await db.commit()
            return True
        return False

    async def is_favorited(
        self, db: AsyncSession, *, user_id: int, product_id: int
    ) -> bool:
        """检查用户是否已收藏某商品"""
        result = await db.execute(
            select(Favorite.id).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        return result.scalar_one_or_none() is not None


# 单例实例
favorite = CRUDFavorite(Favorite)
