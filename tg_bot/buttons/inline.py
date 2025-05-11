from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from decouple import config


def degree():
    payment_date = InlineKeyboardButton(text="✏️ Sanani o'zgartirish", callback_data="Sanani o'zgartirish")
    accept = InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="accepted")
    cancel = InlineKeyboardButton(text = "🗑 Buyurtmani bekor qilish", callback_data="cancelled")
    return InlineKeyboardMarkup(inline_keyboard=[[accept], [payment_date],[cancel]])

MINI_APP_URL = config("MINI_APP_URL")

def start_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Imtihonni boshlash",
            web_app=WebAppInfo(url="https://your-mini-app-url.com")  # ← replace with your real Mini App URL
        )]
    ])
