@echo off
REM 安装依赖（如已安装可忽略此步）
pip install -r self_agent/requirements.txt

REM 启动 FastAPI 后端服务
cd self_agent
uvicorn app:app --reload --host 0.0.0.0 --port 5000
