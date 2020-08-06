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
import aiogram.utils.exceptions

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

    button_info_project = KeyboardButton('О проекте🧑‍💻')

    rules = KeyboardButton('Правила📖')

    mark_menu = ReplyKeyboardMarkup()

    mark_menu.add(button_search,button_info_project,rules)

    await bot.send_message(message.chat.id,'Привет!\n\nЭто Гомельский Анонимный чат для пожилых кролов....\nкхм шучу\n\n',reply_markup=mark_menu)


@dp.message_handler(lambda message : message.text == 'О проекте🧑‍💻' or message.text == 'Все ссылки на нас' or message.text == '[ Для разработчиков ]',state='*')
async def about_project(message : types.Message):
    if message.text == 'О проекте🧑‍💻':
        links = KeyboardButton('Все ссылки на нас')

        for_developers = KeyboardButton('[ Для разработчиков ]')

        back = KeyboardButton('Назад')

        mark_menu = ReplyKeyboardMarkup()

        mark_menu.add(links,for_developers,back)

        await bot.send_message(message.chat.id,'Вся информация тут👇',reply_markup=mark_menu)
    elif message.text == 'Все ссылки на нас':
        await message.answer('Главный разработчик - Якублевич Ренат\nСотрудничество - merlinincorp@gmail.com\n\nGithub - https://github.com/RenatYakublevich/AnonymChat')

    elif message.text == '[ Для разработчиков ]':
        await message.answer('Если вы разработчик и хотите поучаствовать в разработке проекта то смело контрибутье на гите или пишите на почту - merlinincorp@gmail.com')

@dp.message_handler(commands=['rules'],state='*')
@dp.message_handler(lambda message : message.text == 'Правила📖')
async def rules(message : types.Message):
    await message.answer('''📌Правила общения в @GomelAnonymChatBot\n1. Любые упоминания психоактивных веществ. (наркотиков)\n2. Детская порнография. ("ЦП")\n3. Мошенничество. (Scam)\n4. Любая реклама, спам.\n5. Продажи чего либо. (например - продажа интимных фотографий, видео)\n6. Любые действия, нарушающие правила Telegram.\n7. Оскорбительное поведение.\n8. Обмен, распространение любых 18+ материалов\n\n❌- За нарушение правил - блокировка аккаунта.''')

@dp.message_handler(lambda message: message.text == 'Начать поиск🔍',state='*')
async def search(message : types.Message):
    if(not db.user_exists(message.from_user.id)): #если пользователя с таким telegram id не найдено
        db.add_user(message.from_user.username,message.from_user.id) #добавляем юзера в табличку дб

    male = KeyboardButton('Парня')

    wooman = KeyboardButton('Девушку')

    back = KeyboardButton('Назад')

    sex_menu = ReplyKeyboardMarkup(one_time_keyboard=True)

    sex_menu.add(male,wooman,back)

    await message.answer('Выбери пол собеседника!\nКого вы ищите?)',reply_markup=sex_menu)

#класс машины состояний
class Chating(StatesGroup):
	msg = State()

@dp.message_handler(lambda message: message.text == 'Парня' or message.text == 'Девушку',state='*')
async def chooce_sex(message : types.Message, state: FSMContext):
    ''' Выбор пола для поиска '''
    if message.text == 'Парня':
        db.edit_sex(True,message.from_user.id)
        db.add_to_queue(message.from_user.id,True)
    else:
        db.edit_sex(False,message.from_user.id)
        db.add_to_queue(message.from_user.id,False)

    #кнопки
    stop = KeyboardButton('❌Остановить диалог')

    next = KeyboardButton('Следующий диалог')

    share_link = KeyboardButton('🏹Отправить ссылку на себя')

    back = KeyboardButton('Назад')

    menu_msg = ReplyKeyboardMarkup()

    menu_msg.add(stop,next,share_link,back)


    await message.answer('Вы в очереди...')

    while True:
        await asyncio.sleep(2)
        if db.search(db.get_sex_user(message.from_user.id)[0]) != None:
            break

    await message.answer('Диалог начался!',reply_markup=menu_msg)
    await Chating.msg.set()
    db.update_connect_with(db.search(db.get_sex_user(message.from_user.id)[0])[0],message.from_user.id)







@dp.message_handler(state=Chating.msg)
async def chating(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен сообщениями '''
    await state.update_data(msg=message.text)
    db.delete_from_queue(message.from_user.id)
    user_data = await state.get_data()

    if user_data['msg'] == '❌Остановить диалог':
        await bot.send_message(message.from_user.id,'Диалог закончился!')
        await bot.send_message(db.select_connect_with_self(message.from_user.id)[0],'Диалог закончился!')
        await state.finish()
        db.update_connect_with(None,message.from_user.id)
        db.update_connect_with(None,db.select_connect_with_self(message.from_user.id)[0])
        return
    try:
        await bot.send_message(db.select_connect_with(message.from_user.id)[0],user_data['msg'])
    except aiogram.utils.exceptions.ChatIdIsEmpty():
        await state.finish()



#хендлер для команды назад
@dp.message_handler(commands=['back'],state='*')
@dp.message_handler(lambda message : message.text == 'Назад')
async def back(message : types.Message, state: FSMContext):
    ''' Функция для команды back '''
    await start(message)
    await state.finish()

#хендлер который срабатывает при непредсказуемом запросе юзера
@dp.message_handler()
async def end(message : types.Message):
	'''Функция непредсказумогого ответа'''
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /start и /help')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
