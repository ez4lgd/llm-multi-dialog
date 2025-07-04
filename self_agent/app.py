# FastAPI 应用主入口
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.auth import jwt_auth
from core.errors import register_exception_handlers
from modules.conversation import router as conversation_router
from modules.folders import router as folders_router
from modules.tags import router as tags_router
from fastapi import APIRouter

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(folders_router, prefix="/api/v1/folders", tags=["Folders"])
app.include_router(tags_router)

# 新增：/api/v1/models 路由，供前端获取模型列表
@app.get("/api/v1/models", tags=["Models"])
async def get_models():
    return {"data": ["gpt-4.1", "o4-mini"]}

# 注册异常处理
register_exception_handlers(app)

# 鉴权中间件（可选，具体实现见 core/auth.py）
# app.middleware("http")(jwt_auth)

# uvicorn app:app --reload --host 0.0.0.0 --port 5000
