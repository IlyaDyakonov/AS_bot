import requests
import bs4
import lxml
import time
import telebot
from telebot import types
import threading


TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

url_1 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_15ml.html"
url_2 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_150_ml.html"
url_test = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_eliksir_dlya_vosstanovleniya_volos_kozhi_golovy_brovey_i_resnits_30_ml.html"

def start_check(url):
    res = requests.get(url)
    html_data = res.text
    soup = bs4.BeautifulSoup(html_data, 'lxml')
    divs_availability = soup.find_all('div', class_='row available-block')
    result = "Недоступно"
    for div in divs_availability:
        answer = div.text.strip()
        if answer == result:
            return "Пасты в наличии нет. =("
        else:
            divs_price = soup.find_all('div', class_='qtyBlockContainer')
            for price in divs_price:
                input_tag = price.find('input', class_='qty')
                data_max_quantity = input_tag.get('data-max-quantity')
                return f"Паста появилась в наличии ^_^\nНа данный момент количество {data_max_quantity} штук."
        break

answer = "Пасты в наличии нет. =("


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Тыкай свои кнопочки, хавнюк =)")
    row1 = []
    row2 = []
    button_help(row1)
    check_button(row2)
    markup.add(*row1, *row2)

    stop_check(markup)

    row3 = []
    row4 = []
    check_button_start_small(row3)
    check_button_start_big(row4)
    markup.add(*row3, *row4)
    
    check_button_start_two(markup)
    
    bot.send_message(message.chat.id, "Привет! Я бот для проверки наличия товаров.", reply_markup=markup)

# ниже идёт код для кнопок бота
def button_help(markup):
    help_button = types.KeyboardButton("❓ Помощь")
    markup.append(help_button)

def stop_check(markup):
    stop_check_button = types.KeyboardButton("📛 Остановить")
    markup.add(stop_check_button)

def check_button(markup):
    check_button = types.KeyboardButton("🤔 Наличие")
    markup.append(check_button)

def check_button_start_small(markup):
    start_button_small = types.KeyboardButton("🤏🏻 Запуск 15мл", request_contact=False, request_location=False)
    markup.append(start_button_small)

def check_button_start_big(markup):
    start_button_big = types.KeyboardButton("💪 Запуск 150мл", request_contact=False, request_location=False)
    markup.append(start_button_big)

def check_button_start_two(markup):
    start_button_two = types.KeyboardButton("🗽 Запуск пасты 150мл и 15мл", request_contact=False, request_location=False)
    markup.add(start_button_two)

# глобальные переменные
stop_parsing_flag = False
is_checking_small = False
is_checking_big = False
is_checking_two = False
timer = None
timer_sleep = 3

# ниже идёт код для логики бота
@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def help(message):
    bot.send_message(message.chat.id, f"""
                    ❓ ***Помощь*** - вызов справки\n\n📛 ***Остановить*** - остановка вообще _всех_ парсингов.\n\n🤔 ***Наличие*** - проверка наличия товара на текущий момент.\n\n🤏🏻 ***Запуск 15мл*** - запуск автоматической проверки на наличие товара _маленькой_ пасты.\n\n💪 ***Запуск 150мл*** - запуск автоматической проверки на наличие товара _большой_ пасты.\n\n🗽 **Запуск пасты 150мл и 15мл** - запуск автоматической проверки на наличие товара и _большой_ и _маленькой_ паст.\n\n⚠️**ВНИМАНИЕ!**⚠️ Работать одновременно может только _один_ парсинг из трёх! Перед запуском другого парсинга, необходимо кнопкой *остановить* работу других. """, parse_mode= "Markdown")

