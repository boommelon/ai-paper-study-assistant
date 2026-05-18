from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from ai_client import AIClient
from config import get_settings
from document_loader import (
    SUPPORTED_EXTENSIONS,
    DocumentContent,
    PdfPage,
    SourceFile,
    content_hash,
    list_source_files,
    read_document,
    read_uploaded_document,
    split_topics,
)
from prompts import TASK_LABELS, build_user_prompt
from storage import JsonCache


st.set_page_config(page_title="AI 论文学习助手", layout="wide")


def build_cache_key(relative_path: str, topic_id: str, content: str) -> str:
    return f"{relative_path}::{topic_id}::{content_hash(content)}"


def render_output(cache: JsonCache, key: str, task: str, label: str) -> str:
    cached = cache.get(key, task)
    if cached:
        st.markdown(cached["content"])
        st.caption(
            f"已缓存：{cached.get('created_at', '未知时间')} | 模型：{cached.get('model', '未知')}"
        )
        return cached["content"]
    st.info(f"还没有生成「{label}」。")
    return ""


def export_markdown(
    source_label: str,
    topic_title: str,
    outputs: dict[str, str],
    content: str,
    include_source: bool,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {source_label}",
        "",
        f"- 生成时间：{now}",
        f"- 主题：{topic_title}",
        "",
    ]

    if include_source:
        lines.extend(["## 原文", "", content.strip(), ""])

    for task_key, title in TASK_LABELS.items():
        value = outputs.get(task_key, "").strip()
        if value:
            lines.extend([f"## {title}", "", value, ""])

    return "\n".join(lines).strip() + "\n"


def render_pdf_preview(pages: list[PdfPage]) -> None:
    if not pages:
        st.info("这个 PDF 没有提取到可显示的文本页。")
        return

    page_labels = [f"第 {page.number} 页" for page in pages]
    selected_page = st.selectbox("查看 PDF 页", page_labels)
    page_index = page_labels.index(selected_page)
    page = pages[page_index]
    st.caption(f"第 {page.number} 页")
    st.text_area("页面文本", value=page.text or "这一页没有提取到文字。", height=260)


