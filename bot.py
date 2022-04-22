import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup

from Api import token
from data import db_session
from data.user import User
from geocoder import get_cooords, geocode

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


class Register(StatesGroup):
    telegram = State()
    interes = State()
    loc = State()


class Loc(StatesGroup):
    new_loc_state = State()


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Отправить геолокацию", request_location=True)
    keyboard.add(button)
    return keyboard


@dp.message_handler(commands='start')
async def start(message: types.Message, state):
    await message.answer(f"Привет, {message.from_user.first_name}.\nХочешь найти себе новых друзей?"
                         f"\nТогда просто напиши /seach."
                         f"Но для начала мне бы хотелось узнать о ваших интересах."
                         f" Напишите все, чем вы интересуетесь через запятую")
    await Register.interes.set()


@dp.message_handler(commands='help')
async def help(message: types.Message):
    await message.answer("Что я умею:\n"
                         "/register - ввод нужной информации для поиска друзей\n"
                         "/newloc - обновление локации\n"
                         "/seach - поиск друзей")


@dp.message_handler(state=Register.interes, content_types=['text'])
async def register_interes(message: types.Message, state: FSMContext):
    await state.update_data(interes=';'.join(message.text.split(',')))
    await Register.telegram.set()
    await message.answer("Можно показывать ваш Телеграм для общения с другими пользователями?")


@dp.message_handler(state=Register.telegram, content_types=['text'])
async def register_telegram(message: types.Message, state: FSMContext):
    if message.text.lower() in ['да', 'конечно', 'хорошо', 'ладно']:
        await state.update_data(telegram='https://t.me/' + message.from_user.username)
    elif message.text.lower() in ['нет', 'нельзя', 'отстань', 'запрещаю']:
        pass
    else:
        return await message.answer("Я вас не понял. Напишите 'Да' или 'Нет'")
    await Register.loc.set()
    await message.answer("Теперь мне нужно узнать ваше местоположение. Можете написать адрес или воспользоваться "
                         "функцией Телеграма", reply_markup=get_keyboard())


@dp.message_handler(state=Register.loc, content_types=['text', 'location'])
async def coord_step(message: types.Message, state: FSMContext):
    try:
        if message.content_type == 'location':
            lat = message.location.latitude
            lon = message.location.longitude
            lat_lon = str(lon) + ',' + str(lat)
        else:
            lat, lon = get_cooords(message.text)
            lat_lon = str(lon) + ',' + str(lat)
        data = await state.get_data()
        remove_buttons = types.ReplyKeyboardRemove()
        await message.answer("Спасибо, теперь мы можем начинать поиск", reply_markup=remove_buttons)
        await state.finish()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == message.from_user.username).first()
        if not user:
            user = User()
        user.name = message.from_user.username
        user.interests = data['interes']
        if 'telegram' in data:
            user.telegram = data['telegram']
        user.location = lat_lon
        if not user:
            db_sess.add(user)
        db_sess.commit()
    except Exception as e:
        print(e)
        await state.finish()
        await message.answer("Что-то пошло не так")


@dp.message_handler(commands='newloc', state="*")
async def new_loc(message: types.Message, state: FSMContext):
    await Loc.new_loc_state.set()
    await message.answer("Узнаем ваше местоположение. Можете написать адрес или воспользоваться "
                         "функцией Телеграма", reply_markup=get_keyboard())


@dp.message_handler(state=Loc.new_loc_state, content_types=['text', 'location'])
async def nwe_coord_step(message: types.Message, state: FSMContext):
    await state.finish()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == message.from_user.username).first()
    if message.content_type == 'location':
        lat = message.location.latitude
        lon = message.location.longitude
        lat_lon = str(lat) + ',' + str(lon)
    else:
        lat, lon = get_cooords(message.text)
        lat_lon = str(lon) + ',' + str(lat)
    if user:
        user.location = lat_lon
        db_sess.commit()
        await message.answer("Все прошло успешно")
    else:
        await message.answer("Что-то пошло не так")


@dp.message_handler(commands='seach')
async def seach(message: types.Message, state: FSMContext):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == message.from_user.username).first()
    users = db_sess.query(User).filter(User.name != message.from_user.username).filter(User.interests.like(f"%{user.interests}%")).all()[::20]
    lis = ['Зарегистрированные пользователи, с похожими увлечениями ', '']
    for i in users:
        lis.append(f'{i.name} - {geocode(",".join(i.location.split(",")[::-1]))["metaDataProperty"]["GeocoderMetaData"]["text"]}')
    await message.answer('\n'.join(lis))


if __name__ == "__main__":
    db_session.global_init('db/user.db')
    executor.start_polling(dp, skip_updates=True)
