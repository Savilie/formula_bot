from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from bot.database import get_db

from bot.keyboards.reply import main_kb
from bot.models import User

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    welcome_text = """
Привет! Я бот-портфолио. Вот что я умею:

• Показывать примеры работ
• Давать контакты для связи

Выбери нужный вариант ниже 👇
"""

    db = next(get_db())

    # Проверяем, есть ли пользователь в базе
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if not user:
        # Добавляем нового пользователя
        new_user = User(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
        db.add(new_user)
        db.commit()

    await message.answer(welcome_text, reply_markup=main_kb(message.from_user.id))


@router.message(F.text == "Назад")
async def back(message: Message):
    await start(message)
