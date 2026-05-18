from __future__ import annotations


TASK_LABELS = {
    "summary": "总结",
    "beginner": "初学者解释",
    "questions": "复习问题",
}


SYSTEM_PROMPT = """你是一个耐心、准确的 AI 论文学习助手。
你的目标是帮助初学者理解论文或学习笔记。
请使用中文回答，保留必要英文术语，并在第一次出现时用括号解释。
不要编造原文没有的信息；如果内容不足，请明确说明。
输出使用 Markdown，结构清楚，适合直接保存成学习笔记。"""


PROMPTS = {
    "summary": """请总结下面的论文/主题内容。

请按这个结构输出：

## 一句话总结

## 核心问题

## 关键方法

## 重要概念

## 适合继续学习的方向

标题：{title}

内容：
{content}
""",
    "beginner": """请把下面的论文/主题内容解释给初学者。

要求：
- 少用术语；必须用术语时，配上中文解释。
- 多用直观类比，但不要过度发挥。
- 先讲它想解决什么问题，再讲它大概怎么做。
- 最后给出 3 个学习建议。

标题：{title}

内容：
{content}
""",
    "questions": """请基于下面的论文/主题内容生成复习问题。

请按这个结构输出：

## 基础题
生成 5 个适合初学者的问题。

## 理解题
生成 5 个需要解释原因或比较概念的问题。

## 参考答案
给出简洁答案。答案必须基于原文内容。

标题：{title}

内容：
{content}
""",
    "folder_summary": """请根据下面这些资料文件的标题和摘要，生成一个整体学习总览。

要求：
- 先判断这些资料主要覆盖了哪些主题
- 用初学者能懂的话，概括每个主题的作用
- 列出这批资料最适合的学习路线
- 最后给出 5 个下一步学习建议

请按这个结构输出：

## 资料总览

## 主题分布

## 推荐学习顺序

## 下一步建议

资料列表：
{content}
""",
}


def build_user_prompt(task: str, title: str, content: str) -> str:
    if task not in PROMPTS:
        raise ValueError(f"Unknown task: {task}")
    return PROMPTS[task].format(title=title, content=content)
