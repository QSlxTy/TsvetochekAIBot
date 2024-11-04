from datetime import timedelta, datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers import SchedulerAlreadyRunningError

from bot_start import bot, scheduler
from utils.all_text import no_answer_notify


async def reg_notify(user_id, test):
    await bot.send_message(chat_id=user_id, text=no_answer_notify)


async def create_reg_notify(user_id):
    run_date = datetime.now() + timedelta(minutes=10)
    try:
        scheduler.add_job(reg_notify, "date", run_date=run_date, args=(user_id,0), id=str(user_id))
    except (SchedulerAlreadyRunningError, ConflictingIdError):
        scheduler.remove_job(str(user_id))
        scheduler.add_job(reg_notify, "date", run_date=run_date, args=(user_id,0), id=str(user_id))


async def remove_reg_notify(user_id):
    scheduler.remove_job(str(user_id))
