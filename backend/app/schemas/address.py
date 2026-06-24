# app/schemas/address.py
from datetime import datetime
from pydantic import BaseModel, field_validator
import re


class AddressBase(BaseModel):
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1\d{10}$", v):
            raise ValueError("手机号格式不正确")
        return v


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    detail: str | None = None
    is_default: bool | None = None


class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
