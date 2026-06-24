# app/models/__init__.py
# 确保导入所有模型类
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.favorite import Favorite
from app.models.address import Address
from app.models.review import Review
from app.models.coupon import Coupon, UserCoupon
from app.models.logistics import LogisticsTracking

# 列出所有模型，方便 Base.metadata 识别
__all__ = ["User", "Product", "CartItem", "Order", "OrderItem",
           "Favorite", "Address", "Review", "Coupon", "UserCoupon",
           "LogisticsTracking"]
