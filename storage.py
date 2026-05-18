from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class JsonCache:
    def __init__(self, path: Path):
        self.path = path
        self.data = self._load()

    def get(self, key: str, task: str) -> dict[str, Any] | None:
        return self.data.get("items", {}).get(key, {}).get("outputs", {}).get(task)

    def set(
        self,
        key: str,
        task: str,
        content: str,
        *,
        model: str,
        meta: dict[str, Any],
    ) -> None:
        items = self.data.setdefault("items", {})
        item = items.setdefault(key, {"meta": meta, "outputs": {}})
        item["meta"] = meta
        item.setdefault("outputs", {})[task] = {
            "content": content,
            "model": model,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.save()

    def delete_task(self, key: str, task: str) -> None:
        item = self.data.get("items", {}).get(key)
        if not item:
            return
        item.get("outputs", {}).pop(task, None)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "items": {}}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            backup = self.path.with_suffix(".broken.json")
            try:
                self.path.replace(backup)
            except OSError:
                pass
            return {"version": 1, "items": {}}
