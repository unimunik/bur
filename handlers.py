import logging
import random
import time
from collections import defaultdict, deque
from typing import Deque, Dict, List

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config_manager import ConfigManager
from generator import MemeGenerator

logger = logging.getLogger(__name__)


class AntiSpamGuard:
    """Простая защита от спама: ограничивает частоту ответов бота."""

    def __init__(self, cooldown_sec: float = 4.0) -> None:
        self.cooldown_sec = cooldown_sec
        self._last_response_by_chat: Dict[int, float] = {}

    def can_reply(self, chat_id: int) -> bool:
        now = time.monotonic()
        last = self._last_response_by_chat.get(chat_id, 0.0)
        if now - last < self.cooldown_sec:
            return False
        self._last_response_by_chat[chat_id] = now
        return True


def setup_handlers(
    config_manager: ConfigManager,
    generator: MemeGenerator,
    bot_username: str,
) -> Router:
    router = Router()
    history: Dict[int, Deque[str]] = defaultdict(lambda: deque(maxlen=60))
    antispam = AntiSpamGuard()

    @router.message(Command(commands=["бур"]))
    async def bur_command(message: Message) -> None:
        cfg = config_manager.get(message.chat.id)
        recent: List[str] = list(history[message.chat.id])[-cfg.analysis_window :]
        reply = generator.generate_from_messages(recent, chaos_mode=cfg.chaos_mode)
        await message.reply(reply)

    @router.message(Command(commands=["бурик"]))
    async def burik_command(message: Message) -> None:
        await message.reply(generator.random_phrase())

    @router.message(Command(commands=["режим"]))
    async def mode_command(message: Message) -> None:
        cfg = config_manager.get(message.chat.id)
        mode = "хаос" if cfg.chaos_mode else "обычный"
        await message.reply(f"Текущий режим: {mode}")

    @router.message(Command(commands=["настройки"]))
    async def settings_command(message: Message) -> None:
        cfg = config_manager.get(message.chat.id)
        text = (
            "Настройки чата:\n"
            f"• Шанс случайного ответа: {cfg.random_reply_chance:.0%}\n"
            f"• Длина анализа: {cfg.analysis_window} сообщений\n"
            f"• Хаос-режим: {'включен' if cfg.chaos_mode else 'выключен'}"
        )
        await message.reply(text)

    @router.message(Command(commands=["хаос"]))
    async def chaos_toggle(message: Message) -> None:
        cfg = config_manager.get(message.chat.id)
        new_value = not cfg.chaos_mode
        config_manager.update(message.chat.id, chaos_mode=new_value)
        await message.reply(f"Хаос-режим {'включен' if new_value else 'выключен'}")

    @router.message(F.text)
    async def collect_and_maybe_reply(message: Message) -> None:
        if message.chat.type not in {"group", "supergroup"}:
            return
        if message.from_user and message.from_user.is_bot:
            return

        text = message.text.strip()
        history[message.chat.id].append(text)

        cfg = config_manager.get(message.chat.id)

        mention_hit = f"@{bot_username.lower()}" in text.lower()
        should_random_reply = random.random() < cfg.random_reply_chance
        if cfg.chaos_mode:
            should_random_reply = should_random_reply or (random.random() < 0.03)

        if not (mention_hit or should_random_reply):
            return

        if not antispam.can_reply(message.chat.id):
            logger.debug("Антиспам: пропущен ответ в chat_id=%s", message.chat.id)
            return

        recent = list(history[message.chat.id])[-cfg.analysis_window :]
        reply = generator.generate_from_messages(recent, chaos_mode=cfg.chaos_mode)
        await message.reply(reply)

    return router
