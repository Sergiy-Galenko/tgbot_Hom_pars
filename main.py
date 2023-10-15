import requests
import time
import json
from bs4 import BeautifulSoup

# Токен вашого бота в Telegram
TOKEN = "6505643635:AAGiVH7PloEUkrEYZTnygcBnNTQjhmDNzNM"
# Загальний URL для роботи з Telegram API
API_URL = f"https://api.telegram.org/bot{TOKEN}/"
# Список підписників, які взаємодіють з ботом
subscribers = []


def get_olx_apartment_details():
    """Отримує деталі квартир з OLX."""
    url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Bfilter_float_price:from%5D=6000&search%5Bfilter_float_price:to%5D=9000"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Ваші CSS селектори для отримання даних з OLX
    apartments = soup.select(".some-class-for-apartments")
    details_list = []

    for apt in apartments:
        image = apt.select_one(".some-class-for-image")["src"]
        location = apt.select_one(".some-class-for-location").text.strip()
        price = apt.select_one(".some-class-for-price").text.strip()

        details_list.append((image, location, price))

    return details_list


def parse_dom_ria():
    """Отримує деталі квартир з dom.ria."""
    url = "https://dom.ria.com/uk/arenda-kvartir/kiev-nedorogo/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Ваші CSS селектори для отримання даних з dom.ria
    apartments = soup.select(".specific-class-for-apartments")
    details_list = []

    for apt in apartments:
        image = apt.select_one(".specific-class-for-image")["src"]
        location = apt.select_one(".specific-class-for-location").text.strip()
        price = apt.select_one(".specific-class-for-price").text.strip()

        details_list.append((image, location, price))

    return details_list


def parse_100realty():
    """Отримує деталі квартир з 100realty."""
    url = "https://100realty.ua/uk/realty_search/apartment/rent/p_4000_8000/cur_3/kch_2"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Ваші CSS селектори для отримання даних з 100realty
    apartments = soup.select(".another-specific-class-for-apartments")
    details_list = []

    for apt in apartments:
        image = apt.select_one(".another-specific-class-for-image")["src"]
        location = apt.select_one(".another-specific-class-for-location").text.strip()
        price = apt.select_one(".another-specific-class-for-price").text.strip()

        details_list.append((image, location, price))

    return details_list


def send_to_telegram(details_list):
    """Надсилає деталі квартир у Telegram."""
    for detail in details_list:
        for subscriber in subscribers:
            caption = f"Місце розташування: {detail[1]}\nЦіна: {detail[2]}"
            data = {
                "chat_id": subscriber,
                "photo": detail[0],
                "caption": caption
            }
            requests.post(API_URL + "sendPhoto", data=data)


def send_keyboard(chat_id, message):
    """Надсилає клавіатуру (випадаючий список команд) у Telegram."""
    keyboard = {
        "keyboard": [[{"text": "/data"}, {"text": "/help"}]],
        "resize_keyboard": True
    }
    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": json.dumps(keyboard)
    }
    requests.post(API_URL + "sendMessage", data=payload)


def check_updates(last_update_id=0):
    """Перевіряє нові повідомлення в Telegram та реагує на команди."""
    response = requests.get(API_URL + "getUpdates", params={"offset": last_update_id + 1})
    updates = response.json().get("result", [])

    for update in updates:
        chat_id = update["message"]["chat"]["id"]
        message_text = update["message"]["text"]

        if message_text == "/data":
            current_date = time.strftime("%Y-%m-%d")
            requests.get(API_URL + "sendMessage", params={"chat_id": chat_id, "text": current_date})
            continue
        elif message_text == "/help":
            help_message = "Виберіть команду з наведеного списку."
            send_keyboard(chat_id, help_message)
            continue
        elif message_text.startswith("/"):
            send_keyboard(chat_id, "Виберіть команду з наведеного списку.")
            continue

        if chat_id not in subscribers:
            subscribers.append(chat_id)
            send_keyboard(chat_id, "Ви підписалися на оновлення! Виберіть команду з наведеного списку.")

    if updates:
        return updates[-1]["update_id"]
    return last_update_id


if __name__ == "__main__":
    last_update_id = 0

    while True:
        last_update_id = check_updates(last_update_id)

        details = get_olx_apartment_details()
        send_to_telegram(details)

        details = parse_dom_ria()
        send_to_telegram(details)

        details = parse_100realty()
        send_to_telegram(details)
