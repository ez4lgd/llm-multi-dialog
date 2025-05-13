# 会话管理路由
import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, Query, Path as FPath, Body
from fastapi import APIRouter
from core.auth import jwt_auth
from modules.llm import llm_engine
from core.logger import logger
import aiofiles
from typing import List, Any, Optional
from datetime import datetime
import uuid

router = APIRouter()

# 数据结构定义
def now_iso():
    return datetime.utcnow().isoformat() + "Z"

def build_conversation_obj(conversation_id: str, messages: Optional[List[dict]] = None, name: Optional[str] = None, summary: Optional[str] = None, created_at: Optional[str] = None, updated_at: Optional[str] = None, config: Optional[dict] = None):
    messages = messages or []
    if not name:
        # 默认取首条用户消息前10字
        first_user = next((m for m in messages if m.get("role") == "user"), None)
        name = first_user["content"][:10] if first_user and first_user.get("content") else conversation_id
    if not summary:
        summary = messages[-1]["content"] if messages else ""
    now = now_iso()
    return {
        "conversation_id": conversation_id,
        "name": name,
        "summary": summary,
        "created_at": created_at or now,
        "updated_at": updated_at or now,
        "messages": messages,
        "config": config if config is not None else {}
    }

def build_message(role: str, content: str, timestamp: Optional[str] = None):
    return {
        "role": role,
        "content": content,
        "timestamp": timestamp or now_iso()
    }

# 路径与数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_conversation_path(conversation_id: str) -> Path:
    return DATA_DIR / f"{conversation_id}.json"


@router.get("/", summary="会话列表")
async def list_conversations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    # user=Depends(jwt_auth)
):
    # 遍历 /data 目录，获取所有会话 id 及 created_at
    all_files = [p for p in DATA_DIR.glob("*.json")]
    convs = []
    for p in all_files:
        try:
            async with aiofiles.open(p, "r", encoding="utf-8") as f:
                content = await f.read()
                obj = json.loads(content)
                created_at = obj.get("created_at")
                # 若无 created_at 字段，取文件创建时间
                if not created_at:
                    created_at = datetime.utcfromtimestamp(p.stat().st_ctime).isoformat() + "Z"
                convs.append({"id": p.stem, "created_at": created_at})
        except Exception as e:
            logger.error(f"[会话ID:{p.stem}] 读取 created_at 失败: {e}")
            convs.append({"id": p.stem, "created_at": "1970-01-01T00:00:00Z"})
    # 按 created_at 降序排序
    convs.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(convs)
    start = (page - 1) * size
    end = start + size
    paged_ids = [c["id"] for c in convs[start:end]]
    return {
        "data": paged_ids,
        "meta": {"page": page, "size": size, "total": total}
    }

@router.get("/{conversation_id}", summary="获取会话历史")
async def get_conversation(
    conversation_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=500),
    # user=Depends(jwt_auth)
):
    conv_path = get_conversation_path(conversation_id)
    if not conv_path.exists():
        return {
            "data": build_conversation_obj(conversation_id, messages=[])
        }
    try:
        async with aiofiles.open(conv_path, "r", encoding="utf-8") as f:
            content = await f.read()
            conv_obj = json.loads(content)
    except Exception as e:
        logger.error(f"[会话ID:{conversation_id}] 读取历史消息失败: {e}")
        conv_obj = build_conversation_obj(conversation_id, messages=[])
    # 分页
    messages = conv_obj.get("messages", [])
    total = len(messages)
    start = (page - 1) * size
    end = start + size
    paged_messages = messages[start:end]
    conv_obj["messages"] = paged_messages
    conv_obj["meta"] = {"page": page, "size": size, "total": total}
    return {
        "data": conv_obj
    }



