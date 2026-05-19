from __future__ import annotations

import re

from openai import OpenAI

from config import Settings
from prompts import SYSTEM_PROMPT, build_user_prompt


class AIClientError(RuntimeError):
    pass


class AIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url or None,
        )

    @property
    def ready(self) -> bool:
        return bool(self.settings.ai_api_key)

    def generate(self, task: str, title: str, content: str) -> str:
        return self.generate_prompt(build_user_prompt(task, title, self._trim(content)))

    def generate_prompt(self, prompt: str, temperature: float = 0.3) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.settings.ai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
        except Exception as exc:
            raise AIClientError(format_ai_error(exc)) from exc
        result = response.choices[0].message.content
        return (result or "").strip()

    def test_connection(self) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are a connection test."},
                    {"role": "user", "content": "请只回复 OK。"},
                ],
                temperature=0,
                max_tokens=8,
            )
        except Exception as exc:
            raise AIClientError(format_ai_error(exc)) from exc

        result = (response.choices[0].message.content or "").strip()
        return result or "OK"

    def _trim(self, content: str) -> str:
        max_chars = self.settings.max_input_chars
        if len(content) <= max_chars:
            return content
        return (
            content[:max_chars]
            + "\n\n[提示：原文较长，当前 MVP 只截取了前半部分用于生成。]"
        )


def format_ai_error(exc: Exception) -> str:
    raw = _hide_api_keys(str(exc))
    lower = raw.lower()

    if "401" in raw or "invalid_api_key" in lower or "incorrect api key" in lower:
        return (
            "API Key 验证失败。请重新生成一个有效 Key，确认它属于当前接口地址，"
            "然后更新 `.env` 里的 `AI_API_KEY`。"
        )
    if "model" in lower and ("not found" in lower or "does not exist" in lower):
        return "模型不可用。请检查 `.env` 里的 `AI_MODEL` 是否写对，以及账号是否有这个模型权限。"
    if "rate" in lower or "quota" in lower or "insufficient_quota" in lower:
        return "接口额度或频率受限。请检查账号余额、额度或稍后再试。"
    if "connection" in lower or "timeout" in lower:
        return "连接接口失败。请检查网络，以及 `.env` 里的 `AI_BASE_URL` 是否正确。"

    return f"AI 调用失败：{raw}"


def _hide_api_keys(text: str) -> str:
    return re.sub(r"sk-[A-Za-z0-9_\-]{6,}", "sk-***", text)
