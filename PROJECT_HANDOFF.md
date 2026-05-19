# AI 论文学习助手阶段交接说明

这份文档用于下次继续开发时快速恢复上下文。可以把本文内容直接粘贴给 Codex / ChatGPT，让它接上当前阶段的项目状态。

## 项目信息

- 项目路径：`D:\Desktop\1`
- GitHub 仓库：<https://github.com/boommelon/ai-paper-study-assistant>
- 当前阶段：`v0.1 MVP` 阶段性完成
- 项目定位：个人自用的本地 AI 论文 / 资料学习助手

用户是学习型开发者，希望解释技术时把缩写和术语讲清楚，不要默认他已经懂架构。

## 项目目标

做一个本地 AI 论文学习助手，可以读取本地资料，然后让 AI 生成：

1. 总结
2. 初学者解释
3. 复习问题
4. 文件夹学习地图
5. Markdown 导出笔记

## 当前技术栈

- `Python`：主语言
- `Streamlit`：本地网页界面，当前阶段前端和后端暂时揉在一起
- `JSON cache`：本地缓存 AI 生成结果
- `OpenAI Python SDK`：调用 OpenAI-compatible API
- `python-dotenv`：读取 `.env` 配置
- `pypdf`：读取 PDF
- `python-docx`：读取 Word `.docx`

## 核心文件

- `app.py`：Streamlit 主界面
- `ai_client.py`：AI 接口调用
- `config.py`：读取 `.env` 配置
- `document_loader.py`：读取 `md / txt / pdf / docx`，提取文本，拆分主题
- `prompts.py`：总结、解释、复习题、文件夹总览提示词
- `storage.py`：JSON 本地缓存
- `requirements.txt`：依赖列表
- `README.md`：项目说明
- `.env.example`：配置模板，可以上传 GitHub
- `.env`：真实本地配置，不能上传 GitHub

## 当前功能状态

- 支持本地目录读取
- 支持单文件上传
- 支持 `.md / .markdown / .txt / .pdf / .docx`
- 支持主题选择
- 支持原文预览
- 支持 PDF 按页文本预览
- 支持生成总结、初学者解释、复习问题
- 支持文件夹学习地图
- 支持导出 Markdown
- 支持 JSON 缓存，避免重复生成
- API 设置已收进侧边栏的 `AI 配置` 折叠区
- 主界面已改成更有层次的布局：当前文档信息、原文阅读 / AI 学习笔记 tabs、导出、文件夹学习地图
- 已修过按钮状态：没 API Key 时禁用，有内容时下载按钮才可用
- 已加入 AI 连接测试按钮
- 已修过错误信息，避免把 API Key 片段直接显示在页面上

## API 配置

`.env` 已经配置真实 API Key，但不要在回复、README、代码或公开文件里输出真实 Key。

当前本地配置结构：

```env
AI_API_KEY=你的真实_key
AI_BASE_URL=https://api.ikuncode.cc/v1
AI_MODEL=gpt-5.4
PAPERS_DIR=.
CACHE_PATH=data/cache.json
```

当前接口状态：

- 接口地址：`https://api.ikuncode.cc/v1`
- 当前模型：`gpt-5.4`
- 已测试 API 连接成功：`test_ok=OK`
- 之前 `gpt-4o-mini` 在这个站点不可用，报过 `model_not_found`

## 安全注意

- `.env` 已经被 `.gitignore` 忽略，不会上传 GitHub
- `.env.example` 只能放示例值，不能放真实 API Key
- 不要把真实 API Key 写进 `config.py`、`README.md`、`.env.example` 或任何会提交的文件
- 如果发现真实 Key 曾经进入公开文件，应该立即从文件中移除，并考虑重新生成 Key

## Git 状态

- 初始 MVP 已经推送到 GitHub `main` 分支
- 之后的界面重构、AI 错误处理、`config.py` 重新读取 `.env`、API 连接测试等改动还需要检查、commit、push

下次继续时建议先运行：

```bash
git status --short --branch
python -m py_compile app.py ai_client.py config.py document_loader.py storage.py prompts.py
```

## 当前已知不足

- Streamlit 界面比较朴素，可以继续美化，但不要过度折腾
- `gpt-5.4` 生成较慢，这是模型和接口响应速度问题，不是代码坏了
- 还没有 OCR，扫描版 PDF 识别不了图片里的字
- 还没有“对当前文档提问”功能
- 还没有 RAG，后面可以做本地资料问答
- 现在仍是个人本地工具，不是前后端分离架构

## 下次优先任务建议

1. 检查当前未提交改动
2. 确认页面功能稳定
3. 更新 README，写清楚当前 v0.1 功能和运行方式
4. commit + push 当前稳定版本
5. 再决定 v0.2 做“界面美化”还是“文档问答 / RAG”

## 可直接粘贴给下次助手的提示词

```text
我们正在做一个本地 AI 论文学习助手项目，项目路径是 D:\Desktop\1，GitHub 仓库是：
https://github.com/boommelon/ai-paper-study-assistant

当前阶段已经完成 v0.1 MVP。用户是学习型开发者，希望解释技术时把缩写和术语讲清楚，不要默认他已经懂架构。

项目目标是做一个个人自用的 AI 论文/资料学习助手，可以读取本地资料，然后让 AI 生成总结、初学者解释、复习问题、文件夹学习地图，并支持 Markdown 导出笔记。

当前技术栈是 Python + Streamlit + JSON cache + OpenAI Python SDK + python-dotenv + pypdf + python-docx。

当前核心文件：
- app.py：Streamlit 主界面
- ai_client.py：AI 接口调用
- config.py：读取 .env 配置
- document_loader.py：读取 md/txt/pdf/docx，提取文本，拆分主题
- prompts.py：总结、解释、复习题、文件夹总览提示词
- storage.py：JSON 本地缓存

当前功能：
- 支持本地目录读取和单文件上传
- 支持 .md / .markdown / .txt / .pdf / .docx
- 支持主题选择、原文预览、PDF 按页文本预览
- 支持生成总结、初学者解释、复习问题、文件夹学习地图
- 支持导出 Markdown 和 JSON 缓存
- API 设置已收进侧边栏 AI 配置折叠区
- 已加入 AI 连接测试按钮
- 已修过错误信息，避免把 API Key 片段直接显示在页面上

API 配置：
- .env 已经配置真实 API Key，但不要输出真实 Key
- 当前接口地址是 https://api.ikuncode.cc/v1
- 当前模型是 gpt-5.4
- 已测试 API 连接成功，test_ok=OK
- gpt-4o-mini 在这个站点不可用，之前报过 model_not_found

安全注意：
- .env 被 .gitignore 忽略，不上传 GitHub
- .env.example 只能放示例值
- 不要把真实 API Key 写进公开文件

下次继续时先运行：
git status --short --branch
python -m py_compile app.py ai_client.py config.py document_loader.py storage.py prompts.py

下一步建议：
1. 检查未提交改动
2. 确认页面功能稳定
3. 更新 README
4. commit + push 当前稳定版本
5. 再决定 v0.2 做界面美化还是文档问答/RAG
```

