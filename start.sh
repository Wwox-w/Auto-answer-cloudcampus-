#!/bin/bash
set -e

cd "$(dirname "$0")"

# 启动后端
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 启动前端 dev server
cd frontend
npx vite --host &
FRONTEND_PID=$!
cd ..

echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo "按 Ctrl+C 停止"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
