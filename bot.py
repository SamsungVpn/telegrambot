import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

if TOKEN is None or ADMIN_ID is None:
    raise ValueError("BOT_TOKEN یا ADMIN_ID تنظیم نشده!")

# ذخیره کاربران
users = {}
current_target = None


# منوی ادمین
def admin_menu():
    keyboard = [
        [KeyboardButton("📋 لیست کاربران")],
        [KeyboardButton("❌ لغو انتخاب")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            "بات فعال است 👌",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text("سلام! پیام خود را ارسال کنید.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_target

    user = update.effective_user
    text = update.message.text

    # اگر کاربر عادی پیام داد
    if user.id != ADMIN_ID:
        users[user.id] = user.first_name
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 پیام از {user.first_name} ({user.id}):\n{text}"
        )
        await update.message.reply_text("پیام شما ارسال شد ✅")
        return

    # اگر ادمین پیام داد
    if text == "📋 لیست کاربران":
        if not users:
            await update.message.reply_text("هیچ کاربری پیام نداده.")
            return

        keyboard = []
        for uid, name in users.items():
            keyboard.append([KeyboardButton(f"{name} | {uid}")])

        await update.message.reply_text(
            "یکی را انتخاب کن 👇",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    if text == "❌ لغو انتخاب":
        current_target = None
        await update.message.reply_text(
            "انتخاب لغو شد.",
            reply_markup=admin_menu()
        )
        return

    # اگر ادمین یکی از کاربران را انتخاب کند
    if "|" in text:
        try:
            uid = int(text.split("|")[1].strip())
            current_target = uid
            await update.message.reply_text(
                f"کاربر انتخاب شد ✅\nحالا پیام بنویس.",
                reply_markup=admin_menu()
            )
        except:
            pass
        return

    # اگر ادمین پیام معمولی بفرستد و کاربری انتخاب شده باشد
    if current_target:
        await context.bot.send_message(chat_id=current_target, text=text)
        await update.message.reply_text("پیام ارسال شد ✅")
    else:
        await update.message.reply_text("اول یک کاربر انتخاب کن.", reply_markup=admin_menu())


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

if __name__ == "__main__":
    print("بات در حال اجراست...")
    app.run_polling()