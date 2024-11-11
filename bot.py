from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime, timedelta

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('bot_statistics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            date TEXT,
            count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Запись данных в базу
def record_data(user_id, username, date):
    conn = sqlite3.connect('bot_statistics.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT count FROM statistics WHERE user_id = ? AND date = ?
    ''', (user_id, date))
    result = cursor.fetchone()
    
    if result:
        cursor.execute('''
            UPDATE statistics SET count = count + 1 WHERE user_id = ? AND date = ?
        ''', (user_id, date))
    else:
        cursor.execute('''
            INSERT INTO statistics (user_id, username, date, count)
            VALUES (?, ?, ?, 1)
        ''', (user_id, username, date))
    conn.commit()
    conn.close()

# Получение отчета
def get_report(period):
    conn = sqlite3.connect('bot_statistics.db')
    cursor = conn.cursor()
    
    now = datetime.now()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        conn.close()
        return "Неверный период!"

    start_date_str = start_date.strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT date, SUM(count) FROM statistics WHERE date >= ?
        GROUP BY date
    ''', (start_date_str,))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "Нет данных за выбранный период!"
    
    report = f"Статистика за {period}:\n"
    for row in results:
        report += f"{row[0]}: {row[1]} сообщений\n"
    return report

# Обработчик команды start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Отправь '+' для записи статистики.")

# Обработчик команды report
def report(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("Используй: /report [week|month|year]")
        return
    
    period = args[0]
    report_data = get_report(period)
    update.message.reply_text(report_data)

# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    if update.message.text == "+":
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        date = datetime.now().strftime('%Y-%m-%d')
        
        record_data(user_id, username, date)
        update.message.reply_text("Записано!")

# Основная функция
def main():
    # Замените TOKEN на токен вашего бота
    TOKEN = "7609323848:AAEi4fr8Bv6sVkKPNVa_mwBigc5lcVh2K2c"
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # Инициализация базы данных
    init_db()
    
    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("report", report))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
