import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_text(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def empty_rates():
    return {
        "USD": {"buy": "N/A", "sell": "N/A"},
        "CNY": {"buy": "N/A", "sell": "N/A"},
    }


def get_union():
    text = get_text("https://www.unionb.com/exchange-rates/")

    usd = re.search(r"US DOLLAR\s+USD\s+([\d.]+)\s+([\d.]+)", text, re.I)
    cny = re.search(r"YUAN RENMINBI\s+CNY\s+([\d.]+)\s+([\d.]+)", text, re.I)

    return {
        "USD": {
            "buy": usd.group(1) if usd else "N/A",
            "sell": usd.group(2) if usd else "N/A",
        },
        "CNY": {
            "buy": cny.group(1) if cny else "N/A",
            "sell": cny.group(2) if cny else "N/A",
        },
    }


def safe(func):
    try:
        return func()
    except Exception:
        return empty_rates()


def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=30
    ).raise_for_status()


def main():
    rates = {
        "CBSL Average": empty_rates(),
        "BOC": empty_rates(),
        "Union Bank": safe(get_union),
    }

    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y %I:%M %p")
    today = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y")

    msg = "🇱🇰 Sri Lanka Daily Exchange Rates\n"
    msg += f"📅 Rate Date: {today}\n"
    msg += "Type: Telegraphic Transfer Buy/Sell\n\n"

    msg += "💵 USD/LKR\n"
    for bank, data in rates.items():
        msg += f"🏦 {bank}: Buy {data['USD']['buy']} | Sell {data['USD']['sell']}\n"

    msg += "\n🇨🇳 CNY/RMB/LKR\n"
    for bank, data in rates.items():
        msg += f"🏦 {bank}: Buy {data['CNY']['buy']} | Sell {data['CNY']['sell']}\n"

    msg += f"\n🕘 Auto time: 9:30 AM Sri Lanka"
    msg += f"\n🕒 Updated: {now}"
    msg += "\n\nBOC/CBSL show N/A until their reliable data source is fixed."
    msg += "\nRates are indicative. Confirm with bank before transactions."

    send_message(msg)


if __name__ == "__main__":
    main()
