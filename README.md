# AI 论文学习助手

个人自用的本地 AI 论文 / 资料学习助手。读取本地资料文件，让 AI 生成总结、初学者解释、复习问题和文件夹学习地图，支持 Markdown 导出。

当前版本：**v0.2**（前后端分离架构）

## 技术栈

- 后端：Python + FastAPI
- 前端：Vue 3 + Vite + Tailwind CSS
- AI：OpenAI 兼容 API

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
```

复制 `.env.example` 为 `.env`，填入 API 配置：

```env
AI_API_KEY=你的key
AI_BASE_URL=https://your-api-url/v1
AI_MODEL=gpt-5.5
PAPERS_DIR=../local_materials
CACHE_PATH=data/cache.json
```

启动：

```bash
uvicorn main:app --reload --port 8000
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。

## 项目结构

```
backend/           Python 后端（FastAPI REST API）
frontend/          Vue 3 前端
local_materials/   本地学习资料（不提交）
```

## 功能

- 读取本地目录 / 上传文件（md、txt、pdf、docx）
- AI 生成总结、初学者解释、复习问题
- 文件夹学习地图
- Markdown 导出
- JSON 缓存避免重复生成
