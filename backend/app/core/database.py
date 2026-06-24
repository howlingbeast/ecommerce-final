# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from app.core.config import settings
from typing import AsyncGenerator, Any
import os

_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

Base: DeclarativeMeta = declarative_base()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Initialize database - create tables and seed data if empty"""
    from app.models import user
    from app.models.product import Product
    from app.models.coupon import Coupon
    from decimal import Decimal
    from datetime import date, datetime
    from sqlalchemy import select, func
    from app.models.user import User
    from app.core.security import get_password_hash

    async with engine.begin() as conn:
        print("Tables to create:", list(Base.metadata.tables.keys()))
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")

    # Check if data already exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(Product))
        product_count = result.scalar() or 0

        if product_count == 0:
            print("Seeding initial data...")

            # 1. Create admin user
            result = await db.execute(select(func.count()).select_from(User))
            user_count = result.scalar() or 0
            if user_count == 0:
                admin = User(
                    username="admin", email="admin@example.com",
                    hashed_password=get_password_hash("Admin123456"),
                    full_name="管理员", is_active=True, is_superuser=True
                )
                db.add(admin)
                test = User(
                    username="testuser", email="test@example.com",
                    hashed_password=get_password_hash("Test123456"),
                    full_name="测试用户", is_active=True, is_superuser=False
                )
                db.add(test)

            # 2. Create products
            products_data = [
                {"name": "iPhone 15 Pro Max", "description": "苹果最新旗舰手机，A17 Pro芯片，钛金属设计", "price": 9999.00, "stock": 50, "category": "手机数码", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACjElEQVR4nO3S1a1QURQA0VMPzykMdx5aDu7uXha3iD0hIStZBczHrJN3/8C49c8L+C8Zi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi8Q6uvMbxhmLxDbWLxi3jm7/gnHbWD9hnLFIrKNbP2CcsUisw1vfYdw6vPkdxm1jfYNxxiKxDm98hXHGIrGN9QXGrcPjLzBuHRx/hnHGIrEOrn+CccYisY31Ecatg2sfYdw21gcYZywSa//qexhnLBLbWO9g3Nq/8g7GbWO9hXHGIrH2L7+BccYisfYuv4Zxa+/Saxi3jfUKxhmLxNq7+BLGGYvENtYLGGcsEmv3wnMYZywS21jPYNzaPf8Mxm1jPYVxxiKxds89gXHGIrF2zj2GcWvn7GMYt431CMYZi8TaOfMQxhmLxDbWAxi3dk4/gHHrxOn7MM5YJNaJU/dg3F/o46RHLWM0uAAAAABJRU5ErkJggg=="},
                {"name": "MacBook Pro 14", "description": "M3 Pro芯片，14英寸Liquid Retina XDR显示屏", "price": 14999.00, "stock": 30, "category": "电脑办公", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACXElEQVR4nO3S16nYUBQAwduCJJf0cnQVzjmXbxVxFoMZmAL2Y9eLPy9h3PrnBfyXjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEXCWCSMRcJYJIxFwlgkjEViHb+fYZyxSBiLxDp+PcM4Y5E4x3qCcev4+QTjjEXCWCSMRWIdPx5hnLFIGIvEOr4/wjhjkTjHeoBx6/j2AOOMRcJYJIxFYu1f72GcsUgYi8Tav9zDOGOROMe6g3Fr/3wH44xFwlgkjEVi7Z9uYZyxSBiLxNo/3sI4Y5E4x7qBcWv/cAPjjEXCWCSMRWJt769hnLFIGIvE2t5dwzhjkTjHuoJxa3t7BeOMRcJYJIxFYm1vLmGcsUgYi8TaXl/COGOROMe6gHFre3UB44xFwlgk/gIC0BgGOoB2BwAAAABJRU5ErkJggg=="},
                {"name": "AirPods Pro 2", "description": "自适应降噪，MagSafe充电盒，USB-C接口", "price": 1899.00, "stock": 100, "category": "手机数码", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACoUlEQVR4nO3SZ44WBBRA0bdJhjKUAdyUiBURZQq9WCnWZfkt4t2YmJOcBdwfd15+8g+sm/+8gP8lY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5GYF3f/hnXGIjHP7/4F64xFYp7d+RPWGYvEPL3zB6wzFol5cvt3WGcsEoexPsK6ubj9EdbNxckHWDfnJx9g3WGs97Buzk7ew7o5u/UO1s3prXew7jDWb7DOWCTm8c1fYZ2xSMwPN3+BdcYiMd/f+BnWGYvEPLrxE6wzFon57vqPsM5YJA5jvYV18/D6W1g3D4/fwLr59vgNrDuM9RrWzYPj17BuHlx7Bevmm2uvYN1hrJewzlgk5uurL2CdsUjMV1efwzpjkZgvrzyDdcYiMV9ceQrrjEViPr/8BNYZi8RhrAtYN/cvX8C6uX90Duvms6NzWHcY6wzWzb2jM1g39y6dwrr59NIprDuM9RjW/QsYPVnTtVPUmgAAAABJRU5ErkJggg=="},
                {"name": "小米手环8 Pro", "description": "1.74英寸AMOLED屏幕，独立GPS定位", "price": 399.00, "stock": 200, "category": "智能穿戴", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACp0lEQVR4nO3SWY4VBBQA0bseuvt1PzeozMgko5tRURTFCZxQFF2Mm7gVE3OSs4D6qPnn4/dg3fznBfwvGYuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIuEsUgYi4SxSBiLhLFIGIvE/P30COvm3dMjrJt3T46wbv56coR1xiIxfz4+wjpjkZi3j4+wbt4+uoB188ejC1g3vz+8gHXGIjFvHl7Aunnz4ALWzW8PLmCdsUjMrx+dwzpjkZhf7p/DOmORmJ/vn8O6+eneOawzFol5fe8c1s3ruwdYN6/uHmDdvLpzgHXz450DrDMWifnh9gHWzfe3D7DOWCTmuw/PYJ2xSMy3t85gnbFIzMtbZ7BuXt48g3Xzzc0zWGcsEvP1jVNYNy9unMK6eXH9FNbNV9dPYZ2xSMyX105hnbFIzPNrp7Bunl89gXXzxdUTWDefXzmBdcYiMc+unMC6eXb5BNbNZ5dPYJ2xSMynH1yCdcYiMZ+8fwnW/QvTYXwHCMmJCQAAAABJRU5ErkJggg=="},
                {"name": "Sony WH-1000XM5", "description": "旗舰级降噪头戴耳机，30小时续航", "price": 2499.00, "stock": 80, "category": "手机数码", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACl0lEQVR4nO3SWW4QBBRA0be4lkJHfyiFUijF1SkOOOCAAw6oy3IT74aEnOQs4H7c+e+TT2HdfPACPkrGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGImEsEsYiYSwSxiJhLBLGIjH/XryEdcYiMf9cvIR1xiIx7y/uYN28P7+DdfP3+R2sMxaJ+ev8BawzFon58+wFrDMWifnj7BbWzQcv4KM0785uYd28O72FdfP76XNYZywS89vpc1hnLBLz68kzWGcsEvPLyTNYZywS8/bkBtbN2+MbWDc/H9/AOmORmJ+On8I6Y5GYHx88hXXGIjE/PLiGdcYiMW8eXMO6eXP/GtbN9/efwDpjkZjv7j+BdcYiMd8ePYZ1xiIx3xw9hnXGIjGvj65g3by+dwXr5ut7V7DOWCTmq3uPYJ2xSMyXh49gnbFIzBeHl7DOWCTm1eElrJtXB5ewbj4/eAjrjEViPjt4COv+B6UYqocb0oS7AAAAAElFTkSuQmCC"},
                {"name": "任天堂Switch OLED", "description": "7英寸OLED屏幕，续航约4.5-9小时", "price": 2599.00, "stock": 60, "category": "游戏娱乐", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAACyklEQVR4nO3SVw4QVBQA0bdJegc3JYINEQti/ZMiRSlSlCJFF+NbxJ2YmJOcBczHrPd++gfGrf+8gP8lY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5EwFgljkTAWCWORMBYJY5FY5378G8btsd7BuHXuh3cwbo/1Fsats9+/hXF7rDcwbp397g2M22O9hnHrzLevYdwe6y8Yt8d6BePWmWuvYNw6fe0ljFunv3kJ4/ZYL2DcOn31BYxbp64+h3Hr1NfPYdwe608YZywS6+RXf8C4PdYzGLdOfvkMxu2xnsK4deKLpzBuj/UExq0TV57AuD3WYxi3jn/+GMbtsX6HcXusRzBuHb/8CMatY5cfwrh17LOHMG6P9QDGrWOXHsC4dfTSfRi3jn56H8btsX6DccYisY588iuM22Pdg3HryMf3YNwe6y6MW4c/ugvj9lh3YNw6/OEdGLfHug3j1qGLt2HcHusXGLcOXbwF49ahC7dg3Dp44SaMWwc/uAnj9lg3YNw6eP4GjFsHzl+HcevA+9dh3B7rZxj3LxMoP9cpKhoyAAAAAElFTkSuQmCC"},
                {"name": "戴尔XPS 15", "description": "15.6英寸OLED屏，i7-13700H，RTX4070", "price": 18999.00, "stock": 25, "category": "电脑办公", "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAIAAAAiOjnJAAADJklEQVR4nO3S2U0QUBgF4amF1YYUF1xQixHFBcUd0VK9Rfw3JzmZ5CtgHoZ7r/9J44gXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVIl4gSoRL1Al4gWqRLxAlYgXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVIl4gSoRL1Al4gWqRLxAlYgXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVIl4gSoRL1Al4gWqRLxAlYgXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVIl4gSoRL1Al4gWqRLxAlYgXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVIl4gSoRL1Al4gWqRLxAlYgXqBLxAlUiXqBKxAtUiXiBKhEvUCXiBapEvECViBeoEvECVSJeoErEC1SJeIEqES9QJeIFqkS8QJWIF6gS8QJVIl6gSsQLVInTV3+lcY6lLdZYd9I4x9IWnL68k8atsf5I4xxLW6yxbqVxnF7cSuMcS1twcvFbGudY2oKTF7+kcY6lLRxLW6yxfkrjOHn+Uxq3xvohjXMsbeFY2oLjZ9+lcY6lLdZY36RxjqUtOH76TRq3xvoqjXMsbbHGupHGcXx+I41zLG3B0fkXaZxjaQuOnnyWxjmWtnAsbbHGupbGcfT4Whq3xvokjXMsbeFY2oLDRx+lcY6lLdZYH6RxjqUtOHz4QRq3xnovjXMsbbHGupLGcXh2JY1zLG3Bwdk7aZxjaQsOHryVxjmWtnAsbbHGupTGcXD/Uhq3xnojjXMsbfEf5gve52Wdn64AAAAASUVORK5CYII="},
            ]
            for p in products_data:
                db.add(Product(**p))

            # 3. Create coupons
            today = date.today()
            coupons_data = [
                {"code": "NEW50", "name": "新用户满减券", "description": "新用户专享，满100减50", "type": "fixed", "value": 50.0, "min_amount": 100.0, "start_date": today, "end_date": date(today.year + 1 if today.month == 12 else today.year, (today.month % 12) + 1, today.day)},
                {"code": "SALE20", "name": "全场折扣券", "description": "全场商品8折优惠", "type": "percent", "value": 20.0, "min_amount": 0.0, "start_date": today, "end_date": date(today.year + 1 if today.month == 12 else today.year, (today.month % 12) + 1, today.day)},
                {"code": "VIP100", "name": "VIP满减券", "description": "VIP专享，满500减100", "type": "fixed", "value": 100.0, "min_amount": 500.0, "start_date": today, "end_date": date(today.year + 1 if today.month == 12 else today.year, (today.month % 12) + 1, today.day)},
            ]
            for c in coupons_data:
                db.add(Coupon(**c))

            await db.commit()
            print("Seed data created: admin/testuser accounts, 7 products, 3 coupons")

async def close_db():
    """Close database connections"""
    await engine.dispose()
    print("Database connections closed")
