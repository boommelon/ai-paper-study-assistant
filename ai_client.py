from __future__ import annotations

from openai import OpenAI

from config import Settings
from prompts import SYSTEM_PROMPT, build_user_prompt


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
        response = self.client.chat.completions.create(
            model=self.settings.ai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        result = response.choices[0].message.content
        return (result or "").strip()

    def _trim(self, content: str) -> str:
        max_chars = self.settings.max_input_chars
        if len(content) <= max_chars:
            return content
        return (
            content[:max_chars]
            + "\n\n[提示：原文较长，当前 MVP 只截取了前半部分用于生成。]"
        )
