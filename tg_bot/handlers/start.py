import os

from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext
from aiogram.handlers import CallbackQueryHandler
from aiogram.types import Message, BufferedInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from icecream import ic

from account.models import CustomUser
from dispatcher import dp, TOKEN
from result.models import Result
from tg_bot.buttons.inline import degree, start_btn
from tg_bot.buttons.reply import phone_number_btn, results, admin
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
        await message.answer(natija_txt,reply_markup=results())


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
    await message.reply(
        text="🏆 Imtihonni boshlashingiz mumkin!",
        reply_markup=results()
    )
    await state.clear()
@dp.message(lambda message: message.text == "📊 Natija")
async def handle_natija_handler(message: Message, state: FSMContext) -> None:
    result = Result.objects.filter(
        user__chat_id=message.from_user.id,
    ).first()

    if result:
        await message.answer(
            text=(
                f"📊 <b>Natijangiz tayyor!</b>\n\n"
                f"🧑‍🎓 <b>Talaba:</b> <i>{result.user.full_name}</i>\n"
                f"🏆 <b> Imtihon darajasi:</b> <i>{result.level.name}</i>\n"
                f"✅ <b>To'g'ri javoblar:</b> <code>{result.correct_answer}</code>\n"
                f"📈 <b>Natija ball:</b> <code>{result.ball}</code> / 100\n\n"
                f"🥳 <b>Ajoyib!</b> Biz bilan ekanligingizdan xursandmiz!"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                "😕 Sizda hali natija mavjud emas.\n\n"
                "📌 Avval imtihonni bajarib, keyin natijangizni ko‘rishingiz mumkin.\n"
                "🚀 Imtihonni boshlash uchun tugmani bosing 👇"
            ),
            reply_markup=start_btn()
        )

@dp.message(lambda msg : msg.text == "Admin_parol")
async def handle_admin_parol_handler(message: Message, state: FSMContext) -> None:
    user = CustomUser.objects.filter(chat_id=message.from_user.id).first()
    if user and user.role == "Admin":
        await message.answer(
            text="🔐 *Admin bo‘limiga hush kelibsiz!* 👋\nSizda to‘liq boshqaruv huquqlari mavjud.",
            reply_markup=admin(),
            parse_mode="Markdown"
        )
    elif user and user.role == "User":
        user.role = "Admin"
        user.save()
        await message.answer(
            text="✅ *Tabriklaymiz!* Sizning huquqingiz *admin* darajasiga yangilandi!",
            reply_markup=admin(),
            parse_mode="Markdown"
        )



@dp.message(lambda msg:msg.text == "👥 Foydalanuvchilar ro‘yxati")
async def handle_users(message: Message, state: FSMContext) -> None:
    await state.set_state(User.user)
    button = InlineKeyboardButton(
        text="Qidirish 🔍",  # Button text
        switch_inline_query_current_chat=""
        # This will be used to handle the button press
    )
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer("Talabalarni tanlang yoki qidiring:",
                         reply_markup=inline_keyboard)


@dp.inline_query()
async def search_customers(inline_query: InlineQuery):
    query = inline_query.query.strip()
    user = CustomUser.objects.filter(role="User", full_name__icontains=query).all()

    results = []
    for installment in user:
        results.append(
            InlineQueryResultArticle(
                id=str(installment.chat_id),
                title=f"{installment.full_name} ({installment.phone})",
                input_message_content=InputTextMessageContent(
                    message_text=f"Tanlangan talaba:\nID: {installment.chat_id} \n{installment.full_name} ({installment.phone})"
                ),
                description="Talaba haqida ma'lumotni ko'rish"
            )
        )

    await inline_query.answer(results, cache_time=0, is_personal=True)

@dp.message(User.user)
async def handle_customer_selection(message: Message, state: FSMContext):
    parts = message.text.split()
    ic(parts)

    if "ID:" in parts:
        phone_index = parts.index("ID:")
        user_id: int = parts[phone_index + 1]
        ic(user_id)
        user = CustomUser.objects.filter(chat_id=user_id).first()
        result = Result.objects.filter(user__chat_id=message.from_user.id).first()
        datas = [
            f"<b>Talaba ismi:</b> {user.full_name}",
            f"<b>Telefon raqami:</b> {user.phone}",
            f"<b>Imtihon darajasi:</b> {result.level.name}",
            f"<b>Imtihon natijasi:</b> {result.ball}",
        ]
        caption_text = "\n".join(datas)
        await message.answer(text=caption_text, reply_markup=admin(), parse_mode="Markdown")

