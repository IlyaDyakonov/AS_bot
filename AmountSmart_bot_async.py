from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
import aiogram.exceptions
import requests
import bs4
import aiohttp
import asyncio
import logging
import sys


TOKEN = "ТУТ ВСТАВЬТЕ ВАШ ТОКЕН Telegram Bot"
dp = Dispatcher()

url_1 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_15ml.html"
url_2 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_150_ml.html"
url_3 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/lechebnoe_maslo_smart_organic_oil_30_ml.html"
url_4 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_balzam_dlya_bystrogo_vosstanovleniya_kozhi_150_ml.html"

url_test = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_eliksir_dlya_vosstanovleniya_volos_kozhi_golovy_brovey_i_resnits_30_ml.html"

async def start_check(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                res = requests.get(url)
                html_data = res.text
                soup = bs4.BeautifulSoup(html_data, 'lxml')
                divs_availability = soup.find_all('div', class_='row available-block')
                result = "Недоступно"
                for div in divs_availability:
                    answer = div.text.strip()
                    if answer == result:
                        return "Товара в наличии нет :("
                    else:
                        divs_price = soup.find_all('div', class_='qtyBlockContainer')
                        for price in divs_price:
                            input_tag = price.find('input', class_='qty')
                            data_max_quantity = input_tag.get('data-max-quantity')
                            return f"Товар появился в наличии ^_^\nНа данный момент количество {data_max_quantity} штук."
                    break

answer = "Товара в наличии нет :("

def create_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data='help_button'),
            InlineKeyboardButton(text="🕵️‍♂️ Наличие", callback_data='check_button')
        ],
        [
            InlineKeyboardButton(text="🛠️ Парсеры в работе", callback_data='pars_job')
        ],
        [
            InlineKeyboardButton(text="📛 Остановить Фиксиков)", callback_data='stop_button')
        ],
        [
            InlineKeyboardButton(text="🤏 Паста 15мл", callback_data='small_pasta'),
            InlineKeyboardButton(text="💪 Паста 150мл", callback_data='big_pasta')
        ],
        [
            InlineKeyboardButton(text="🍼 Масло 30мл", callback_data='small_balzam'),
            InlineKeyboardButton(text="🍷 Бальзам 150мл", callback_data='big_balzam')
        ],
    ])


    # кнопка ❓ Помощь
@dp.callback_query(lambda query: query.data == 'help_button')
async def process_help_command(call: CallbackQuery):
    await help_command(call.message)
    await call.answer()  # Отправляем пустое уведомление для закрытия всплывающего окна

    # кнопка 🕵️‍♂️ Наличие
@dp.callback_query(lambda query: query.data == 'check_button')
async def process_one_check(call: CallbackQuery):
    await one_check(call.message)
    await call.answer()

    # кнопка 🛠️ Парсеры в работе
@dp.callback_query(lambda query: query.data == 'pars_job')
async def process_print_active_parser(call: CallbackQuery):
    await print_active_parser(call.message)
    await call.answer()

    # кнопка 📛 Остановить
@dp.callback_query(lambda query: query.data == 'stop_button')
async def process_stop_parsing(call: CallbackQuery):
    await stop_parsing(call.message)
    await call.answer()

    # кнопка 🤏 Паста 15мл
@dp.callback_query(lambda query: query.data == 'small_pasta')
async def process_check_products_handler1(call: CallbackQuery):
    await check_products_small_pasta(call.message)
    await call.answer()

    # кнопка 💪 Паста 150мл
@dp.callback_query(lambda query: query.data == 'big_pasta')
async def process_check_products_handler2(call: CallbackQuery):
    await check_products_big_pasta(call.message)
    await call.answer()

    # кнопка 🍼 Масло 30мл
@dp.callback_query(lambda query: query.data == 'small_balzam')
async def process_check_products_handler3(call: CallbackQuery):
    await check_products_small_balzam(call.message)
    await call.answer()

    # кнопка 🍷 Бальзам 150мл
@dp.callback_query(lambda query: query.data == 'big_balzam')
async def process_check_products_handler4(call: CallbackQuery):
    await check_products_big_balzam(call.message)
    await call.answer()

