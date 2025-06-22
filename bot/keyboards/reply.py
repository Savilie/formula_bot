from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from bot.config.settings import settings


def main_kb(user_id: int | None = None) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Посмотреть портфолио")
    builder.button(text="Контакты")

    if user_id and user_id == settings.ADMIN_UID:
        builder.button(text="Админ-панель")

    builder.adjust(1, 2)  # 1 кнопка в первом ряду, 2 во втором
    return builder.as_markup(resize_keyboard=True)


# админка
def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Добавить проект")
    builder.button(text="Удалить проект")
    builder.button(text="Редактировать контакты")
    builder.button(text="Сделать рассылку")
    builder.button(text="В главное меню")
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)