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

### 全局约定

- **Base URL**：`/api/v1`
- **鉴权**：除登录注册外，全部接口需在 `Authorization: Bearer <token>` 头中携带 JWT
- **分页**：列表接口支持 `?page=<int>&size=<int>`，默认 `page=1, size=20`
- **错误返回**：
  ```json
  {
    "code": 4001,
    "message": "Invalid conversation_id",
    "details": null
  }
  ```
  - `code`：自定义错误码，前两位为 HTTP 状态
  - `message`：简要描述
  - `details`：可选，错误细节

---

### 1. 会话列表

> **GET** `/api/v1/conversations`

- **参数**：
  - `page`：页码（默认 1）
  - `size`：单页数量（默认 20）
- **返回**：
  ```json
  {
    "data": [
      {
        "conversation_id": "conv_123",
        "name": "测试会话",
        "summary": "最新摘要...",
        "updated_at": "2025-04-29T15:32:10Z"
      }
    ],
    "meta": {
      "page": 1,
      "size": 20,
      "total": 42
    }
  }
  ```

---

### 2. 获取会话历史

> **GET** `/api/v1/conversations/{conversation_id}`

- **参数**：`conversation_id`（路径）
- **查询**：可选 `?page`, `?size` 分页
- **返回**：
  ```json
  {
    "data": {
      "conversation_id": "conv_123",
      "messages": [
        {"role":"user","content":"你好","timestamp":"..."},
        {"role":"assistant","content":"...","timestamp":"..."}
      ]
    }
  }
  ```

---

### 3. 发送消息

> **POST** `/api/v1/conversations/{conversation_id}/messages`

- **请求体**：
  ```json
  { "message": "你好" }
  ```
- **返回**：
  ```json
  {
    "data": {
      "reply": "AI 回复内容",
      "messages": [ /* 最新消息列表 */ ]
    }
  }
  ```

> **备注**：支持在 `modules/llm.py` 中通过参数选择不同模型（OpenAI / Anthropic / 本地模型等）。

---

### 4. 删除会话

> **DELETE** `/api/v1/conversations/{conversation_id}`

- **返回**：
  ```json
  { "data": { "success": true } }
  ```

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