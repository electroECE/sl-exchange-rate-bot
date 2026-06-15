import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BANKS = {
    "BOC": "https://www.boc.lk/rates-tariff",
    "Pan Asia Bank": "https://www.pabcbank.com/treasury/exchange-rate/",
    "Union Bank": "https://www.unionb.com/exchange-rates/",
}

CURRENCY_KEYWORDS = {
    "USD": ["USD", "US Dollar", "United States Dollar", "US DOLLAR"],
    "CNY": ["CNY", "Chinese Yuan", "RMB", "CHINESE YUAN"],
}


def fetch_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text("\n", strip=True)


def extract_rate(text, keywords):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        combined = " ".join(lines[i:i+6])

        if any(k.lower() in combined.lower() for k in keywords):
            numbers = re.findall(r"\d+\.\d+|\d+", combined)

            clean_numbers = []
            for n in numbers:
                try:
                    value = float(n)
                    if 20 <= value <= 500:
                        clean_numbers.append(n)
                except:
                    pass

            if len(clean_numbers) >= 2:
                return {
                    "buy": clean_numbers[0],
                    "sell": clean_numbers[1],
                }

    return {"buy": "N/A", "sell": "N/A"}


def get_bank_rates():
    result = {}

    for bank, url in BANKS.items():
        try:
            text = fetch_text(url)

            result[bank] = {
                "USD": extract_rate(text, CURRENCY_KEYWORDS["USD"]),
                "CNY": extract_rate(text, CURRENCY_KEYWORDS["CNY"]),
            }

        except Exception:
            result[bank] = {
                "USD": {"buy": "N/A", "sell": "N/A"},
                "CNY": {"buy": "N/A", "sell": "N/A"},
            }

    return result


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
    rates = get_bank_rates()
    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y %I:%M %p")
    today = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y")

    message = "🇱🇰 Sri Lanka Daily Exchange Rates\n"
    message += f"📅 Rate Date: {today}\n\n"

    message += "💵 USD/LKR\n"
    for bank, data in rates.items():
        message += f"🏦 {bank}: Buy {data['USD']['buy']} | Sell {data['USD']['sell']}\n"

    message += "\n🇨🇳 CNY/RMB/LKR\n"
    for bank, data in rates.items():
        message += f"🏦 {bank}: Buy {data['CNY']['buy']} | Sell {data['CNY']['sell']}\n"

    message += f"\n🕒 Bot Updated: {now}"
    message += "\n\nRates are indicative. Please confirm with the bank before transactions."

    send_message(message)


if __name__ == "__main__":
    main()
