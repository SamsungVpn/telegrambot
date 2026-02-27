import asyncio
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# ===== تنظیمات logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===== خواندن توکن و آی‌دی از Variable های Railway =====
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# ===== لیست کاربرهایی که قبلاً /start زدن =====
started_users = set()

# ===== دکمه‌های شیشه‌ای کاربران =====
def user_menu():
    keyboard = [
        [InlineKeyboardButton("📩 ارسال پیام", callback_data="send_message")],
        [InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== دکمه‌های شیشه‌ای پنل مدیر =====
def admin_menu():
    keyboard = [
        [InlineKeyboardButton("👁️ مشاهده کاربران", callback_data="view_users")],
        [InlineKeyboardButton("✉️ ارسال به همه", callback_data="broadcast")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== تابع /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # مدیر
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 پنل مدیریت فعال شد.",
            reply_markup=admin_menu()
        )
        return

    final_text = f"""
🎉 خوش اومدی {user.first_name}!

🤖 این ربات برای ارتباط مستقیم با پشتیبانی ساخته شده.

💬 روی دکمه زیر بزن و پیامتو بفرست 👇
"""

    # فقط بار اول لودینگ اجرا میشه
    if user.id not in started_users:
        started_users.add(user.id)

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        msg = await update.message.reply_text("🔄 در حال آماده‌سازی حساب کاربری")

        # افکت لودینگ
        for i in range(6):
            dots = "." * (i % 4)
            await msg.edit_text(f"🔄 در حال آماده‌سازی حساب کاربری{dots}")
            await asyncio.sleep(0.5)

        # جایگزین متن لودینگ با متن نهایی و دکمه‌ها
        try:
            await msg.edit_text(final_text, reply_markup=user_menu())
        except:
            # اگر edit_text مشکل داشت، پیام جدید بفرست
            await update.message.reply_text(final_text, reply_markup=user_menu())
    else:
        await update.message.reply_text(final_text, reply_markup=user_menu())

# ===== هندلر کلیک دکمه‌ها =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "send_message":
        await query.message.reply_text("💬 لطفاً پیام خود را ارسال کنید (نمونه).")
    elif query.data == "about":
        await query.message.reply_text("ℹ️ این ربات نمونه برای خوش‌آمدگویی و منو است.")
    elif query.data == "view_users" and query.from_user.id == ADMIN_ID:
        await query.message.reply_text(f"👥 کاربران فعلی: {len(started_users)} نفر")
    elif query.data == "broadcast" and query.from_user.id == ADMIN_ID:
        await query.message.reply_text("✉️ ارسال به همه (نمونه، هنوز عملیاتی نیست).")

# ===== اجرای بات =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()