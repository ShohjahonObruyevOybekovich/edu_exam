from aiogram.fsm.state import State, StatesGroup


class User(StatesGroup):
    phone = State()
    full_name = State()
    user = State()