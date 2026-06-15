import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BANKS = ["BOC", "Pan Asia Bank", "Union Bank"]

def get_rates():
    # Temporary test rates.
    # After this works, we will connect live bank websites.
    return {
        "BOC": {
            "USD": {"buy": "Checking", "sell": "Checking"},
            "CNY": {"buy": "Checking", "sell": "Checking"},
        },
        "Pan Asia Bank": {
            "USD": {"buy": "Checking", "sell": "Checking"},
            "CNY": {"buy": "Checking", "sell": "Checking"},
        },
        "Union Bank": {
            "USD": {"buy": "Checking", "sell": "Checking"},
            "CNY": {"buy": "Checking", "sell": "Checking"},
        },
    }

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=30,
    ).raise_for_status()

def main():
    rates = get_rates()
    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y %I:%M %p")

    message = "🇱🇰 Sri Lanka Daily Exchange Rates\n\n"

    message += "💵 USD/LKR\n"
    for bank in BANKS:
        buy = rates[bank]["USD"]["buy"]
        sell = rates[bank]["USD"]["sell"]
        message += f"🏦 {bank}: Buy {buy} | Sell {sell}\n"

    message += "\n🇨🇳 CNY/RMB/LKR\n"
    for bank in BANKS:
        buy = rates[bank]["CNY"]["buy"]
        sell = rates[bank]["CNY"]["sell"]
        message += f"🏦 {bank}: Buy {buy} | Sell {sell}\n"

    message += f"\n🕒 Updated: {now}"

    send_message(message)

if __name__ == "__main__":
    main()
