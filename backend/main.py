from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_client import AIClient, AIClientError
from config import get_settings
from document_loader import (
    list_source_files,
    read_document,
    read_uploaded_document,
    split_topics,
    content_hash,
)
from prompts import TASK_LABELS, build_user_prompt
from storage import JsonCache

app = FastAPI(title="AI 论文学习助手 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()
cache = JsonCache(settings.cache_path)
client = AIClient(settings)


def build_cache_key(relative_path: str, topic_id: str, content: str) -> str:
    return f"{relative_path}::{topic_id}::{content_hash(content)}"


# --- 请求/响应模型 ---

class GenerateRequest(BaseModel):
    file_path: str
    topic_id: str
    topic_title: str
    topic_content: str
    task: str


class GenerateAllRequest(BaseModel):
    file_path: str
    topic_id: str
    topic_title: str
    topic_content: str


class FolderMapRequest(BaseModel):
    folder: str
    max_files: int = 30


class ChatRequest(BaseModel):
    question: str
    context: str
    history: list[dict] = []


class ExtractTermsRequest(BaseModel):
    content: str
    title: str = ""


# --- API 路由 ---

@app.get("/api/config")
def get_config():
    return {
        "model": settings.ai_model,
        "base_url": settings.ai_base_url,
        "has_key": bool(settings.ai_api_key),
    }


@app.get("/api/test-connection")
def test_connection():
    try:
        result = client.test_connection()
        return {"ok": True, "message": result}
    except AIClientError as e:
        return {"ok": False, "message": str(e)}


@app.get("/api/files")
def list_files(folder: str = Query(default=""), recursive: bool = Query(default=False)):
    root = Path(folder) if folder else settings.papers_dir
    if not root.is_absolute():
        root = (Path(__file__).resolve().parent / root).resolve()
    files = list_source_files(root, recursive=recursive)
    return [
        {
            "path": str(f.path),
            "relative_path": f.relative_path,
            "title": f.title,
            "size": f.size,
            "extension": f.extension,
        }
        for f in files
    ]


@app.get("/api/document")
def get_document(path: str = Query(...)):
    file_path = Path(path)
    doc = read_document(file_path)
    topics = split_topics(doc.content)
    return {
        "title": doc.title,
        "content": doc.content,
        "pages": [{"number": p.number, "text": p.text} for p in doc.pages] if doc.pages else None,
        "topics": [
            {"id": t.id, "title": t.title, "content": t.content, "level": t.level}
            for t in topics
        ],
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    data = await file.read()
    doc = read_uploaded_document(file.filename, data)
    topics = split_topics(doc.content)
    return {
        "title": doc.title,
        "content": doc.content,
        "filename": file.filename,
        "pages": [{"number": p.number, "text": p.text} for p in doc.pages] if doc.pages else None,
        "topics": [
            {"id": t.id, "title": t.title, "content": t.content, "level": t.level}
            for t in topics
        ],
    }


@app.post("/api/generate")
def generate_note(req: GenerateRequest):
    if req.task not in TASK_LABELS:
        return {"ok": False, "message": f"未知任务类型: {req.task}"}

    cache_key = build_cache_key(req.file_path, req.topic_id, req.topic_content)
    cached = cache.get(cache_key, req.task)
    if cached:
        return {"ok": True, "content": cached["content"], "cached": True, "created_at": cached.get("created_at")}

    try:
        result = client.generate(req.task, req.topic_title, req.topic_content)
    except AIClientError as e:
        return {"ok": False, "message": str(e)}

    meta = {"file": req.file_path, "topic": req.topic_title, "topic_id": req.topic_id}
    cache.set(cache_key, req.task, result, model=settings.ai_model, meta=meta)
    return {"ok": True, "content": result, "cached": False}


@app.post("/api/generate-all")
def generate_all(req: GenerateAllRequest):
    cache_key = build_cache_key(req.file_path, req.topic_id, req.topic_content)
    results = {}
    for task, label in TASK_LABELS.items():
        cached = cache.get(cache_key, task)
        if cached:
            results[task] = {"content": cached["content"], "cached": True}
            continue
        try:
            result = client.generate(task, req.topic_title, req.topic_content)
        except AIClientError as e:
            return {"ok": False, "message": f"生成「{label}」失败: {str(e)}"}
        meta = {"file": req.file_path, "topic": req.topic_title, "topic_id": req.topic_id}
        cache.set(cache_key, task, result, model=settings.ai_model, meta=meta)
        results[task] = {"content": result, "cached": False}
    return {"ok": True, "results": results}


@app.post("/api/folder-map")
def folder_map(req: FolderMapRequest):
    root = Path(req.folder)
    if not root.is_absolute():
        root = (Path(__file__).resolve().parent / root).resolve()

    files = list_source_files(root, recursive=True)
    if not files:
        return {"ok": False, "message": "目录中没有可用资料文件"}

    summary_lines = []
    for f in files[: req.max_files]:
        try:
            doc = read_document(f.path)
            snippet = " ".join(doc.content.split())[:280]
        except Exception:
            snippet = ""
        summary_lines.append(f"- {f.relative_path}: {snippet}")

    source_text = "\n".join(summary_lines)
    try:
        result = client.generate_prompt(
            build_user_prompt("folder_summary", "文件夹总览", source_text),
            temperature=0.3,
        )
    except AIClientError as e:
        return {"ok": False, "message": str(e)}

    return {"ok": True, "content": result, "total_files": len(files), "read_files": min(len(files), req.max_files)}


@app.post("/api/chat")
def chat_with_doc(req: ChatRequest):
    system = (
        "你是一个论文学习助手。用户正在阅读一篇文档，会基于文档内容向你提问。\n"
        "请基于提供的文档内容回答问题。如果文档中没有相关信息，请明确说明。\n"
        "使用中文回答，保留必要英文术语并在首次出现时解释。输出使用 Markdown。"
    )
    messages = [{"role": "system", "content": system}]
    messages.append({"role": "user", "content": f"以下是文档内容：\n\n{req.context[:20000]}"})
    messages.append({"role": "assistant", "content": "好的，我已经阅读了这篇文档。请问你有什么问题？"})

    for msg in req.history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    messages.append({"role": "user", "content": req.question})

    try:
        response = client.client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
            temperature=0.4,
        )
        answer = (response.choices[0].message.content or "").strip()
        return {"ok": True, "answer": answer}
    except Exception as e:
        return {"ok": False, "message": str(e)}


@app.post("/api/extract-terms")
def extract_terms(req: ExtractTermsRequest):
    prompt = (
        "请从以下文档中提取 5-10 个最重要的关键术语或概念。\n"
        "对每个术语，给出：\n"
        "1. 术语名称（中英文）\n"
        "2. 一句话解释（30字以内）\n\n"
        "请用 JSON 数组格式返回，每个元素包含 term 和 explanation 字段。\n"
        "只返回 JSON，不要其他内容。\n\n"
        f"文档标题：{req.title}\n\n"
        f"文档内容：\n{req.content[:15000]}"
    )
    try:
        response = client.client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": "你是一个术语提取助手。只返回 JSON 数组。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        import json
        raw = (response.choices[0].message.content or "").strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        terms = json.loads(raw)
        return {"ok": True, "terms": terms}
    except Exception as e:
        return {"ok": False, "message": str(e), "terms": []}
