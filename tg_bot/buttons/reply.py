from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def phone_number_btn():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = "Raqamni yuborish 📞",
                                                         request_contact=True) ]] ,
                               resize_keyboard=True)

def results():
    return ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="📊 Natija")
    ]],resize_keyboard=True)


def admin():
    k1 = KeyboardButton(text="👥 Foydalanuvchilar ro‘yxati")
    # k2 = KeyboardButton(text="📊 Hisobotlar")

    return ReplyKeyboardMarkup(
        keyboard=[[k1]],
        resize_keyboard=True
    )