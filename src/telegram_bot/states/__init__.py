from aiogram.fsm.state import State, StatesGroup


class GameInteractions(StatesGroup):
    selecting_game = State()
    interacting_with_game = State()
    waiting_for_task_acknowledge = State()
    waiting_for_artwork = State()
