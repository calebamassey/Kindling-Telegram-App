from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import asyncio


jsonFileName = './info.json'
timeHour1 = 20
timeMinute1 = 32

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I will send 'Hello World' every day at the scheduled time.")


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")


async def send_hello_world(bot, chat_id):
    await bot.send_message(chat_id=chat_id, text="Hello World")


async def post_init(application: Application):
    chat_id = getChatID()
    if chat_id:
        start_scheduler(application.bot, chat_id, asyncio.get_running_loop())
    else:
        print("No chat ID found in JSON.")


def start_scheduler(bot, chat_id, loop):
    scheduler = BackgroundScheduler(timezone="UTC")
    trigger = CronTrigger(hour=timeHour1, minute=timeMinute1)

    def job_wrapper():
        asyncio.run_coroutine_threadsafe(
            send_hello_world(bot, chat_id),
            loop
        )

    scheduler.add_job(job_wrapper, trigger, id="daily_hello_world", replace_existing=True)
    scheduler.start()


def getToken():
    try:
        with open(jsonFileName, 'r') as file:
            data = json.load(file)
            return data.get('token')
    except Exception as e:
        print(f"Error loading token: {e}")
        return None


def getChatID():
    try:
        with open(jsonFileName, 'r') as file:
            data = json.load(file)
            return data.get('chat_id')
    except Exception as e:
        print(f"Error loading chat id: {e}")
        return None


def startBot():
    TOKEN = getToken()
    if not TOKEN:
        print("Missing token.")
        return

    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chatid", chat_id))

    application.run_polling()


if __name__ == "__main__":
    startBot()
