# AI 论文学习助手

个人自用的本地 AI 论文 / 资料学习助手。读取本地资料文件，让 AI 生成总结、初学者解释、复习问题和文件夹学习地图，支持 Markdown 导出笔记。

当前版本：**v0.1 MVP**

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API 配置：

```bash
cp .env.example .env
```

需要填写的字段：

- `AI_API_KEY`：你的 API Key
- `AI_BASE_URL`：API 接口地址（兼容 OpenAI 格式）
- `AI_MODEL`：使用的模型名称
- `PAPERS_DIR`：默认读取的本地资料目录（默认为当前目录）
- `CACHE_PATH`：缓存文件路径（默认 `data/cache.json`）

### 3. 启动

```bash
streamlit run app.py
```

启动后浏览器会自动打开本地页面。

## 功能列表

### 资料读取

- 支持读取本地文件夹中的资料
- 支持单文件上传
- 支持格式：`.md` / `.markdown` / `.txt` / `.pdf` / `.docx`
- PDF 支持按页文本预览

### AI 学习笔记

- 生成总结
- 生成初学者解释（把术语讲清楚）
- 生成复习问题
- 文件夹学习地图（一键总览当前目录所有资料的关系）

### 主题与导航

- 自动拆分文档主题，支持按主题选择学习
- 主界面分为「原文阅读」和「AI 学习笔记」两个 Tab

### 导出与缓存

- 导出当前学习笔记为 Markdown 文件
- JSON 本地缓存，避免重复调用 AI 生成

### 配置与安全

- API 设置收纳在侧边栏「AI 配置」折叠区
- 内置 AI 连接测试按钮，一键验证 API 是否可用
- 错误信息不会泄露 API Key 片段

## 注意事项

- 旧式 `.doc` 暂不支持，请先另存为 `.docx`
- 扫描版 PDF 如果提取不出文字，需要先做 OCR（当前版本不含 OCR）
- 文件夹学习地图最多读取前 30 个文件的内容摘要，避免输入过长
- AI 生成速度取决于所用模型和接口响应，不是程序问题

## 目录说明

| 文件 | 用途 |
|------|------|
| `app.py` | Streamlit 主界面 |
| `ai_client.py` | AI 接口调用 |
| `config.py` | 读取 `.env` 配置 |
| `document_loader.py` | 读取多格式文件、提取文本、拆分主题 |
| `prompts.py` | 总结、解释、复习题、文件夹总览提示词 |
| `storage.py` | JSON 本地缓存 |
| `requirements.txt` | Python 依赖列表 |
| `.env.example` | 配置模板（可提交） |
| `.env` | 本地真实配置（不提交） |

## 技术栈

- Python
- Streamlit（本地 Web 界面）
- OpenAI Python SDK（兼容 OpenAI 格式的 API）
- pypdf / python-docx（文档解析）
- python-dotenv（环境变量）

## License

个人学习项目，仅供参考。
