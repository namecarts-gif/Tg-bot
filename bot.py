import datetime
import random
from collections import defaultdict
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# Фейковый веб-сервер, чтобы Render не ругался на порты
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

BOT_TOKEN = "8991528748:AAErqctNdHVU8t4kHnsnL3fmiGKwuF58T1o"
bot = telebot.TeleBot(BOT_TOKEN)

karma_db = defaultdict(lambda: defaultdict(lambda: {"name": "", "points": 0}))
active_users = defaultdict(dict)
dick_db = defaultdict(dict)


# === КОМАНДА ПОМОЩИ И СПИСОК КОМАНД ===
@bot.message_handler(commands=["helppenis", "help", "команды"])
def cmd_helppenis(message):
    help_text = (
        "📜 **Список всех команд бота:**\n\n"
        "🔥 **Развлечения и Интерактив:**\n"
        "• `/lips` (или `/губы`) — Поводить членом по губам\n"
        "• `/slap` — Дать леща\n"
        "• `/roulette` — Русская рулетка\n"
        "• `/who [вопрос]` — Выбрать участника беседы\n\n"
        "📏 **Измерение и Топ размера:**\n"
        "• `/dick` — Измерить размер на сегодня\n"
        "• `/topdick` — Топ гигантов беседы\n"
        "• `/checkdick` — Узнать размер другого\n\n"
        "🏆 **Карма и Респект:**\n"
        "• `+` / `респект` (в ответ) — Поднять карму\n"
        "• `/top` — Топ по карме"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")


# === ПОВЕСТИ ЧЛЕНОМ ПО ГУБАМ ===
@bot.message_handler(commands=["lips", "губы", "поводить"])
def cmd_lips(message):
    if message.reply_to_message:
        target_name = message.reply_to_message.from_user.first_name
    else:
        args = message.text.replace("/lips", "").replace("/губы", "").replace("/поводить", "").strip()
        if args:
            target_name = args
        else:
            users = active_users.get(message.chat.id, {})
            target_name = random.choice(list(users.values())) if users else "воздух"
            
    actions = [
        f"ловко поводил членом по губам **{target_name}** 🍌😏",
        f"нежно провёл членом по губам **{target_name}** ✨🍆",
        f"решил поводить членом по губам **{target_name}**, но тот попытался попробовать на вкус! 😱🦷",
        f"устроил мастер-класс и поводил членом по губам **{target_name}** 🗿🔥"
    ]
    action = random.choice(actions)
    bot.reply_to(message, f"😏 **{message.from_user.first_name}** {action}", parse_mode="Markdown")


# === ИЗМЕРЕНИЕ РАЗМЕРА ===
@bot.message_handler(commands=["dick", "penis", "size"])
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["сколько см", "измерить", "член"])
def cmd_dick(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    today = datetime.date.today()
    
    user_data = dick_db[chat_id].get(user_id)
    if user_data and user_data["date"] == today:
        bot.reply_to(message, f"За сегодня ты уже мерил! 📏\nРезультат: **{user_data['size']} см**.", parse_mode="Markdown")
        return
        
    size = random.randint(1, 35)
    dick_db[chat_id][user_id] = {"size": size, "date": today, "name": user_name}
    
    comments = [
        (5, "Микроскоп в комплект не входит... 🔬"),
        (10, "Главное — не размер, а харизма! 🤏"),
        (16, "Уверенный середнячок, уважение! 👍"),
        (23, "Ого, солидный гигант! 🍌"),
        (30, "Это уже опасное оружие! ⚔️"),
        (36, "ЛЕГЕНДА! Как ты с этим ходишь?! 🐘")
    ]
    comment = next(c for limit, c in comments if size < limit)
    bot.reply_to(message, f"📏 **{user_name}**, твой результат на сегодня: **{size} см**!\n💬_{comment}_", parse_mode="Markdown")


# === ТОП ГИГАНТОВ ===
@bot.message_handler(commands=["topdick", "dicktop", "топчленов"])
def cmd_topdick(message):
    chat_id = message.chat.id
    today = datetime.date.today()
    chat_dicks = dick_db.get(chat_id, {})
    
    today_dicks = [data for data in chat_dicks.values() if data.get("date") == today]
    
    if not today_dicks:
        bot.reply_to(message, "Сегодня ещё никто не мерился! Будь первым — напиши `/dick`", parse_mode="Markdown")
        return
        
    sorted_dicks = sorted(today_dicks, key=lambda x: x["size"], reverse=True)
    text = "🍆 **Топ гигантов на сегодня:**\n\n"
    for i, user in enumerate(sorted_dicks[:10]):
        text += f"{i+1}. {user['name']} — **{user['size']} см**\n"
    bot.reply_to(message, text, parse_mode="Markdown")


# === ПРОВЕРКА ЧУЖОГО РАЗМЕРА ===
@bot.message_handler(commands=["checkdick", "чекчлен"])
def cmd_checkdick(message):
    chat_id = message.chat.id
    today = datetime.date.today()
    target_id = None
    target_name = None
    
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
    else:
        args = message.text.replace("/checkdick", "").replace("/чекчлен", "").strip()
        if args:
            for uid, name in active_users.get(chat_id, {}).items():
                if args.lower() in name.lower() or args.lower() in f"@{name}".lower():
                    target_id = uid
                    target_name = name
                    break
            if not target_id:
                target_name = args
        else:
            bot.reply_to(message, "Ответь этой командой на сообщение человека или напиши его имя!")
            return

    if target_id and target_id in dick_db[chat_id]:
        data = dick_db[chat_id][target_id]
        if data["date"] == today:
            bot.reply_to(message, f"🔍 У **{target_name}** сегодня результат: **{data['size']} см**!", parse_mode="Markdown")
            return

    bot.reply_to(message, f"🔍 **{target_name}** сегодня ещё не производил замеры! 📏")


# === РУЛЕТКА ===
@bot.message_handler(commands=["roulette"])
def cmd_roulette(message):
    if random.randint(1, 6) == 1:
        bot.reply_to(message, f"💥 **БАХ!** {message.from_user.first_name} не повезло... Выбыл! 🪦", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"🎯 {message.from_user.first_name}, повезло — холостой!")


# === КТО / РАНДОМНЫЙ ВЫБОР ===
@bot.message_handler(commands=["who"])
def cmd_who(message):
    users = active_users.get(message.chat.id, {})
    if not users:
        bot.reply_to(message, "Я пока не запомнил участников! Попишите в чат.")
        return
    chosen_name = random.choice(list(users.values()))
    question = message.text.replace("/who", "").strip()
    text = f"🎲 Я думаю, что **{chosen_name}** {question}" if question else f"🎲 Жребий пал на **{chosen_name}**!"
    bot.reply_to(message, text, parse_mode="Markdown")


# === ДОБАВЛЕНИЕ КАРМЫ ===
@bot.message_handler(func=lambda m: m.text in ["+", "+1", "респект", "лайк"] and m.reply_to_message)
def add_karma(message):
    reply = message.reply_to_message
    if reply.from_user.id == message.from_user.id or reply.from_user.is_bot:
        return
    chat_id, target_id = message.chat.id, reply.from_user.id
    karma_db[chat_id][target_id]["name"] = reply.from_user.first_name
    karma_db[chat_id][target_id]["points"] += 1
    total = karma_db[chat_id][target_id]["points"]
    bot.reply_to(message, f"👍 **{message.from_user.first_name}** поднял карму **{reply.from_user.first_name}**! (Всего: **{total}**)", parse_mode="Markdown")


# === ТОП ПО КАРМЕ ===
@bot.message_handler(commands=["top"])
def cmd_top(message):
    chat_karma = karma_db.get(message.chat.id, {})
    if not chat_karma:
        bot.reply_to(message, "Пока никто не получал карму!")
        return
    sorted_users = sorted(chat_karma.values(), key=lambda x: x["points"], reverse=True)
    text = "🏆 **Топ по карме:**\n\n"
    for i, user in enumerate(sorted_users[:10]):
        text += f"{i+1}. {user['name']} — **{user['points']}** респектов\n"
    bot.reply_to(message, text, parse_mode="Markdown")


# === СЛАП ===
@bot.message_handler(commands=["slap"])
def cmd_slap(message):
    item = random.choice(["мокрой рыбой 🐟", "клавиатурой ⌨️", "учебником по физике 📚", "букетом роз 🌹"])
    if message.reply_to_message:
        target_name = message.reply_to_message.from_user.first_name
    else:
        args = message.text.replace("/slap", "").strip()
        if args:
            target_name = args
        else:
            users = active_users.get(message.chat.id, {})
            target_name = random.choice(list(users.values())) if users else "воздух"
    bot.reply_to(message, f"💥 **{message.from_user.first_name}** дал леща **{target_name}** {item}", parse_mode="Markdown")


# === ТРЕКИНГ УЧАСТНИКОВ ===
@bot.message_handler(func=lambda message: message.chat.type in ["group", "supergroup"])
def track_users(message):
    if message.from_user and not message.from_user.is_bot:
        active_users[message.chat.id][message.from_user.id] = message.from_user.first_name


if __name__ == "__main__":
    try:
        bot.remove_webhook()
    except:
        pass
    print("🚀 Бот запущен!")
    bot.infinity_polling(skip_pending=True)
    
