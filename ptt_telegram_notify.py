import requests
from bs4 import BeautifulSoup
import os
import datetime

# ========= 設定區 =========
BOT_TOKEN = os.environ.get('8482553745:AAHM7PxZNJg9j7ot7u88nAqJURchOSAnNp8')
CHAT_ID = os.environ.get('7701043479')
PTT_BOARDS = ['carshop', 'car']
# ==========================

# ✅ 儲存記憶在 Telegram pinned message 中的方式
PIN_STORAGE_API = f"https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=payload)
    if resp.ok:
        msg_id = resp.json()['result']['message_id']
        requests.post(PIN_STORAGE_API, data={
            "chat_id": CHAT_ID,
            "message_id": msg_id
        })

def get_latest_article(board):
    url = f"https://www.ptt.cc/bbs/{board}/index.html"
    res = requests.get(url, cookies={'over18': '1'})
    soup = BeautifulSoup(res.text, 'html.parser')
    title_tag = soup.select_one('div.title a')
    if title_tag:
        title = title_tag.text.strip()
        link = 'https://www.ptt.cc' + title_tag['href']
        return title, link
    return None, None

def load_last_articles():
    try:
        with open("ptt_cache.txt", 'r') as f:
            return dict(line.strip().split('|||') for line in f if '|||' in line)
    except:
        return {}

def save_last_articles(data):
    with open("ptt_cache.txt", 'w') as f:
        for board, title in data.items():
            f.write(f'{board}|||{title}\n')

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_telegram_message(f"📬 Bot 每日檢查中：{now}")

    last_articles = load_last_articles()
    new_articles = {}

    for board in PTT_BOARDS:
        title, link = get_latest_article(board)
        if not title:
            continue

        if board not in last_articles or last_articles[board] != title:
            msg = f"<b>[{board}] 有新文章：</b>\n{title}\n🔗 <a href=\"{link}\">{link}</a>"
            send_telegram_message(msg)
            new_articles[board] = title
        else:
            new_articles[board] = last_articles[board]

    save_last_articles(new_articles)

if __name__ == '__main__':
    main()
