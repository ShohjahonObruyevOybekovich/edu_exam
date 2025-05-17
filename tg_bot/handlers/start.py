import os

from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.handlers import CallbackQueryHandler
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from icecream import ic

from account.models import CustomUser
from dispatcher import dp, TOKEN
from tg_bot.buttons.inline import degree, start_btn
from tg_bot.buttons.reply import phone_number_btn
from tg_bot.buttons.text import start_txt, natija_txt
from tg_bot.state.main import User
from tg_bot.utils import format_phone_number

bot = Bot(token=TOKEN)

# /start handler
@dp.message(F.text == "/start")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    user = CustomUser.objects.filter(chat_id=message.from_user.id).first()

    # First-time user registration
    if not user:
        CustomUser.objects.create(
            chat_id=message.from_user.id,
            full_name=message.from_user.full_name,
        )
        await message.answer(start_txt)
        await state.set_state(User.full_name)
        return

    if user.role == "ADMIN":
        # Optional: send admin-specific buttons or info
        pass
    if user:
        await message.answer(natija_txt,reply_markup=degree())


@dp.message(User.full_name)
async def user_lang_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    data['full_name'] = message.text
    await state.set_data(data)
    await state.set_state(User.phone)
    await message.answer(
        "Telefon raqamingizni Raqamni yuborish \n📞 tugmasi orqali yuboring ! \n",
        reply_markup=phone_number_btn()
    )


@dp.message(User.phone)
async def handle_phone_number(message: Message, state: FSMContext) -> None:
    if not message.contact:
        # Faqat contact yuborilmagan holatda ogohlantirish
        await state.set_state(User.phone)
        await message.answer(
            "❗️Telefon raqamingizni *Raqamni yuborish 📞* tugmasi orqali yuboring!",
            reply_markup=phone_number_btn(),
            parse_mode="Markdown"
        )
        return

    # Agar contact yuborilgan bo‘lsa, raqamni saqlash
    phone_number = format_phone_number(message.contact.phone_number)

    user = CustomUser.objects.filter(chat_id=message.from_user.id).first()
    if user:
        user.phone = phone_number
        user.save()

    await message.answer(
        text=(
            f"✅ <b>Telefon raqamingiz muvaffaqiyatli saqlandi!</b>\n"
            f"📞 <b>{phone_number}</b>\n\n"
            f"🚀 <b>Endi imtihonni boshlashga tayyormisiz?</b>\n"
            f"Quyidagi tugmani bosing va darajangizni aniqlang! 👇🏿"
        ),
        parse_mode="HTML",
        reply_markup=start_btn()
    )
