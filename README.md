# 🤖 LYAITEST — AI驱动的测试智能体平台

**LYAITEST** 是一个基于 LangGraph 和 FastAPI 构建的智能测试平台。它通过自然语言驱动 Agent 执行接口测试、Web 自动化测试和测试用例生成，并自动记录测试报告。

---

## 🎯 项目背景与目标

传统测试工具需要编写脚本或手动操作，学习成本高、效率低。LYAITEST 通过 AI Agent 实现“用对话驱动测试”，让测试人员用自然语言描述测试需求，Agent 自动解析意图、调用测试工具、执行并生成报告。

---

## 🏗️ 项目架构
┌─────────────────────────────────────────────────────────────────┐
│ 用户界面 (Streamlit) │
├─────────────────────────────────────────────────────────────────┤
│ 会话管理 │
├─────────────────────────────────────────────────────────────────┤
│ API 网关 (FastAPI) │
├─────────────────────────────────────────────────────────────────┤
│ Agent 核心 (LangGraph) │
│ 意图识别 → 节点分流 → 工具执行 → 结果返回 │
├─────────────────────────────────────────────────────────────────┤
│ 工具层 (Tools) │
│ 接口测试工具 │ Web自动化工具 │ 用例生成工具 │
├─────────────────────────────────────────────────────────────────┤
│ 数据存储 (SQLite) │
│ 会话/消息/测试报告 → 持久化存储 │
└─────────────────────────────────────────────────────────────────┘

text

### 核心模块说明

| 模块 | 技术栈 | 职责 |
|------|--------|------|
| 前端界面 | Streamlit | 提供会话管理、聊天界面、报告查看 |
| API 网关 | FastAPI | 处理 HTTP 请求，路由分发 |
| Agent 引擎 | LangGraph + LangChain | 意图识别、状态管理、工具调用编排 |
| 测试工具 | requests + Playwright | 执行接口测试和 Web 自动化测试 |
| 数据存储 | SQLite | 保存会话、消息、测试报告 |

---

## 📁 项目目录结构
lyaitest/
├── app/
│ ├── routers/ # API 路由层
│ │ ├── agent.py # Agent 对话接口
│ │ ├── chat.py # 聊天接口
│ │ ├── sessions.py # 会话管理接口
│ │ └── report.py # 测试报告查询接口
│ ├── services/ # 业务逻辑层
│ │ ├── agent.py # Agent 核心逻辑 (LangGraph)
│ │ └── report_service.py # 测试报告存储服务
│ ├── models/ # 数据模型层
│ │ ├── session.py # 会话数据模型
│ │ └── report.py # 测试报告数据模型
│ ├── database.py # SQLite 数据库连接与表初始化
│ └── main.py # FastAPI 应用入口
├── app_frontend.py # Streamlit 前端主程序
├── requirements.txt # Python 依赖包列表
├── render.yaml # Render 部署配置
├── .streamlit/config.toml # Streamlit 主题配置
├── .env # 环境变量 (不上传 GitHub)
└── README.md # 项目文档

text

---

## ⚙️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端框架 | Streamlit |
| Agent 引擎 | LangGraph + LangChain |
| 大模型 | DeepSeek / 智谱 GLM |
| 接口测试 | requests |
| Web 自动化 | Playwright |
| 数据库 | SQLite |
| 部署平台 | Render (后端) + Streamlit Cloud (前端) |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/LvRaya-bit/lyaitest.git
cd lyaitest
2. 创建虚拟环境
bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
3. 安装依赖
bash
pip install -r requirements.txt
python -m playwright install
4. 配置环境变量
创建 .env 文件：

env
DEEPSEEK_API_KEY=your_deepseek_api_key
ZHIPU_API_KEY=your_zhipu_api_key   # 如果用智谱
5. 启动后端服务
bash
uvicorn app.main:app --reload
后端默认运行在 http://localhost:8000

6. 启动前端界面
bash
streamlit run app_frontend.py
前端默认运行在 http://localhost:8501

📊 核心数据模型
表名	字段	说明
sessions	session_id, name, created_at	会话信息
messages	id, session_id, role, content, created_at	聊天消息
reports	id, session_id, test_type, url, status_code, title, screenshot, error, created_at	测试报告
🔗 相关链接
FastAPI 文档

Streamlit 文档

LangGraph 文档

Playwright 文档

📌 注意事项
API Key 请通过环境变量配置，不要硬编码到代码中。

SQLite 数据库文件 lyaitest.db 会在首次启动时自动生成。

部署到 Render 时，需要在后台配置环境变量。
