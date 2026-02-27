import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# کاربران و وضعیت پیام‌ها
users = {}  # user_id: {"name": ..., "pending": False}

# کاربر فعلی که مدیر قراره براش پیام بده
current_chat_user = None

# ===== دکمه‌های کاربر =====
def user_menu():
    keyboard = [
        [InlineKeyboardButton("📩 ارسال پیام", callback_data="send_message")],
        [InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== دکمه‌های پنل مدیر =====
def admin_menu():
    buttons = []
    for uid, info in users.items():
        buttons.append([InlineKeyboardButton(f"{info['name']}", callback_data=f"user_{uid}")])
    return InlineKeyboardMarkup(buttons)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # مدیر
    if user.id == ADMIN_ID:
        await update.message.reply_text("👑 پنل مدیریت فعال شد.", reply_markup=admin_menu())
        return

    # ذخیره کاربر
    if user.id not in users:
        users[user.id] = {"name": user.first_name, "pending": False}

    # پیام خوش‌آمدگویی مستقیم
    final_text = f"""
🎉 خوش اومدی {user.first_name}!

🤖 این ربات برای ارتباط مستقیم با پشتیبانی ساخته شده.
💬 روی دکمه زیر بزن و پیامتو بفرست 👇
"""
    await update.message.reply_text(final_text, reply_markup=user_menu())

# ===== هندلر کلیک دکمه‌ها =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_chat_user
    query = update.callback_query
    await query.answer()
    data = query.data

    # دکمه‌های کاربر
    if data == "send_message":
        users[query.from_user.id]["pending"] = True
        await query.message.reply_text("💬 لطفاً پیام خود را ارسال کنید.")
    elif data == "about":
        await query.message.reply_text("ℹ️ این ربات نمونه برای خوش‌آمدگویی و منو است.")

    # دکمه‌های مدیر
    elif data.startswith("user_") and query.from_user.id == ADMIN_ID:
        uid = int(data.split("_")[1])
        current_chat_user = uid
        await query.message.reply_text(f"💬 اکنون پیام‌های شما فقط برای {users[uid]['name']} ارسال می‌شود.")

# ===== دریافت پیام =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_chat_user
    user_id = update.effective_user.id
    text = update.message.text

    # پیام کاربر به ادمین
    if user_id in users and users[user_id]["pending"]:
        users[user_id]["pending"] = False
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 پیام از {users[user_id]['name']}:\n{text}")
        await update.message.reply_text("✅ پیام شما ارسال شد.")
        return

    # پیام مدیر به کاربر انتخابی
    if user_id == ADMIN_ID and current_chat_user is not None:
        if current_chat_user in users:
            await context.bot.send_message(chat_id=current_chat_user, text=f"💬 پاسخ مدیر:\n{text}")
            await update.message.reply_text("✅ پیام ارسال شد.")
        else:
            await update.message.reply_text("❌ کاربر یافت نشد.")

# ===== اجرای بات =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()