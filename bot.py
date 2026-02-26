import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# گرفتن توکن و آیدی از Variables
TOKEN = os.environ.get("BOT_TOKEN")          # Variable توکن
ADMIN_ID = int(os.environ.get("ADMIN_ID"))   # Variable آیدی عددی خودت

if TOKEN is None or ADMIN_ID is None:
    raise ValueError("BOT_TOKEN یا ADMIN_ID در Variables تنظیم نشده!")

# پاسخ به دستورات /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("بات فعال است و آماده ارسال پیام به کاربران.")
    else:
        await update.message.reply_text("شما مجاز به استفاده از این بات نیستید.")

# دریافت پیام از کاربران و فوروارد به ADMIN_ID
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    # فقط پیام‌ها از کاربران دیگه به ADMIN_ID فرستاده میشه
    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"پیام از {user.username or user.first_name} ({user.id}): {text}")
        await update.message.reply_text("پیام شما ارسال شد!")

# ارسال پاسخ از ADMIN_ID به کاربر مشخص
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # فقط Admin می‌تواند پاسخ بده
    if len(context.args) < 2:
        await update.message.reply_text("استفاده: /reply <user_id> <پیام>")
        return
    user_id = int(context.args[0])
    reply_text = " ".join(context.args[1:])
    await context.bot.send_message(chat_id=user_id, text=reply_text)
    await update.message.reply_text("پیام ارسال شد!")

# ایجاد برنامه و ثبت هندلرها
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", reply_to_user))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

if __name__ == "__main__":
    print("بات در حال اجراست...")
    app.run_polling()