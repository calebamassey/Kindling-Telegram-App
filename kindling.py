from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import asyncio
import random

promptCount = -1
jsonFileName = './info.json'
timeZone = "EST"
timeHour1 = 12
timeMinute1 = 12
timeHour2 = 12
timeMinute2 = 13
promptList = [
    "What's one small thing I did recently that made you smile?",
    "If we could teleport anywhere right now for a date, where would we go?",
    "What’s a song that makes you think of me—and why?",
    "Describe your dream weekend getaway for just the two of us.",
    "If our relationship were a movie, what genre would it be and what’s the title?",
    "What’s something you want us to learn or try together this year?",
    "When did you first realize you liked me more than just a little?",
    "What’s your favorite physical touch or gesture from me?",
    "If we had a pet together right now, what would we name it?",
    "What's one way we could make each other feel even more loved this week?",
    "If we had a couple's bucket list, what’s one thing you’d put on it today?",
    "What's something small but meaningful we could do for each other tonight?"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(getPrompt())


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")


async def send_prompt(bot, chat_id):
    await bot.send_message(chat_id=chat_id, text=getPrompt())


async def post_init(application: Application):
    chat_id = getChatID()
    if chat_id:
        start_scheduler(application.bot, chat_id, asyncio.get_running_loop())
    else:
        print("No chat ID found in JSON.")


def start_scheduler(bot, chat_id, loop):
    scheduler = BackgroundScheduler(timezone=timeZone)
    trigger = CronTrigger(hour=timeHour1, minute=timeMinute1)
    trigger2 = CronTrigger(hour=timeHour2, minute=timeMinute2)

    def job_wrapper():
        asyncio.run_coroutine_threadsafe(
            send_prompt(bot, chat_id),
            loop
        )

    scheduler.add_job(job_wrapper, trigger, id="first_prompt", replace_existing=True)
    scheduler.add_job(job_wrapper, trigger2, id="second_prompt", replace_existing=True)
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

def randomizePrompt():
    return random.sample(promptList, len(promptList))  # cleaner shuffle without modifying original

def getPrompt():
    global promptCount, randomPromptList

    if promptCount == -1 or promptCount >= len(promptList):
        randomPromptList = randomizePrompt()
        promptCount = 0
        return getPrompt()
    else:
        prompt = randomPromptList[promptCount]
        promptCount += 1
        return prompt