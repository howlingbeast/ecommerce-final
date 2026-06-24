"""
添加测试商品数据
使用方法：python -m app.scripts.seed_products
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.core.database import engine
from app.crud.product import product as product_crud
from app.schemas.product import ProductCreate


SAMPLE_PRODUCTS = [
    {
        "name": "iPhone 15 Pro Max",
        "description": "苹果最新旗舰手机，A17 Pro芯片，钛金属设计",
        "price": 9999.00,
        "stock": 50,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfkbU8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7miYvmnI3mlbTnoIE8L3RleHQ+PC9zdmc+",
        "category": "手机数码",
        "is_active": True
    },
    {
        "name": "MacBook Pro 14",
        "description": "M3 Pro芯片，14英寸Liquid Retina XDR显示屏",
        "price": 14999.00,
        "stock": 30,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfkrs8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7nlLvnrqHlip/lhazvvIjlt7Tnu4PvvIk8L3RleHQ+PC9zdmc+",
        "category": "电脑办公",
        "is_active": True
    },
    {
        "name": "AirPods Pro 2",
        "description": "主动降噪无线耳机，自适应音频",
        "price": 1899.00,
        "stock": 100,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfj6c8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7lv67pn7PlkqzoiJ08L3RleHQ+PC9zdmc+",
        "category": "影音娱乐",
        "is_active": True
    },
    {
        "name": "小米手环8 Pro",
        "description": "1.74英寸AMOLED大屏，独立GPS",
        "price": 399.00,
        "stock": 200,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfirQ8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7mmZrlhpnnq5LluqY8L3RleHQ+PC9zdmc+",
        "category": "智能穿戴",
        "is_active": True
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "顶级降噪耳机，30小时续航",
        "price": 2499.00,
        "stock": 45,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCf6Yc8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7lv67pn7PlkqzoiJ08L3RleHQ+PC9zdmc+",
        "category": "影音娱乐",
        "is_active": True
    },
    {
        "name": "任天堂Switch OLED",
        "description": "7英寸OLED屏幕，续航增强版",
        "price": 2599.00,
        "stock": 25,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfjq48L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7muLjmiI/lk63niZvvvIhPTERE77yJPC90ZXh0Pjwvc3ZnPg==",
        "category": "游戏娱乐",
        "is_active": True
    },
    {
        "name": "戴尔XPS 15",
        "description": "3.5K OLED触控屏，i9处理器",
        "price": 18999.00,
        "stock": 15,
        "image_url": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgNDAwIDMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGNUY1RjciLz48dGV4dCB4PSIyMDAiIHk9IjE0MCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjAiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMxRDFEMUYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfkrs8L3RleHQ+PHRleHQgeD0iMjAwIiB5PSIxODAiIGZvbnQtZmFtaWx5PSItYXBwbGUtc3lzdGVtLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSIjNkU2RTczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7nlLvnrqHlip/lhazvvIjlt7Tnu4PvvIk8L3RleHQ+PC9zdmc+",
        "category": "电脑办公",
        "is_active": True
    }
]


async def seed_products():
    """添加测试商品"""
    print("🔄 开始添加测试商品...")
    
    async with AsyncSessionLocal() as db:
        created_count = 0
        failed_count = 0
        
        for product_data in SAMPLE_PRODUCTS:
            try:
                # 检查是否已存在
                existing = await product_crud.get_by_name(db, name=product_data["name"])
                if existing:
                    print(f"⚠️ 商品已存在，跳过: {product_data['name']}")
                    continue
                
                # 创建商品
                product_in = ProductCreate(**product_data)
                await product_crud.create(db, obj_in=product_in)
                created_count += 1
                print(f"✅ 创建商品: {product_data['name']} - ¥{product_data['price']}")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ 创建失败 {product_data['name']}: {e}")
        
        print(f"\n📊 商品初始化完成！")
        print(f"   ✅ 成功创建: {created_count} 个")
        print(f"   ❌ 失败: {failed_count} 个")
        print(f"   📦 总计商品数: {created_count + failed_count}")


async def main():
    try:
        await seed_products()
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await engine.dispose()
        print("🔌 数据库连接已关闭")


if __name__ == "__main__":
    # Windows 特定的事件循环设置
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())