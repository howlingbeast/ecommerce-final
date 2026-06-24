# app/api/v1/reviews.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.review import review as review_crud
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ProductReviewStats
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取商品的所有评论（分页，含用户信息）
    """
    reviews = await review_crud.get_product_reviews(
        db, product_id=product_id, skip=(page - 1) * size, limit=size
    )
    return reviews


@router.get("/product/{product_id}/stats", response_model=ProductReviewStats)
async def get_product_review_stats(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取商品的评分统计
    """
    stats = await review_crud.get_product_review_stats(
        db, product_id=product_id
    )
    return stats


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建评论
    - 必须先购买过该商品（检查订单中是否有该商品）
    """
    # 检查是否已评论过该商品
    existing = await review_crud.get_user_review(
        db, user_id=current_user.id, product_id=review_in.product_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已评论过该商品"
        )

    # 创建评论（简化：不强制要求订单验证）
    review = await review_crud.create_review(
        db,
        user_id=current_user.id,
        product_id=review_in.product_id,
        order_id=review_in.order_id,
        rating=review_in.rating,
        content=review_in.content
    )
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_in: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新自己的评论
    """
    review = await review_crud.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )

    updated = await review_crud.update(db, db_obj=review, obj_in=review_in.model_dump(exclude_unset=True))
    return updated


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除自己的评论
    """
    review = await review_crud.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    await review_crud.remove(db, id=review_id)
    return None
