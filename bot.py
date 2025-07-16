import os
import asyncio
import feedparser
from pyrogram import Client
from telegram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import time

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # куда постим
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RSS_FEED = os.getenv("RSS_FEED", "https://lenta.ru/rss/news")

# Pyrogram для чтения каналов
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS", "").split(",")

bot = Bot(token=BOT_TOKEN)
client_openai = OpenAI(api_key=OPENAI_API_KEY)
posted_links_file = "posted_links.txt"


def load_posted_links():
    if not os.path.exists(posted_links_file):
        return set()
    with open(posted_links_file, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


def save_posted_link(link):
    with open(posted_links_file, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def rewrite_text(text):
    prompt = f"Перепиши текст новости коротко, понятно и интересно:\n\n{text}"
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты редактор новостей. Пиши лаконично."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def fetch_rss_news():
    feed = feedparser.parse(RSS_FEED)
    return [(entry.title, entry.link) for entry in feed.entries[:5]]


async def fetch_telegram_news(app, posted_links):
    for channel in SOURCE_CHANNELS:
        async for message in app.get_chat_history(channel, limit=5):
            if message.text and str(message.id) not in posted_links:
                yield message.text, str(message.id)
                save_posted_link(str(message.id))


async def main():
    posted_links = load_posted_links()

    # Запускаем Pyrogram для чтения каналов
    app = Client("session", api_id=API_ID, api_hash=API_HASH)
    await app.start()

    while True:
        # RSS
        rss_news = fetch_rss_news()
        for title, link in rss_news:
            if link not in posted_links:
                rewritten = rewrite_text(f"{title}\n{link}")
                bot.send_message(chat_id=CHANNEL_ID, text=rewritten)
                save_posted_link(link)
                time.sleep(10)

        # Telegram
        async for news_text, msg_id in fetch_telegram_news(app, posted_links):
            rewritten = rewrite_text(news_text)
            bot.send_message(chat_id=CHANNEL_ID, text=rewritten)
            time.sleep(10)

        await asyncio.sleep(600)  # каждые 10 минут

    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
