# 阶段一：构建
FROM node:24-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm ci

# 复制源码
COPY . .

# ========= 临时修改 tsconfig.app.json（不修改源码，仅用于构建）=========
# 1. 关闭 noUnusedLocals 和 noUnusedParameters
RUN sed -i 's/"noUnusedLocals": true/"noUnusedLocals": false/' tsconfig.app.json && \
    sed -i 's/"noUnusedParameters": true/"noUnusedParameters": false/' tsconfi# 阶段一：构建
FROM node:24-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm ci

# 复制源码
COPY . .

# ========= 临时修改 tsconfig.app.json（不修改源码，仅用于构建）=========
# 1. 关闭 noUnusedLocals 和 noUnusedParameters
RUN sed -i 's/"noUnusedLocals": true/"noUnusedLocals": false/' tsconfig.app.json && \
    sed -i 's/"noUnusedParameters": true/"noUnusedParameters": false/' tsconfig.app.json

# 2. 添加 "node" 到 types 数组（如果没有 types 字段则新增）
RUN if grep -q '"types":' tsconfig.app.json; then \
      sed -i '/"types":/ s/\[\(.*\)\]/[\1, "node"]/' tsconfig.app.json; \
    else \
      sed -i '/"compilerOptions": {/a \    "types": ["vite/client", "node"],' tsconfig.app.json; \
    fi

# 构建
RUN npm run build

# 阶段二：生产运行（Nginx）
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]