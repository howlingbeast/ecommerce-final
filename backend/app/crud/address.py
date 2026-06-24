# app/crud/address.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.crud.base import CRUDBase
from app.models.address import Address


class CRUDAddress(CRUDBase[Address]):
    async def get_user_addresses(
        self, db: AsyncSession, *, user_id: int
    ) -> list[Address]:
        """获取用户的所有收货地址"""
        result = await db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.id.desc())
        )
        return list(result.scalars().all())

    async def get_default_address(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Address]:
        """获取用户的默认收货地址"""
        result = await db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.is_default == True
            )
        )
        return result.scalar_one_or_none()

    async def count_user_addresses(
        self, db: AsyncSession, *, user_id: int
    ) -> int:
        """统计用户地址数量"""
        result = await db.execute(
            select(func.count(Address.id)).where(Address.user_id == user_id)
        )
        return result.scalar() or 0

    async def create_address(
        self, db: AsyncSession, *, user_id: int, obj_in: dict
    ) -> Address:
        """创建收货地址"""
        address = Address(user_id=user_id, **obj_in)
        db.add(address)
        await db.commit()
        await db.refresh(address)
        return address

    async def update_address(
        self, db: AsyncSession, *, address_id: int, user_id: int, obj_in: dict
    ) -> Optional[Address]:
        """更新收货地址"""
        result = await db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()
        if not address:
            return None

        # 如果设置为默认地址，先取消其他默认
        if obj_in.get("is_default") and not address.is_default:
            await self._unset_default(db, user_id)

        for field, value in obj_in.items():
            setattr(address, field, value)

        await db.commit()
        await db.refresh(address)
        return address

    async def delete_address(
        self, db: AsyncSession, *, address_id: int, user_id: int
    ) -> bool:
        """删除收货地址"""
        result = await db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()
        if not address:
            return False

        await db.delete(address)
        await db.commit()
        return True

    async def set_default_address(
        self, db: AsyncSession, *, address_id: int, user_id: int
    ) -> Optional[Address]:
        """设置默认收货地址"""
        result = await db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()
        if not address:
            return None

        # 取消所有默认地址，再设置当前地址为默认
        await self._unset_default(db, user_id)
        address.is_default = True
        await db.commit()
        await db.refresh(address)
        return address

    async def _unset_default(self, db: AsyncSession, user_id: int) -> None:
        """将用户所有地址的 is_default 设为 False"""
        result = await db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.is_default == True
            )
        )
        for addr in result.scalars().all():
            addr.is_default = False
        await db.commit()


# 单例实例
address = CRUDAddress(Address)
