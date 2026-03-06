import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.types import ErrorEvent

from config_manager import ConfigManager
from generator import MemeGenerator
from handlers import setup_handlers


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def main() -> None:
    configure_logging()
    logger = logging.getLogger("bur-bot")

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Переменная окружения BOT_TOKEN не установлена")

    bot = Bot(token=token)
    dp = Dispatcher()

    me = await bot.get_me()
    bot_username = me.username or "burik_bot"
    logger.info("Бот запущен как @%s", bot_username)

    config_manager = ConfigManager()
    generator = MemeGenerator()

    dp.include_router(setup_handlers(config_manager, generator, bot_username))

    error_router = Router()

    @error_router.error()
    async def on_error(event: ErrorEvent) -> bool:
        logger.exception("Ошибка обработки апдейта: %s", event.exception)
        return True

    dp.include_router(error_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
