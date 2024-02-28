import requests
import bs4
import lxml
import time
import telebot
from telebot import types
import threading


TOKEN = 'ТУТ ВСТАВЬТЕ ВАШ ТОКЕН Telegram Bot'
bot = telebot.TeleBot(TOKEN)

url_1 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_15ml.html"
url_2 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/multi_pasta_smart_150_ml.html"
url_3 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_balzam_dlya_bystrogo_vosstanovleniya_kozhi_15ml.html"
url_4 = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_balzam_dlya_bystrogo_vosstanovleniya_kozhi_150_ml.html"

url_test = "https://smart-pilka.ru/catalog/professionalnaya_kosmetika/umnyy_eliksir_dlya_vosstanovleniya_volos_kozhi_golovy_brovey_i_resnits_30_ml.html"

print("Бот запущен и готов к работе! 🤖")

def start_check(url):
    res = requests.get(url)
    html_data = res.text
    soup = bs4.BeautifulSoup(html_data, 'lxml')
    divs_availability = soup.find_all('div', class_='row available-block')
    result = "Недоступно"
    for div in divs_availability:
        answer = div.text.strip()
        if answer == result:
            return "Пасты в наличии нет =("
        else:
            divs_price = soup.find_all('div', class_='qtyBlockContainer')
            for price in divs_price:
                input_tag = price.find('input', class_='qty')
                data_max_quantity = input_tag.get('data-max-quantity')
                return f"Товар появился в наличии ^_^\nНа данный момент количество {data_max_quantity} штук."
        break

answer = "Пасты в наличии нет =("


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
    check_button_start_small_pasta(row3)
    check_button_start_big_pasta(row4)
    markup.add(*row3, *row4)

    row5 = []
    row6 = []
    check_button_start_small_balzam(row5)
    check_button_start_big_balzam(row6)
    markup.add(*row5, *row6)

    check_button_start_two_pasta(markup)

    check_button_start_two_balzam(markup)

    bot.send_message(message.chat.id, "Привет! Я бот для проверки наличия товаров Smart Master 🤖", reply_markup=markup)

# ниже идёт код для кнопок бота
def button_help(markup):
    help_button = types.KeyboardButton("❓ Помощь")
    markup.append(help_button)

def stop_check(markup):
    stop_check_button = types.KeyboardButton("📛 Остановить")
    markup.add(stop_check_button)

def check_button(markup):
    check_button = types.KeyboardButton("🕵️‍♂️ Наличие")
    markup.append(check_button)

def check_button_start_small_pasta(markup):
    start_button_small_pasta = types.KeyboardButton("🤏 Паста 15мл", request_contact=False, request_location=False)
    markup.append(start_button_small_pasta)

def check_button_start_big_pasta(markup):
    start_button_big_pasta = types.KeyboardButton("💪 Паста 150мл", request_contact=False, request_location=False)
    markup.append(start_button_big_pasta)

def check_button_start_small_balzam(markup):
    start_button_small_balzam = types.KeyboardButton("🤏🏽 Бальзам 15мл", request_contact=False, request_location=False)
    markup.append(start_button_small_balzam)

def check_button_start_big_balzam(markup):
    start_button_big_balzam = types.KeyboardButton("💪🏽 Бальзам 150мл", request_contact=False, request_location=False)
    markup.append(start_button_big_balzam)

def check_button_start_two_pasta(markup):
    start_button_two_pasta = types.KeyboardButton("🌓 Пасты 15мл и 150мл", request_contact=False, request_location=False)
    markup.add(start_button_two_pasta)

def check_button_start_two_balzam(markup):
    start_button_two_balzam = types.KeyboardButton("🌗 Бальзамы 15мл и 150мл", request_contact=False, request_location=False)
    markup.add(start_button_two_balzam)

# глобальные переменные - флаги
stop_parsing_flag = False
is_checking_small_pasta = False
is_checking_big_pasta = False
is_checking_two_pasta = False
is_checking_small_balzam = False
is_checking_big_balzam = False
is_checking_two_balzam = False
timer = None
timer_sleep = 300

