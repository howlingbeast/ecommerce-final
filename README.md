# 🔮 电商平台（EasyShop）

基于 FastAPI + React 的全栈电商平台，咒术回战主题风格。

---

## 🚀 快速启动（老师专用）

### 方式一：双击运行（推荐）

1. 确保电脑已安装 **Python 3.9+**
2. 双击 `run.bat`
3. 等待终端显示 `Uvicorn running on http://0.0.0.0:8000`
4. 打开浏览器访问 **http://localhost:8000**

### 方式二：命令行手动运行

```bash
# 1. 进入 backend 目录
cd backend

# 2. 安装依赖（仅首次需要）
pip install -r requirements.txt

# 3. 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `Admin123456` |
| 普通用户 | `testuser` | `Test123456` |

---

## 🗺️ 功能导航

| 页面 | 地址 | 说明 |
|------|------|------|
| 首页 | `/` | 商品展示、Hero区视频 |
| 商品详情 | 点击商品卡片 | 查看详情、收藏、评价 |
| 购物车 | 顶栏购物车图标 | 增删改商品数量 |
| 结算 | `/checkout` | 填写地址 + 使用优惠券 |
| 订单 | `/orders` | 查看订单、去支付 |
| 收藏 | `/account` → 收藏tab | 查看/取消收藏 |
| 优惠券 | `/coupons` | 领券 + 查看已有券 |
| 地址管理 | `/account` → 地址tab | 增删改收货地址 |
| 管理员后台 | `/admin` | 仪表盘/商品/用户/订单/购物车管理 |
| 支付宝支付 | 订单页→去支付 | 沙箱环境模拟支付 |

---

## 📦 项目结构

```
ecommerce-final/
├── run.bat                 # Windows 一键启动
├── backend/
│   ├── app/
│   │   ├── main.py         # 入口
│   │   ├── api/            # 后端 API 路由
│   │   ├── crud/           # 数据库操作
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 校验
│   │   ├── services/       # 业务逻辑（含支付宝）
│   │   └── core/           # 配置、数据库
│   ├── keys/               # 支付宝密钥
│   ├── .env                # 环境配置
│   ├── requirements.txt    # Python 依赖
│   └── ecommerce.db        # SQLite 数据库（预置数据）
└── frontend/
    ├── src/                # React 源代码
    ├── dist/               # 构建后的前端（已打包）
    └── package.json        # Node 依赖（无需安装）
```

> ⚠️ 前端已预构建在 `frontend/dist/`，**无需安装 Node.js**。

---

## 💡 注意事项

- 数据库使用 **SQLite**，无需额外安装数据库软件
- 数据库会自动创建（首次启动时），已预置测试商品和用户数据
- 支付宝使用**沙箱环境**（测试用，不涉及真实资金）
- 默认端口：**8000**
- 前端由后端统一托管，**无跨域问题**
- 测试环境验签已关闭（`VERIFY_SIGN=false`）
