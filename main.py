from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import contact
from bot.config.settings import settings
from bot.database import init_db
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Инициализация базы данных
        init_db()

        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML)
        )

        dp = Dispatcher()

        # Импорт и подключение роутеров
        from bot.handlers import admin, portfolio, start, contacts
        dp.include_router(start.router)
        dp.include_router(admin.router)
        dp.include_router(portfolio.router)
        dp.include_router(contacts.router)
        logger.info("Бот запущен")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())