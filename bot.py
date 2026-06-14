import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BANK_URLS = {
    "BOC": "https://www.boc.lk/rates-tariff",
    "Sampath": "https://www.sampath.lk/rates-and-charges?activeTab=exchange-rates",
    "HNB": "https://www.hnb.lk/exchange-rates",
    "Union Bank": "https://www.unionb.com/exchange-rates/",
    "Pan Asia": "https://www.pabcbank.com/treasury/exchange-rate/",
}

CURRENCIES = {
    "USD": ["USD", "US Dollar", "United States Dollar", "US DOLLAR"],
    "CNY": ["CNY", "Chinese Yuan", "RMB", "CHINESE YUAN"],
}


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_rates_from_text(text, currency_keys):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if any(key.lower() in line.lower() for key in currency_keys):
            numbers = re.findall(r"\d+\.\d+|\d+", line)

            if len(numbers) >= 2:
                return {
                    "buy": numbers[-2],
                    "sell": numbers[-1],
                }

    return {"buy": "N/A", "sell": "N/A"}


def get_bank_rate(bank, url):
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text("\n", strip=True)

        return {
            "USD": extract_rates_from_text(text, CURRENCIES["USD"]),
            "CNY": extract_rates_from_text(text, CURRENCIES["CNY"]),
        }

    except Exception:
        return {
            "USD": {"buy": "N/A", "sell": "N/A"},
            "CNY": {"buy": "N/A", "sell": "N/A"},
        }


def get_all_rates():
    all_rates = {}

    for bank, url in BANK_URLS.items():
        all_rates[bank] = get_bank_rate(bank, url)

    return all_rates


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=30,
    ).raise_for_status()


def main():
    rates = get_all_rates()

    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y %I:%M %p")

    message = "🇱🇰 Sri Lanka Daily Exchange Rates\n\n"

    message += "💵 USD/LKR\n"
    for bank, data in rates.items():
        message += f"🏦 {bank}: Buy {data['USD']['buy']} | Sell {data['USD']['sell']}\n"

    message += "\n🇨🇳 CNY/RMB/LKR\n"
    for bank, data in rates.items():
        message += f"🏦 {bank}: Buy {data['CNY']['buy']} | Sell {data['CNY']['sell']}\n"

    message += f"\n🕒 Updated: {now}"
    message += "\n\nRates are indicative and may change during the day."

    send_message(message)


if __name__ == "__main__":
    main()
