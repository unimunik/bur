import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class ChatConfig:
    random_reply_chance: float = 0.04
    analysis_window: int = 10
    chaos_mode: bool = False


class ConfigManager:
    """Управляет настройками чатов в JSON-файле."""

    def __init__(self, path: str = "chat_configs.json") -> None:
        self.path = Path(path)
        self._lock = Lock()
        self._configs: Dict[str, ChatConfig] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            logger.info("Файл конфигурации не найден, будет создан новый: %s", self.path)
            return

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for chat_id, data in raw.items():
                self._configs[chat_id] = ChatConfig(
                    random_reply_chance=float(data.get("random_reply_chance", 0.04)),
                    analysis_window=max(5, min(20, int(data.get("analysis_window", 10)))),
                    chaos_mode=bool(data.get("chaos_mode", False)),
                )
            logger.info("Загружено %d конфигураций чатов", len(self._configs))
        except Exception as exc:
            logger.exception("Ошибка загрузки конфигурации: %s", exc)

    def _save(self) -> None:
        with self._lock:
            payload = {chat_id: asdict(cfg) for chat_id, cfg in self._configs.items()}
            self.path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def get(self, chat_id: int) -> ChatConfig:
        key = str(chat_id)
        if key not in self._configs:
            self._configs[key] = ChatConfig()
            self._save()
        return self._configs[key]

    def update(self, chat_id: int, **kwargs) -> ChatConfig:
        cfg = self.get(chat_id)

        if "random_reply_chance" in kwargs:
            chance = float(kwargs["random_reply_chance"])
            cfg.random_reply_chance = max(0.0, min(1.0, chance))

        if "analysis_window" in kwargs:
            window = int(kwargs["analysis_window"])
            cfg.analysis_window = max(5, min(20, window))

        if "chaos_mode" in kwargs:
            cfg.chaos_mode = bool(kwargs["chaos_mode"])

        self._configs[str(chat_id)] = cfg
        self._save()
        return cfg
