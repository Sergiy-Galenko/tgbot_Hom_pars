import requests
import time
from bs4 import BeautifulSoup
from telegram import Bot, InputMediaPhoto
from telegram.ext import Updater, MessageHandler, Filters

TOKEN = "6505643635:AAGiVH7PloEUkrEYZTnygcBnNTQjhmDNzNM"
bot = Bot(token=TOKEN)

subscribers = []


def get_apartment_details():
    url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Bfilter_float_price:from%5D=6000&search%5Bfilter_float_price:to%5D=9000"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Знаходимо контейнери з квартирами (цей селектор може вимагати налаштування в залежності від структури сайту)
    apartments = soup.select(".some-class-for-apartments")

    details_list = []

    for apt in apartments:
        image = apt.select_one(".some-class-for-image")["src"]
        location = apt.select_one(".some-class-for-location").text.strip()
        price = apt.select_one(".some-class-for-price").text.strip()

        details_list.append((image, location, price))

    return details_list


def send_to_telegram(details_list):
    for detail in details_list:
        media = InputMediaPhoto(media=detail[0], caption=f"Місце розташування: {detail[1]}\nЦіна: {detail[2]}")
        for subscriber in subscribers:
            bot.send_media_group(chat_id=subscriber, media=[media])


def handle_messages(update, context):
    chat_id = update.message.chat_id
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        update.message.reply_text("Ви підписалися на оновлення!")
    else:
        update.message.reply_text("Ви вже підписані!")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))
    updater.start_polling()

    # Цей код буде виконувати парсинг та надсилати оновлення кожні 60 хвилин
    while True:
        details = get_apartment_details()
        send_to_telegram(details)
        time.sleep(3600)


if __name__ == "__main__":
    main()
