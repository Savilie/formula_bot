from aiogram import Router, types, F
from bot.database import get_db
from bot.models import Contact

router = Router()


@router.message(F.text == "Контакты")
async def show_contacts(message: types.Message):
    db = next(get_db())
    contacts = db.query(Contact).first()

    if not contacts:
        await message.answer("Контактная информация отсутствует")
        return

    response = (
        f"📞 Телефон: {contacts.phone}\n"
        f"🏢 Адрес: {contacts.address}\n"
        f"🌐 Сайт: {contacts.website}"
    )
    await message.answer(response)