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


def empty():
    return {
        "USD": {"buy": "N/A", "sell": "N/A"},
        "CNY": {"buy": "N/A", "sell": "N/A"},
    }


def find_after(text, patterns):
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return {"buy": m.group(1), "sell": m.group(2)}
    return {"buy": "N/A", "sell": "N/A"}


def get_union():
    text = get_text("https://www.unionb.com/exchange-rates/")

    return {
        "USD": find_after(text, [
            r"US DOLLAR\s+USD\s+([\d.]+)\s+([\d.]+)"
        ]),
        "CNY": find_after(text, [
            r"YUAN RENMINBI\s+CNY\s+([\d.]+)\s+([\d.]+)"
        ]),
    }


def get_peoples():
    text = get_text("https://www.peoplesbank.lk/exchange-rates/")

    return {
        "USD": find_after(text, [
            r"US Dollars\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"
        ]),
        "CNY": find_after(text, [
            r"Chinese Yuan\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)",
            r"CNY\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"
        ]),
    }


def get_dfcc():
    text = get_text("https://www.dfcc.lk/rates-and-tariff/exchange-rates")

    return {
        "USD": find_after(text, [
            r"USD\s+([\d.]+)\s+[\d.]+\s+([\d.]+)"
        ]),
        "CNY": find_after(text, [
            r"CNY\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"
        ]),
    }


def safe(func):
    try:
        return func()
    except Exception:
        return empty()


def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=30,
    ).raise_for_status()


def main():
    rates = {
        "Union Bank": safe(get_union),
        "People's Bank": safe(get_peoples),
        "DFCC Bank": safe(get_dfcc),
    }

    today = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y")
    now = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%d-%m-%Y %I:%M %p")

    msg = "🇱🇰 Sri Lanka Daily Exchange Rates\n"
    msg += f"📅 Rate Date: {today}\n"
    msg += "Type: Telegraphic Transfer Buy/Sell\n\n"

    msg += "💵 USD/LKR\n"
    for bank, data in rates.items():
        msg += f"🏦 {bank}: Buy {data['USD']['buy']} | Sell {data['USD']['sell']}\n"

    msg += "\n🇨🇳 CNY/RMB/LKR\n"
    for bank, data in rates.items():
        msg += f"🏦 {bank}: Buy {data['CNY']['buy']} | Sell {data['CNY']['sell']}\n"

    msg += "\n\n⏰ Auto time: 9:30 AM Sri Lanka"
    msg += f"\n🕒 Updated: {now}"
    msg += "\n\nRates are indicative. Confirm with bank before transactions."

    send_message(msg)


if __name__ == "__main__":
    main()
