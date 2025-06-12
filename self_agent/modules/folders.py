import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import aiofiles

router = APIRouter()

FOLDER_DATA_PATH = Path(__file__).parent.parent / "data" / "folders.json"
FOLDER_DATA_PATH.parent.mkdir(exist_ok=True)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

class Folder(BaseModel):
    folder_id: str
    name: str
    conversation_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    is_default: bool = False

async def load_folders() -> List[Folder]:
    if not FOLDER_DATA_PATH.exists():
        return []
    async with aiofiles.open(FOLDER_DATA_PATH, "r", encoding="utf-8") as f:
        content = await f.read()
        try:
            data = json.loads(content)
            return [Folder(**item) for item in data]
        except Exception:
            return []

async def save_folders(folders: List[Folder]):
    async with aiofiles.open(FOLDER_DATA_PATH, "w", encoding="utf-8") as f:
        await f.write(json.dumps([f.dict() for f in folders], ensure_ascii=False, indent=2))

async def get_folder_by_id(folder_id: str) -> Optional[Folder]:
    folders = await load_folders()
    for folder in folders:
        if folder.folder_id == folder_id:
            return folder
    return None

@router.get("/", summary="获取所有收藏夹及内容")
async def list_folders():
    folders = await load_folders()
    return {"data": [f.dict() for f in folders]}

@router.post("/", summary="新建收藏夹")
async def create_folder(body: dict = Body(...)):
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="收藏夹名称不能为空")
    folders = await load_folders()
    if any(f.name == name for f in folders):
        raise HTTPException(status_code=400, detail="收藏夹名称已存在")
    folder_id = str(uuid.uuid4())
    folder = Folder(folder_id=folder_id, name=name)
    folders.append(folder)
    await save_folders(folders)
    return {"data": folder.dict()}

@router.patch("/{folder_id}", summary="重命名收藏夹")
async def rename_folder(folder_id: str, body: dict = Body(...)):
    new_name = body.get("name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="收藏夹名称不能为空")
    folders = await load_folders()
    for f in folders:
        if f.name == new_name and f.folder_id != folder_id:
            raise HTTPException(status_code=400, detail="收藏夹名称已存在")
    for folder in folders:
        if folder.folder_id == folder_id:
            if folder.is_default:
                raise HTTPException(status_code=400, detail="默认收藏夹不可重命名")
            folder.name = new_name
            folder.updated_at = now_iso()
            await save_folders(folders)
            return {"data": folder.dict()}
    raise HTTPException(status_code=404, detail="收藏夹不存在")

@router.delete("/{folder_id}", summary="删除收藏夹")
async def delete_folder(folder_id: str):
    folders = await load_folders()
    for folder in folders:
        if folder.folder_id == folder_id:
            if folder.is_default:
                raise HTTPException(status_code=400, detail="默认收藏夹不可删除")
            folders.remove(folder)
            await save_folders(folders)
            return {"data": {"success": True}}
    raise HTTPException(status_code=404, detail="收藏夹不存在")

@router.post("/{folder_id}/add", summary="添加会话到收藏夹")
async def add_conversation(folder_id: str, body: dict = Body(...)):
    conv_id = body.get("conversation_id")
    if not conv_id:
        raise HTTPException(status_code=400, detail="会话ID不能为空")
    folders = await load_folders()
    for folder in folders:
        if folder.folder_id == folder_id:
            if conv_id not in folder.conversation_ids:
                folder.conversation_ids.append(conv_id)
                folder.updated_at = now_iso()
                await save_folders(folders)
            return {"data": folder.dict()}
    raise HTTPException(status_code=404, detail="收藏夹不存在")

@router.post("/{folder_id}/remove", summary="从收藏夹移除会话")
async def remove_conversation(folder_id: str, body: dict = Body(...)):
    conv_id = body.get("conversation_id")
    if not conv_id:
        raise HTTPException(status_code=400, detail="会话ID不能为空")
    folders = await load_folders()
    for folder in folders:
        if folder.folder_id == folder_id:
            if conv_id in folder.conversation_ids:
                folder.conversation_ids.remove(conv_id)
                folder.updated_at = now_iso()
                await save_folders(folders)
            return {"data": folder.dict()}
    raise HTTPException(status_code=404, detail="收藏夹不存在")

# 初始化时自动生成默认收藏夹（如不存在）
async def ensure_default_folder():
    folders = await load_folders()
    if not any(f.is_default for f in folders):
        default_folder = Folder(
            folder_id="default",
            name="默认收藏夹",
            is_default=True
        )
        folders.append(default_folder)
        await save_folders(folders)

import asyncio
asyncio.get_event_loop().create_task(ensure_default_folder())
