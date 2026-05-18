from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

from ai_client import AIClient
from config import get_settings
from document_loader import (
    SUPPORTED_EXTENSIONS,
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


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
        }

        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
        }

        div[data-testid="stMetric"] label {
            color: #475569;
            font-size: 0.86rem;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }

        .section-note {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: -0.45rem;
            margin-bottom: 0.75rem;
        }

        .status-strip {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            background: #ffffff;
            color: #334155;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_cache_key(relative_path: str, topic_id: str, content: str) -> str:
    return f"{relative_path}::{topic_id}::{content_hash(content)}"


def resolve_folder_path(folder_input: str) -> Path:
    folder = Path(folder_input).expanduser()
    if not folder.is_absolute():
        folder = (Path(__file__).resolve().parent / folder).resolve()
    return folder


def render_action_notice() -> None:
    notice = st.session_state.pop("action_notice", "")
    if notice:
        st.success(notice)


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


def render_sidebar(
    settings,
    client: AIClient,
) -> tuple[str, Path, str, Path | None, object | None, SourceFile | None, list[SourceFile]]:
    selected_relative_path = ""
    selected_path: Path | None = None
    uploaded_file = None
    source_file: SourceFile | None = None
    files: list[SourceFile] = []

    with st.sidebar:
        st.title("学习资料")
        source_mode = st.radio(
            "资料来源",
            ["本地目录", "上传文件"],
            horizontal=True,
            index=0 if st.session_state["source_mode"] == "本地目录" else 1,
        )
        st.session_state["source_mode"] = source_mode

        supported_text = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        st.caption(f"支持格式：{supported_text}")

        papers_dir = resolve_folder_path(st.session_state["source_root"])

        if source_mode == "本地目录":
            folder_input = st.text_input(
                "资料文件夹路径",
                value=str(papers_dir),
            )
            st.session_state["source_root"] = folder_input
            recursive = st.checkbox("包含子文件夹", value=False)
            papers_dir = resolve_folder_path(folder_input)

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
                "上传资料文件",
                type=[ext.lstrip(".") for ext in sorted(SUPPORTED_EXTENSIONS)],
            )
            if uploaded_file is None:
                st.info("请先上传一个文件。")
            else:
                selected_relative_path = f"uploaded/{uploaded_file.name}"

        st.divider()
        with st.expander("AI 配置", expanded=False):
            st.text_input("模型", value=settings.ai_model, disabled=True)
            st.text_input("接口地址", value=settings.ai_base_url, disabled=True)
            if settings.ai_api_key:
                st.success("已读取 API Key（未自动验证）")
                if st.button("测试 API 连接", use_container_width=True):
                    with st.spinner("正在测试 API 连接..."):
                        try:
                            result = client.test_connection()
                        except Exception as exc:
                            st.error(str(exc))
                        else:
                            st.success(f"连接成功：{result}")
            else:
                st.error("还没有配置 API Key")
                st.caption("复制 `.env.example` 为 `.env`，然后填写 `AI_API_KEY`。")

    return (
        source_mode,
        papers_dir,
        selected_relative_path,
        selected_path,
        uploaded_file,
        source_file,
        files,
    )


def generate_task(
    client: AIClient,
    cache: JsonCache,
    cache_key: str,
    task: str,
    label: str,
    topic_title: str,
    topic_content: str,
    meta: dict[str, str],
    model: str,
) -> None:
    with st.spinner(f"正在生成{label}..."):
        try:
            result = client.generate(task, topic_title, topic_content)
        except Exception as exc:
            st.error(f"生成失败：{exc}")
            return

    cache.set(cache_key, task, result, model=model, meta=meta)
    st.session_state["action_notice"] = f"已生成：{label}"
    st.rerun()