# ниже идут кнопки для бота
@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def help(message):
    bot.send_message(message.chat.id, f"""
                    ❓ ***Помощь*** - вызов справки 👻\n\n📛 ***Остановить*** - остановка вообще _всех_ парсингов.\n\n🕵️‍♂️ ***Наличие*** - проверка наличия товара на текущий момент.\n\n🤏 ***Паста 15мл*** - запуск автоматической проверки на наличие товара _маленькой_ пасты.\n\n💪 ***Паста 150мл*** - запуск автоматической проверки на наличие товара _большой_ пасты.\n\n🌓 **Пасты 15мл и 150мл** - запуск автоматической проверки на наличие товара и _большой_ и _маленькой_ паст.\n\n🤏🏽 ***Бальзам 15мл*** - запуск автоматической проверки на наличие товара _маленького_ бальзама.\n\n💪🏽 ***Бальзам 150мл*** - запуск автоматической проверки на наличие товара _большого_ бальзама.\n\n🌗 **Бальзамы 15мл и 150мл** - запуск автоматической проверки на наличие товара и _большого_ и _маленького_ бальзама.\n\n⚠️**ВНИМАНИЕ!**⚠️ Работать одновременно может только _один_ парсинг из всех! Перед запуском другого парсинга, необходимо кнопкой *остановить* работу действующих парсингов и дождаться ответа от Фиксиков 👾 =)""", parse_mode= "Markdown")

@bot.message_handler(func=lambda message: message.text == "📛 Остановить")
def stop_parsing(message):
    global stop_parsing_flag, is_checking_big_pasta, is_checking_small_pasta, is_checking_two_pasta, timer, is_checking_big_balzam, is_checking_small_balzam, is_checking_two_balzam
    stop_parsing_flag = True
    is_checking_small_pasta = False
    is_checking_big_pasta = False
    is_checking_two_pasta = False
    is_checking_small_balzam = False
    is_checking_big_balzam = False
    is_checking_two_balzam = False
    bot.send_message(message.chat.id, f"Немного терпения!🍿\nФиксикам надо остановить все работы и убрать рабочее место!🧘‍♂️🧘‍♀️\n\nПридёт уведомление когда можно начать новый парсинг.....⏳")
    if timer:
        timer.join()  # Дождаться завершения потока
        timer = None
    bot.send_message(message.chat.id, f"Весь парсинг был успешно остановлен!✅\nСпасибо за ожидание!🍨\nФиксики ждут новых заданий!🧟🧟‍♀️🧟‍♂️")


@bot.message_handler(func=lambda message: message.text == "🕵️‍♂️ Наличие")
def one_check(message):
        availability_1 = start_check(url_1)
        availability_2 = start_check(url_2)
        availability_3 = start_check(url_3)
        availability_4 = start_check(url_4)
        bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_1}\n\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}\n\n\n{availability_3}\nэто Смарт Бальзам 15мл: {url_3}\n\n\n{availability_4}\nэто Смарт Бальзам 150мл: {url_4}")

# дальше логика бота.
# избавимся от дублирования, указание какой парсинг уже запущен.
def check_products_parsing_status(message):
    status_messages = {
        "is_checking_small_pasta": "Парсинг пасты 15мл уже запущен.",
        "is_checking_big_pasta": "Парсинг пасты 150мл уже запущен.",
        "is_checking_two_pasta": "Парсинг пасты 15мл и 150мл уже запущен.",
        "is_checking_small_balzam": "Парсинг бальзама 15мл уже запущен.",
        "is_checking_big_balzam": "Парсинг бальзама 150мл уже запущен.",
        "is_checking_two_balzam": "Парсинг бальзама 15мл и 150мл уже запущен."
    }
    for product_type, status_message in status_messages.items():
        if globals()[f'{product_type}']:
            bot.send_message(message.chat.id, status_message)
            return False
    return True

