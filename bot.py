import os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_text(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.get_text(" ", strip=True)

def find_rate(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return {"buy": m.group(1), "sell": m.group(2)}
    return {"buy": "N/A", "sell": "N/A"}

def get_boc():
    text = get_text("https://www.boc.lk/rates-tariff")
    return {
        "USD": find_rate(text, [r"USD\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"]),
        "CNY": find_rate(text, [r"CNY\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"]),
    }

def get_union():
    text = get_text("https://www.unionb.com/exchange-rates/")
    return {
        "USD": find_rate(text, [r"US DOLLAR\s+USD\s+([\d.]+)\s+([\d.]+)"]),
        "CNY": find_rate(text, [r"YUAN RENMINBI\s+CNY\s+([\d.]+)\s+([\d.]+)"]),
    }

def get_panasia():
    text = get_text("https://www.pabcbank.com/treasury/exchange-rate/")

    print("===== PAN ASIA DATA START =====")
    print(text[:5000])
    print("===== PAN ASIA DATA END =====")

    return {
        "USD": {"buy": "TEST", "sell": "TEST"},
        "CNY": {"buy": "TEST", "sell": "TEST"},
    }

def safe(fn):
    try:
        return fn()
    except Exception:
        return {
            "USD": {"buy": "N/A", "sell": "N/A"},
            "CNY": {"buy": "N/A", "sell": "N/A"},
        }

def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=30).raise_for_status()

def main():
    rates = {
        "BOC": safe(get_boc),
        "Pan Asia Bank": safe(get_panasia),
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

    msg += f"\n🕒 Updated: {now}"
    msg += "\n\nRates are indicative. Confirm with bank before transactions.Vignes"

    send_message(msg)

if __name__ == "__main__":
    main()
