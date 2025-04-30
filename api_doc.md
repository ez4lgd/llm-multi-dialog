# 多轮对话系统后端接口文档（基于实际实现）

> 说明：本接口文档完全基于 self_agent 实际后端实现，所有接口均无需鉴权（鉴权相关已注释，后续如需可补充）。  
> 鉴权部分备注：**暂不做**。

---

## 1. 获取会话ID列表

- **接口**：GET `/api/v1/conversations/`
- **参数**（Query）：
  - `page`：页码（默认 1，最小 1）
  - `size`：每页数量（默认 20，最大 100）
- **返回示例**：
```json
{
  "data": [
    "conv_123",
    "conv_456"
  ],
  "meta": {
    "page": 1,
    "size": 20,
    "total": 2
  }
}
```
- **说明**：仅返回会话ID列表，具体会话内容需通过下述接口获取。

---

## 2. 获取会话详情（含消息历史）

- **接口**：GET `/api/v1/conversations/{conversation_id}`
- **参数**：
  - `conversation_id`：路径参数，会话唯一ID
  - `page`：消息分页页码（默认 1，最小 1）
  - `size`：每页消息数（默认 100，最大 500）
- **返回示例**：
```json
{
  "data": {
    "conversation_id": "conv_123",
    "name": "你好世界",
    "summary": "最新AI回复",
    "created_at": "2025-04-30T10:00:00Z",
    "updated_at": "2025-04-30T10:10:00Z",
    "messages": [
      {
        "role": "user",
        "content": "你好",
        "timestamp": "2025-04-30T10:00:01Z"
      },
      {
        "role": "assistant",
        "content": "你好，有什么可以帮您？",
        "timestamp": "2025-04-30T10:00:02Z"
      }
    ],
    "meta": {
      "page": 1,
      "size": 100,
      "total": 2
    }
  }
}
```
- **说明**：如会话不存在，返回空消息列表。消息支持分页，meta 字段包含分页信息。

---

## 3. 发送消息

- **接口**：POST `/api/v1/conversations/{conversation_id}/messages`
- **参数**：
  - `conversation_id`：路径参数，会话唯一ID
- **请求体**（JSON）：
```json
{
  "content": "你好"
}
```
- **返回示例**：
```json
{
  "data": {
    "reply": "AI 回复内容",
    "messages": [
      {
        "role": "user",
        "content": "你好",
        "timestamp": "2025-04-30T10:00:01Z"
      },
      {
        "role": "assistant",
        "content": "AI 回复内容",
        "timestamp": "2025-04-30T10:00:02Z"
      }
      // ...最近20条消息
    ],
    "conversation_id": "conv_123",
    "name": "你好",
    "summary": "AI 回复内容",
    "created_at": "2025-04-30T10:00:00Z",
    "updated_at": "2025-04-30T10:10:00Z"
  }
}
```
- **说明**：
  - 请求体字段为 `content`，表示用户输入内容。
  - 返回字段 `reply` 为AI回复内容，`messages`为最近20条消息，附带会话元数据。
  - 如会话不存在则自动新建。

---

## 4. 删除会话

- **接口**：DELETE `/api/v1/conversations/{conversation_id}`
- **参数**：
  - `conversation_id`：路径参数，会话唯一ID
- **返回示例**：
```json
{
  "data": {
    "success": true
  }
}
```
- **说明**：如会话不存在，`success` 为 false，并返回错误信息。

---

## 5. 鉴权说明

- 当前所有接口**无需鉴权**，后端实现中鉴权相关依赖已注释。
- 如需鉴权，可启用 JWT 相关中间件，详见 core/auth.py。
- **备注：鉴权暂不做。**

---

## 6. 错误处理

- 绝大多数接口异常时返回如下结构：
```json
{
  "data": {
    "success": false,
    "error": "错误描述"
  }
}
```
- 具体错误码与 message 可根据 core/errors.py 及日志输出追踪。

---

## 7. 数据结构说明

### 会话对象（Conversation）

| 字段           | 类型     | 说明                       |
|----------------|----------|----------------------------|
| conversation_id| string   | 会话唯一ID                 |
| name           | string   | 会话标题（默认首条用户消息前10字）|
| summary        | string   | 最新一条消息内容           |
| created_at     | string   | 创建时间（ISO8601）        |
| updated_at     | string   | 最后更新时间（ISO8601）    |
| messages       | array    | 消息列表                   |

### 消息对象（Message）

| 字段     | 类型   | 说明                |
|----------|--------|---------------------|
| role     | string | "user" 或 "assistant"|
| content  | string | 消息内容            |
| timestamp| string | 消息时间（ISO8601） |

---

## 8. 其他说明

- 所有时间均为 UTC，ISO8601 格式。
- 数据持久化采用本地 data/ 目录下 JSON 文件。
- 日志输出见 logs/ 目录。
- 未来如需支持 WebSocket、鉴权、数据库等，可按需扩展。

---
