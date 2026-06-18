#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
while ! mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --ssl=0 -e "SELECT 1" >/dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "MySQL not ready after $MAX_RETRIES attempts, exiting."
        exit 1
    fi
    echo "MySQL not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES), retrying in 2s..."
    sleep 2
done
echo "MySQL is ready."

echo "Ensuring database exists with correct charset..."
mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --ssl=0 <<-EOSQL
    CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`
    DEFAULT CHARACTER SET = gb2312
    DEFAULT COLLATE = gb2312_chinese_ci;
EOSQL

echo "Creating tables..."
python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
"

if [ ! -f /app/.init_done ]; then
    echo "Seeding initial data..."
    python -m app.scripts.seed_products
    python -m app.scripts.init_admin
    touch /app/.init_done
    echo "Initialization completed."
else
    echo "Data already initialized, skipping seed."
fi

echo "Starting Uvicorn server..."
# 关键修复：使用 python -m 方式启动 uvicorn
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000