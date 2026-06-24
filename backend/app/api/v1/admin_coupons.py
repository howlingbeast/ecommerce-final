# app/api/v1/admin_coupons.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.coupon import coupon as coupon_crud
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse
from app.api.deps import get_current_superuser
from app.models.user import User

router = APIRouter(tags=["admin-coupons"])


@router.get("/", response_model=list[CouponResponse])
async def list_coupons_admin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取所有优惠券列表（管理员）
    """
    coupons = await coupon_crud.get_multi(
        db, skip=(page - 1) * size, limit=size
    )
    return coupons


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_in: CouponCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    创建优惠券（管理员）
    """
    # 检查优惠券码是否已存在
    existing = await coupon_crud.get_coupon_by_code(db, code=coupon_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Coupon with code '{coupon_in.code}' already exists"
        )

    coupon = await coupon_crud.create(db, obj_in=coupon_in.model_dump())
    return coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    coupon_in: CouponUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    更新优惠券（管理员）
    """
    coupon = await coupon_crud.get(db, id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    updated = await coupon_crud.update(db, db_obj=coupon, obj_in=coupon_in)
    return updated


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    删除优惠券（管理员）
    """
    coupon = await coupon_crud.get(db, id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    await coupon_crud.remove(db, id=coupon_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
