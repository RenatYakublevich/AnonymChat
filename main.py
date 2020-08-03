import asyncio

#aiogram и всё утилиты для коректной работы с Telegram API
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#конфиг с настройками
import config
from database import dbworker

#инициализируем базу данных
db = dbworker('db.db')

#инициализируем бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())

#хендлер команды /start
@dp.message_handler(commands=['start'],state='*')
async def start(message : types.Message):

    button_search = KeyboardButton('Начать поиск🔍')

    mark_menu = ReplyKeyboardMarkup()

    mark_menu.add(button_search)

    await bot.send_message(message.chat.id,'Привет!\n\nЭто Гомельский Анонимный чат для пожилых кролов....\nкхм шучу\n\n',reply_markup=mark_menu)



@dp.message_handler(lambda message: message.text == 'Начать поиск🔍',state='*')
async def search(message : types.Message):
    if(not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.username,message.from_user.id)

    male = KeyboardButton('Парня')

    wooman = KeyboardButton('Девушку')

    sex_menu = ReplyKeyboardMarkup()

    sex_menu.add(male,wooman)

    await message.answer('Выбери пол собеседника!\nКого вы ищите?)',reply_markup=sex_menu)


class Chating(StatesGroup):
	msg = State()

@dp.message_handler(lambda message: message.text == 'Парня' or message.text == 'Девушку',state='*')
async def chooce_sex(message : types.Message):
    if message.text == 'Парня':
        db.edit_sex(True,message.from_user.id)
    else:
        db.edit_sex(False,message.from_user.id)

    all_users = db.search(db.get_info_user('sex',message.from_user.id))
    print(all_users)

    await Chating.msg.set()


@dp.message_handler(state=Chating.msg)
async def chating(message : types.Message, state: FSMContext):
    await state.update_data(msg=message.text)

    user_data = await state.get_data()

    await message.answer(user_data['msg'])








executor.start_polling(dp, skip_updates=True)
