import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot.services.analytics_service import gather_analytics
from bot.db import AsyncSessionLocal
from bot.core import settings

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id in settings.ALLOWED_USER_IDS:
        async with AsyncSessionLocal() as session:
            report = await gather_analytics(session)
        await update.message.reply_text(report, parse_mode="HTML")
    else:
        await update.message.reply_text("You are not authorized to use this command. \n\nContact @AnatolyVarkus")

def run():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()