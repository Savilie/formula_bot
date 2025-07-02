from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.database import get_db
from bot.handlers.portfolio import PortfolioStates, show_project
from bot.models import PortfolioItem, User, Contact
from bot.config.settings import settings
from bot.keyboards.reply import get_admin_keyboard, main_kb
import os
from datetime import datetime
router = Router()


# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_UID


# Клавиатура для отмены удаления
def get_cancel_delete_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить удаление", callback_data="cancel_delete")]
    ])


# Клавиатура с кнопкой отмены
def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить добавление")
    return builder.as_markup(resize_keyboard=True)


# Состояния для добавления проекта
class AddPortfolioState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_photo = State()


# Состояния для удаления проекта
class DeletePortfolioState(StatesGroup):
    waiting_for_project_id = State()


# Состояния для рассылки сообщений
class BroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()


# Состояния для редактирования контактов
class EditContactsState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_address = State()
    waiting_for_website = State()


# Обработчик админ-панели
@router.message(Command("admin"))
@router.message(F.text == "Админ-панель")
async def admin_panel(message: types.Message, state: FSMContext | None = None):
    if state:
        await state.clear()  # Очищаем состояние, если оно передано

    if not is_admin(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return

    await message.answer(
        "🔐 Панель администратора:",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )


# Обработчик кнопки "Добавить проект"
@router.message(F.text == "Добавить проект")
async def add_project_command(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "Введите название проекта (или отмените):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AddPortfolioState.waiting_for_title)


# Обработчик отмены
@router.message(
    AddPortfolioState.waiting_for_title,
    F.text == "❌ Отменить добавление"
)
@router.message(
    AddPortfolioState.waiting_for_description,
    F.text == "❌ Отменить добавление"
)
@router.message(
    AddPortfolioState.waiting_for_photo,
    F.text == "❌ Отменить добавление"
)
async def cancel_add_project(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добавление проекта отменено",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )


# Шаг 1: Получаем название проекта
@router.message(AddPortfolioState.waiting_for_title, F.text)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь введите описание проекта:")
    await state.set_state(AddPortfolioState.waiting_for_description)


# Шаг 2: Получаем описание проекта
@router.message(AddPortfolioState.waiting_for_description, F.text)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Теперь отправьте фото проекта:")
    await state.set_state(AddPortfolioState.waiting_for_photo)


# Шаг 3: Получаем фото проекта
@router.message(AddPortfolioState.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    # Создаем папку для загрузок
    os.makedirs("uploads/portfolio", exist_ok=True)

    # Получаем данные из состояния
    data = await state.get_data()

    # Сохраняем фото
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    ext = file.file_path.split(".")[-1]
    filename = f"uploads/portfolio/{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    await message.bot.download_file(file.file_path, filename)

    # Сохраняем в базу данных
    db = next(get_db())
    project = PortfolioItem(
        title=data['title'],
        description=data['description'],
        image_url=filename
    )
    db.add(project)
    db.commit()

    await message.answer(
        "✅ Проект успешно добавлен!\n"
        f"Название: {data['title']}\n"
        f"Описание: {data['description']}",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    await state.clear()


# Обработчик кнопки "Удалить проект"
@router.message(F.text == "Удалить проект")
async def start_deleting_project(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return

    db = next(get_db())
    projects = db.query(PortfolioItem).all()

    if not projects:
        await message.answer("ℹ️ Нет проектов для удаления.", reply_markup=get_admin_keyboard())
        return

    projects_list = "\n".join([f"{p.id}: {p.title}" for p in projects])
    await message.answer(
        f"📋 Список проектов:\n{projects_list}\n\n"
        "Введите ID проекта для удаления или нажмите кнопку отмены:",
        reply_markup=get_cancel_delete_keyboard()
    )
    await state.set_state(DeletePortfolioState.waiting_for_project_id)


# Обработчик отмены удаления
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_project(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Удаление отменено.")
    await admin_panel(callback.message)


# Обработчик ID проекта для удаления
@router.message(DeletePortfolioState.waiting_for_project_id, F.text.regexp(r'^\d+$'))
async def process_delete_project(message: types.Message, state: FSMContext):
    db = next(get_db())
    project_id = int(message.text)
    project = db.query(PortfolioItem).filter(PortfolioItem.id == project_id).first()

    if not project:
        await message.answer("❌ Проект с таким ID не найден!", reply_markup=get_admin_keyboard())
        return

    # Удаляем файл изображения
    try:
        if os.path.exists(project.image_url):
            os.remove(project.image_url)
    except Exception as e:
        print(f"⚠️ Ошибка при удалении файла: {e}")

    # Удаляем проект из БД
    db.delete(project)
    db.commit()

    await message.answer(
        f"✅ Проект '{project.title}' удален!",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    await state.clear()


# Обработчик кнопки "Список проектов"
@router.message(F.text == "Список проектов")
async def show_projects_list(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return

    db = next(get_db())
    projects = db.query(PortfolioItem).all()

    if not projects:
        await message.answer("ℹ️ Портфолио пустое.")
        return

    # Используем ту же систему просмотра, что и для пользователей
    await state.update_data(
        projects=[p.__dict__ for p in projects],
        current_index=0,
        total_items=len(projects)
    )
    await state.set_state(PortfolioStates.viewing)
    await show_project(message, state)


# Обработчик рассылки
@router.message(F.text == "Сделать рассылку")
async def start_broadcast(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Доступ запрещен!")
        return

    await message.answer(
        "✉️ Введите сообщение для рассылки (можно с фото):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(BroadcastState.waiting_for_message)


# Подтвердить / отменить рассылку
@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    # Сохраняем сообщение для рассылки
    if message.photo:
        await state.update_data(
            photo=message.photo[-1].file_id,
            caption=message.caption,
            has_photo=True
        )
    else:
        await state.update_data(
            text=message.text,
            has_photo=False
        )

    # Показываем подтверждение
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Начать рассылку", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
    ])

    if message.photo:
        await message.answer_photo(
            photo=message.photo[-1].file_id,
            caption=f"Подтвердите рассылку этого сообщения:\n\n{message.caption or ''}",
            reply_markup=confirm_keyboard
        )
    else:
        await message.answer(
            f"Подтвердите рассылку этого сообщения:\n\n{message.text}",
            reply_markup=confirm_keyboard
        )

    await state.set_state(BroadcastState.waiting_for_confirmation)


# Подтвердить рассылку
@router.callback_query(BroadcastState.waiting_for_confirmation, F.data == "confirm_broadcast")
async def confirm_broadcast(message: types.Message, callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()  # Убираем кнопки
    data = await state.get_data()
    db = next(get_db())
    users = db.query(User).all()
    success = 0
    errors = 0

    for user in users:
        try:
            if data.get('has_photo'):
                await callback.bot.send_photo(
                    chat_id=user.user_id,
                    photo=data['photo'],
                    caption=data.get('caption', '')
                )
            else:
                await callback.bot.send_message(
                    chat_id=user.user_id,
                    text=data['text']
                )
            success += 1
        except Exception as e:
            errors += 1
            print(f"Ошибка при отправке пользователю {user.user_id}: {e}")

    await callback.message.answer(
        f"✅ Рассылка завершена!\n"
        f"Успешно отправлено: {success}\n"
        f"Не удалось отправить: {errors}",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    await state.clear()


# Отменить рассылку
@router.callback_query(BroadcastState.waiting_for_confirmation, F.data == "cancel_broadcast")
async def cancel_broadcast(message: types.Message, callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Рассылка отменена")
    await callback.message.answer(
        "🔐 Панель администратора:",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    await state.clear()


@router.message(F.text == "Редактировать контакты")
async def start_edit_contacts(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "Введите новый телефон (или отмените):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(EditContactsState.waiting_for_phone)


# Обработчик отмены для контактов
@router.message(
    EditContactsState.waiting_for_phone,
    F.text == "❌ Отменить добавление"
)
@router.message(
    EditContactsState.waiting_for_email,
    F.text == "❌ Отменить добавление"
)
@router.message(
    EditContactsState.waiting_for_address,
    F.text == "❌ Отменить добавление"
)
@router.message(
    EditContactsState.waiting_for_website,
    F.text == "❌ Отменить добавление"
)
async def cancel_edit_contacts(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Редактирование контактов отменено",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )


# Обработчики для каждого поля
# Обработчик поля адреса
@router.message(EditContactsState.waiting_for_phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Теперь введите email:")
    await state.set_state(EditContactsState.waiting_for_email)


@router.message(EditContactsState.waiting_for_email, F.text)
async def process_email(message: types.Message, state: FSMContext):
    if "@" not in message.text:  # Простейшая валидация
        await message.answer("Неверный формат email. Попробуйте еще раз:")
        return

    await state.update_data(email=message.text)
    await message.answer("Теперь введите адрес:")
    await state.set_state(EditContactsState.waiting_for_address)


# Обработчик поля ссылки
@router.message(EditContactsState.waiting_for_address, F.text)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Теперь введите новую ссылку на сайт:")
    await state.set_state(EditContactsState.waiting_for_website)


@router.message(EditContactsState.waiting_for_website, F.text)
async def process_website(message: types.Message, state: FSMContext):
    contact_data = await state.get_data()
    db = next(get_db())

    contacts = db.query(Contact).first()
    if contacts:
        contacts.phone = contact_data['phone']
        contacts.email = contact_data['email']  # Сохраняем email
        contacts.address = contact_data['address']
        contacts.website = message.text
    else:
        contacts = Contact(
            phone=contact_data['phone'],
            email=contact_data['email'],  # Новое поле
            address=contact_data['address'],
            website=message.text
        )
        db.add(contacts)

    db.commit()

    await message.answer(
        "✅ Контакты обновлены!\n"
        f"Телефон: {contact_data['phone']}\n"
        f"Email: {contact_data['email']}\n"
        f"Адрес: {contact_data['address']}\n"
        f"Сайт: {message.text}",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    await state.clear()


# Обработчик возврата в меню
@router.message(F.text == "В главное меню")
async def return_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=main_kb(message.from_user.id)
    )


@router.message(Command("admin_add"))
async def add_admin(message: types.Message):
    if message.from_user.id != settings.ADMIN_UID[0]:
        return await message.answer("❌ Недостаточно прав")

    try:
        new_admin_id = int(message.text.split()[1])
        if new_admin_id in settings.ADMIN_UID:
            return await message.answer("⚠️ Этот пользователь уже администратор")

        settings.ADMIN_UID.append(new_admin_id)
        # Обновляем .env файл
        with open(".env", "a") as f:
            f.write(f",{new_admin_id}")

        await message.answer(f"✅ Пользователь {new_admin_id} добавлен в админы")
    except (IndexError, ValueError):
        await message.answer("Использование: /admin_add <user_id>")


@router.message(Command("admin_remove"))
async def remove_admin(message: types.Message):
    if message.from_user.id != settings.ADMIN_UID[0]:
        return await message.answer("❌ Недостаточно прав")

    try:
        admin_id = int(message.text.split()[1])
        if admin_id not in settings.ADMIN_UID:
            return await message.answer("⚠️ Этот пользователь не администратор")

        settings.ADMIN_UID.remove(admin_id)
        # Обновляем .env файл
        with open(".env", "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if line.startswith("ADMIN_UIDS="):
                    line = f"ADMIN_UIDS={','.join(map(str, settings.ADMIN_UIDS))}\n"
                f.write(line)
            f.truncate()

        await message.answer(f"✅ Пользователь {admin_id} удалён из админов")
    except (IndexError, ValueError):
        await message.answer("Использование: /admin_remove <user_id>")


@router.message(Command("admin_list"))
@router.message(F.text == "Управление админами")
async def list_admins(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Недостаточно прав")

    admins_list = "\n".join(f"👉 {uid}" for uid in settings.ADMIN_UID)
    await message.answer(f"📋 Список администраторов:\n{admins_list}")
