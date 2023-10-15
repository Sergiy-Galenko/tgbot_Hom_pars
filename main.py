import requests
import time
import json
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = "6505643635:AAGiVH7PloEUkrEYZTnygcBnNTQjhmDNzNM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
subscribed_users = []


def extract_apartment_information_from_olx():
    olx_url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Bfilter_float_price:from%5D=6000&search%5Bfilter_float_price:to%5D=9000"
    website_response = requests.get(olx_url)

    if website_response.status_code != 200:
        print(f"Failed to fetch data from OLX. Status code: {website_response.status_code}")
        return []

    html_content = BeautifulSoup(website_response.content, 'html.parser')

    apartment_elements = html_content.select(".some-class-for-apartments")
    apartment_information = []

    for apartment in apartment_elements:
        image_url = apartment.select_one(".some-class-for-image")["src"]
        apartment_location = apartment.select_one(".some-class-for-location").text.strip()
        apartment_price = apartment.select_one(".some-class-for-price").text.strip()

        apartment_information.append((image_url, apartment_location, apartment_price))

    return apartment_information


def send_apartment_information_to_user(details_list):
    for apartment_detail in details_list:
        for user in subscribed_users:
            information_caption = f"Location: {apartment_detail[1]}\nPrice: {apartment_detail[2]}"
            data_to_send = {
                "chat_id": user,
                "photo": apartment_detail[0],
                "caption": information_caption
            }
            requests.post(TELEGRAM_API_URL + "sendPhoto", data=data_to_send)


def display_commands_to_user(chat_id, message_text):
    command_keyboard = {
        "keyboard": [[{"text": "/data"}, {"text": "/help"}, {"text": "/home"}]],
        "resize_keyboard": True
    }
    message_payload = {
        "chat_id": chat_id,
        "text": message_text,
        "reply_markup": json.dumps(command_keyboard)
    }
    requests.post(TELEGRAM_API_URL + "sendMessage", data=message_payload)


def check_new_telegram_messages(last_update_id=0):
    telegram_response = requests.get(TELEGRAM_API_URL + "getUpdates", params={"offset": last_update_id + 1})
    message_updates = telegram_response.json().get("result", [])

    for update in message_updates:
        user_chat_id = update["message"]["chat"]["id"]
        user_message_text = update["message"]["text"]

        if user_message_text == "/data":
            current_date_string = time.strftime("%Y-%m-%d")
            requests.get(TELEGRAM_API_URL + "sendMessage",
                         params={"chat_id": user_chat_id, "text": current_date_string})
            continue
        elif user_message_text == "/help":
            display_commands_to_user(user_chat_id, "Please select a command from the list.")
            continue
        elif user_message_text == "/home":
            olx_apartment_details = extract_apartment_information_from_olx()
            if olx_apartment_details:
                send_apartment_information_to_user([olx_apartment_details[0]])
            continue
        elif user_message_text.startswith("/"):
            display_commands_to_user(user_chat_id, "Please select a command from the list.")
            continue

        if user_chat_id not in subscribed_users:
            subscribed_users.append(user_chat_id)
            display_commands_to_user(user_chat_id,
                                     "You have subscribed for updates! Please select a command from the list.")

    if message_updates:
        return message_updates[-1]["update_id"]
    return last_update_id


if __name__ == "__main__":
    last_processed_update_id = 0

    while True:
        last_processed_update_id = check_new_telegram_messages(last_processed_update_id)