@router.post("/{conversation_id}/messages", summary="发送消息")
async def send_message(
    conversation_id: str,
    body: dict = Body(...),
    # user=Depends(jwt_auth)
):
    user_input = body.get("content", "")
    model = body.get("model")
    logger.info(f"[会话ID:{conversation_id}] 用户输入: {user_input}, 模型: {model}")

    # 读取历史会话对象
    conv_path = get_conversation_path(conversation_id)
    if conv_path.exists():
        try:
            async with aiofiles.open(conv_path, "r", encoding="utf-8") as f:
                content = await f.read()
                conv_obj = json.loads(content)
        except Exception as e:
            logger.error(f"[会话ID:{conversation_id}] 读取历史消息失败: {e}")
            conv_obj = build_conversation_obj(conversation_id, messages=[])
    else:
        conv_obj = build_conversation_obj(conversation_id, messages=[])

    messages = conv_obj.get("messages", [])

    # 处理模型参数，优先用本次传入的 model
    if model:
        if "config" not in conv_obj or not isinstance(conv_obj["config"], dict):
            conv_obj["config"] = {}
        conv_obj["config"]["model"] = model
        conv_obj["model"] = model  # 兼容老字段

    # 添加本次用户输入
    user_msg = build_message("user", user_input)
    messages.append(user_msg)

    # 调用大模型，优先用本次模型参数
    chat_model = model or conv_obj.get("config", {}).get("model")
    if chat_model:
        reply = await llm_engine.chat(messages, model=chat_model)
    else:
        reply = await llm_engine.chat(messages)
    logger.info(f"[会话ID:{conversation_id}] 模型输出: {reply}")

    # 添加AI回复
    ai_msg = build_message("assistant", reply)
    messages.append(ai_msg)

    # 更新会话元数据
    conv_obj["messages"] = messages
    conv_obj["summary"] = reply
    conv_obj["updated_at"] = now_iso()
    if not conv_obj.get("created_at"):
        conv_obj["created_at"] = now_iso()
    if not conv_obj.get("name"):
        # 默认取首条用户消息前10字
        first_user = next((m for m in messages if m.get("role") == "user"), None)
        conv_obj["name"] = first_user["content"][:10] if first_user and first_user.get("content") else conversation_id

    # 保存到json
    try:
        async with aiofiles.open(conv_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(conv_obj, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"[会话ID:{conversation_id}] 保存消息失败: {e}")

    # 返回最近20条消息
    return {
        "data": {
            "reply": reply,
            "messages": messages[-20:],
            "conversation_id": conversation_id,
            "name": conv_obj.get("name"),
            "summary": conv_obj.get("summary"),
            "created_at": conv_obj.get("created_at"),
            "updated_at": conv_obj.get("updated_at")
        }
    }

@router.delete("/{conversation_id}", summary="删除会话")
async def delete_conversation(
    conversation_id: str,
    # user=Depends(jwt_auth)
):
    conv_path = get_conversation_path(conversation_id)
    if conv_path.exists():
        try:
            conv_path.unlink()
            logger.info(f"[会话ID:{conversation_id}] 会话已删除")
            return {"data": {"success": True}}
        except Exception as e:
            logger.error(f"[会话ID:{conversation_id}] 删除会话失败: {e}")
            return {"data": {"success": False, "error": str(e)}}
    else:
        logger.warning(f"[会话ID:{conversation_id}] 会话不存在，无法删除")
        return {"data": {"success": False, "error": "会话不存在"}}

# 新增：设置会话模型/参数配置
@router.post("/{conversation_id}/set_config", summary="设置会话模型/参数配置")
async def set_conversation_config(
    conversation_id: str,
    body: dict = Body(...),
    # user=Depends(jwt_auth)
):
    conv_path = get_conversation_path(conversation_id)
    if not conv_path.exists():
        return {"data": {"error": "会话不存在"}}
    try:
        async with aiofiles.open(conv_path, "r", encoding="utf-8") as f:
            content = await f.read()
            conv_obj = json.loads(content)
    except Exception as e:
        logger.error(f"[会话ID:{conversation_id}] 读取会话失败: {e}")
        return {"data": {"error": "读取会话失败"}}
    # 更新config字段
    conv_obj["config"] = body
    # 兼容老字段
    if "model" in body:
        conv_obj["model"] = body["model"]
    conv_obj["updated_at"] = now_iso()
    try:
        async with aiofiles.open(conv_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(conv_obj, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"[会话ID:{conversation_id}] 保存配置失败: {e}")
        return {"data": {"error": "保存配置失败"}}
    return {"data": conv_obj.get("config", {})}
