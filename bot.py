import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BANKS = [
    "BOC",
    "Pan Asia Bank",
    "Union Bank",
    "HBL",
    "Sampath Bank",
]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text}).raise_for_status()

def get_bank_rates():
    # Temporary manual/test rates.
    # Next step: replace these with live website scraping.
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
        "HBL": {
            "USD": {"buy": "Checking", "sell": "Checking"},
            "CNY": {"buy": "Checking", "sell": "Checking"},
        },
        "Sampath Bank": {
            "USD": {"buy": "Checking", "sell": "Checking"},
            "CNY": {"buy": "Checking", "sell": "Checking"},
        },
    }

def main():
    rates = get_bank_rates()
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