def generate_all_tasks(
    client: AIClient,
    cache: JsonCache,
    cache_key: str,
    topic_title: str,
    topic_content: str,
    meta: dict[str, str],
    model: str,
) -> None:
    with st.spinner("正在生成全部学习笔记..."):
        for task, label in TASK_LABELS.items():
            try:
                result = client.generate(task, topic_title, topic_content)
            except Exception as exc:
                st.error(f"生成「{label}」失败：{exc}")
                return
            cache.set(cache_key, task, result, model=model, meta=meta)

    st.session_state["action_notice"] = "已生成全部学习笔记。"
    st.rerun()


def build_folder_source_text(root_dir: Path, max_files: int) -> tuple[str, int]:
    files = list_source_files(root_dir, recursive=True)
    summary_lines: list[str] = []

    for file in files[:max_files]:
        try:
            doc = read_document(file.path)
            snippet = " ".join(doc.content.split())[:280]
        except Exception:
            snippet = ""
        summary_lines.append(f"- {file.relative_path}: {snippet}")

    return "\n".join(summary_lines), len(files)


def render_folder_overview(
    client: AIClient,
    source_mode: str,
    root_dir: Path,
) -> None:
    st.subheader("文件夹学习地图")
    st.markdown(
        '<div class="section-note">把当前文件夹里的资料合成一个整体学习路线。</div>',
        unsafe_allow_html=True,
    )

    if source_mode != "本地目录":
        st.info("切换到本地目录后，可以生成整个文件夹的学习地图。")
        return

    col_a, col_b, col_c = st.columns([1, 1, 1.25])
    with col_a:
        max_files = st.slider("读取文件数", min_value=5, max_value=50, value=30, step=5)
    with col_b:
        generate_clicked = st.button(
            "生成学习地图",
            use_container_width=True,
            disabled=not client.ready,
            key="generate_folder_overview",
        )
    with col_c:
        if not client.ready:
            st.warning("需要 API Key 后才能生成。")

    if generate_clicked:
        source_text, total_files = build_folder_source_text(root_dir, max_files)
        if not source_text.strip():
            st.warning("这个目录里没有可用于总览的资料文件。")
        else:
            with st.spinner("正在生成文件夹学习地图..."):
                try:
                    folder_result = client.generate_prompt(
                        build_user_prompt(
                            "folder_summary",
                            "文件夹总览",
                            source_text,
                        ),
                        temperature=0.3,
                    )
                except Exception as exc:
                    st.error(f"学习地图生成失败：{exc}")
                else:
                    st.session_state["folder_overview"] = folder_result
                    st.session_state["folder_overview_name"] = str(root_dir)
                    st.session_state["folder_overview_meta"] = (
                        f"{min(total_files, max_files)} / {total_files} 个文件"
                    )
                    st.session_state["action_notice"] = "已生成文件夹学习地图。"
                    st.rerun()

    overview = st.session_state.get("folder_overview", "")
    if not overview:
        st.info("还没有生成文件夹学习地图。")
        return

    st.caption(
        f"{st.session_state.get('folder_overview_name', root_dir)} | "
        f"{st.session_state.get('folder_overview_meta', '')}"
    )
    st.markdown(overview)

    actions = st.columns([1, 1, 2])
    with actions[0]:
        st.download_button(
            "下载学习地图",
            data=overview,
            file_name="folder_overview.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_folder_overview",
        )
    with actions[1]:
        if st.button("清空学习地图", use_container_width=True, key="clear_folder_overview"):
            st.session_state["folder_overview"] = ""
            st.session_state["folder_overview_name"] = ""
            st.session_state["folder_overview_meta"] = ""
            st.session_state["action_notice"] = "已清空文件夹学习地图。"
            st.rerun()