def main() -> None:
    settings = get_settings()
    cache = JsonCache(settings.cache_path)

    st.title("AI 论文学习助手")
    st.caption("读取本地资料文件，生成总结、初学者解释和复习问题。")

    if "folder_overview" not in st.session_state:
        st.session_state["folder_overview"] = ""
    if "folder_overview_name" not in st.session_state:
        st.session_state["folder_overview_name"] = ""
    if "source_root" not in st.session_state:
        st.session_state["source_root"] = str(settings.papers_dir)
    if "source_mode" not in st.session_state:
        st.session_state["source_mode"] = "本地目录"

    selected_relative_path = ""
    selected_path: Path | None = None
    uploaded_file = None
    document: DocumentContent | None = None
    source_file: SourceFile | None = None
    papers_dir = Path(st.session_state["source_root"]).expanduser()

    with st.sidebar:
        st.header("资料来源")
        source_mode = st.radio(
            "资料来源",
            ["本地目录", "上传文件"],
            horizontal=True,
            index=0 if st.session_state["source_mode"] == "本地目录" else 1,
        )
        st.session_state["source_mode"] = source_mode
        supported_text = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        st.caption(f"支持格式：{supported_text}")

        if source_mode == "本地目录":
            folder_input = st.text_input(
                "本地资料文件夹路径",
                value=str(papers_dir),
            )
            st.session_state["source_root"] = folder_input
            recursive = st.checkbox("包含子文件夹", value=False)
            papers_dir = Path(folder_input).expanduser()
            if not papers_dir.is_absolute():
                papers_dir = (Path(__file__).resolve().parent / papers_dir).resolve()

            files = list_source_files(papers_dir, recursive=recursive)
            if not files:
                st.warning("这个目录里还没有找到支持的资料文件。")
            else:
                file_options = {
                    f"{file.title} ({file.relative_path})": file for file in files
                }
                selected_label = st.selectbox("选择文档", list(file_options.keys()))
                source_file = file_options[selected_label]
                selected_path = source_file.path
                selected_relative_path = source_file.relative_path
        else:
            uploaded_file = st.file_uploader(
                "上传一个资料文件",
                type=[ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)],
            )
            if uploaded_file is None:
                st.info("请先上传一个文件。")
            else:
                selected_relative_path = f"uploaded/{uploaded_file.name}"

        st.divider()
        st.header("AI 设置")
        st.text_input("模型", value=settings.ai_model, disabled=True)
        st.text_input("接口地址", value=settings.ai_base_url, disabled=True)
        if settings.ai_api_key:
            st.success("已读取 API Key")
        else:
            st.error("还没有配置 API Key")
            st.caption("复制 .env.example 为 .env，然后填写 AI_API_KEY。")

    if source_mode == "本地目录" and selected_path is None:
        st.info("请先在左侧选择一个可读取的本地资料文件。")
        st.stop()
    if source_mode == "上传文件" and uploaded_file is None:
        st.info("请先在左侧上传一个资料文件。")
        st.stop()

    try:
        if source_mode == "本地目录":
            document = read_document(selected_path)
        else:
            document = read_uploaded_document(uploaded_file.name, uploaded_file.getvalue())
    except Exception as exc:
        st.error(f"读取文件失败：{exc}")
        st.stop()

    content = document.content
    if not content.strip():
        st.warning("这个文件没有提取到可用文字。扫描版 PDF 可能需要先做 OCR。")
        st.stop()

    topics = split_topics(content)
    topic_options = {
        f"{index + 1}. {topic.title}": topic for index, topic in enumerate(topics)
    }
    selected_topic_label = st.selectbox("选择主题", list(topic_options.keys()))
    selected_topic = topic_options[selected_topic_label]

    cache_key = build_cache_key(
        selected_relative_path,
        selected_topic.id,
        selected_topic.content,
    )
    meta = {
        "file": selected_relative_path,
        "topic": selected_topic.title,
        "topic_id": selected_topic.id,
    }

    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.subheader("原文")
        st.caption(f"{selected_relative_path} | {len(selected_topic.content)} 字符")
        st.markdown(selected_topic.content)

        if document.pages:
            with st.expander("PDF 页预览", expanded=False):
                render_pdf_preview(document.pages)

    with right:
        st.subheader("AI 学习笔记")
        client = AIClient(settings)

        button_cols = st.columns(3)
        for index, (task, label) in enumerate(TASK_LABELS.items()):
            with button_cols[index]:
                if st.button(label, use_container_width=True, disabled=not client.ready):
                    with st.spinner(f"正在生成{label}..."):
                        try:
                            result = client.generate(
                                task, selected_topic.title, selected_topic.content
                            )
                        except Exception as exc:
                            st.error(f"生成失败：{exc}")
                        else:
                            cache.set(
                                cache_key,
                                task,
                                result,
                                model=settings.ai_model,
                                meta=meta,
                            )
                            st.rerun()

        regen_label = st.selectbox("选择要重新生成的内容", list(TASK_LABELS.values()))
        regen_task = next(task for task, label in TASK_LABELS.items() if label == regen_label)

        if st.button("重新生成", disabled=not client.ready):
            cache.delete_task(cache_key, regen_task)
            with st.spinner("正在重新生成..."):
                try:
                    result = client.generate(
                        regen_task, selected_topic.title, selected_topic.content
                    )
                except Exception as exc:
                    st.error(f"生成失败：{exc}")
                else:
                    cache.set(
                        cache_key,
                        regen_task,
                        result,
                        model=settings.ai_model,
                        meta=meta,
                    )
                    st.rerun()

        tabs = st.tabs(
            [TASK_LABELS["summary"], TASK_LABELS["beginner"], TASK_LABELS["questions"]]
        )

        current_outputs: dict[str, str] = {}
        for tab, task in zip(tabs, TASK_LABELS.keys()):
            with tab:
                current_outputs[task] = render_output(
                    cache, cache_key, task, TASK_LABELS[task]
                )

        st.divider()
        st.subheader("导出")
        include_source = st.checkbox("导出时包含原文", value=False)
        export_name = st.text_input(
            "导出文件名",
            value=f"{Path(selected_relative_path).stem}_learning_notes.md",
        )
        export_text = export_markdown(
            selected_relative_path,
            selected_topic.title,
            current_outputs,
            selected_topic.content,
            include_source,
        )
        st.download_button(
            "下载 Markdown",
            data=export_text,
            file_name=export_name,
            mime="text/markdown",
            use_container_width=True,
        )

    st.divider()
    st.subheader("文件夹总览")
    st.caption("把当前目录里找到的资料先做一个整体学习地图。")
    if source_mode == "本地目录" and selected_path is not None:
        if st.button("生成当前文件夹总览", disabled=not client.ready):
            root_dir = Path(st.session_state["source_root"]).expanduser()
            if not root_dir.is_absolute():
                root_dir = (Path(__file__).resolve().parent / root_dir).resolve()
            files = list_source_files(root_dir, recursive=True)
            if not files:
                st.warning("这个目录里没有可用于总览的资料文件。")
            else:
                summary_lines = []
                for file in files[:30]:
                    try:
                        doc = read_document(file.path)
                        snippet = " ".join(doc.content.split())[:280]
                    except Exception:
                        snippet = ""
                    summary_lines.append(f"- {file.relative_path}: {snippet}")
                with st.spinner("正在生成文件夹总览..."):
                    try:
                        folder_result = client.generate_prompt(
                            build_user_prompt(
                                "folder_summary",
                                "文件夹总览",
                                "\n".join(summary_lines),
                            ),
                            temperature=0.3,
                        )
                    except Exception as exc:
                        st.error(f"总览生成失败：{exc}")
                    else:
                        st.session_state["folder_overview"] = folder_result
                        st.session_state["folder_overview_name"] = str(root_dir)
                        st.markdown(folder_result)
                        st.download_button(
                            "下载总览 Markdown",
                            data=folder_result,
                            file_name="folder_overview.md",
                            mime="text/markdown",
                            key="folder_overview_download",
                        )
        if st.session_state["folder_overview"]:
            st.markdown(st.session_state["folder_overview"])
    else:
        st.info("切换到“本地目录”后，可以一键生成整个文件夹的总览。")


if __name__ == "__main__":
    main()
