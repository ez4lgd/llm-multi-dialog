import os
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tags.json")
router = APIRouter(prefix="/api/v1/conversation_tags", tags=["conversation_tags"])

def load_tags():
    if not os.path.exists(DATA_PATH):
        return {"tags": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tags(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

@router.post("/", summary="为会话添加标签")
def add_tag(
    body: dict = Body(..., example={"conversation_id": "conv-uuid-1", "tag": "工作"})
):
    data = load_tags()
    tag_obj = {
        "id": str(uuid.uuid4()),
        "conversation_id": body["conversation_id"],
        "tag": body["tag"],
        "created_at": now_iso(),
        "updated_at": now_iso()
    }
    data["tags"].append(tag_obj)
    save_tags(data)
    return tag_obj

@router.delete("/{tag_id}", summary="删除标签")
def delete_tag(tag_id: str):
    data = load_tags()
    tags = data["tags"]
    new_tags = [t for t in tags if t["id"] != tag_id]
    if len(tags) == len(new_tags):
        raise HTTPException(status_code=404, detail="标签不存在")
    data["tags"] = new_tags
    save_tags(data)
    return {"ok": True}

@router.put("/{tag_id}", summary="修改标签")
def update_tag(tag_id: str, body: dict = Body(..., example={"tag": "新标签内容"})):
    data = load_tags()
    found = False
    for t in data["tags"]:
        if t["id"] == tag_id:
            t["tag"] = body["tag"]
            t["updated_at"] = now_iso()
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="标签不存在")
    save_tags(data)
    return t

@router.get("/", summary="查询会话的所有标签")
def list_tags(conversation_id: str = Query(...)):
    data = load_tags()
    tags = [t for t in data["tags"] if t["conversation_id"] == conversation_id]
    return {"tags": tags}

@router.get("/all", summary="查询所有标签")
def list_all_tags():
    data = load_tags()
    return data
