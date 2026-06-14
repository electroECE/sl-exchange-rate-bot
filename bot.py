import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

message = f"""
🇱🇰 Sri Lanka Daily Exchange Rates

💵 USD/LKR: Test
🇨🇳 CNY/RMB/LKR: Test

Updated: {datetime.now()}
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
).raise_for_status()
