# AI 论文学习助手

一个本地自用的 MVP 工具：读取你的本地资料文件，让 AI 生成总结、初学者解释和复习问题。

## 运行方式

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置 API Key：

复制 `.env.example` 为 `.env`，填入你的 `AI_API_KEY`。

3. 启动：

```bash
streamlit run app.py
```

## 当前功能

- 读取本地文件夹
- 上传单个资料文件
- 支持 `.md` / `.txt` / `.pdf` / `.docx`
- 生成总结
- 生成初学者解释
- 生成复习问题
- PDF 按页预览文本
- 导出当前学习笔记为 Markdown
- 一键生成当前文件夹总览
- 用 `data/cache.json` 缓存生成结果

## 注意事项

- 旧式 `.doc` 暂不支持，请先另存为 `.docx`。
- 扫描版 PDF 如果提取不出文字，通常需要先做 OCR。
- 文件夹总览最多先读取前 30 个支持文件的内容摘要，避免一次输入过长。

## 目录说明

- `app.py`：本地网页界面
- `document_loader.py`：读取多格式文件、提取文本、拆分主题
- `ai_client.py`：调用 AI 接口
- `prompts.py`：总结、解释、复习题、文件夹总览提示词
- `storage.py`：本地 JSON 缓存
- `.env.example`：配置模板
