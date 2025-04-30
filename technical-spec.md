下面对已有文档做进一步优化，补充了错误处理、鉴权、分页及部署等关键点，并调整了排版与术语，以便开发和维护。

---

## 一、项目总览

- **前端**：Vue 3 + Vite  
- **后端**：FastAPI + Uvicorn  
- **通信方式**：RESTful API （局部支持 WebSocket 推送）  
- **持久化**：JSON 文件（`data/`）或可扩展至数据库  
- **日记**：按天轮转的日志文件（`logs/`）

## 二、目录结构

```
chat-frontend/                  # 前端项目
├── package.json
├── vite.config.js
└── src/
    ├── main.js                 # 程序入口
    ├── App.vue
    ├── index.html
    └── components/
        ├── ChatWindow.vue
        ├── ConversationSidebar.vue
        └── MessageItem.vue

self_agent/                     # 后端项目
├── app.py                      # FastAPI 应用与路由注册
├── requirements.txt
├── modules/
│   ├── conversation.py         # 会话管理（CRUD、分页、搜索）
│   └── llm.py                  # 大模型调用封装（支持多引擎）
├── core/
│   ├── config.py               # 环境变量与配置管理
│   ├── auth.py                 # Token 鉴权与权限检查
│   ├── errors.py               # 自定义异常及错误码
│   └── websocket.py            # WebSocket 服务（可选）
├── data/                       # JSON 存储（或 SQLite、MongoDB）
├── logs/                       # 日志目录（按天轮转）
└── tests/
    ├── test_conversation.py
    └── test_llm.py
```

## 三、关键技术选型

| 领域       | 技术 / 库                        | 说明                                   |
|------------|----------------------------------|----------------------------------------|
| 前端框架   | Vue 3                            | 组件化、易扩展                         |
| 构建工具   | Vite                             | 快速冷启动                             |
| Markdown   | markdown-it + 插件               | 支持 emoji、任务列表、表格             |
| 代码高亮   | highlight.js                     | 支持多种语言块                         |
| 后端框架   | FastAPI                          | 类型声明、自动生成文档                 |
| ASGI 服务器| Uvicorn                          | 高性能                               |
| HTTP 客户端| aiohttp                          | 异步请求                             |
| 文件 IO    | aiofiles                         | 异步文件读写                         |
| 序列化     | pydantic + orjson                | 高性能 JSON 序列化                   |
| AI 接入    | langchain / openai / anthropic   | 可插拔式多模型支持                   |
| 日志管理   | loguru + TimedRotatingFileHandler| 按日期轮转                             |
| 验证鉴权   | JWT（`python-jose`）             | Token 鉴权                            |

## 四、配置管理

- **`core/config.py`** 统一管理，支持环境变量覆盖：
  ```python
  from pydantic import BaseSettings

  class Settings(BaseSettings):
      APP_NAME: str = "ChatAgent"
      HOST: str = "0.0.0.0"
      PORT: int = 5000
      DEBUG: bool = False
      DATA_PATH: str = "./data"
      LOG_LEVEL: str = "INFO"
      JWT_SECRET: str
      JWT_ALGORITHM: str = "HS256"
      OPENAI_API_KEY: str

      class Config:
          env_file = ".env"
  ```
- **`.env`** 示例：
  ```
  DEBUG=True
  JWT_SECRET=your_jwt_secret
  OPENAI_API_KEY=sk-...
  ```

## 五、数据模型

### Conversation

| 字段              | 类型     | 说明                                        |
|-------------------|----------|---------------------------------------------|
| conversation_id   | `str`    | 唯一标识（UUID 或自定义前缀）               |
| name              | `str`    | 会话标题（默认取首条用户消息前 10 字）       |
| summary           | `str`    | 摘要（最新一条消息内容）                     |
| created_at        | `datetime` | 创建时间                                   |
| updated_at        | `datetime` | 最后更新时间                               |
| messages          | `List[Message]` | 消息列表                               |

### Message

| 字段     | 类型     | 说明                          |
|----------|----------|-------------------------------|
| role     | `str`    | `"user"`│`"assistant"`│`"ai"` |
| content  | `str`    | 文本内容（支持 Markdown）     |
| timestamp| `datetime` | 发送时间                     |

## 六、API 设计

> 本节接口设计已完全同步实际后端实现，所有接口当前**无需鉴权**（鉴权相关已注释，后续如需可补充）。  
> 鉴权部分备注：**暂不做**。

### 全局约定

- **Base URL**：`/api/v1`
- **鉴权**：当前所有接口无需鉴权，后端实现中鉴权相关依赖已注释。如需鉴权可启用 JWT 中间件，详见 core/auth.py。
- **分页**：会话列表与消息历史均支持分页，参数为 `?page=<int>&size=<int>`，默认 `page=1, size=20`（消息历史最大 size=500）。
- **错误返回**：
  ```json
  {
    "data": {
      "success": false,
      "error": "错误描述"
    }
  }
  ```
- **所有时间均为 UTC，ISO8601 格式。**

---

### 1. 获取会话ID列表

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

### 2. 获取会话详情（含消息历史）

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

### 3. 发送消息

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

### 4. 删除会话

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

### 5. 数据结构说明

#### 会话对象（Conversation）

| 字段           | 类型     | 说明                       |
|----------------|----------|----------------------------|
| conversation_id| string   | 会话唯一ID                 |
| name           | string   | 会话标题（默认首条用户消息前10字）|
| summary        | string   | 最新一条消息内容           |
| created_at     | string   | 创建时间（ISO8601）        |
| updated_at     | string   | 最后更新时间（ISO8601）    |
| messages       | array    | 消息列表                   |

#### 消息对象（Message）

| 字段     | 类型   | 说明                |
|----------|--------|---------------------|
| role     | string | "user" 或 "assistant"|
| content  | string | 消息内容            |
| timestamp| string | 消息时间（ISO8601） |

---

## 七、WebSocket（可选）

- **用途**：新消息实时推送、typing 状态、在线用户列表
- **端点**：`/ws/chat/{conversation_id}`
- **协议**：JSON 消息包 `{ "event": ..., "payload": ... }`

## 八、安全与性能

1. **鉴权**：JWT，支持 Token 刷新  
2. **限流**：基于 IP 或用户 ID 的漏桶算法  
3. **缓存**：对热门会话摘要或模型结果使用内存缓存（如 Redis）  
4. **日志**：记录请求 ID、耗时、错误堆栈  
5. **负载**：可水平扩展，通过 Nginx 或 Kubernetes 进行反向代理与自动伸缩

## 九、测试与 CI/CD

- **单元测试**：`pytest` 覆盖率 ≥ 90%  
- **接口测试**：`httpx` + `pytest`  
- **静态检查**：`flake8` + `mypy`  
- **部署**：
  - Dockerfile + Docker Compose  
  - GitHub Actions 流水线：构建镜像→测试→推送→部署（可选 k8s）

## 十、扩展与维护

- **多模型接入**：`modules/llm.py` 中按策略注入  
- **存储切换**：可替换 `data/` 目录为 MongoDB、PostgreSQL  
- **前端插件**：自定义 Markdown 插件、表情包  
- **国际化**：Vue i18n + FastAPI-Babel  

---

以上方案已覆盖项目结构、配置、接口、安全、部署及扩展点，方便后续迭代与维护。如需进一步细化示例代码、CI/CD 脚本或部署指南，请告知！
