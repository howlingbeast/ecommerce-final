# app/schemas/logistics.py
from datetime import datetime
from pydantic import BaseModel
from app.models.logistics import LogisticsStatus


class LogisticsEvent(BaseModel):
    """物流事件"""
    time: str
    description: str
    location: str | None = None


class LogisticsResponse(BaseModel):
    id: int
    order_id: int
    tracking_number: str | None = None
    carrier: str | None = None
    status: LogisticsStatus
    events: list[LogisticsEvent] = []
    estimated_delivery: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SimulateLogisticsRequest(BaseModel):
    """模拟物流更新请求"""
    tracking_number: str = "SF"  # 默认顺丰
    carrier: str = "顺丰速运"