def main() -> None:
    inject_styles()
    settings = get_settings()
    cache = JsonCache(settings.cache_path)
    client = AIClient(settings)

    if "folder_overview" not in st.session_state:
        st.session_state["folder_overview"] = ""
    if "folder_overview_name" not in st.session_state:
        st.session_state["folder_overview_name"] = ""
    if "folder_overview_meta" not in st.session_state:
        st.session_state["folder_overview_meta"] = ""
    if "source_root" not in st.session_state:
        st.session_state["source_root"] = str(settings.papers_dir)
    if "source_mode" not in st.session_state:
        st.session_state["source_mode"] = "本地目录"

    (
        source_mode,
        papers_dir,
        selected_relative_path,
        selected_path,
        uploaded_file,
        source_file,
        files,
    ) = render_sidebar(settings, client)

    st.title("AI 论文学习助手")
    st.caption("把论文、笔记和资料整理成可复习的学习笔记。")
    render_action_notice()

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

    st.subheader("当前文档")
    selected_topic_label = st.selectbox("选择主题", list(topic_options.keys()))
    selected_topic = topic_options[selected_topic_label]

    metrics = st.columns(4)
    metrics[0].metric("当前文件", Path(selected_relative_path).name)
    metrics[1].metric("主题数量", str(len(topics)))
    metrics[2].metric("当前主题字数", f"{len(selected_topic.content)}")
    metrics[3].metric("资料数量", str(len(files)) if source_mode == "本地目录" else "1")

    if source_file:
        st.markdown(
            f'<div class="status-strip">来源：{escape(source_file.relative_path)} | '
            f'格式：{escape(source_file.extension)} | 大小：{source_file.size} 字节</div>',
            unsafe_allow_html=True,
        )

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

    st.divider()
    reader_tab, notes_tab = st.tabs(["原文阅读", "AI 学习笔记"])

    with reader_tab:
        st.subheader("原文阅读")
        st.markdown(
            f'<div class="section-note">{selected_relative_path} | '
            f'{len(selected_topic.content)} 字符</div>',
            unsafe_allow_html=True,
        )
        st.markdown(selected_topic.content)

        if document.pages:
            with st.expander("PDF 页预览", expanded=False):
                render_pdf_preview(document.pages)

    with notes_tab:
        st.subheader("AI 学习笔记")
        if not client.ready:
            st.info("AI 生成功能暂不可用。打开侧边栏的 AI 配置查看状态。")

        if st.button(
            "生成全部",
            use_container_width=True,
            disabled=not client.ready,
            key="generate_all_notes",
        ):
            generate_all_tasks(
                client,
                cache,
                cache_key,
                selected_topic.title,
                selected_topic.content,
                meta,
                settings.ai_model,
            )

        task_cols = st.columns(len(TASK_LABELS))
        for task_col, (task, label) in zip(task_cols, TASK_LABELS.items()):
            with task_col:
                cached = cache.get(cache_key, task)
                button_label = f"更新{label}" if cached else f"生成{label}"
                if st.button(
                    button_label,
                    use_container_width=True,
                    disabled=not client.ready,
                    key=f"generate_{task}",
                ):
                    cache.delete_task(cache_key, task)
                    generate_task(
                        client,
                        cache,
                        cache_key,
                        task,
                        label,
                        selected_topic.title,
                        selected_topic.content,
                        meta,
                        settings.ai_model,
                    )

        tabs = st.tabs(list(TASK_LABELS.values()))

        current_outputs: dict[str, str] = {}
        for tab, (task, label) in zip(tabs, TASK_LABELS.items()):
            with tab:
                current_outputs[task] = render_output(cache, cache_key, task, label)

        st.divider()
        st.subheader("导出笔记")
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
        has_export_content = include_source or any(
            value.strip() for value in current_outputs.values()
        )
        if not has_export_content:
            st.info("先生成至少一类 AI 笔记，或勾选“导出时包含原文”。")
        st.download_button(
            "下载 Markdown",
            data=export_text,
            file_name=export_name,
            mime="text/markdown",
            use_container_width=True,
            disabled=not has_export_content,
            key="download_learning_notes",
        )

    st.divider()
    render_folder_overview(client, source_mode, papers_dir)


if __name__ == "__main__":
    main()
