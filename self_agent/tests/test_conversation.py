import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

import sys
import os

from typing import Generator, Any

# 动态导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import conversation

app = FastAPI()

@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, Any, None]:
    monkeypatch.setattr(conversation.llm_engine, "chat", fake_llm_chat)
    app.dependency_overrides[conversation.jwt_auth] = fake_jwt_auth
    app.include_router(conversation.router, prefix="/modules/conversation")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

# mock jwt_auth 依赖
def fake_jwt_auth():
    return {"user_id": "test_user"}

# mock llm_engine.chat
async def fake_llm_chat(messages):
    return "这是AI的回复"

# patch 依赖
# 已合并到 client fixture，不再需要 patch_dependencies

def test_list_conversations(client):
    # 先初始化会话和消息
    client.post(
        "/modules/conversation/test_conversation/messages",
        json={"content": "初始化消息"}
    )
    resp = client.get("/modules/conversation/")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert "test_conversation" in data["data"]

def test_get_conversation(client):
    # 先初始化会话和消息
    client.post(
        "/modules/conversation/test_conversation/messages",
        json={"content": "初始化消息"}
    )
    resp = client.get("/modules/conversation/test_conversation")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"]["conversation_id"] == "test_conversation"
    assert isinstance(data["data"]["messages"], list)
    assert len(data["data"]["messages"]) >= 1

def test_send_message(client):
    resp = client.post(
        "/modules/conversation/test_conversation/messages",
        json={"content": "测试消息"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "reply" in data["data"]
    assert data["data"]["reply"] == "这是AI的回复"
    assert any(msg["role"] == "user" and msg["content"] == "测试消息" for msg in data["data"]["messages"])
    assert any(msg["role"] == "assistant" and msg["content"] == "这是AI的回复" for msg in data["data"]["messages"])

def test_delete_conversation(client):
    # 先确保文件存在
    resp = client.get("/modules/conversation/test_conversation")
    assert resp.status_code == 200
    # 删除
    resp = client.delete("/modules/conversation/test_conversation")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["success"] is True
    # 再次删除应失败
    resp = client.delete("/modules/conversation/test_conversation")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["success"] is False