# команда старт
@dp.message(CommandStart())
async def on_startup(message: Message):
    markup = create_keyboard()

    await message.answer(f"Привет ***{message.from_user.first_name}!*** 👋 \nЯ бот для проверки наличия товаров Smart Master 🤖\n\nНажми на кнопочку '❓ Помощь' и прочитай справку если тут впервые!", parse_mode= "Markdown", reply_markup=markup)

    await message.answer_sticker('CAACAgIAAxkBAAIHG2T-IYEAAc4d4bsfPOoizGVDkFuJygACOAsAAk7kmUsysUfS2U-M0DAE')

# глобальные переменные - флаги
# флаг времени между каждым запросом на сайт
timer_sleep = 300

@dp.message(Command('help'))
async def help_command(message: Message):
    markup = create_keyboard()
    await message.answer(
                    f"❓ ***Помощь*** - вызов справки 👻\n\n"
                    f"🕵️‍♂️ ***Наличие*** - проверка наличия товара на текущий момент.\n\n"
                    f"🛠️ ***Парсеры в работе*** - проверка какие парсеры запущены в данный момент.\n\n"
                    f"📛 ***Остановить Фиксиков)*** - остановка вообще _ВСЕХ_ парсингов.\n\n"
                    f"🤏 ***Паста 15мл*** - запуск автоматической проверки на наличие товара _маленькой_ пасты.\n\n"
                    f"💪 ***Паста 150мл*** - запуск автоматической проверки на наличие товара _большой_ пасты.\n\n"
                    f"🍼 ***Масло 30мл*** - запуск автоматической проверки на наличие товара _маленького_ бальзама.\n\n"
                    f"🍷 ***Бальзам 150мл*** - запуск автоматической проверки на наличие товара _большого_ бальзама.\n\n"
                    f"⚠️**ВНИМАНИЕ!**⚠️ Работать могут _любые_ комбинации парсингов одновременно! Если Вам надо остановить работу парсингов, или отключить какой либо из них, необходимо кнопкой ***Остановить*** работу _ВСЕХ_ действующих парсингов и дождаться ответа от Фиксиков, а затем запускать нужные парсеры 👾 =)", parse_mode= "Markdown", reply_markup=markup)

# функция для кнопки 🕵️‍♂️ Наличие
@dp.message()
async def one_check(message: Message):
    markup = create_keyboard()
    await message.answer(f"Собираем информацию, секунду...🧮")
    availability_1 = await start_check(url_1)
    availability_2 = await start_check(url_2)
    availability_3 = await start_check(url_3)
    availability_4 = await start_check(url_4)
    await message.answer(f"Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_1}\n\n\n"
                        f"{availability_2}\nэто Смарт Паста 150мл: {url_2}\n\n\n"
                        f"{availability_3}\nэто Смарт Масло 30мл: {url_3}\n\n\n"
                        f"{availability_4}\nэто Смарт Бальзам 150мл: {url_4}",
                        reply_markup=markup)

# словарь с содержимым запросов пользователей бота
user_states = {}

# кнопка остановить парсинг
@dp.message(Command('stop'))
async def stop_parsing(message: Message):
    chat_id = message.chat.id
    for user_id in user_states:
        if user_id == chat_id:
            if ('stop_pars_small_pasta' in user_states[user_id] and user_states[user_id]['stop_pars_small_pasta'] == True) and ('stop_pars_big_pasta' in user_states[user_id] and user_states[user_id]['stop_pars_big_pasta'] == True) and ('stop_pars_small_oil' in user_states[user_id] and user_states[user_id]['stop_pars_small_oil'] == True) and ('stop_pars_big_balzam' in user_states[user_id] and user_states[user_id]['stop_pars_big_balzam'] == True):
                await message.answer(f"Фиксики отдыхают 😸")
                break
            try:
                if chat_id in user_states:
                    user_states[chat_id]['stop_pars_small_pasta'] = True
                    user_states[chat_id]['stop_pars_big_pasta'] = True
                    user_states[chat_id]['stop_pars_small_oil'] = True
                    user_states[chat_id]['stop_pars_big_balzam'] = True
                else:
                    user_states[chat_id] = {'stop_pars_small_pasta': True}
                    user_states[chat_id] = {'stop_pars_big_pasta': True}
                    user_states[chat_id] = {'stop_pars_small_oil': True}
                    user_states[chat_id] = {'stop_pars_big_balzam': True}
                await message.answer(f"Немного терпения!🍿\nФиксикам надо остановить все работы и убрать рабочее место!🧘‍♂️🧘‍♀️\n\nПридёт уведомление когда парсинг определённого товара будет остановлен......⏳")
            except aiogram.exceptions.TelegramBadRequest as e:
                if "TelegramBadRequest" in str(e) or "aiogram.exceptions.TelegramBadRequest" in str(e):
                    pass
                else:
                    print("Неопознанные ошибки")

