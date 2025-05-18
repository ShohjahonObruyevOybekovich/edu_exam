import io

import pandas as pd
from aiogram import Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, BufferedInputFile
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from icecream import ic

from account.models import CustomUser
from dispatcher import dp, TOKEN
from result.models import Result
from tg_bot.buttons.inline import start_btn
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
        await message.answer(
            text="🔐 *Admin bo‘limiga hush kelibsiz!* 👋\nSizda to‘liq boshqaruv huquqlari mavjud.",
            reply_markup=admin(),
            parse_mode="Markdown"
        )
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
    await message.answer("👤 Talabalarni tanlang yoki qidiring:",
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
                    message_text=f"👤 Tanlangan talaba:\nID: {installment.chat_id} \n{installment.full_name} ({installment.phone})"
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
        correct_answer = result.correct_answer
        incorrect_answer = 20 - int(result.correct_answer)
        percent = (int(correct_answer)/20)*100
        datas = [
            "📋 <b>Imtihon natijalari</b>\n",
            f"👤 <b>Talaba ismi:</b> {user.full_name or ""}",
            f"📞 <b>Telefon raqami:</b> {user.phone or ""}",
            f"🎯 <b>Imtihon darajasi:</b> {result.level.name or ""}",
            f"📊 <b>Natija foizi:</b> {percent or ""}%",
            f"✅ <b>To‘g‘ri javoblar:</b> {correct_answer or ""} ta",
            f"❌ <b>Noto‘g‘ri javoblar:</b> {incorrect_answer or ""} ta",
            f"🕒 <b>Test vaqti:</b> {result.created_at.strftime('%d.%m.%Y %H:%M') or ""}"
        ]

        caption_text = "\n".join(datas)
        await message.answer(text=caption_text, reply_markup=admin())
        await state.clear()



# @dp.message(lambda msg : msg.text == "📊 Hisobotlar")
# async def handle_users(message: Message, state: FSMContext) -> None:
#     await state.set_state(User.user)
#
#     users = CustomUser.objects.all()
#
#     if not users:
#         await message.answer("📭 Hozircha foydalanuvchilar ro'yxati bo'sh.")
#         return
#
#     # Ma'lumotlarni to'plash
#     data = []
#     for user in users:
#         result = Result.objects.filter(user=user).first()
#         data.append({
#             "I.F.O": user.full_name,
#             "Telefon raqami": user.phone or "",
#             "Imtihon darajasi": result.level.name if result else "",
#             "To'g'ri javoblar soni": result.correct_answer if result else "",
#             "Ball": result.ball if result else "",
#             "Imtihon sanasi": result.created_at.strftime("%d/%m/%Y") if result and result.created_at else ""
#         })
#
#     df = pd.DataFrame(data)
#
#     output = io.BytesIO()
#
#     # Excel faylni yaratish
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, startrow=2, sheet_name='Talabalar')
#
#         workbook = writer.book
#         worksheet = writer.sheets['Talabalar']
#
#         # Sarlavha qo'shish (masalan 1-qator uchun)
#         header_format = workbook.add_format({
#             'bold': True,
#             'align': 'center',
#             'valign': 'vcenter',
#             'fg_color': '#D7E4BC',
#             'border': 1
#         })
#
#         worksheet.merge_range('A1:F1', 'Talabalar hisobotlari', header_format)
#
#         for col_num, value in enumerate(df.columns.values):
#             worksheet.write(2, col_num, value, header_format)
#
#     output.seek(0)
#     file = BufferedInputFile(output, filename="talabalar_hisobot.xlsx")
#
#     try:
#         await bot.send_document(
#             chat_id=message.from_user.id,
#             document=file,
#             caption="📊 Talabalar hisoboti"
#         )
#     except Exception as e:
#         error_text = f"Faylni yuborishda xatolik yuz berdi:\n{e}"
#         await message.answer(error_text, parse_mode=None)
