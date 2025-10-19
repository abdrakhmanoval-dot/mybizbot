import os
import telebot
from telebot import types
from fastapi import FastAPI
import uvicorn
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен зададим на Render
if not BOT_TOKEN:
    raise RuntimeError("Нет BOT_TOKEN (задать как переменную окружения).")

bot = telebot.TeleBot(BOT_TOKEN)

# --- Кнопки главного меню ---
def kb_main():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Кампания"), types.KeyboardButton("Уроки"))
    kb.add(types.KeyboardButton("Глоссарий"))
    return kb

CAMPAIGN_CHAPTERS = [
    "Глава 1: Вступление",
    "Глава 2: Запуск MVP",
    "Глава 3: Масштабирование",
]

def kb_campaign():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for title in CAMPAIGN_CHAPTERS:
        row.append(types.KeyboardButton(title))
        if len(row) == 2:
            kb.add(*row); row = []
    if row: kb.add(*row)
    kb.add(types.KeyboardButton("Назад в меню"))
    return kb

def kb_chapter():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Назад к Кампании"))
    kb.add(types.KeyboardButton("Назад в меню"))
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Это мой бизнес-бот. Выбирай раздел:",
        reply_markup=kb_main()
    )

@bot.message_handler(func=lambda m: m.text == "Кампания")
def section_campaign(message):
    bot.send_message(message.chat.id, "Кампания. Выбери главу:", reply_markup=kb_campaign())

@bot.message_handler(func=lambda m: m.text == "Уроки")
def section_lessons(message):
    bot.send_message(message.chat.id, "Раздел 'Уроки' пока пуст.", reply_markup=kb_main())

@bot.message_handler(func=lambda m: m.text == "Глоссарий")
def section_glossary(message):
    bot.send_message(message.chat.id, "Раздел 'Глоссарий' пока пуст.", reply_markup=kb_main())

@bot.message_handler(func=lambda m: m.text in CAMPAIGN_CHAPTERS)
def chapter_selected(message):
    bot.send_message(message.chat.id, f"{message.text}\nСодержимое главы пока пусто.", reply_markup=kb_chapter())

@bot.message_handler(func=lambda m: m.text == "Назад к Кампании")
def back_to_campaign(message):
    section_campaign(message)

@bot.message_handler(func=lambda m: m.text == "Назад в меню")
def back_to_main(message):
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=kb_main())

# --- Запуск polling в отдельном потоке ---
def run_bot():
    bot.polling(none_stop=True, timeout=90)

# --- Мини-вебсервер, чтобы Render не засыпал ---
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
