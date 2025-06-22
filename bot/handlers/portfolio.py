from aiogram import F, Router, types
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.database import get_db
from bot.models import PortfolioItem
import os

router = Router()


# Состояния для пагинации
class PortfolioStates(StatesGroup):
    viewing = State()  # Состояние просмотра портфолио


# Клавиатура для навигации
def get_portfolio_keyboard(current_index: int, total_items: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"prev_{current_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{total_items}", callback_data="count"),
            InlineKeyboardButton(text="➡️", callback_data=f"next_{current_index}"),
        ],
        [InlineKeyboardButton(text="Закрыть", callback_data="close_portfolio")]
    ])
    return keyboard


# Обработчик команды "Портфолио"
@router.message(F.text == "Посмотреть портфолио")
async def show_portfolio_start(message: types.Message, state: FSMContext):
    db = next(get_db())
    projects = db.query(PortfolioItem).all()

    if not projects:
        await message.answer("Портфолио пока пустое.")
        return

    # Сохраняем данные в состояние
    await state.update_data(
        projects=[p.__dict__ for p in projects],
        current_index=0,
        total_items=len(projects)
    )
    await state.set_state(PortfolioStates.viewing)

    # Показываем первый проект
    await show_project(message, state)


# Показ конкретного проекта
async def show_project(message: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    projects = data['projects']
    current_index = data['current_index']
    total_items = data['total_items']

    project = projects[current_index]

    try:
        photo = FSInputFile(project['image_url'])
        caption = f"<b>{project['title']}</b>\n\n{project['description']}"

        keyboard = get_portfolio_keyboard(current_index, total_items)

        if isinstance(message, types.CallbackQuery):
            await message.message.edit_media(
                media=types.InputMediaPhoto(
                    media=photo,
                    caption=caption,
                    parse_mode="HTML"
                ),
                reply_markup=keyboard
            )
            await message.answer()
        else:
            await message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        error_msg = f"Ошибка при отображении проекта: {str(e)}"
        if isinstance(message, types.CallbackQuery):
            await message.message.edit_text(error_msg)
        else:
            await message.answer(error_msg)


# Обработка навигации
@router.callback_query(PortfolioStates.viewing, F.data.startswith(("prev_", "next_")))
async def handle_navigation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_index = data['current_index']
    total_items = data['total_items']

    if callback.data.startswith("prev_"):
        new_index = max(0, current_index - 1)
    else:
        new_index = min(total_items - 1, current_index + 1)

    if new_index != current_index:
        await state.update_data(current_index=new_index)
        await show_project(callback, state)
    else:
        await callback.answer()


# Закрытие просмотра
@router.callback_query(F.data == "close_portfolio")
async def close_portfolio(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.answer("Портфолио закрыто")