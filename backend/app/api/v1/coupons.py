# app/api/v1/coupons.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.database import get_db
from app.crud.coupon import coupon as coupon_crud
from app.schemas.coupon import (
    CouponResponse,
    ClaimCouponRequest,
    UserCouponResponse,
    ApplyCouponRequest,
    ApplyCouponResult,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.models.coupon import CouponType

router = APIRouter(tags=["coupons"])


@router.get("/available", response_model=list[CouponResponse])
async def get_available_coupons(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取当前可领取的优惠券列表（分页）
    """
    coupons, total = await coupon_crud.get_available_coupons(
        db, page=page, size=size
    )
    return coupons


@router.get("/mine", response_model=list[UserCouponResponse])
async def get_my_coupons(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户已领取的优惠券
    """
    user_coupons, total = await coupon_crud.get_user_coupons(
        db, user_id=current_user.id, page=1, size=100
    )
    return user_coupons


@router.post("/claim", response_model=UserCouponResponse, status_code=status.HTTP_201_CREATED)
async def claim_coupon(
    claim_in: ClaimCouponRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    通过优惠券码领取优惠券
    """
    try:
        user_coupon = await coupon_crud.claim_coupon(
            db, user_id=current_user.id, code=claim_in.code
        )
        return user_coupon
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/apply", response_model=ApplyCouponResult)
async def apply_coupon(
    apply_in: ApplyCouponRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    计算优惠券折扣
    - FIXED: 直接减免优惠金额
    - PERCENT: 按百分比减免
    """
    coupon = await coupon_crud.get_coupon_by_code(db, code=apply_in.coupon_code)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="优惠券不存在"
        )

    # 检查是否在有效期内
    today = date.today()
    if today < coupon.start_date or today > coupon.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已过期或尚未生效"
        )

    if not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠券已失效"
        )

    # 检查是否满足最低金额
    if apply_in.order_amount < coupon.min_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单金额需满 {coupon.min_amount} 元才能使用该优惠券"
        )

    # 计算折扣金额
    value = float(coupon.value)
    if coupon.type == CouponType.FIXED:
        discount_amount = value
    elif coupon.type == CouponType.PERCENT:
        discount_amount = round(apply_in.order_amount * value / 100, 2)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未知的优惠券类型"
        )

    # 折扣不能超过订单金额
    if discount_amount > apply_in.order_amount:
        discount_amount = apply_in.order_amount

    final_amount = round(apply_in.order_amount - discount_amount, 2)

    return ApplyCouponResult(
        coupon_id=coupon.id,
        code=coupon.code,
        name=coupon.name,
        type=coupon.type,
        value=coupon.value,
        discount_amount=discount_amount,
        final_amount=final_amount,
    )
