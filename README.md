# Telegram News Bot + GPT + Telegram Parsing
Этот бот:
- Читает новости из RSS
- Парсит посты из Telegram-каналов
- Переписывает текст через GPT
- Публикует в ваш Telegram-канал

## ✅ Установка
```bash
git clone <your_repo>
cd telegram-news-gpt-bot-telegram-parser
cp .env.example .env
nano .env
```

## ▶ Запуск локально
```bash
pip install -r requirements.txt
python bot.py
```

## ▶ Запуск через Docker
```bash
docker build -t news-bot .
docker run --env-file .env news-bot
```
