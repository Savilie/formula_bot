from dotenv import load_dotenv
import os
import logging

load_dotenv()


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_UID = [int(uid.strip()) for uid in os.getenv("ADMIN_UID").split(",")]

    # MySQL настройки
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")


settings = Settings()

logger.info(str(settings.ADMIN_UID))
