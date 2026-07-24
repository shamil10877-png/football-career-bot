from aiogram.fsm.state import StatesGroup, State

class CreatePlayer(StatesGroup):
    first_name = State()
    last_name = State()
    nation = State()
    position = State()
