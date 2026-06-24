# app/crud/coupon.py
from datetime import date, datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.coupon import Coupon, UserCoupon


class CRUDCoupon(CRUDBase[Coupon]):
    # ── 优惠券模板 ──

    async def get_coupon_by_code(
        self, db: AsyncSession, *, code: str
    ) -> Optional[Coupon]:
        """根据优惠码获取优惠券"""
        result = await db.execute(
            select(Coupon).where(Coupon.code == code)
        )
        return result.scalar_one_or_none()

    async def get_available_coupons(
        self, db: AsyncSession, *, page: int = 1, size: int = 20
    ) -> tuple[list[Coupon], int]:
        """分页获取当前可领取的优惠券（未过期且 active）"""
        today = date.today()
        query = select(Coupon).where(
            Coupon.is_active == True,
            Coupon.start_date <= today,
            Coupon.end_date >= today
        )

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        offset = (page - 1) * size
        result = await db.execute(
            query.offset(offset).limit(size).order_by(Coupon.created_at.desc())
        )
        items = list(result.scalars().all())

        return items, total

    async def increment_used_count(
        self, db: AsyncSession, *, coupon_id: int
    ) -> Optional[Coupon]:
        """增加优惠券使用次数"""
        result = await db.execute(
            select(Coupon).where(Coupon.id == coupon_id)
        )
        coupon = result.scalar_one_or_none()
        if coupon:
            coupon.used_count += 1
            await db.commit()
            await db.refresh(coupon)
        return coupon

    # ── 用户优惠券 ──

    async def claim_coupon(
        self, db: AsyncSession, *, user_id: int, code: str
    ) -> UserCoupon:
        """用户领取优惠券"""
        # 查找优惠券模板
        coupon = await self.get_coupon_by_code(db, code=code)
        if not coupon:
            raise ValueError("Coupon not found")
        if not coupon.is_active:
            raise ValueError("Coupon is not active")
        if coupon.end_date < date.today():
            raise ValueError("Coupon has expired")
        if coupon.start_date > date.today():
            raise ValueError("Coupon is not yet available")
        if coupon.usage_limit > 0 and coupon.used_count >= coupon.usage_limit:
            raise ValueError("Coupon usage limit reached")

        # 检查用户是否已领取
        existing = await db.execute(
            select(UserCoupon).where(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon.id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("You have already claimed this coupon")

        # 创建用户优惠券
        user_coupon = UserCoupon(user_id=user_id, coupon_id=coupon.id)
        db.add(user_coupon)
        await db.commit()
        # 用 selectinload 重新查询
        result = await db.execute(
            select(UserCoupon)
            .where(UserCoupon.id == user_coupon.id)
            .options(selectinload(UserCoupon.coupon))
        )
        return result.scalar_one()

    async def get_user_coupons(
        self, db: AsyncSession, *, user_id: int, page: int = 1, size: int = 20
    ) -> tuple[list[UserCoupon], int]:
        """分页获取用户领取的优惠券"""
        query = (
            select(UserCoupon)
            .where(UserCoupon.user_id == user_id)
            .options(selectinload(UserCoupon.coupon))
        )

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        offset = (page - 1) * size
        result = await db.execute(
            query.offset(offset).limit(size).order_by(UserCoupon.created_at.desc())
        )
        items = list(result.scalars().all())

        return items, total

    async def get_usable_user_coupons(
        self, db: AsyncSession, *, user_id: int, amount: float
    ) -> list[UserCoupon]:
        """
        获取用户可用的优惠券（未使用、未过期、满足最低金额条件）
        返回按优惠力度从大到小排序
        """
        today = date.today()
        # 子查询：找出符合条件的优惠券模板
        result = await db.execute(
            select(UserCoupon)
            .join(Coupon, UserCoupon.coupon_id == Coupon.id)
            .where(
                UserCoupon.user_id == user_id,
                UserCoupon.is_used == False,
                Coupon.is_active == True,
                Coupon.start_date <= today,
                Coupon.end_date >= today,
                Coupon.min_amount <= amount
            )
            .order_by(Coupon.value.desc())
        )
        return list(result.scalars().all())

    async def use_coupon(
        self, db: AsyncSession, *, user_coupon_id: int, order_id: int
    ) -> Optional[UserCoupon]:
        """使用优惠券（标记为已使用）"""
        result = await db.execute(
            select(UserCoupon).where(UserCoupon.id == user_coupon_id)
        )
        user_coupon = result.scalar_one_or_none()
        if not user_coupon:
            return None
        if user_coupon.is_used:
            raise ValueError("Coupon has already been used")

        user_coupon.is_used = True
        user_coupon.used_at = datetime.now()
        user_coupon.order_id = order_id
        await db.commit()
        await db.refresh(user_coupon)
        return user_coupon


# 单例实例
coupon = CRUDCoupon(Coupon)
