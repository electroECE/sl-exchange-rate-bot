import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    ).raise_for_status()


def get_rates():
    # We will replace this with live bank data next
    return {
        "USD": {
            "buy": "299.00",
            "sell": "305.00"
        },
        "CNY": {
            "buy": "41.50",
            "sell": "42.20"
        }
    }


def main():
    rates = get_rates()

    time = datetime.now(
        ZoneInfo("Asia/Colombo")
    ).strftime("%d-%m-%Y %I:%M %p")

    message = f"""
🇱🇰 Sri Lanka Daily Exchange Rates

💵 USD/LKR
Buy : Rs. {rates["USD"]["buy"]}
Sell: Rs. {rates["USD"]["sell"]}

🇨🇳 CNY/RMB/LKR
Buy : Rs. {rates["CNY"]["buy"]}
Sell: Rs. {rates["CNY"]["sell"]}

🕒 Updated:
{time}
"""

    send_message(message)


if __name__ == "__main__":
    main()
