# app/api/v1/favorites.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import traceback

from app.core.database import get_db
from app.crud.favorite import favorite as favorite_crud
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteWithProduct
from app.api.deps import get_current_user
from app.models.user import User
from app.models.favorite import Favorite

router = APIRouter(tags=["favorites"])


@router.get("/")
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取当前用户的收藏列表（分页，含商品信息）
    """
    try:
        items = await favorite_crud.get_user_favorites(
            db, user_id=current_user.id, skip=(page - 1) * size, limit=size
        )
        total = await favorite_crud.count_user_favorites(
            db, user_id=current_user.id
        )
        # 手动序列化
        result_items = []
        for f in items:
            p = f.product
            result_items.append({
                "id": f.id, "user_id": f.user_id, "product_id": f.product_id,
                "created_at": str(f.created_at),
                "product": {
                    "id": p.id, "name": p.name, "price": float(p.price),
                    "image_url": p.image_url, "category": p.category,
                    "is_active": p.is_active
                } if p else None
            })
        return {"items": result_items, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    添加商品到收藏
    """
    # 检查是否已收藏
    existing = await favorite_crud.get_by_user_and_product(
        db, user_id=current_user.id, product_id=product_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该商品已在收藏列表中"
        )

    fav = Favorite(user_id=current_user.id, product_id=product_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除收藏
    """
    removed = await favorite_crud.remove_favorite(
        db, user_id=current_user.id, product_id=product_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    return None


@router.get("/check/{product_id}", response_model=dict)
async def check_favorite(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    检查商品是否已被当前用户收藏
    """
    existing = await favorite_crud.get_by_user_and_product(
        db, user_id=current_user.id, product_id=product_id
    )
    return {"is_favorited": existing is not None}