@bot.message_handler(func=lambda message: message.text == "📛 Остановить")
def stop_parsing(message):
    global stop_parsing_flag, is_checking_big, is_checking_small, is_checking_two, timer
    stop_parsing_flag = True
    is_checking_small = False
    is_checking_big = False
    is_checking_two = False
    bot.send_message(message.chat.id, f"Немного терпения!🍿\nФиксикам надо остановить все работы и убрать рабочее место!🧘‍♂️🧘‍♀️\n\nПридёт уведомление когда можно начать новый парсинг.....⏳")
    if timer:
        timer.join()  # Дождаться завершения потока
        timer = None
    bot.send_message(message.chat.id, f"Весь парсинг был успешно остановлен!✅\nСпасибо за ожидание!🍨")


@bot.message_handler(func=lambda message: message.text == "🤔 Наличие")
def one_check(message):
        availability_1 = start_check(url_1)
        availability_2 = start_check(url_2)
        bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_1}\n\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}")

@bot.message_handler(func=lambda message: message.text == "🤏🏻 Запуск 15мл")
def check_products_small(message):
    global stop_parsing_flag, is_checking_big, is_checking_small, is_checking_two, timer
    if is_checking_small:
        bot.send_message(message.chat.id, "Парсинг пасты 15мл уже запущен.")
        return
    elif is_checking_big:
        bot.send_message(message.chat.id, "Парсинг пасты 150мл уже запущен.")
        return
    elif is_checking_two:
        bot.send_message(message.chat.id, "Парсинг пасты 15мл и 150мл уже запущен.")
        return
    else:
        bot.send_message(message.chat.id, f"Запустился парсинг пасты 15мл.")
    is_checking_small = True
    stop_parsing_flag = False
    def parsing_loop1():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability_1 = start_check(url_1)
            if availability_1 == answer:
                # pass
                bot.send_message(message.chat.id, f"test 15")
            else:
                bot.send_message(message.chat.id, f"Состояние товара:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_1}")
                break
    timer = threading.Thread(target=parsing_loop1)
    timer.start()

@bot.message_handler(func=lambda message: message.text == "💪 Запуск 150мл")
def check_products_big(message):
    global stop_parsing_flag, is_checking_big, is_checking_small, is_checking_two, timer
    if is_checking_big:
        bot.send_message(message.chat.id, "Парсинг пасты 150мл уже запущен.")
        return
    elif is_checking_small:
        bot.send_message(message.chat.id, "Парсинг пасты 15мл уже запущен.")
        return
    elif is_checking_two:
        bot.send_message(message.chat.id, "Парсинг пасты 15мл и 150мл уже запущен.")
        return
    else:
        bot.send_message(message.chat.id, f"Запустился парсинг пасты 150мл.")
    is_checking_big = True
    stop_parsing_flag = False
    def parsing_loop2():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability_2 = start_check(url_2)
            if availability_2 == answer:
                # pass
                bot.send_message(message.chat.id, f"test 150")
            else:
                bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}")
                break
    timer = threading.Thread(target=parsing_loop2)
    timer.start()

@bot.message_handler(func=lambda message: message.text == "🗽 Запуск пасты 150мл и 15мл")
def check_products_two(message):
    global stop_parsing_flag, is_checking_big, is_checking_small, is_checking_two, timer
    if is_checking_two:
        bot.send_message(message.chat.id, "Парсинг паст 15мл и 150мл уже запущен.")
        return
    elif is_checking_small:
        bot.send_message(message.chat.id, "Парсинг пасты 15мл уже запущен.")
        return
    elif is_checking_big:
        bot.send_message(message.chat.id, "Парсинг пасты 150мл уже запущен.")
        return
    else:
        bot.send_message(message.chat.id, f"Запустился парсинг паст 150мл и 15мл.")
    is_checking_two = True
    stop_parsing_flag = False
    def parsing_loop3():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability_1 = start_check(url_1)
            availability_2 = start_check(url_2)
            if availability_1 == answer or availability_2 == answer:
                # pass
                bot.send_message(message.chat.id, f"test 15 and 150")
            else:
                bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_2}\n\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}")
                break
    timer = threading.Thread(target=parsing_loop3)
    timer.start()

bot.polling()