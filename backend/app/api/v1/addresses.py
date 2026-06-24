# app/api/v1/addresses.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.address import address as address_crud
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["addresses"])


@router.get("/", response_model=list[AddressResponse])
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的所有地址
    """
    addresses = await address_crud.get_user_addresses(
        db, user_id=current_user.id
    )
    return addresses


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_in: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新地址
    - 最多 10 个地址
    """
    # 检查地址数量限制
    current_count = await address_crud.count_user_addresses(
        db, user_id=current_user.id
    )
    if current_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 10 addresses reached"
        )

    address = await address_crud.create_address(
        db, user_id=current_user.id, obj_in=address_in.model_dump()
    )
    return address


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新地址
    """
    updated = await address_crud.update_address(
        db, address_id=address_id, user_id=current_user.id, obj_in=address_in.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return updated


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除地址
    """
    address = await address_crud.get(db, id=address_id)
    if not address or address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    await address_crud.remove(db, id=address_id)
    return None


@router.put("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    设置默认地址
    """
    updated = await address_crud.set_default_address(
        db, address_id=address_id, user_id=current_user.id
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return updated
