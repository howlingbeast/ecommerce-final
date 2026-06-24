# app/crud/order.py
from decimal import Decimal
from typing import Tuple, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.product import product as product_crud
from app.crud.cart import cart as cart_crud
from app.models.order import Order, OrderItem, OrderStatus
from app.models.coupon import UserCoupon, Coupon, CouponType
from app.schemas.order import OrderCreate

class CRUDOrder(CRUDBase[Order]):

    # ========== 创建订单（支持优惠券）==========
    async def create_order_from_cart(
        self, db: AsyncSession, *, user_id: int, obj_in: OrderCreate
    ) -> Order:
        """从购物车创建订单，支持优惠券抵扣"""
        cart_items = await cart_crud.get_user_cart(db, user_id=user_id)
        if not cart_items:
            raise ValueError("购物车为空，无法创建订单")

        order_items_data = []
        total_amount = Decimal('0.0')
        for item in cart_items:
            product = item.product
            if not product or not product.is_active:
                raise ValueError(f"商品 {product.name if product else '未知'} 已下架或不存在")
            if product.stock < item.quantity:
                raise ValueError(f"商品 {product.name} 库存不足，当前库存: {product.stock}")

            item_price = Decimal(str(product.price))
            item_total = item_price * item.quantity
            total_amount += item_total
            order_items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": float(item_price),  # 存储快照时转为 float（数据库 DECIMAL 列）
            })

        # 优惠券处理
        discount_amount = Decimal('0.0')
        used_user_coupon = None
        if obj_in.coupon_code:
            # 查找用户已领取的优惠券
            result = await db.execute(
                select(UserCoupon)
                .join(Coupon, UserCoupon.coupon_id == Coupon.id)
                .where(
                    UserCoupon.user_id == user_id,
                    UserCoupon.is_used == False,
                    Coupon.code == obj_in.coupon_code,
                    Coupon.is_active == True,
                    Coupon.start_date <= date.today(),
                    Coupon.end_date >= date.today(),
                    Coupon.min_amount <= float(total_amount)
                )
            )
            user_coupon = result.scalar_one_or_none()
            if not user_coupon:
                raise ValueError("优惠券不可用或已使用")

            coupon = await db.get(Coupon, user_coupon.coupon_id)
            value = float(coupon.value)
            if coupon.type == CouponType.FIXED:
                discount_amount = Decimal(str(value))
            elif coupon.type == CouponType.PERCENT:
                discount_amount = Decimal(str(round(float(total_amount) * value / 100, 2)))
            else:
                raise ValueError("未知的优惠券类型")

            if discount_amount > total_amount:
                discount_amount = total_amount

            total_amount -= discount_amount
            used_user_coupon = user_coupon

        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id:04d}"

        order = Order(
            user_id=user_id,
            order_number=order_number,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            shipping_address=obj_in.shipping_address
        )
        db.add(order)
        await db.flush()

        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                price=item_data["price"]
            )
            db.add(order_item)

        for item in cart_items:
            await product_crud.reduce_stock(db, product_id=item.product_id, quantity=item.quantity)

        await cart_crud.clear_cart(db, user_id=user_id)

        # 标记优惠券已使用
        if used_user_coupon:
            used_user_coupon.is_used = True
            used_user_coupon.used_at = datetime.now()
            used_user_coupon.order_id = order.id

        await db.commit()
        # 返回完整订单
        return await self.get_with_items(db, id=order.id)

    # ========== 获取订单（含完整预加载）==========
    async def get_with_items(self, db: AsyncSession, *, id: int) -> Optional[Order]:
        """获取订单（含订单项、商品详情、用户信息）"""
        result = await db.execute(
            select(Order)
            .where(Order.id == id)
            .options(
                selectinload(Order.user),  # 新增：预加载用户
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        return result.scalar_one_or_none()

    # ========== 用户订单列表 ==========
    async def get_user_orders(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[list[Order], int]:
        count_query = select(func.count()).where(Order.user_id == user_id)
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        orders = list(result.scalars().all())
        return orders, total

    # ========== 取消订单（核心修复）==========
    async def cancel_order(self, db: AsyncSession, *, order: Order) -> Order:
        """取消订单：恢复库存，修改状态"""
        if order.status not in (OrderStatus.PENDING, OrderStatus.PAID):
            raise ValueError("只能取消待处理或已支付订单")
        # 恢复库存
        for item in order.items:
            if item.product_id:
                await product_crud.increase_stock(
                    db, product_id=item.product_id, quantity=item.quantity
                )
        order.status = OrderStatus.CANCELLED
        await db.commit()
        # 重新加载带有关联关系的订单（避免懒加载异常）
        return await self.get_with_items(db, id=order.id)

    # ========== 更新订单状态 ==========
    async def update_status(self, db: AsyncSession, *, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        await db.commit()
        # 重新加载带有关联关系的订单
        return await self.get_with_items(db, id=order.id)

    # ========== 管理员订单列表 ==========
    async def get_all_orders(
        self, db: AsyncSession, *, status: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> Tuple[list[Order], int]:
        query = select(Order).options(
            selectinload(Order.user),  # 新增：预加载用户
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        count_query = select(func.count()).select_from(Order)
        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        orders = list(result.scalars().all())
        return orders, total


# 单例实例
order_crud = CRUDOrder(Order)