# смотрим какие парсеры сейчас работают
@dp.message()
async def print_active_parser(message: Message):
    active_functions = []
    chat_id = message.chat.id

    for user_id in user_states:
        if user_id == chat_id:
            if 'stop_pars_small_pasta' in user_states[user_id] and user_states[user_id]['stop_pars_small_pasta'] == False:
                active_functions.append('Запущенна проверка 🤏 Смарт Пасты 15мл')

            if 'stop_pars_big_pasta' in user_states[user_id] and user_states[user_id]['stop_pars_big_pasta'] == False:
                active_functions.append('Запущенна проверка 💪 Смарт Пасты 150мл')

            if 'stop_pars_small_oil' in user_states[user_id] and user_states[user_id]['stop_pars_small_oil'] == False:
                active_functions.append('Запущенна проверка 🍼Смарт Масла 30мл')

            if 'stop_pars_big_balzam' in user_states[user_id] and user_states[user_id]['stop_pars_big_balzam'] == False:
                active_functions.append('Запущенна проверка 🍷Смарт Бальзама 150мл')

    if active_functions:
        active_functions_text = "\n".join(active_functions)
        await message.answer(f'***Активные парсеры:***\n👇\n{active_functions_text}', parse_mode= "Markdown")
    else:
        await message.answer(f"Фиксики отдыхают 😸")

# это кнопка small_pasta
@dp.message()
async def check_products_small_pasta(message: Message):
    markup = create_keyboard()
    chat_id = message.chat.id

    if chat_id in user_states and 'stop_pars_small_pasta' in user_states[chat_id] and not user_states[chat_id]['stop_pars_small_pasta']:
        await message.answer(f'Парсер 💪 ***Смарт Пасты 15мл*** _уже выполняется_!', parse_mode= "Markdown")
    else:
        if chat_id in user_states:
            user_states[chat_id]['stop_pars_small_pasta'] = False
        else:
            user_states[chat_id] = {'stop_pars_small_pasta': False}
        await message.answer(f'Парсинг ***Смарт Пасты 15мл*** запущен!', parse_mode= "Markdown")
        while True:
            try:
                if user_states[chat_id]['stop_pars_small_pasta']:
                    await message.answer(f"Парсинг 🤏***Смарт Пасты 15мл*** остановлен!✅\nФиксики ждут новых поручений!🧟🧟‍♀️🧟‍♂️", parse_mode= "Markdown", reply_markup=markup)
                    break
                else:
                    await asyncio.sleep(timer_sleep)
                    availability_1 = await start_check(url_1)
                    if availability_1 == answer:
                        # await message.answer(f'pasta test 15')
                        pass
                    else:
                        await message.answer(f'Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 150мл: {url_1}', reply_markup=markup)
                        user_states[chat_id]['stop_pars_small_pasta'] = True
                        break
            except aiogram.exceptions.TelegramBadRequest as e:
                if "TelegramBadRequest" in str(e) or "aiogram.exceptions.TelegramBadRequest" in str(e):
                    break
                else:
                    print("Неопознанные ошибки")
                    break

# это кнопка big_pasta
@dp.message()
async def check_products_big_pasta(message: Message):
    markup = create_keyboard()
    chat_id = message.chat.id

    if chat_id in user_states and 'stop_pars_big_pasta' in user_states[chat_id] and not user_states[chat_id]['stop_pars_big_pasta']:
        await message.answer(f'Парсер 💪 ***Смарт Пасты 150мл*** _уже выполняется_!', parse_mode= "Markdown")
    else:
        if chat_id in user_states:
            user_states[chat_id]['stop_pars_big_pasta'] = False
        else:
            user_states[chat_id] = {'stop_pars_big_pasta': False}
        await message.answer(f'Парсинг ***Смарт Пасты 150мл*** запущен!', parse_mode= "Markdown")
        while True:
            try:
                if user_states[chat_id]['stop_pars_big_pasta']:
                    await message.answer(f"Парсинг 💪***Смарт Пасты 150мл*** остановлен!✅\nФиксики ждут новых поручений!🧟🧟‍♀️🧟‍♂️", parse_mode= "Markdown", reply_markup=markup)
                    break
                else:
                    await asyncio.sleep(timer_sleep)
                    availability_2 = await start_check(url_2)
                    if availability_2 == answer:
                        # await message.answer(f'pasta test 150')
                        pass
                    else:
                        await message.answer(f'Состояние товаров:\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}', reply_markup=markup)
                        user_states[chat_id]['stop_pars_big_pasta'] = True
                        break
            except aiogram.exceptions.TelegramBadRequest as e:
                if "TelegramBadRequest" in str(e) or "aiogram.exceptions.TelegramBadRequest" in str(e):
                    break
                else:
                    print("Неопознанные ошибки")
                    break

