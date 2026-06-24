# app/api/v1/logistics.py
from datetime import datetime, timedelta
import json
import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.logistics import logistics as logistics_crud
from app.crud.order import order_crud
from app.schemas.logistics import LogisticsResponse, SimulateLogisticsRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.models.logistics import LogisticsStatus

router = APIRouter(tags=["logistics"])

# 物流状态流转顺序
STATUS_FLOW = [
    LogisticsStatus.PENDING,
    LogisticsStatus.SHIPPED,
    LogisticsStatus.IN_TRANSIT,
    LogisticsStatus.DELIVERING,
    LogisticsStatus.DELIVERED,
]

# 物流事件模板
EVENT_TEMPLATES = {
    LogisticsStatus.SHIPPED: [
        {"description": "包裹已揽收", "location": "发货仓库"},
    ],
    LogisticsStatus.IN_TRANSIT: [
        {"description": "已到达XX中转站", "location": "中转中心"},
    ],
    LogisticsStatus.DELIVERING: [
        {"description": "正在派送中", "location": "本地配送站"},
    ],
    LogisticsStatus.DELIVERED: [
        {"description": "已签收", "location": "收件地址"},
    ],
}


@router.get("/order/{order_id}", response_model=LogisticsResponse)
async def get_logistics(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取订单的物流信息
    - 订单必须属于当前用户
    """
    # 验证订单属于当前用户
    order = await order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Order does not belong to current user"
        )

    logistics = await logistics_crud.get_tracking_by_order(db, order_id=order_id)
    if not logistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics not found for this order"
        )

    # 解析 events JSON
    events = []
    if logistics.events:
        try:
            raw_events = json.loads(logistics.events)
            for e in raw_events:
                events.append({
                    "time": e.get("time", ""),
                    "description": e.get("description", ""),
                    "location": e.get("location"),
                })
        except (json.JSONDecodeError, TypeError):
            pass

    # 构建返回数据
    return LogisticsResponse(
        id=logistics.id,
        order_id=logistics.order_id,
        tracking_number=logistics.tracking_number,
        carrier=logistics.carrier,
        status=logistics.status,
        events=events,
        estimated_delivery=logistics.estimated_delivery,
        created_at=logistics.created_at,
        updated_at=logistics.updated_at,
    )


@router.post("/order/{order_id}/simulate", response_model=LogisticsResponse)
async def simulate_logistics(
    order_id: int,
    sim_in: SimulateLogisticsRequest = SimulateLogisticsRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    模拟创建物流追踪
    - 订单必须属于当前用户
    - 如果已存在物流则返回现有记录
    """
    # 验证订单属于当前用户
    order = await order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Order does not belong to current user"
        )

    # 检查是否已有物流
    existing = await logistics_crud.get_tracking_by_order(db, order_id=order_id)
    if existing:
        return await _build_logistics_response(existing)

    # 创建初始物流追踪
    now = datetime.now()
    initial_event = {
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "订单已创建，等待发货",
        "location": None,
    }

    tracking = await logistics_crud.create(
        db,
        obj_in={
            "order_id": order_id,
            "tracking_number": sim_in.tracking_number,
            "carrier": sim_in.carrier,
            "status": LogisticsStatus.PENDING,
            "events": json.dumps([initial_event], ensure_ascii=False),
            "estimated_delivery": now + timedelta(days=random.randint(3, 7)),
        },
    )

    return await _build_logistics_response(tracking)


@router.post("/order/{order_id}/advance", response_model=LogisticsResponse)
async def advance_logistics(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    推进物流状态到下一步
    - 订单必须属于当前用户
    - 按 PENDING -> SHIPPED -> IN_TRANSIT -> DELIVERING -> DELIVERED 顺序推进
    """
    # 验证订单属于当前用户
    order = await order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Order does not belong to current user"
        )

    tracking = await logistics_crud.get_tracking_by_order(db, order_id=order_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics not found. Please simulate first."
        )

    # 确定当前状态在流转顺序中的位置
    current_status = tracking.status
    try:
        current_idx = STATUS_FLOW.index(current_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown logistics status: {current_status}"
        )

    # 检查是否已经是最后一步
    if current_idx >= len(STATUS_FLOW) - 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logistics already at final status (delivered)"
        )

    # 推进到下一步
    next_status = STATUS_FLOW[current_idx + 1]

    # 解析已有事件
    events_list = []
    if tracking.events:
        try:
            events_list = json.loads(tracking.events)
        except (json.JSONDecodeError, TypeError):
            events_list = []

    # 添加新事件
    now = datetime.now()
    template_events = EVENT_TEMPLATES.get(next_status, [])
    for te in template_events:
        events_list.append({
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "description": te["description"],
            "location": te.get("location"),
        })

    # 更新物流记录
    tracking.status = next_status
    tracking.events = json.dumps(events_list, ensure_ascii=False)
    await db.commit()
    await db.refresh(tracking)

    return await _build_logistics_response(tracking)


async def _build_logistics_response(tracking) -> LogisticsResponse:
    """构建物流响应"""
    events = []
    if tracking.events:
        try:
            raw_events = json.loads(tracking.events)
            for e in raw_events:
                events.append({
                    "time": e.get("time", ""),
                    "description": e.get("description", ""),
                    "location": e.get("location"),
                })
        except (json.JSONDecodeError, TypeError):
            pass

    return LogisticsResponse(
        id=tracking.id,
        order_id=tracking.order_id,
        tracking_number=tracking.tracking_number,
        carrier=tracking.carrier,
        status=tracking.status,
        events=events,
        estimated_delivery=tracking.estimated_delivery,
        created_at=tracking.created_at,
        updated_at=tracking.updated_at,
    )
