# MultiConversation

MultiConversation 是一个支持多会话的智能聊天系统，包含前端（基于 Vue3 + Vite）和后端（基于 Python）的完整实现。适用于多轮对话、智能问答、会话管理等场景，便于二次开发和扩展。

## 项目结构

```
MultiConversation/
├── chat-frontend/         # 前端项目（Vue3 + Vite）
│   ├── src/               # 前端源码
│   ├── public/            # 静态资源
│   ├── package.json       # 前端依赖
│   └── ...                
├── self_agent/            # 后端项目（Python）
│   ├── core/              # 核心模块
│   ├── modules/           # 功能模块
│   ├── data/              # 数据存储
│   ├── app.py             # 后端入口
│   └── requirements.txt   # 后端依赖
├── api_doc.md             # API 文档
├── product_requirements_document.md # 产品需求文档
├── technical-spec.md      # 技术规格说明
└── README.md              # 项目说明（当前文件）
```

## 主要功能

- 多会话管理
- 智能问答与消息处理
- 前后端分离架构，易于扩展
- 支持自定义模块与插件
- 丰富的 API 接口

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/MultiConversation.git
cd MultiConversation
```

### 2. 启动后端

确保已安装 Python 3.11+，并在 `self_agent` 目录下安装依赖：

```bash
cd self_agent
pip install -r requirements.txt
python app.py
```

### 3. 启动前端

确保已安装 Node.js 16+，并在 `chat-frontend` 目录下安装依赖并运行：

```bash
cd chat-frontend
npm install
npm run dev
```

前端默认运行在 [http://localhost:5173](http://localhost:5173)。

### 4. 访问与体验

- 前端页面：[http://localhost:5173](http://localhost:5173)
- 后端 API 默认端口：`http://localhost:8000`（如有变动请参考 `self_agent/app.py`）

## 依赖

- 前端：Vue3、Vite、相关 UI 组件库
- 后端：Python 3.11+、Flask/FastAPI（具体见 requirements.txt）

## 贡献

欢迎提交 Issue 或 Pull Request 参与项目改进！

1. Fork 本仓库
2. 新建分支进行开发
3. 提交 PR 并描述变更内容

## 许可证

本项目采用 MIT License，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过 Issue 反馈或联系项目维护者。
