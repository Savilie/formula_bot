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
        f"📞 <b>Телефон:</b> {contacts.phone}\n"
        f"📧 <b>Email:</b> {contacts.email}\n"
        f"🏢 <b>Адрес:</b> {contacts.address}\n"
        f"🌐 <b>Сайт:</b> {contacts.website}"
    )
    await message.answer(response, parse_mode="HTML")