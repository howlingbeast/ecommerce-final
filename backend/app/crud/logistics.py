# app/crud/logistics.py
import json
import random
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.crud.base import CRUDBase
from app.models.logistics import LogisticsTracking, LogisticsStatus


class CRUDLogistics(CRUDBase[LogisticsTracking]):
    async def get_tracking_by_order(
        self, db: AsyncSession, *, order_id: int
    ) -> Optional[LogisticsTracking]:
        """根据订单ID获取物流追踪信息"""
        result = await db.execute(
            select(LogisticsTracking).where(
                LogisticsTracking.order_id == order_id
            )
        )
        return result.scalar_one_or_none()

    async def create_tracking(
        self,
        db: AsyncSession,
        *,
        order_id: int,
        tracking_number: Optional[str] = None,
        carrier: Optional[str] = None
    ) -> LogisticsTracking:
        """创建物流追踪记录"""
        tracking = LogisticsTracking(
            order_id=order_id,
            tracking_number=tracking_number,
            carrier=carrier,
            status=LogisticsStatus.PENDING
        )
        db.add(tracking)
        await db.commit()
        await db.refresh(tracking)
        return tracking

    async def simulate_update(
        self, db: AsyncSession, *, tracking_id: int
    ) -> Optional[LogisticsTracking]:
        """
        模拟物流状态更新（用于测试/演示）
        随机推进状态并生成物流事件
        """
        result = await db.execute(
            select(LogisticsTracking).where(
                LogisticsTracking.id == tracking_id
            )
        )
        tracking = result.scalar_one_or_none()
        if not tracking:
            return None

        # 定义状态流转顺序
        status_flow = [
            LogisticsStatus.PENDING,
            LogisticsStatus.SHIPPED,
            LogisticsStatus.IN_TRANSIT,
            LogisticsStatus.DELIVERING,
            LogisticsStatus.DELIVERED
        ]

        current_idx = status_flow.index(tracking.status) if tracking.status in status_flow else -1

        # 如果已签收或异常，不再更新
        if tracking.status == LogisticsStatus.DELIVERED or \
           tracking.status == LogisticsStatus.EXCEPTION:
            return tracking

        # 随机前进 1~2 个状态
        steps = random.randint(1, min(2, len(status_flow) - current_idx - 1))
        new_idx = current_idx + steps
        new_status = status_flow[new_idx]

        # 生成物流事件
        now = datetime.now()
        events = []
        existing_events = []
        if tracking.events:
            try:
                existing_events = json.loads(tracking.events)
                if isinstance(existing_events, list):
                    events = existing_events
            except (json.JSONDecodeError, TypeError):
                events = []

        # 为每个跳过的状态生成事件
        for i in range(current_idx + 1, new_idx + 1):
            event_time = now - timedelta(hours=random.randint(1, 48))
            events.append({
                "status": status_flow[i].value,
                "time": event_time.isoformat(),
                "description": self._get_status_description(status_flow[i])
            })

        tracking.status = new_status
        tracking.events = json.dumps(events, ensure_ascii=False)

        # 如果已签收，设置预计送达时间为当前时间
        if new_status == LogisticsStatus.DELIVERED:
            tracking.estimated_delivery = now

        await db.commit()
        await db.refresh(tracking)
        return tracking

    async def update_events(
        self, db: AsyncSession, *, tracking_id: int, events_json: str
    ) -> Optional[LogisticsTracking]:
        """更新物流事件（JSON字符串）"""
        result = await db.execute(
            select(LogisticsTracking).where(
                LogisticsTracking.id == tracking_id
            )
        )
        tracking = result.scalar_one_or_none()
        if not tracking:
            return None

        tracking.events = events_json
        await db.commit()
        await db.refresh(tracking)
        return tracking

    def _get_status_description(self, status: LogisticsStatus) -> str:
        """获取状态描述文案"""
        descriptions = {
            LogisticsStatus.PENDING: "订单已创建，待发货",
            LogisticsStatus.SHIPPED: "包裹已出库，等待快递公司揽收",
            LogisticsStatus.IN_TRANSIT: "包裹正在运输中",
            LogisticsStatus.DELIVERING: "快递员正在派送中，请保持电话畅通",
            LogisticsStatus.DELIVERED: "包裹已签收",
            LogisticsStatus.EXCEPTION: "物流异常，请联系客服",
        }
        return descriptions.get(status, "物流状态更新")


# 单例实例
logistics = CRUDLogistics(LogisticsTracking)
