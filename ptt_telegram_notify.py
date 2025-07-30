import requests
from bs4 import BeautifulSoup
import os
import datetime

# ========== 設定區 ==========
BOT_TOKEN = '8482553745:AAHM7PxZNJg9j7ot7u88nAqJURchOSAnNp8'
CHAT_ID = '7701043479'
PTT_BOARDS = ['carshop', 'car']  # ← 可放多個看板
LAST_FILE = 'last_articles.txt'
# ===========================

# 發送測試訊息（每次執行都會推送）
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
send_telegram_message(f"📬 Bot 每日檢查中：{now}")

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
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, 'r') as f:
            return dict(line.strip().split('|||') for line in f if '|||' in line)
    return {}

def save_last_articles(data):
    with open(LAST_FILE, 'w') as f:
        for board, title in data.items():
            f.write(f'{board}|||{title}\n')

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

def main():
    last_articles = load_last_articles()
    new_articles = {}

    for board in PTT_BOARDS:
        title, link = get_latest_article(board)
        if not title:
            continue

        if board not in last_articles or last_articles[board] != title:
            msg = f"[{board}] 有新文章：\n{title}\n{link}"
            send_telegram(msg)
            new_articles[board] = title
        else:
            new_articles[board] = last_articles[board]

    save_last_articles(new_articles)

if __name__ == '__main__':
    main()