# это кнопка small_balzam
@dp.message()
async def check_products_small_balzam(message: Message):
    markup = create_keyboard()
    chat_id = message.chat.id

    if chat_id in user_states and 'stop_pars_small_oil' in user_states[chat_id] and not user_states[chat_id]['stop_pars_small_oil']:
        await message.answer(f'Парсер 💪 ***Смарт Масла 30мл*** _уже выполняется_!', parse_mode= "Markdown")
    else:
        if chat_id in user_states:
            user_states[chat_id]['stop_pars_small_oil'] = False
        else:
            user_states[chat_id] = {'stop_pars_small_oil': False}
        await message.answer(f'Парсинг ***Смарт Масла 30мл*** запущен!', parse_mode= "Markdown")
        while True:
            try:
                if user_states[chat_id]['stop_pars_small_oil']:
                    await message.answer(f"Парсинг 🍼***Смарт Масла 30мл*** остановлен!✅\nФиксики ждут новых поручений!🧟🧟‍♀️🧟‍♂️", parse_mode= "Markdown", reply_markup=markup)
                    break
                else:
                    await asyncio.sleep(timer_sleep)
                    availability_3 = await start_check(url_3)
                    if availability_3 == answer:
                        # await message.answer(f'oil test 30')
                        pass
                    else:
                        await message.answer(f'Состояние товаров:\n\n{availability_3}\nэто Смарт Паста 150мл: {url_3}', reply_markup=markup)
                        user_states[chat_id]['stop_pars_small_oil'] = True
                        break
            except aiogram.exceptions.TelegramBadRequest as e:
                if "TelegramBadRequest" in str(e) or "aiogram.exceptions.TelegramBadRequest" in str(e):
                    break
                else:
                    print("Неопознанные ошибки")
                    break

# это кнопка big_balzam
@dp.message()
async def check_products_big_balzam(message: Message):
    markup = create_keyboard()
    chat_id = message.chat.id

    if chat_id in user_states and 'stop_pars_big_balzam' in user_states[chat_id] and not user_states[chat_id]['stop_pars_big_balzam']:
            await message.answer(f'Парсер 💪 ***Смарт Бальзама 150мл*** _уже выполняется_!', parse_mode= "Markdown")
    else:
        if chat_id in user_states:
            user_states[chat_id]['stop_pars_big_balzam'] = False
        else:
            user_states[chat_id] = {'stop_pars_big_balzam': False}
        await message.answer(f'Парсинг ***Смарт Бальзама 150мл*** запущен!', parse_mode= "Markdown")
        while True:
            try:
                if user_states[chat_id]['stop_pars_big_balzam']:
                    await message.answer(f"Парсинг 🍷***Смарт Бальзама 150мл*** остановлен!✅\nФиксики ждут новых поручений!🧟🧟‍♀️🧟‍♂️", parse_mode= "Markdown", reply_markup=markup)
                    break
                else:
                    await asyncio.sleep(timer_sleep)
                    availability_4 = await start_check(url_4)
                    if availability_4 == answer:
                        # await message.answer(f'balzam test 150')
                        pass
                    else:
                        await message.answer(f'Состояние товаров:\n\n{availability_4}\nэто Смарт Паста 150мл: {url_4}', reply_markup=markup)
                        user_states[chat_id]['stop_pars_big_balzam'] = True
                        break
            except aiogram.exceptions.TelegramBadRequest as e:
                if "TelegramBadRequest" in str(e) or "aiogram.exceptions.TelegramBadRequest" in str(e):
                    break
                else:
                    print("Неопознанные ошибки")
                    break


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
