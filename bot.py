import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# گرفتن توکن و آیدی ادمین از متغیر محیطی
TOKEN = os.environ.get("8617460304:AAE5N0Ye2XU9OvrB9NI_2t-IYBbMdXa4-5Y")
ADMIN_ID = int(os.environ.get("594994498"))

# تابع شروع بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من بات تو هستم. پیام بده!")

# وقتی کسی به بات پیام میده
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # فقط پیام‌ها رو به ادمین فوروارد کن
    if user_id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"پیام از {update.message.from_user.first_name} ({user_id}):\n{text}")
        await update.message.reply_text("پیامت به ادمین ارسال شد!")
    else:
        await update.message.reply_text("تو خودت ادمین هستی.")

# راه‌اندازی بات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()