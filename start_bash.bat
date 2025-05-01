@echo off
REM 启动前端服务
start cmd /k "cd /d %~dp0chat-frontend && npm run dev"
REM 启动后端服务
start cmd /k "cd /d %~dp0self_agent && uvicorn app:app --reload --host 0.0.0.0 --port 5000"