# общая функция запуска парсинга
@bot.message_handler(func=lambda message: message.text in ["🤏 Паста 15мл", "💪 Паста 150мл", "🤏🏽 Бальзам 15мл", "💪🏽 Бальзам 150мл"])
def check_products_pasta_handler(message):
    product_types = {
        "🤏 Паста 15мл": ("small_pasta", "пасты 15мл", url_1),
        "💪 Паста 150мл": ("big_pasta", "пасты 150мл", url_2),
        "🤏🏽 Бальзам 15мл": ("small_balzam", "бальзама 15мл", url_3),
        "💪🏽 Бальзам 150мл": ("big_balzam", "бальзама 150мл", url_4),
    }
    product_type, product_name, url = product_types.get(message.text)
    print(message.text)
    check_products_pasta(message, product_type, product_name, url)

def check_products_pasta(message, product_type, product_name, url):
    global stop_parsing_flag, is_checking_big_pasta, is_checking_small_pasta, is_checking_two_pasta, timer, is_checking_big_balzam, is_checking_small_balzam, is_checking_two_balzam

    if not check_products_parsing_status(message):
        return

    bot.send_message(message.chat.id, f"Запустился парсинг {product_name}.")
    globals()[f'is_checking_{product_type}'] = True
    stop_parsing_flag = False

    def parsing_loop():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability = start_check(url)
            if availability == answer:
                pass
                # bot.send_message(message.chat.id, f"test {product_name}")
            else:
                bot.send_message(message.chat.id, f"Состояние товара:\n\n{availability}\nэто {product_name}: {url}")
                break

    timer = threading.Thread(target=parsing_loop)
    timer.start()


@bot.message_handler(func=lambda message: message.text == "🌓 Пасты 15мл и 150мл")
def check_products_two_pasta(message):
    global stop_parsing_flag, is_checking_big_pasta, is_checking_small_pasta, is_checking_two_pasta, timer, is_checking_big_balzam, is_checking_small_balzam, is_checking_two_balzam
    if not check_products_parsing_status(message):
        return

    bot.send_message(message.chat.id, f"Запустился парсинг паст 15мл и 150мл.")
    is_checking_two_pasta = True
    stop_parsing_flag = False
    def parsing_loop():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability_1 = start_check(url_1)
            availability_2 = start_check(url_2)
            if availability_1 != answer or availability_2 != answer:
                bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_1}\nэто Смарт Паста 15мл: {url_1}\n\n\n{availability_2}\nэто Смарт Паста 150мл: {url_2}")
                break
            else:
                pass
                # bot.send_message(message.chat.id, f"test 15 and 150 pasta")
    timer = threading.Thread(target=parsing_loop)
    timer.start()


@bot.message_handler(func=lambda message: message.text == "🌗 Бальзамы 15мл и 150мл")
def check_products_two_balzam(message):
    global stop_parsing_flag, is_checking_big_pasta, is_checking_small_pasta, is_checking_two_pasta, timer, is_checking_big_balzam, is_checking_small_balzam, is_checking_two_balzam
    if not check_products_parsing_status(message):
        return

    bot.send_message(message.chat.id, f"Запустился парсинг бальзамов 15мл и 150мл.")
    is_checking_two_balzam = True
    stop_parsing_flag = False
    def parsing_loop():
        while not stop_parsing_flag:
            time.sleep(timer_sleep)
            availability_1 = start_check(url_3)
            availability_2 = start_check(url_4)
            if availability_1 != answer or availability_2 != answer:
                bot.send_message(message.chat.id, f"Состояние товаров:\n\n{availability_1}\nэто Смарт Бальзам 15мл: {url_3}\n\n\n{availability_2}\nэто Смарт Бальзам 150мл: {url_4}")
                break
            else:
                pass
                # bot.send_message(message.chat.id, f"test 15 and 150 balzam")
    timer = threading.Thread(target=parsing_loop)
    timer.start()

bot.polling()
