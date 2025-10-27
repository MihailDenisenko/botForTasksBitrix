from aiogram.fsm.state import State, StatesGroup

class TaskCreation(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_responsible = State()
    waiting_project = State()