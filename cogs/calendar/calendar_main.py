import asyncio
from globals import *
from time import sleep
from datetime import date, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler import events
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobExecutionEvent
from apscheduler.triggers.date import DateTrigger

from discord.ext import commands
from calendar.academic_cal import events_from_webpage

schedule = BackgroundScheduler()

class AcadCal(commands.Cog) :
    def __init__(self, bot):
        self.bot = bot
        self.events = []
    
    async def send_to_channel(channel_id: int, event: str) -> None:
        print("txt")

    async def read_dates(self, dates: list):
        channel_id = 123456

        for date in dates:
            schedule.add_job(self.send_to_channel, 'date', run_date = date['date'],
                            kwargs={ "channel_id" : channel_id, "event" : date['event']})
            schedule.start()

        return

async def setup(bot):
    await bot.add_cog(AcadCal(bot))
